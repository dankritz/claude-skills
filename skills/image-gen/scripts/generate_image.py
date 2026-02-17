#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "requests>=2.31.0",
#   "pillow>=10.0.0",
#   "python-dotenv>=1.0.0",
# ]
# ///
"""
Generate or edit images using Google's gemini-3-pro-image-preview via OpenRouter.

Usage:
  # Generate a new image
  uv run generate_image.py --prompt "description" --filename "output.png"

  # Edit an existing image
  uv run generate_image.py --prompt "instructions" --filename "output.png" --input-image "source.png"
"""

import argparse
import base64
import json
import os
import sys
from io import BytesIO
from pathlib import Path


OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-3-pro-image-preview"


def load_env():
    """Search for .env in cwd, skill dir, and home dir, load the first one found."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("Warning: python-dotenv not available, skipping .env load.", file=sys.stderr)
        return

    search_paths = [
        Path.cwd() / ".env",
        Path(__file__).parent.parent / ".env",  # skills/image-gen/.env
        Path.home() / ".env",
    ]

    for path in search_paths:
        if path.exists():
            load_dotenv(path)
            print(f"Loaded .env: {path}", file=sys.stderr)
            return

    print("Warning: No .env file found. Relying on environment variables.", file=sys.stderr)


def get_api_key(provided_key: str | None) -> str | None:
    if provided_key:
        return provided_key
    return os.environ.get("OPENROUTER_API_KEY")


def encode_image(image_path: str) -> tuple[str, str]:
    """Load an image, normalise to RGB PNG, and return (base64_string, mime_type)."""
    from PIL import Image as PILImage

    try:
        img = PILImage.open(image_path)
    except Exception as e:
        print(f"Error opening image '{image_path}': {e}", file=sys.stderr)
        sys.exit(1)

    # Flatten transparency onto white background
    if img.mode in ("RGBA", "LA", "P"):
        bg = PILImage.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        if img.mode in ("RGBA", "LA"):
            bg.paste(img, mask=img.split()[-1])
        else:
            bg.paste(img)
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    return b64, "image/png"


def save_image_bytes(image_bytes: bytes, output_path: Path):
    """Save raw image bytes as PNG, handling mode conversion."""
    from PIL import Image as PILImage

    img = PILImage.open(BytesIO(image_bytes))

    if img.mode == "RGBA":
        bg = PILImage.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        bg.save(str(output_path), "PNG")
    elif img.mode == "RGB":
        img.save(str(output_path), "PNG")
    else:
        img.convert("RGB").save(str(output_path), "PNG")


def save_image(b64_data: str, output_path: Path):
    """Decode a base64 image (with or without data-URL prefix) and save as PNG."""
    if "," in b64_data:
        b64_data = b64_data.split(",", 1)[1]
    save_image_bytes(base64.b64decode(b64_data), output_path)


def try_decode_as_image(b64_data: str) -> bytes | None:
    """Attempt to base64-decode and open with PIL. Returns raw bytes or None."""
    from PIL import Image as PILImage, UnidentifiedImageError

    try:
        raw = base64.b64decode(b64_data)
        PILImage.open(BytesIO(raw)).verify()  # raises if not a valid image
        return raw
    except Exception:
        return None


def extract_image_from_response(data: dict) -> bytes | None:
    """
    Walk the response looking for image data.
    OpenRouter/Gemini may return images in several formats:
      - choices[0].message.content: list of parts with type "image_url" or "image"
      - choices[0].message.content: plain base64 data-URL string
      - choices[0].message.reasoning_details: list where an item has a "data" field
        containing the base64-encoded image (observed with google/gemini-3-pro-image-preview)
    Returns raw image bytes, or None.
    """
    try:
        message = data["choices"][0]["message"]
    except (KeyError, IndexError):
        return None

    content = message.get("content", "")

    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue

            part_type = part.get("type", "")

            if part_type == "image_url":
                url = part.get("image_url", {}).get("url", "")
                if url.startswith("data:image"):
                    b64 = url.split(",", 1)[1] if "," in url else url
                    raw = try_decode_as_image(b64)
                    if raw:
                        return raw

            elif part_type == "image":
                # Google-style: {"type": "image", "image": {"data": "<b64>", ...}}
                b64 = (
                    part.get("data")
                    or part.get("image", {}).get("data")
                    or part.get("image", {}).get("url", "")
                )
                if b64:
                    raw = try_decode_as_image(b64)
                    if raw:
                        return raw

            elif part_type == "text":
                # Sometimes the image is embedded as a data-URL inside the text part
                text = part.get("text", "")
                if text.startswith("data:image"):
                    b64 = text.split(",", 1)[1] if "," in text else text
                    raw = try_decode_as_image(b64)
                    if raw:
                        return raw

    elif isinstance(content, str) and content.startswith("data:image"):
        b64 = content.split(",", 1)[1] if "," in content else content
        raw = try_decode_as_image(b64)
        if raw:
            return raw

    # OpenRouter puts Gemini-generated images in message.images[]
    # (non-standard field, observed with google/gemini-3-pro-image-preview)
    for img_entry in message.get("images", []):
        url = img_entry.get("image_url", {}).get("url", "")
        if url:
            b64 = url.split(",", 1)[1] if "," in url else url
            raw = try_decode_as_image(b64)
            if raw:
                return raw

    return None


def print_text_from_response(data: dict):
    """Print any text parts from the response to stdout."""
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return

    if isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                text = part.get("text", "").strip()
                if text:
                    print(f"Model: {text}")
    elif isinstance(content, str) and not content.startswith("data:image"):
        print(f"Model: {content}")


def main():
    load_env()

    parser = argparse.ArgumentParser(
        description="Generate or edit images using gemini-3-pro-image-preview via OpenRouter"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Image description or editing instructions")
    parser.add_argument("--filename", "-f", required=True, help="Output file path (e.g. my-image.png)")
    parser.add_argument("--input-image", "-i", help="Path to source image for editing mode")
    parser.add_argument("--api-key", "-k", help="OpenRouter API key (overrides .env / env var)")

    args = parser.parse_args()

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set.", file=sys.stderr)
        print("Add it to a .env file in your working directory or pass --api-key.", file=sys.stderr)
        sys.exit(1)

    import requests

    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build the user message content
    if args.input_image:
        print(f"Mode: editing  |  Source: {args.input_image}", file=sys.stderr)
        b64_image, mime_type = encode_image(args.input_image)
        content = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{b64_image}"},
            },
            {
                "type": "text",
                "text": args.prompt,
            },
        ]
    else:
        print("Mode: generation", file=sys.stderr)
        content = args.prompt

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": content}],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/claude-skills/image-gen",
        "X-Title": "Claude Image Gen Skill",
    }

    print(f"Calling OpenRouter ({MODEL})...", file=sys.stderr)

    try:
        resp = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=180,
        )
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        try:
            print(f"Response body: {resp.text}", file=sys.stderr)
        except Exception:
            pass
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)

    data = resp.json()

    # Print any text the model returned
    print_text_from_response(data)

    # Extract and save the image
    image_bytes = extract_image_from_response(data)

    if image_bytes:
        save_image_bytes(image_bytes, output_path)
        print(f"\nImage saved: {output_path.resolve()}")
    else:
        print("Error: No image found in the API response.", file=sys.stderr)
        print("Full response:", file=sys.stderr)
        print(json.dumps(data, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
