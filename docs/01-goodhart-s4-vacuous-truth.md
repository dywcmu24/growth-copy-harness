# Debug Log #01 — The S4 "Vacuous Truth" Failure (a Goodhart's-law trap)

> Part of the Growth-Copy Harness debug series. Each entry follows the same shape:
> **Failure → Root cause → Fix → Lesson.** This is how a harness earns the right to
> call a criterion "load-bearing."

## Context

After the Generator built `variant-a`, the structural verifier (`verify.py`, driven by
a real Chromium via Playwright) reported **8/8 structural criteria passing**:

```json
{ "S1": true, "S2": true, "S3": true, "S4": true,
  "S5": true, "S6": true, "S7": true, "S8": true }
```

A green board. But one of those greens was lying.

## Failure

**S4** is defined as: *"Every `<img>` element has a non-empty alt attribute."*
Its purpose is **accessibility** — screen-reader users need alt text to understand images.

The generated page passed S4. But on inspection, the page contains **zero `<img>` elements** —
it uses inline SVG icons and CSS instead. So the rule "every image has alt" was satisfied
**vacuously**: a statement of the form "all X are Y" is automatically true when there are no X.

The accessibility goal was **not** actually met (the SVG icons carry meaning and have no
accessible labels), yet the check went green.

The verifier output below shows all 8 structural criteria green — including S4:

![Structural verification reports 8/8 passing, with S4 marked OK on a page that has no images](screenshots/s4-vacuously-ok.png)

The same false-green seen from the feature-list / verdict side — S4 "passes" with no real images behind it:

![S4 marked as a fake pass, vacuously true because the page contains zero img elements](screenshots/fake-pass-s4-vacuous-truth.png)

## Root cause — which layer failed?

Not the model. Not the prompt. The failure lives in the **verification / harness layer**:
the *acceptance criterion itself* was written in a way that could be **bypassed** rather
than **met**.

This is a textbook **Goodhart's law** trap: *"When a measure becomes a target, it ceases
to be a good measure."* An agent (or a developer) optimizing to turn the check green will
find the cheapest path to green — here, "use no images at all" — which is orthogonal to the
real intent (accessible visuals).

## Fix — patch the harness, not the page

The wrong fix would be to edit the page to add a dummy `<img>` so S4 has something to check.
That games the metric in the other direction.

The right fix is to **make the criterion harder to bypass**, so the check can only go green
when the underlying intent is genuinely satisfied. S4 is upgraded from:

- **Before:** every `<img>` has non-empty `alt`.
- **After:** every information-bearing visual element — `<img>` **and** non-decorative inline
  `<svg>` — carries an accessible label (`alt`, or `aria-label`, or `role="img"` + label),
  and a page that conveys meaning through visuals cannot pass with zero labeled visuals.

This changes `verify.py` (the sensor) and the S4 description in `feature_list.json` (the spec).
The page is untouched; the harness is what gets stronger.

## Lesson

A criterion that can be **satisfied vacuously** is not load-bearing — it is theater.
The test of a good acceptance criterion: **is "pretending to comply" as hard as "actually
complying"?** If not, the criterion needs to be tightened until the two converge.

This is the core of harness engineering: you don't ask the agent to be honest, you design
checks that make dishonest-but-green outcomes impossible. Every patch like this one removes
one more way for "done" to mean less than it should.

## Status

- [ ] verify.py S4 logic upgraded
- [ ] feature_list.json S4 description updated
- [ ] re-verified: a no-image page no longer passes S4 vacuously
- [ ] evidence sample saved under docs/screenshots/

---

## Appendix — Evidence

The generated landing page (variant-a), as captured by Playwright during verification:

![variant-a landing page, full-page screenshot captured by Playwright](screenshots/generated-landing-page.png)

The independent evaluator sub-agent's copy verdict:

```json
{ "C1": true, "C2": true, "C3": true, "C4": true }
```
