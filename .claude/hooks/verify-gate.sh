#!/usr/bin/env bash
# verify-gate.sh — the load-bearing lock.
# Checks that every criterion marked "passes": true in feature_list.json has
# matching evidence on disk. Structural (S*) criteria need a Playwright result
# of true; copy (C*) criteria need an evaluator verdict file.
# Exit 0 = all claimed passes are backed by evidence. Exit 1 = a claim lacks evidence.

python3 - << 'PY'
import json, sys, os
from pathlib import Path

d = json.load(open("specs/feature_list.json"))
variants = d.get("variants", [])
violations = []

for c in d["criteria"]:
    if not c.get("passes"):
        continue  # only audit criteria CLAIMED as passing
    cid, ctype = c["id"], c["type"]
    backed = False
    for v in variants:
        if ctype == "structural":
            f = Path(f"evidence/{v}/structural_results.json")
            if f.exists():
                res = json.loads(f.read_text())
                if res.get(cid) is True:
                    backed = True; break
        else:  # copy -> evaluator verdict
            f = Path(f"evidence/{v}/evaluator_verdict.json")
            if f.exists():
                res = json.loads(f.read_text())
                if res.get(cid) is True:
                    backed = True; break
    if not backed:
        violations.append(cid)

if violations:
    print("GATE FAILED — these criteria are marked passes=true but have NO supporting evidence:")
    for cid in violations: print(f"   {cid}")
    print("Fix: either build/verify properly so evidence exists, or set these back to false.")
    sys.exit(1)
else:
    print("GATE PASSED — every claimed pass is backed by evidence on disk.")
    sys.exit(0)
PY
