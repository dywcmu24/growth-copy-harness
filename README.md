# Growth-Copy Harness

A single-session agent harness that generates marketing landing pages and **proves they meet their acceptance criteria** — instead of taking the agent's word for it.

The point of this project is not "an agent that builds landing pages." It is the **verification discipline** around it: every acceptance criterion defaults to `FAIL`, and can only flip to `PASS` when backed by **evidence written to disk** and checked by an independent gate. The agent cannot self-declare "done."

## The problem it addresses

The most common failure mode of coding agents is **premature "done"** — the agent announces completion based on its own loose judgment. This harness removes that possibility structurally: an agent can claim a criterion passes, but a gate rejects the claim unless matching evidence exists on disk. You don't ask the agent to be honest; you make dishonest-but-green outcomes impossible.

## How it works

Pipeline: CLAUDE.md declares intent, feature_list.json holds state, two sensors produce evidence, and a gate enforces.

- **CLAUDE.md** — declares intent (rules, rituals, constraints).
- **feature_list.json** — holds state: 12 criteria, every one starts `"passes": false`.
- **verify.py** — structural sensor (8 criteria), Playwright DOM assertions, writes evidence.
- **.claude/agents/evaluator.md** — copy sensor (4 criteria), independent sub-agent, writes a verdict.
- **verify-gate.sh** — enforces: a claimed pass with no evidence on disk exits 1 and is rejected.

Two kinds of verification, by design:

- **Computational sensor** (`verify.py`): a real Chromium via Playwright asserts structural facts — viewport meta, CTA above the fold, single `<h1>`, schema.org markup, accessible visuals, and so on. Deterministic and objective.
- **Inferential sensor** (`evaluator.md`): an independent sub-agent with **no write tools** and a **fresh context** judges copy quality. It cannot edit project state and cannot favor work it didn't write — referee separated from player.

## Quick start

Requires the Claude Code CLI, Python 3.11+, and Node (for Playwright).To generate a page, open a Claude Code session in this directory and run the generator/evaluator loop (see CLAUDE.md for the working agreement the agent follows).

## Design highlights

- **Default-FAIL criteria** — the burden of proof is on the agent, not the reviewer.
- **Evidence gate** — verify-gate.sh only trusts files on disk, not the agent's claims.
- **Player/referee separation** — the evaluator sub-agent has no write tools and a fresh context.
- **Intent over implementation** — acceptance criteria target the goal (e.g. "every information-bearing visual is accessible"), not a specific tag, so they cannot be bypassed by switching implementations.

## A worked failure to fix to verify loop

The docs folder documents a real harness-engineering episode: a structural check (S4) passed **vacuously** because a page used inline SVG instead of img, so "every image has alt" was trivially true on a page with zero images.

To diagnose whether the agent was evading the check or just defaulting to SVG, I ran a controlled A/B experiment (Opus 4.7, 40 runs): telling the model about the alt rule made it use **more** images, not fewer — the opposite of what evasion would predict. So the failure was a **verification-layer blind spot**, not gaming. The fix widened the criterion from "img has alt" to "every information-bearing visual (img and inline svg) is accessible," verified across three cases including the original false-green page.

Full write-up: docs/01-goodhart-s4-vacuous-truth.md

## Scope and boundaries (intentional cuts, not blind spots)

This is a deliberately single-session, one-day demo. Known boundaries, each with a planned fix:

- **No sandbox isolation** — the agent runs directly on the local filesystem; production should use an ephemeral sandbox.
- **Not a long-running task** — single session, single variant; no cross-context-window compaction or progress hand-off under stress.
- **Partial guardrails** — only a cost cap (in the experiment script); no loop-breaking or tool-call limits yet.
- **Gate trust boundary** — the gate trusts files in the evidence folder; anything that can write files could forge evidence. Production should add signing or permission isolation.
- **Detection limit** — CSS background images carry no DOM tag and cannot be checked.

These define the v2 roadmap: long-running multi-session execution, sandbox isolation, and an experiment isolating how harness constraints reshape model behavior.
