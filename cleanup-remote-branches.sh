#!/usr/bin/env bash
#
# cleanup-remote-branches.sh
# Finishes the single-branch consolidation on the remote (origin).
# Safe by design: deletes ONLY the 12 branches verified as fully merged into main.
# The 6 unmerged branches are listed but NOT touched.
#
# Run from the repo root:  bash cleanup-remote-branches.sh
#
set -euo pipefail

# --- Fully merged into main: 0 unique commits, safe to delete -----------------
MERGED=(
  "claude/analyze-gdpr-holdings-7uunF"
  "claude/analyze-judgment-citations-o92fz"
  "claude/cjeu-pro-controller-analysis-FTi2c"
  "claude/extract-judge-names-exqy7"
  "claude/judicial-analysis-methodology-J6UOg"
  "claude/organize-files-update-docs-C0Fk1"
  "claude/organize-structure-docs-87Yks"
  "claude/review-docs-outliers-tKfZS"
  "claude/review-topic-clustering-gGZAT"
  "claude/statistical-analysis-methodology-cTipf"
  "claude/temporal-analysis-planning-K3IuX"
  "claude/topic-focus-graphs-ayuok"
)

# --- Unmerged: have unique commits. NOT deleted. Review on GitHub if wanted. ---
UNMERGED=(
  "claude/court-decision-analysis-1cd5U     # content already recovered into docs/methodology/"
  "claude/consolidate-reports-summary-HS9Hx"
  "claude/coder-comparison-ui-QnqBH"
  "claude/gdpr-cjeu-chapter-E5G9Z"
  "claude/analyze-judge-specialization-UGH1F"
  "claude/add-printable-reports-g4C1F"
)

echo "This will delete these FULLY-MERGED remote branches from origin:"
printf '  - %s\n' "${MERGED[@]}"
echo
echo "It will KEEP (not touch) these UNMERGED branches:"
printf '  - %s\n' "${UNMERGED[@]}"
echo
read -r -p "Proceed with deleting the merged branches? [y/N] " ans
if [[ "${ans:-N}" =~ ^[Yy]$ ]]; then
  for b in "${MERGED[@]}"; do
    echo "Deleting origin/$b ..."
    git push origin --delete "$b" || echo "  (skip: $b not found or already gone)"
  done
  echo "Done. Merged branches removed."
else
  echo "Aborted. Nothing deleted."
fi

echo
echo "To publish the consolidated main, review then run:"
echo "  git push origin main"
