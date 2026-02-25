---
name: slopradar
description: Performs comprehensive security audits across 5 threat domains — secrets management, input validation & injection, authentication & authorization, code execution & sandbox, and infrastructure & CI/CD. Scopes the target project, launches 5 parallel specialist agents, and compiles findings into a security-review.md report. Use when the user wants a security review, security audit, vulnerability assessment, or asks whether code is secure.
allowed-tools: Task,Bash,Read,Write,Glob,Grep
---

# SlopRadar — Security Audit Skill

Performs a comprehensive, multi-domain security audit of any codebase by:
1. **Scoping** the project — language, frameworks, infrastructure, CI/CD
2. **Launching 5 parallel specialist agents** each focused on a different threat domain
3. **Compiling** all findings into a `security-review.md` in the project root

---

## Step 1 — Identify the Target

If the user has not specified which project to audit, ask:
> "Which project should I audit? Please provide the path or name."

Confirm the target exists:
```bash
ls <project-path>
```

---

## Step 2 — Scope Reconnaissance

Run these in parallel to understand the project structure:

```bash
# Get all files (limit to 150 to avoid noise)
find <project-path> -type f | grep -v '.git/' | head -150
```

```bash
# Detect primary language(s) and frameworks
find <project-path> -maxdepth 2 -name "*.go" -o -name "package.json" \
  -o -name "requirements.txt" -o -name "Gemfile" -o -name "pom.xml" \
  -o -name "Cargo.toml" -o -name "*.tf" -o -name "Dockerfile" \
  -o -name "docker-compose.yml" -o -name "*.yaml" | grep -v '.git/' | head -50
```

**Component detection cheatsheet:**
- `go.mod` → Go service
- `package.json` → Node.js / TypeScript
- `requirements.txt` / `pyproject.toml` → Python
- `Dockerfile` / `docker-compose.yml` → containerised
- `.github/workflows/` → GitHub Actions CI/CD
- `.infra/` / `*.tf` / `helm/` / `Chart.yaml` → Kubernetes / Terraform infrastructure
- `*.sql` / ORM models → database layer
- Slack / webhook handlers → webhook authentication surface
- LLM / AI SDK imports → prompt injection surface
- Script execution / `exec.Command` / `subprocess` / `eval` → code execution surface

Fill in `[PROJECT_TYPE]`, `[LANGUAGE]`, and `[KEY_COMPONENTS]` from these results before launching agents.

---

## Step 3 — Launch 5 Parallel Agents

Read `AGENTS.md` for the full agent prompt templates. Then launch all five agents in a **single message** with five Task tool calls — never sequentially. Use `subagent_type: Explore` and `run_in_background: true` for all five.

The five domains:
1. **Secrets & Credential Management** — see Agent 1 in AGENTS.md
2. **Input Validation & Injection** — see Agent 2 in AGENTS.md
3. **Authentication & Authorization** — see Agent 3 in AGENTS.md
4. **Code Execution & Sandbox Security** — see Agent 4 in AGENTS.md
5. **Infrastructure & CI/CD Security** — see Agent 5 in AGENTS.md

Tailor each agent's prompt to what actually exists in the project. Remove irrelevant sections to keep agents focused. See **Adapting for Project Type** in `OUTPUT.md` for guidance.

---

## Step 4 — Wait for All Agents

Wait for all 5 background agents to complete. You will receive notifications as each one finishes. Do not start compiling until all 5 are done.

---

## Step 5 — Compile `security-review.md`

Read `OUTPUT.md` for the full output template and structure. Write `<PROJECT_PATH>/security-review.md`. Deduplicate findings that multiple agents flagged for the same issue (keep the most detailed description). Assign the highest severity given by any agent.

---

## Key Principles

- **Always launch all 5 agents in parallel** — never sequentially.
- **Do not write the report until all 5 agents finish** — missing one agent's findings produces an incomplete review.
- **Deduplicate carefully** — multiple agents may flag the same file for different reasons; keep both perspectives.
- **Be specific** — every finding must include file path, line number (where possible), severity, and a concrete fix.
- **Acknowledge what's done well** — security reviews are more useful when they confirm safe practices, not just list problems.
