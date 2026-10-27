# Git & GitHub workflow (Assessment 2)

Development happens in stages. Each stage is a feature branch, merged into
`main` through a pull request. Commit small, working steps with clear messages.

## Stage 0 — repository set-up (`main`)

```bash
git init
git add .
git commit -m "Initial project skeleton: core package, CLI/GUI stubs, README, .gitignore"
git branch -M main
git remote add origin https://github.com/<your-username>/library-manager.git
git push -u origin main
```

Then on GitHub, create one issue per stage below (Issues → New issue)
and a milestone called `v1.0`.

## Stage-by-stage plan

| Stage | Branch | Example commit messages | Closes | Status |
|-------|--------|-------------------------|--------|--------|
| 0 | `main` | "Initial project skeleton: core package, CLI/GUI stubs, README, .gitignore" | set-up | Done |
| 1 | `feature/core` | "Implement stable merge sort and iterative binary search" · "Add JSON load and atomic save to storage module" · "Add FIFO reservation queue to Library" | Implement core logic (FR1–FR10) | Done |
| 2 | `feature/cli` | "Add input helpers and table printing to text version" · "Add issue, return and reserve actions to text menu" | Text-based version | Done |
| 3 | `feature/tests` | "Add unit tests for merge sort and binary search" · "Add tests for loans, fines and reservations" | Unit tests (76 tests) | Done |
| 4 | `feature/gui` | "Add Books tab with sortable table, search and add/remove form" · "Add Overdue tab with fines table and total as of today" | GUI version | Done |
| 5 | `docs/final` | "Add design document with data structures, algorithms and diagrams" | Final documentation | Done |

For each stage:

```bash
git checkout main
git pull
git checkout -b feature/core          # use the stage's branch name
# ...work, test, then commit in small steps:
git add core/algorithms.py
git commit -m "Implement merge sort and binary search"
git push -u origin feature/core
```

On GitHub: **Compare & pull request** → write what changed and
`Closes #<issue-number>` → **Merge pull request** → delete branch.

## Finish

```bash
git checkout main
git pull
git tag -a v1.0 -m "Final submitted version"
git push origin v1.0
```

Optionally create a GitHub Release from the `v1.0` tag.

## Before submitting the URL

- Open the repository URL in a private/incognito window to confirm it is **public**.
- No passwords, API keys or real personal data anywhere in the history.
- README explains the project and how to run both versions, and states GenAI use.
