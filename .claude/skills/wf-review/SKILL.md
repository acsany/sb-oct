---
name: wf-review
description: >-
  Review a pull request for critical issues and post findings as a PR comment.
  Focuses on bugs, performance, security, and correctness. Use when reviewing
  a PR, checking code quality, or auditing changes before merge.
argument-hint: "[pr-number-or-url]"
allowed-tools: Bash(gh pr view *) Bash(gh pr diff *) Bash(gh pr comment *) Read Glob Grep
model: opus
effort: max
---

# Review — Review a Pull Request

Analyze a pull request for critical issues and post the review as a comment.

> Based on [Jose Casanova's PR review prompt](https://www.josecasanova.com/prompts/git-concise-pr-review-prompt).

## Context

- PR: `$ARGUMENTS`

## Steps

### 1. Fetch and Analyze Changes

Run `gh pr diff $ARGUMENTS` to get the diff. Focus **only** on critical issues:

- **Bugs** — logic errors, edge cases, race conditions
- **Performance** — inefficient queries, unnecessary loops, memory issues
- **Security** — injection, exposure, auth gaps
- **Correctness** — does the code do what it claims?

### 2. Write the Review

- If **critical issues found**: list them as short bullet points
- If **no critical issues**: provide a simple approval

Skip style suggestions and minor nitpicks unless they impact performance, security, or correctness.

### 3. Post as PR Comment

Post the review with `gh pr comment $ARGUMENTS --body "<review>"`. Use a HEREDOC via `--body-file -` if the review spans multiple lines. **Never merge.**

Open the comment with ✅ (approved) or ⚠️ (issues found), and close it with the model and effort this skill runs at:

```
---
🤖 Automated review via `/wf-review` — model: opus, effort: max
```
