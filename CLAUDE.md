# Growth-Copy Harness

## What this project is
An agent harness that takes a product brief and produces VERIFIED
marketing landing pages. The harness - not the model - is responsible for making
"done" mean "actually meets every acceptance criterion, with evidence."

Pipeline: Planner (writes specs) -> Generator (builds pages) -> Evaluator (verifies, PASS/NEEDS_WORK).

## Project structure (do not deviate)
- specs/feature_list.json  : acceptance criteria. Every criterion starts "passes": false.
- output/<variant>/index.html : each generated landing page variant.
- evidence/<variant>/ : Playwright screenshots + DOM dumps. Proof a criterion passed.
- .claude/agents/evaluator.md : the evaluator sub-agent.
- .claude/hooks/ : gate scripts.

## Working agreement (rules below each map to ONE failure mode)

# Failure mode: premature "done" / self-evaluation leniency
- You may set a criterion's "passes" to true ONLY after the evaluator has written
  matching evidence into evidence/<variant>/. No evidence file = criterion stays false.
- You MUST NOT edit or delete acceptance criteria in feature_list.json. You may only
  change the "passes" field. Removing or weakening a criterion is unacceptable.

# Failure mode: lost context across sessions
- At the START of every session: run pwd, read claude-progress.txt, read feature_list.json,
  then pick the single highest-priority variant whose criteria are not all passing.
- At the END of every session: append a 2-3 line summary to claude-progress.txt and git commit
  with a descriptive message.

# Failure mode: doing too much at once / context exhaustion
- Work on ONE variant per session. Do not attempt to build all variants in one pass.

# Failure mode: structural quality cannot be eyeballed reliably
- Structural criteria (CTA above the fold, viewport meta tag, schema.org markup, alt text
  on every image) are verified by Playwright DOM assertions, NOT by your own judgment.

# Failure mode: copy quality is fuzzy
- Copy criteria (headline clarity, single clear value prop, one primary CTA) are judged by
  the evaluator sub-agent. Keep copy claims concrete; no placeholder lorem ipsum.

## Tech constraints (stability over novelty)
- Plain static HTML + inline CSS only. No frameworks, no build step, no external JS.
- Each variant is a single self-contained output/<variant>/index.html that opens directly
  in a browser with no server.
