---
name: slopradar
description: SlopRadar — comprehensive security audit skill. Use when the user wants a security review, security audit, vulnerability assessment, or asks "is this code secure?". Scopes the target project, launches 5 parallel specialist agents, and compiles findings into security-review.md.
allowed-tools: Task,Bash,Read,Write,Glob,Grep
---

# SlopRadar — Security Audit Skill

SlopRadar performs a comprehensive, multi-domain security audit of any codebase. It works by:
1. **Scoping** the project — language, frameworks, infrastructure, CI/CD
2. **Launching 5 parallel specialist agents** each focused on a different threat domain
3. **Compiling** all findings into a `security-review.md` in the project root

---

## Step 1 — Identify the Target

If the user has not specified which project to audit, ask:
> "Which project should I audit? Please provide the path or name."

Once you have the target path, confirm it exists:
```bash
ls <project-path>
```

---

## Step 2 — Scope Reconnaissance

Before launching agents, do a quick structural scan to understand what you're dealing with. Run these in parallel:

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

Use the results to fill in the `[PROJECT_TYPE]`, `[LANGUAGE]`, and `[KEY_COMPONENTS]` placeholders in the agent prompts below. The five domains are always used — but tailor the focus areas to what the project actually contains.

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

---

## Step 3 — Launch 5 Parallel Agents

Launch all five agents in a **single message** with five Task tool calls. This is mandatory — do not launch them sequentially.

Use `subagent_type: Explore` and `run_in_background: true` for all five.

---

### Agent 1 — Secrets & Credential Management

**Prompt template:**

```
Perform a thorough security audit of the project at <PROJECT_PATH>, focused on SECRETS MANAGEMENT AND CREDENTIAL HANDLING.

Project type: <PROJECT_TYPE> (<LANGUAGE>)

Examine ALL of the following that are present:

SECRETS IN CODE
- Hardcoded API keys, tokens, passwords, connection strings anywhere in source
- Secrets committed to version control (including test fixtures, VCR cassettes, test data)
- .gitignore — are secret files (.env, *.pem, *.key) properly excluded?
- Secrets in comments or documentation

SECRET LOADING & RUNTIME HANDLING
- How are secrets loaded at startup? (env vars, secret managers, config files)
- Are required secrets validated on startup with a clear error if missing?
- Are secrets stored in memory longer than necessary?
- Are secrets logged, printed, or included in error messages or stack traces?
- Are API keys or tokens passed through error objects that could be serialised?

TRANSPORT & STORAGE
- Is TLS/HTTPS enforced for all external calls? Any InsecureSkipVerify?
- Are secrets stored encrypted at rest (database, cache)?
- Are secrets passed via URL parameters (logged in access logs)?

CI/CD & INFRASTRUCTURE
- GitHub Actions: Are secrets accessed correctly? Any `echo $SECRET` patterns?
- `secrets: inherit` usage — is it documented and intentional?
- Docker: Are secrets baked into image layers during build? (RUN with secrets, ARG for secrets)
- Kubernetes / Helm: Are secrets in values files? Are they using external secret managers?
- Terraform: Are secrets in .tfvars or state files?
- Any cloud metadata endpoint accessible that could expose credentials?

DEPENDENCY SECURITY
- Are auth/crypto library versions recent and without known CVEs?
- Any suspicious dependencies with access to auth flows?

For each finding: file path, line number, severity (Critical/High/Medium/Low), and description of risk.
Also list positive practices observed.
```

---

### Agent 2 — Input Validation & Injection

**Prompt template:**

