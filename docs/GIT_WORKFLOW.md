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

| Stage | Branch | Example commit messages | Closes |
|-------|--------|-------------------------|--------|
| 1 | `feature/core` | "Implement merge sort and binary search" · "Add JSON load/save with safe write" · "Add book and member management to Library" · "Add issue/return with fine calculation" · "Add FIFO reservation queue" | FR1–FR10 logic |
| 2 | `feature/cli` | "Wire add/remove book to text menu" · "Add search and sorted listing to text version" · "Add input validation to text menu" | text version |
| 3 | `feature/tests` | "Add unit tests for algorithms" · "Add tests for loans, fines and reservations" | testing |
| 4 | `feature/gui` | "Add Books tab with table and form" · "Add Loans tab to GUI" · "Add overdue view to GUI" | GUI version |
| 5 | `docs/readme` | "Update README with run instructions and screenshots" | docs |

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
