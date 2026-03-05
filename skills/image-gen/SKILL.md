---
name: image-gen
description: Generate new images from text prompts or edit existing images using Google Gemini via OpenRouter. Use when the user wants to create, generate, or edit images. Requires OPENROUTER_API_KEY in a .env file.
allowed-tools: Bash
---

# Image Generation & Editing Skill

Generate new images from text prompts or edit/modify existing images using Google's `gemini-3.1-flash-image-preview` model via the OpenRouter API.

---

## Setup

Create a `.env` file in your working directory containing your OpenRouter API key:

```
OPENROUTER_API_KEY=sk-or-your-key-here
```

Get an API key at https://openrouter.ai/settings/keys

---

## Command Structure

The script uses [PEP 723 inline metadata](https://peps.python.org/pep-0723/) and can be run two ways:

**Preferred (auto-installs dependencies via uv):**
```bash
uv run ~/.claude/skills/image-gen/scripts/generate_image.py \
  --prompt "your image description" \
  --filename "output.png"
```

**Alternative (requires requests, pillow, python-dotenv already installed):**
```bash
python3 ~/.claude/skills/image-gen/scripts/generate_image.py \
  --prompt "your image description" \
  --filename "output.png"
```

**Generate a new image (uv):**
```bash
uv run ~/.claude/skills/image-gen/scripts/generate_image.py \
  --prompt "your image description" \
  --filename "output.png"
```

**Edit an existing image (uv):**
```bash
uv run ~/.claude/skills/image-gen/scripts/generate_image.py \
  --prompt "editing instructions" \
  --filename "output.png" \
  --input-image "path/to/source.png"
```

---

## Parameters

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--prompt` | `-p` | Yes | Text description (generation) or editing instructions (editing) |
| `--filename` | `-f` | Yes | Output file path (e.g., `image.png` or `outputs/my-image.png`) |
| `--input-image` | `-i` | No | Path to existing image — activates editing mode |
| `--api-key` | `-k` | No | Override the `.env` API key |

---

## Filename Convention

Use timestamps to avoid collisions:

```
yyyy-mm-dd-hh-mm-ss-descriptive-name.png
```

Example: `2025-01-15-14-30-00-sunset-mountains.png`

Derive the descriptive name from the user's prompt.

---

## Behavior Rules

1. **Always run from the user's current working directory** — the script searches for `.env` there first
2. **For editing**: pass the path to the input image directly; do not pre-read or base64-encode it yourself
3. **For generation**: use a clear, descriptive prompt; include style, lighting, mood, and subject details for best results
4. **If no image is produced**: the script will print the full API response to help diagnose the issue

---

## Model Capabilities

`google/gemini-3.1-flash-image-preview` supports:
- Text-to-image generation at high fidelity
- Image-to-image editing with fine-grained control
- Style transfers, lighting adjustments, background changes
- Text rendering in images (multilingual)
- Identity preservation across subjects
- Localized edits (change one part of an image)

---

## Examples

**User:** "Generate a photo of a red fox sitting in a snowy forest at dawn"
```bash
uv run ~/.claude/skills/image-gen/scripts/generate_image.py \
  --prompt "A red fox sitting in a snowy forest at dawn, golden light filtering through pine trees, photorealistic" \
  --filename "2025-01-15-09-00-00-red-fox-snowy-forest.png"
```

**User:** "Edit this image to add a sunset sky"
```bash
uv run ~/.claude/skills/image-gen/scripts/generate_image.py \
  --prompt "Replace the sky with a vibrant orange and pink sunset, keep everything else the same" \
  --filename "2025-01-15-09-01-00-sunset-edit.png" \
  --input-image "original.png"
```
