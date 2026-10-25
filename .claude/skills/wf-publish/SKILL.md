---
name: wf-publish
description: >-
  Merge a pull request and clean up branches and issues. Use when publishing,
  merging a PR, finalizing work, or cleaning up after a merge.
argument-hint: "[pr-number-or-url]"
allowed-tools: Bash(gh pr view *) Bash(gh pr merge *) Bash(gh issue close *) Bash(git branch *) Bash(git checkout *) Bash(git switch *) Bash(git fetch *) Bash(git pull *) Bash(git push origin --delete *)
model: sonnet
effort: medium
---

# Publish — Merge PR and Clean Up

Merge an approved pull request and clean up Git.

## Context

- PR: `$ARGUMENTS`

## Steps

### 1. Check PR Status

Run `gh pr view $ARGUMENTS --json state,mergeable,mergeStateStatus` to check the PR status. If there are merge conflicts with the base branch, **stop immediately** and tell the user. Do not attempt to resolve conflicts automatically.

### 2. Confirm, then Merge

Merging is irreversible. Use the AskUserQuestion tool to confirm before merging, showing the PR title, the base branch it merges into, and the working branch that step 3 will delete.

Only after the user confirms, merge using a **merge commit** (not squash or rebase):

```bash
gh pr merge $ARGUMENTS --merge
```

### 3. Clean Up

After a successful merge:

- **Delete the working branch** — remote and local. Delete only the PR's own working branch; leave every other branch alone.
- **Close any still-open linked issues.** GitHub already closes issues referenced with a closing keyword (`Closes #123`) when the PR merges into the **default** branch, so most will need nothing. Run `gh pr view $ARGUMENTS --json closingIssuesReferences` and close only those still open.

Do **not** review the PR — that has already been done.
