# Claude Skills Management

This repository manages all Claude Code and Claude Desktop skills in a centralized location. Skills are automatically loaded through symlinks, making them available across all Claude sessions.

## How It Works

### Architecture

Claude Code and Claude Desktop both support loading custom skills from a `skills/` directory. This repo uses symlinks to make the same skills available to both applications:

```
claude-skills/skills/          # Git repository (source of truth)
    ├── frontend-design/
    ├── n8n-code-javascript/
    ├── youtube-transcript/
    └── ...

~/.claude/skills               # Symlink → claude-skills/skills/
                              # (Used by Claude Code CLI)

~/Library/Application Support/Claude/skills
                              # Symlink → claude-skills/skills/
                              # (Used by Claude Desktop app)
```

**Benefits:**
- Single source of truth in git
- Skills automatically available in both Claude Code and Claude Desktop
- Version controlled with git (commit history, branches, rollback)
- Easy to share and sync across machines
- Changes pushed to remote are available on all your devices

### Skill Structure

Each skill is a directory containing a `SKILL.md` file with frontmatter:

```markdown
---
name: skill-name
description: When to use this skill
allowed-tools: Bash,Read,Write
---

# Skill Content
Instructions for Claude on how to perform the skill...
```

## Initial Setup

### Prerequisites

- Claude Code CLI installed
- Claude Desktop app installed (optional)
- Git configured with authentication

### Installation Steps

1. **Clone this repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/claude-skills.git ~/git/claude-skills
   cd ~/git/claude-skills
   ```

2. **Create symlink for Claude Code:**
   ```bash
   ln -s ~/git/claude-skills/skills ~/.claude/skills
   ```

3. **Create symlink for Claude Desktop (optional):**
   ```bash
   ln -s ~/git/claude-skills/skills ~/Library/Application\ Support/Claude/skills
   ```

4. **Verify symlinks:**
   ```bash
   ls -l ~/.claude/skills
   ls -l ~/Library/Application\ Support/Claude/skills
   ```

   Both should point to: `/Users/YOUR_USERNAME/git/claude-skills/skills`

5. **Restart Claude Desktop** (if applicable) to load the skills

## Adding New Skills

### Automated Workflow (Preferred)

When you find a skill you want to add, simply ask Claude Code:

> "Download and activate the skill from [GitHub URL]"

Claude will automatically:
1. Download the skill files to `skills/SKILL_NAME/`
2. Update the README.md with the skill description
3. Commit the changes with a descriptive message
4. Push to the remote repository

**Example:**
```
You: Download and activate this skill:
     https://github.com/user/repo/tree/main/skill-name

Claude:
  1. Downloads skill-name to skills/skill-name/
  2. Updates README.md
  3. Commits: "Add skill-name skill"
  4. Pushes to origin/main
  5. Skill is now available globally
```

### Manual Workflow

If you need to add a skill manually:

1. **Create the skill directory:**
   ```bash
   mkdir -p skills/my-new-skill
   ```

2. **Create the SKILL.md file:**
   ```bash
   cat > skills/my-new-skill/SKILL.md << 'EOF'
   ---
   name: my-new-skill
   description: What this skill does and when to use it
   allowed-tools: Bash,Read,Write
   ---

   # Skill Instructions
   Detailed instructions for Claude...
   EOF
   ```

3. **Update README.md:**
   Add an entry in the "Available Skills" section

4. **Commit and push:**
   ```bash
   git add skills/my-new-skill/ README.md
   git commit -m "Add my-new-skill"
   git push origin main
   ```

5. **Verify the skill is available:**
   ```bash
   ls -la ~/.claude/skills/my-new-skill/
   ```

## Using Skills

### In Claude Code

Skills are automatically detected and shown in system reminders. Claude will suggest relevant skills based on your requests.

**Invoke a skill explicitly:**
```bash
/skill-name
```

**Or simply ask:**
```
"Help me download a YouTube transcript"
# Claude automatically invokes the youtube-transcript skill
```

### In Claude Desktop

Skills work the same way in Claude Desktop. The app will automatically detect and suggest skills based on context.

## Managing Skills

### Updating an Existing Skill

1. **Edit the skill file:**
   ```bash
   # Edit directly
   code skills/skill-name/SKILL.md

   # Or let Claude do it
   "Update the youtube-transcript skill to support playlists"
   ```

2. **Commit and push:**
   ```bash
   git add skills/skill-name/
   git commit -m "Update skill-name: add playlist support"
   git push origin main
   ```

### Removing a Skill

1. **Delete the skill directory:**
   ```bash
   git rm -r skills/skill-name/
   ```

2. **Update README.md:**
   Remove the skill entry from "Available Skills"

3. **Commit and push:**
   ```bash
   git add README.md
   git commit -m "Remove skill-name skill"
   git push origin main
   ```

### Viewing All Skills

```bash
# List all skill directories
ls -1 skills/

