Photoplasm Quick Start Guide  ·  Chapter 2 — GitHub & Version Control

# Chapter 2 — GitHub & Version Control

*Eric Schneider · Makerspace Charlotte · HTGAA 2026*

Version 1.0.0  ·  2026-04-28  ·  github.com/ericview-dev/photoplasm

---

## Overview

GitHub is the central source of truth for all Photoplasm code. Every script is version-controlled, backed up, and synchronised between your Mac and the Raspberry Pi (eyepi) through GitHub. This chapter covers repository setup, the branch strategy, and the daily development workflow.

## The Three-Way Architecture

```
Mac (VS Code)  ──push▶  GitHub  ──pull▶  Pi (eyepi)
      ▲                                           │
      └─────────────────pull──────────────────────┘
```

- **Mac** — where you write and edit code in VS Code
- **GitHub** — source of truth, backup, version history
- **Pi** — where code runs against real hardware

Always edit on Mac, always pull to Pi before running.

## 2.1 — Prerequisites

- GitHub account at github.com
- Git installed on Mac (via Xcode Command Line Tools: `xcode-select --install`)
- Personal Access Token (PAT) with repo scope
- SSH connection to eyepi established (Chapter 1)

## 2.2 — Generate a Personal Access Token (PAT)

- GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
- Generate new token — select repo scope
- Copy the token — you will not see it again
- Store it securely (1Password, Notes, etc.)

Use the PAT as your password whenever Git prompts for GitHub credentials.

## 2.3 — Configure Git Identity on Mac

```bash
git config --global user.name "ericview-dev"
git config --global user.email "your@email.com"
```

Confirm:

```bash
git config --list
```

## 2.4 — Repository Setup

The photoplasm repository was created on GitHub with:

- Python .gitignore template
- MIT license
- README.md
- Default branch: main

## 2.5 — Clone to Mac

```bash
cd ~
git clone https://github.com/ericview-dev/photoplasm.git
cd photoplasm
```

Enter your PAT when prompted for password.

## 2.6 — .gitignore — Photoplasm Additions

Add these entries to the bottom of `.gitignore`:

```
# Photoplasm — calibration data and outputs
cal_logs/
*.csv

# macOS
.DS_Store
```

Save, commit, push:

```bash
git add .gitignore
git commit -m "chore: add Photoplasm gitignore entries"
git push origin dev
```

## 2.7 — Branch Strategy

| Branch | Purpose |
|---|---|
| main | Stable, tested, release-ready |
| dev | Active development — all day-to-day work happens here |
| feature/name | New features, branched from dev |
| hotfix/name | Urgent hardware bug fixes |

All work happens on dev. Merge to main only when stable.

```bash
git checkout dev
```

## 2.8 — Daily Development Workflow

**Start of session — always pull first:**

```bash
cd ~/photoplasm
git pull origin dev
```

**Make changes in VS Code, then commit and push:**

```bash
git add photoplasm_cal01.py
git commit -m "fix: add oled.on() before density frames"
git push origin dev
```

**Pull to Pi:**

```bash
ssh eyepi "cd ~/photoplasm && git pull origin dev"
```

**Or SSH in and pull manually:**

```bash
ssh eyepi
cd ~/photoplasm
git pull origin dev
```

## 2.9 — First Time Clone on Pi

If the repo doesn't exist on the Pi yet:

```bash
ssh eyepi
git clone -b dev https://github.com/ericview-dev/photoplasm.git
cd photoplasm
```

If a folder exists but isn't a git repo:

```bash
cd ~/photoplasm
git init
git remote add origin https://github.com/ericview-dev/photoplasm.git
git fetch origin dev
git checkout -b dev origin/dev
```

## 2.10 — Commit Message Convention

```
feat     — new feature or script
fix      — bug fix
chore    — maintenance, gitignore, deps
docs     — documentation only
refactor — code change, no new feature
test     — test scripts
```

Examples:

```bash
git commit -m "feat: add photoplasm_densitometer.py — 16-step Bayer dither"
git commit -m "fix: derive MEASURE_DELAY from SETTLE_SEC, clean up argparse"
git commit -m "docs: publish Appendix A calibration protocol markdown"
```

## 2.11 — Promoting dev → main

When dev is stable:

```bash
git checkout main
git merge dev
git push origin main
git checkout dev
```

## Known Issues & Fixes

| Error | Cause | Fix |
|---|---|---|
| fatal: repository not found | Wrong URL or username | Copy exact HTTPS URL from GitHub Code button |
| Authentication failed | Using GitHub password not PAT | Generate PAT with repo scope, use as password |
| Push rejected: non-fast-forward | Remote has commits you don't have | `git pull origin dev` first, then push |
| fatal: not a git repository | Folder exists but not initialised | `git init` then add remote |
| SCP wildcard: no matches found | Shell expands wildcard locally | Quote remote path: `scp eyepi:'/path/*.py' ~/local/` |
| Xcode tools required | First git command on fresh Mac | Click Install on popup, wait 3–5 minutes |

## Summary — Git Quick Reference

```bash
git status                    # what's changed
git add filename.py           # stage a file
git add .                     # stage all changes
git commit -m "message"       # commit staged changes
git push origin dev           # push to GitHub
git pull origin dev           # pull from GitHub
git log --oneline             # recent commits
git checkout -b feature/name  # new branch
git merge dev                 # merge dev into current branch
```

---

*Photoplasm · HTGAA 2026 · Genspace Node · Eric Schneider · Makerspace Charlotte*

*Repository: github.com/ericview-dev/photoplasm · branch: dev*

> v1.0.0  ·  2026-04-28  ·  published