```
Perform a thorough security audit of the project at <PROJECT_PATH>, focused on INPUT VALIDATION, INJECTION VULNERABILITIES, AND PROMPT INJECTION.

Project type: <PROJECT_TYPE> (<LANGUAGE>)

Examine ALL of the following that are present:

CLASSIC INJECTION
- SQL injection: are parameterized queries / prepared statements used everywhere?
- Command injection: any os/exec, subprocess, child_process, shell=True with user input?
- Path traversal: user-controlled file paths without sanitisation?
- LDAP / XML / XPath injection
- Template injection: are template engines passed user data directly?
- GraphQL injection: search queries built with string concatenation from user input?
- JQL / JIRA query injection?
- NoSQL injection (MongoDB $where, etc.)?

WEB / API INJECTION
- XSS: are HTML responses escaped? CSP headers set?
- HTTP header injection: user input in response headers?
- Open redirect: redirect URLs from user input?
- SSRF: user-controlled URLs fetched by the server? Any allowlist? DNS rebinding risk?
- XXE: XML parsing with external entity resolution enabled?

PROMPT INJECTION (for AI/LLM applications)
- Is user-controlled text embedded directly into LLM system prompts or conversation history?
- Is external content (emails, PRs, Slack messages, web pages) inserted into prompts without boundaries?
- Is prompt output stored and later re-fed to the model (stored prompt injection)?
- Are tool call results from untrusted sources sanitised before the LLM sees them?
- Can an attacker craft content in a connected system (GitHub PR, Jira ticket, email) that hijacks the AI's actions?
- Is there a distinction between "instruction" context and "data" context for the LLM?

BROWSER / SCRAPING TOOLS (if present)
- Can users navigate to internal network addresses (SSRF via browser)?
- Are type/fill inputs sanitised before being passed to browser automation?
- Is the allowed domain list enforced with DNS-rebinding protection?

VALIDATION QUALITY
- Are all external inputs validated at system boundaries (HTTP, CLI args, webhooks, queue messages)?
- Are validation errors safe (no stack traces, no internal paths exposed)?
- Is input rejected with an allowlist approach rather than a denylist?

For each finding: file path, line number, severity (Critical/High/Medium/Low), and description of risk.
```

---

### Agent 3 — Authentication & Authorization

**Prompt template:**

```
Perform a thorough security audit of the project at <PROJECT_PATH>, focused on AUTHENTICATION, AUTHORIZATION, AND ACCESS CONTROL.

Project type: <PROJECT_TYPE> (<LANGUAGE>)

Examine ALL of the following that are present:

AUTHENTICATION
- How are incoming requests authenticated? (API keys, JWTs, sessions, OAuth)
- Are webhook signatures verified? (Slack signing secret, GitHub X-Hub-Signature, Stripe, etc.)
  - Is HMAC comparison done in constant time?
  - Is the timestamp checked to prevent replay attacks?
- Are JWTs validated fully? (signature, expiry, issuer, audience)
- Are sessions properly secured? (HttpOnly, Secure, SameSite cookie flags)
- Are passwords hashed with a modern algorithm (bcrypt, argon2, scrypt)?
- Is there brute-force protection (rate limiting, lockout) on login endpoints?

AUTHORIZATION
- Is there a clear authorisation model? (RBAC, ABAC, ownership checks)
- Are all routes / endpoints protected? Any missing auth middleware?
- Is authorisation enforced server-side (not just hidden on the client)?
- Can a user access another user's data by changing an ID in the request?
  (IDOR — Insecure Direct Object Reference)
- Are admin-only operations gated on admin role, not just "logged in"?
- Are there operations that bypass auth for "convenience"?

MULTI-TENANT / ISOLATION
- Is data properly isolated between tenants/teams/organisations?
- Are database queries always filtered by the authenticated tenant?
- Could a user in one workspace access data from another workspace?
- Are session keys namespaced by tenant?

OAUTH / THIRD-PARTY AUTH
- Is the OAuth state parameter validated to prevent CSRF?
- Are redirect URIs validated against an allowlist?
- Are tokens stored securely and rotated?

CRITICAL OPERATIONS
- Is there authorisation on destructive operations (delete, terminate, deploy)?
- Are there any "god mode" paths that skip auth?
- Are privileged tools / admin endpoints protected separately?

MONITORING & AUDIT
- Are authentication failures logged?
- Are privilege escalation attempts detected?
- Is there an audit trail for sensitive operations?

For each finding: file path, line number, severity (Critical/High/Medium/Low), and description of risk.
```

---

### Agent 4 — Code Execution & Sandbox Security

**Prompt template:**

