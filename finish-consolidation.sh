#!/usr/bin/env bash
#
# finish-consolidation.sh
# Run this ONCE on your own machine to complete the single-branch consolidation.
# (It could not be run inside the Cowork sandbox because a stale .git/index.lock,
#  left by a crashed git process, could not be removed there.)
#
# What it does:
#   1. clears the stale index lock
#   2. commits all the consolidation changes
#   3. fast-forwards `main` to include them + the newest tool work
#   4. switches you to `main` and deletes the leftover feature branch
#
# Then publish + clean the remote with:  git push origin main && bash cleanup-remote-branches.sh
#
set -euo pipefail
cd "$(dirname "$0")"

CUR="claude/add-judgement-headings-M7Kg5"   # the branch holding the newest work

echo "==> 1/5 clearing any stale index lock"
rm -f .git/index.lock

echo "==> 2/5 untracking committed .DS_Store files (now gitignored)"
git rm -r --cached --ignore-unmatch '*.DS_Store' >/dev/null 2>&1 || true

echo "==> 3/5 committing consolidation changes"
git add -A
git commit -m "Consolidate to single branch: navigation layer, reconciled key claims, cleanup

- Rewrite README as skimmable orientation hub (10 headline findings)
- Add docs/KEY_CLAIMS.md (ranked, strength-graded claim ledger + reconciliations)
- Add docs/REPOSITORY_MAP.md (full directory + analysis-pipeline map)
- Recover PROPOSED_ methodology docs from unmerged court-decision branch
- Reduce docs/FINDINGS_OVERVIEW.md to a redirect stub
- Fix 67-vs-69 case counts; correct teleology-vs-purpose claim; untrack .DS_Store
- Add branch-cleanup tooling and CONSOLIDATION_NOTES.md"

echo "==> 4/5 fast-forwarding main"
git checkout main
git merge --ff-only "$CUR"

echo "==> 5/5 deleting the leftover feature branch (locally)"
git branch -d "$CUR" || git branch -D "$CUR"

echo
echo "Local repo is now single-branch (main). To finish on GitHub:"
echo "    git push origin main"
echo "    bash cleanup-remote-branches.sh   # deletes the 12 merged remote branches"
