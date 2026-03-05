# Claude Skills Collection

This is a private repository that collects all the Claude Code skills I find useful.

## Setup

The skills in this repo are automatically available to Claude Code via a symlink:
```
~/.claude/skills -> /path/to/claude-skills/skills
```

## Available Skills

### SlopRadar
Comprehensive security audit skill. Scopes a target project, launches 5 parallel specialist agents (secrets management, input validation & injection, authentication & authorization, code execution & sandbox, infrastructure & CI/CD), and compiles all findings into a `security-review.md` in the project root. Use when running a security review or vulnerability assessment on any codebase.

### frontend-design
Create distinctive, production-grade frontend interfaces with high design quality. Generates creative, polished code that avoids generic AI aesthetics.

### image-gen
Generate and edit images using Google Gemini via OpenRouter. Requires `OPENROUTER_API_KEY` in a `.env` file.

### tibber
Query the Tibber electricity API to analyze power consumption, costs, and price trends. Requires a Tibber API token — get one at https://developer.tibber.com/settings/access-token and add it to `skills/tibber/.env` (see `.env-template`).

### youtube-transcript
Download YouTube video transcripts using yt-dlp. Supports manual subtitles, auto-generated captions, and Whisper transcription as fallback. Automatically converts VTT to plain text with deduplication.

## Usage

Skills are automatically loaded by Claude Code from the `skills/` directory. Each skill is contained in its own subdirectory with a `SKILL.md` file.
