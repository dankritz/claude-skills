# Claude Skills Collection

This is a private repository that collects all the Claude Code skills I find useful.

## Setup

The skills in this repo are automatically available to Claude Code via a symlink:
```
~/.claude/skills -> /path/to/claude-skills/skills
```

## Available Skills

### ai-agent-builder
Use when building AI agents from Jira tickets. Reads ticket requirements, Confluence agent cards, creates implementation plans, and builds n8n workflows with Jira updates.

### frontend-design
Create distinctive, production-grade frontend interfaces with high design quality. Generates creative, polished code that avoids generic AI aesthetics.

### n8n-code-javascript
Write JavaScript code in n8n Code nodes. Use when writing JavaScript in n8n, using $input/$json/$node syntax, making HTTP requests with $helpers, working with dates using DateTime, troubleshooting Code node errors, or choosing between Code node modes.

### n8n-code-python
Write Python code in n8n Code nodes. Use when writing Python in n8n, using _input/_json/_node syntax, working with standard library, or need to understand Python limitations in n8n Code nodes.

### n8n-expression-syntax
Validate n8n expression syntax and fix common errors. Use when writing n8n expressions, using {{}} syntax, accessing $json/$node variables, troubleshooting expression errors, or working with webhook data in workflows.

### n8n-mcp-tools-expert
Expert guide for using n8n-mcp MCP tools effectively. Use when searching for nodes, validating configurations, accessing templates, managing workflows, or using any n8n-mcp tool. Provides tool selection guidance, parameter formats, and common patterns.

### n8n-node-configuration
Operation-aware node configuration guidance. Use when configuring nodes, understanding property dependencies, determining required fields, choosing between get_node detail levels, or learning common configuration patterns by node type.

### n8n-validation-expert
Interpret validation errors and guide fixing them. Use when encountering validation errors, validation warnings, false positives, operator structure issues, or need help understanding validation results. Also use when asking about validation profiles, error types, or the validation loop process.

### n8n-workflow-patterns
Proven workflow architectural patterns from real n8n workflows. Use when building new workflows, designing workflow structure, choosing workflow patterns, planning workflow architecture, or asking about webhook processing, HTTP API integration, database operations, AI agent workflows, or scheduled tasks.

### youtube-transcript
Download YouTube video transcripts using yt-dlp. Supports manual subtitles, auto-generated captions, and Whisper transcription as fallback. Automatically converts VTT to plain text with deduplication.

## Usage

Skills are automatically loaded by Claude Code from the `skills/` directory. Each skill is contained in its own subdirectory with a `SKILL.md` file.