```
Perform a thorough security audit of the project at <PROJECT_PATH>, focused on CODE EXECUTION, SANDBOX SECURITY, AND SCRIPT INJECTION.

Project type: <PROJECT_TYPE> (<LANGUAGE>)

Examine ALL of the following that are present:

CODE / SCRIPT EXECUTION
- Any eval(), exec(), os.system(), shell=True, child_process.exec, exec.Command with user input?
- Dynamic code generation from user-supplied strings?
- Scripting engines (Starlark, Lua, JavaScript sandboxes, Python exec) — what can scripts access?
- Are script timeouts enforced?
- Are step / instruction count limits enforced?
- Are memory limits enforced?
- Can scripts access the host filesystem?
- Can scripts make arbitrary network requests (SSRF)?
- Can scripts spawn child processes?
- Can scripts access environment variables containing secrets?
- Is there rate limiting on script execution per user?

SANDBOX DESIGN
- Is the "sandbox" truly isolated (separate process, container, VM)?
- What is the blast radius if the sandbox is escaped?
- Are the sandbox capabilities documented and intentionally minimal?
- Are dangerous standard library functions removed from scripting environments?
- Is print/logging output size bounded to prevent memory exhaustion?

DESERIALIZATION
- Is untrusted data deserialised using unsafe methods? (pickle, yaml.load, unserialize)
- Are serialisation formats validated against a schema before processing?

DEPENDENCY EXECUTION
- Are dependencies fetched and executed at runtime from user-controlled sources?
- Are build scripts or Makefiles safe from injection via environment variables?

CONTAINER / PROCESS ISOLATION
- Do Dockerfiles run processes as root? Is there a USER directive?
- Do containers have --privileged or dangerous capabilities?
- Is the container filesystem writable where it doesn't need to be?
- Are seccomp / AppArmor profiles applied?

RESOURCE EXHAUSTION
- Are there limits on: request body size, file upload size, regex complexity, loop iterations?
- Can a single user exhaust CPU, memory, or I/O for all users (DoS)?
- Are long-running operations cancellable?

For each finding: file path, line number, severity (Critical/High/Medium/Low), and description of risk.
```

---

### Agent 5 — Infrastructure & CI/CD Security

**Prompt template:**

```
Perform a thorough security audit of the project at <PROJECT_PATH>, focused on INFRASTRUCTURE SECURITY, CI/CD PIPELINE SECURITY, AND SUPPLY CHAIN.

Project type: <PROJECT_TYPE> (<LANGUAGE>)

Examine ALL of the following that are present:

CONTAINER SECURITY
- Dockerfile base images: floating tags (:latest)? Should be pinned to digest.
- Is there an explicit USER directive (non-root)?
- Are build secrets passed safely (--mount=type=secret, not ARG/ENV)?
- Is the final image minimal (distroless, alpine, slim)?
- Are unnecessary tools / shells removed from the production image?
- Are there any COPY --chown or file permission issues?

KUBERNETES / HELM
- Are pod security contexts set? (runAsNonRoot, readOnlyRootFilesystem, allowPrivilegeEscalation: false, capabilities.drop: ALL)
- Are resource limits (CPU, memory) set on all containers?
- Are NetworkPolicies defined (default-deny + explicit allow)?
- RBAC: are roles using least privilege? Any wildcard verbs or resources?
- Are secrets stored in K8s Secrets (not ConfigMaps)? Are they using external secret managers?
- Are service accounts bound to pods unnecessarily?
- Are Helm values files free of hardcoded secrets?

GITHUB ACTIONS / CI/CD
- Are third-party Actions pinned to commit SHAs (not @main, not @v1 floating tags)?
- Are workflow permissions minimal? (contents: read by default, not write)
- Are workflows that run on pull_request events using write permissions? (pwn-request risk)
- Is GITHUB_TOKEN used carefully? (no unnecessary repo write access)
- Are secrets echoed or logged anywhere in steps?
- Is user-controlled data (PR title, branch name, commit message) used in run: steps? (injection risk)
- Are matrix values from user-controlled sources?
- `secrets: inherit` — is it intentional and documented?

TERRAFORM / IaC
- Are provider credentials hardcoded?
- Is remote state encrypted? Who has access?
- Are IAM policies following least privilege?
- Are security groups / firewall rules overly permissive (0.0.0.0/0)?
- Are resources publicly exposed that shouldn't be?
- Any sensitive outputs in state file?

IAM & ACCESS MANAGEMENT
- Are IAM roles following least privilege?
- Are long-lived credentials used where short-lived (OIDC/Workload Identity) should be?
- Are individual user grants used instead of group-based grants?
- Are service account keys stored as files or secrets? (vs. metadata server)

SUPPLY CHAIN
- Are dependencies pinned to exact versions or digests?
- Is there a dependency audit / SCA step in CI?
- Are Docker Hub images used without digest pinning?
- Is dependabot or renovate configured?
- Are private registries authenticated correctly?

NETWORK & EXPOSURE
- Are metrics / debug endpoints (Prometheus /metrics, /debug/pprof, /actuator) protected?
- Are admin endpoints exposed externally?
- Are databases / caches exposed outside the cluster?

For each finding: file path, line number, severity (Critical/High/Medium/Low), and description of risk.
```