# View skill frontmatter
head -n 10 skills/*/SKILL.md
```

## Syncing Across Machines

Since skills are stored in git, syncing to another machine is simple:

**On a new machine:**

1. Clone the repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/claude-skills.git ~/git/claude-skills
   ```

2. Create symlinks:
   ```bash
   ln -s ~/git/claude-skills/skills ~/.claude/skills
   ln -s ~/git/claude-skills/skills ~/Library/Application\ Support/Claude/skills
   ```

3. Restart Claude Desktop (if applicable)

**To sync changes:**
```bash
cd ~/git/claude-skills
git pull origin main
```

Changes are automatically reflected in both Claude Code and Claude Desktop through the symlinks.

## Troubleshooting

### Skills Not Loading

1. **Verify symlinks exist:**
   ```bash
   ls -l ~/.claude/skills
   ls -l ~/Library/Application\ Support/Claude/skills
   ```

2. **Check symlink targets:**
   Both should point to your skills directory:
   ```
   ~/.claude/skills -> /Users/YOUR_USERNAME/git/claude-skills/skills
   ```

3. **Verify skills directory has content:**
   ```bash
   ls -la ~/git/claude-skills/skills/
   ```

4. **Restart Claude Desktop:**
   Close and reopen the app to reload skills

5. **Check skill file format:**
   Ensure `SKILL.md` has valid frontmatter with `---` delimiters

### Symlink Issues

**Error: File exists**
```bash
# Remove existing symlink/directory
rm ~/.claude/skills

# Create new symlink
ln -s ~/git/claude-skills/skills ~/.claude/skills
```

**Error: Permission denied**
```bash
# Check directory permissions
ls -la ~/.claude/

# Ensure you have write access
chmod 755 ~/.claude/
```

### Git Issues

**Push rejected:**
```bash
# Pull latest changes first
cd ~/git/claude-skills
git pull --rebase origin main
git push origin main
```

**Merge conflicts:**
```bash
# Resolve conflicts manually
git status
# Edit conflicting files
git add .
git rebase --continue
git push origin main
```

## Best Practices

1. **Commit frequently:** Each skill addition/update should be its own commit
2. **Descriptive commit messages:** Use the format "Add/Update/Remove skill-name: brief description"
3. **Update README.md:** Always keep the skill list synchronized
4. **Test locally first:** Verify a skill works before pushing
5. **Use branches for experiments:** Create feature branches for testing new skills
6. **Keep skills focused:** One skill = one specific capability
7. **Document dependencies:** Note any required tools or setup in the skill

## Advanced Usage

### Skill Development Workflow

```bash
# Create a feature branch
git checkout -b add-new-skill

# Develop the skill
mkdir -p skills/new-skill
# ... create SKILL.md

# Test locally
# (symlinks automatically reflect changes)

# Commit when satisfied
git add skills/new-skill/ README.md
git commit -m "Add new-skill: description"

# Push to remote
git push origin add-new-skill

# Merge to main
git checkout main
git merge add-new-skill
git push origin main
```

### Sharing Skills

This repo can be:
- Made public to share with others
- Forked by team members
- Used as a template for personal skill collections

### Backup Strategy

Since skills are in git:
- Remote repository = automatic backup
- Can push to multiple remotes (GitHub, GitLab, etc.)
- Can clone to multiple machines for redundancy

## Integration with Claude

When you ask Claude to "download and activate a skill", Claude will:

1. **Download:** Use `curl` or `git` to fetch the skill
2. **Place:** Create directory in `skills/SKILL_NAME/`
3. **Document:** Update `README.md` with skill description
4. **Commit:** Create a descriptive commit message with Co-Authored-By tag
5. **Push:** Push to `origin/main`
6. **Verify:** Confirm the skill is available via symlink

The entire process is automated - you just provide the URL.

## Repository Structure

```
claude-skills/
├── CLAUDE.md           # This file (how-to guide)
├── README.md           # Public-facing documentation
├── skills/             # All skills (symlinked to Claude)
│   ├── frontend-design/
│   │   └── SKILL.md
│   ├── n8n-code-javascript/
│   │   ├── SKILL.md
│   │   ├── DATA_ACCESS.md
│   │   └── ...
│   ├── youtube-transcript/
│   │   └── SKILL.md
│   └── ...
└── .git/              # Git version control
```

## Configuration Files

### Claude Code
- Config: `~/.claude/settings.json`
- Skills: `~/.claude/skills/` (symlink)
- History: `~/.claude/history.jsonl`

### Claude Desktop
- Config: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Skills: `~/Library/Application Support/Claude/skills/` (symlink)

## Questions & Support

### Where do skills come from?

Skills can be found:
- GitHub repositories (user-created)
- Community skill collections
- Custom skills you write yourself

### Can I modify official skills?

Yes! Since skills are in your repo, you can:
- Fork and customize any skill
- Add features to existing skills
- Create variants for specific use cases

### Will updates break my setup?

No. Your skills are versioned in git:
- Can rollback with `git revert`
- Can create branches for testing
- Full history preserved

### Can I use private skills?

Yes! This repo can be:
- Public (share with community)
- Private (personal/team only)
- Use different repos for public vs private skills

## Resources

- [Claude Code Documentation](https://github.com/anthropics/claude-code)
- [Claude Skills Guide](https://docs.anthropic.com/claude/docs/claude-code-skills)
- [Example Skills Repository](https://github.com/michalparkola/tapestry-skills-for-claude-code)
