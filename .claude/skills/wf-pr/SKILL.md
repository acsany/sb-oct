---
name: wf-pr
description: >-
  Create a pull request from the current branch. Summarizes all commits and
  references connected issues. Use when creating a PR, staging changes, or
  opening a pull request.
argument-hint: "[target-branch]"
allowed-tools: Bash(gh pr create *) Bash(git log *) Bash(git diff *) Bash(git branch *) Bash(git rev-parse *) Bash(git symbolic-ref *) Bash(git push *)
model: haiku
---

# PR — Create a Pull Request

Create a pull request from the current branch.

## Context

```!
git rev-parse --git-dir >/dev/null 2>&1 || { echo "Not a git repository — stop and tell the user."; exit 0; }
BASE=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@')
[ -z "$BASE" ] && for b in main master develop trunk; do
  git show-ref --verify --quiet "refs/heads/$b" && BASE=$b && break
done
echo "Base branch: ${BASE:-<none detected>}"
echo "Current branch: $(git branch --show-current)"
echo "--- Commits on this branch ---"
git log --oneline "${BASE:-HEAD}..HEAD"
echo "--- Changed files ---"
git diff "${BASE:-HEAD}..HEAD" --stat
```

## Steps

### 1. Review All Commits

Look at **all** commits on this branch (not just the latest). Understand the full scope of changes.

### 2. Create the PR

Use `gh pr create` to create a pull request. Target the branch named in `$ARGUMENTS`; if no argument was given, target the base branch detected above.

If `$ARGUMENTS` names a branch other than the detected base, re-run `git log --oneline <target>..HEAD` and `git diff <target>..HEAD --stat` first — the context above was computed against the default branch.

The PR should include:
- A clear, concise title
- A summary of what changed and why
- References to connected GitHub issues (e.g., `Closes #123`, `Fixes #45`)

Keep it short and focused — this is mechanical work, not a review.