---

## Step 4 — Wait for All Agents

Wait for all 5 background agents to complete. You will receive notifications as each one finishes. Do not start compiling until all 5 are done.

---

## Step 5 — Compile `security-review.md`

Once all agents report back, write `<PROJECT_PATH>/security-review.md` using the structure below. Deduplicate findings that multiple agents flagged for the same issue (keep the most detailed description). Assign the highest severity given by any agent.

### Output structure

```markdown
# Security Review: <project-name>

**Date:** <today's date>
**Scope:** Full codebase — secrets management, input validation & injection, authentication
& authorization, code execution & sandbox, infrastructure & CI/CD.

---

## Executive Summary

<2–4 sentence summary of overall risk posture. Call out the most important issues.>

| Severity | Count |
|---|---|
| Critical | N |
| High | N |
| Medium | N |
| Low | N |

---

## Critical Findings

### C1 — <Short title>
**File:** `path/to/file.go` line N
**Category:** <category>

<Description of the vulnerability, including attack vector and blast radius.>

**Fix:** <Concrete remediation action.>

---

[repeat for each Critical finding]

---

## High Findings

### H1 — <Short title>
...

---

## Medium Findings

### M1 — <Short title>
...

---

## Low Findings

### L1 — <Short title>
...

---

## Positive Security Practices

<Bullet list of things done well that should be preserved.>

---

## Recommended Remediation Plan

### Immediate (this sprint)
| # | Action |
|---|---|
| 1 | ... |

### Short-term (next sprint)
| # | Action |
|---|---|
| 1 | ... |

### Medium-term (within 2 sprints)
| # | Action |
|---|---|
| 1 | ... |

---

*Generated by SlopRadar — five-agent parallel security audit.*
```

---

## Severity Definitions

| Level | Meaning |
|---|---|
| **Critical** | Exploitable now with direct, high-impact consequence (data breach, RCE, auth bypass). Fix before next deploy. |
| **High** | Significant risk; likely exploitable with modest effort. Fix this sprint. |
| **Medium** | Real risk but requires specific conditions or chaining. Fix within 2 sprints. |
| **Low** | Defence-in-depth, best practice, or low-probability issue. Fix in planning cycle. |

---

## Adapting for Project Type

**No infrastructure / no Dockerfile?**
Have Agent 5 focus on: dependency supply chain, secrets in CI, package manager lockfiles, SCA.

**No LLM / AI features?**
Have Agent 2 skip prompt injection; double down on SQLi, XSS, SSRF, and deserialization instead.

**No script execution engine?**
Have Agent 4 focus on: deserialization, dangerous eval/exec patterns, regex DoS, resource limits.

**Monorepo with multiple services?**
Scope each agent to the most security-sensitive service first; note other services for follow-up.

**Frontend / browser app?**
Add XSS, CSP, CORS misconfiguration, local storage secrets, and Subresource Integrity to Agent 2's scope.

---

## Key Principles

- **Always launch all 5 agents in parallel** — never sequentially.
- **Tailor agent prompts** to what actually exists in the project. Remove irrelevant sections to keep agents focused.
- **Do not write the report until all 5 agents finish** — missing one agent's findings produces an incomplete review.
- **Deduplicate carefully** — multiple agents may flag the same file for different reasons; keep both perspectives.
- **Be specific** — every finding must include file path, line number (where possible), severity, and a concrete fix.
- **Acknowledge what's done well** — security reviews are more useful when they confirm safe practices, not just list problems.
