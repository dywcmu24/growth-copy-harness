#!/usr/bin/env bash
# Growth-Copy Harness — session bootstrap / "getting up to speed" ritual.
# Run this at the START of every session to rebuild context cheaply.
set -e

echo "=== WHERE AM I ==="
pwd

echo ""
echo "=== RECENT WORK (last 5 commits) ==="
git log --oneline -5 2>/dev/null || echo "(no commits yet)"

echo ""
echo "=== PROGRESS NOTES ==="
cat claude-progress.txt 2>/dev/null || echo "(no progress notes yet)"

echo ""
echo "=== CRITERIA STATUS (per variant) ==="
if [ -f specs/feature_list.json ]; then
  python3 - << 'PY'
import json
d = json.load(open("specs/feature_list.json"))
crit = d["criteria"]
passed = sum(1 for c in crit if c.get("passes"))
print(f"Product: {d.get('product_brief','?')[:70]}")
print(f"Variants: {', '.join(d.get('variants', []))}")
print(f"Criteria passing: {passed}/{len(crit)}")
not_done = [c['id'] for c in crit if not c.get('passes')]
print("Still failing:", ', '.join(not_done) if not_done else "NONE — all pass!")
PY
else
  echo "(no feature_list.json found)"
fi

echo ""
echo "=== NEXT ACTION ==="
echo "Pick the highest-priority variant whose criteria are not all passing, build/fix ONE, then verify."
