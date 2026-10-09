# Experiment log

Each round follows the same loop: **hypothesis → change one thing → run on the dev set → item-level review → keep / revert.**
Prompt version, model and date are recorded for every run; per-essay metrics are in `results/<tag>/summary.csv`
(raw outputs contain essay text and are not published).

## Method

- **Dev set:** 5 essays — 2 public/self-written samples (`data/samples/`) + 3 private learner essays (not in the repo). The same set was used in every round so versions are comparable.
- **Review:** every piece of feedback becomes one row in `review_items.csv`. The teacher marks **✓** correct and useful · **~** correct but needs work · **✗** wrong, invented or harmful, and labels failures with a fixed vocabulary:
  `fake` (problem doesn't exist) · `duplicate` · `too_hard` (above i+1) · `severity` · `rewrite_off` (rewrite wrong or changes more than the issue) · `band` · `want_more` (correct, but wants more help) · `other`.
- **Row types:** `I/O/V/G` issues per aspect · `N` grammar structures to learn · `W` vocabulary to learn · `P` perspectives · `S` summary · `L` level · `B` band · `X` items the pipeline dropped (✓ = correct drop, ✗ = a real item was dropped).
- **Model:** Claude Sonnet via the Anthropic API. Temperature cannot be set with the SDK version used, so run-to-run variance is not controlled; differences of 1–2 items between rounds may be noise.

## Results at a glance

| Tag | Issues ✓ | Grammar ✗ | Learning items (N+W) ✓ | Tokens in / out per essay | Calls |
|---|---|---|---|---|---|
| v1 | (read-through only) | — | — | 6.8k / 4.3k | 1 |
| v2 | 81% (35/43) | 2 / 9 | — | ~7.2k / ~4.0k | 1 |
| v3 | 83% (30/36) | 5 / 8 | 6/8 (structures only) | ~9.3k / ~4.0k | 1 (+1 retry on one essay) |
| v4 | **97% (29/30)** | **0 / 3** | **48/50** | ~12.4k / ~5.0k | 2 |
| v4.1 | filters re-run on v4 outputs (no API calls) | — | removes the 2 remaining ✗ | — | 2 |

---

## legacy-v1 — 2026-10-06 · `scoring_v1 + diagnosis_v1`
- **Change:** inherited from the earlier prototype (`ielts-writing-feedback-agent`): output via forced tool use + JSON schema instead of free-text JSON.
- **Result:** no more crashes from malformed JSON; bands vary between two identical runs.
- **Decision:** keep `core/llm.py`.

## v1 — 2026-10-06 · `ielts_v1`
- **Change:** new 4-aspect prompt + band, one call, Pydantic schema.
- **Hypothesis:** runs end to end.
- **Result:** valid schema first time, 0 invented quotes. Read-through found: one problem reported under two aspects; rewrites far above i+1 (*affluence, prerequisites, leveraged* for a B1 writer); rewrites changing more than the issue; empty `learn_cefr`; "perspectives" written as long C1 sentences; severity too high.
- **Decision:** → v2.

## v2 — 2026-10-06 · `ielts_v2`
- **Change:** (1) one problem = one aspect, with routing rules; (2) rewrite fixes only the issue; (3) hard i+1 limit with banned-word examples; (4) `learn_cefr` required; (5) perspectives as ≤12-word notes; (6) understandable-but-wrong = medium severity; (7) TR ≤ 6.5 if a body paragraph is undeveloped.
- **Hypothesis:** removes the six v1 problems.
- **Result:** 43 items: **✓ 81% · ~ 12% · ✗ 7%**. Band, level and perspectives 100% ✓; no `too_hard` or `duplicate` → v1 problems fixed.
  Remaining: **2/9 grammar issues invented** (`fake`); one ideas rewrite inconsistent with the next sentence; teacher wanted *more* help (ways to develop ideas, ~4 alternatives, new structures); the summary missed a missing conclusion and rambling.
  Code: the duplicate detector raised 26 false alarms; 3 "invented quotes" were actually quoted from the question.
- **Decision:** keep → v3.

## v3 — 2026-10-06 · `ielts_v3`
- **Change:** prompt tells the model to re-check grammar/vocabulary issues before reporting, forbids quoting the question, requires rewrites to fit the surrounding sentences, adds an essay-structure check to the summary. Schema adds `hints_vi`, `alternatives_en`, `next_structures`, `summary.structure`. Duplicate detection only compares vocabulary × grammar issue pairs; quotes from the question are counted separately.
- **Hypothesis:** grammar `fake` → 0, ✓ ≥ 81%, output ~20–30% longer.
- **Result:** 36 items: ✓ 83% · ~ 3% · ✗ 14%. **Grammar ✗ 5/8 — worse than v2 (2/9).** 2 of the 5 had a rewrite identical to the original (the model itself found nothing to fix); 2 named the wrong error; 1 contradicted its own rewrite.
  Ideas 10/10 ✓ (hints accepted), summary 5/5 ✓, structure flags correctly caught missing introductions/conclusions. Teacher: suggested structures not new enough and too few; alternatives must be full chunks. Input ~9k tokens (+30%); one essay needed a schema retry (2× cost).
- **Takeaway:** an instruction inside the same prompt does not make the model verify itself.
- **Decision:** keep ideas/summary changes → v4.

## v4 — 2026-10-07 · `ielts_v4 + verify_v1`
- **Change:** (1) code drops grammar/vocabulary issues whose rewrite equals the original (on v3 outputs: caught 2 of 5 ✗, no false drops); (2) **separate verifier call** for grammar + vocabulary claims → `real` / `mislabeled` (rename) / `not_real` (drop); (3) learning lists with minimums — `next_structures` 3–4 (new structure or new combination), `next_vocab` 4–6 chunks, alternatives as full chunks; (4) prompt lists known false alarms. Dropped items are shown to reviewers as `X` rows.
- **Hypothesis:** grammar ✗ ≤ 1; no real issue dropped (X ✗ = 0); +1 call costs ~1–2k tokens.
- **Result:** **issues ✓ 97% (29/30)**, ~ 1, ✗ 0. **Grammar ✗ 0/3** (v3: 5/8). X rows: 3/3 correct drops (2 by code, 1 by verifier); the verifier renamed 3 issues, including the *for/in* preposition error mislabelled as an article error in v3. Learning items: **48/50 ✓** (20 structures + 30 chunks). All 113 rows: ✓ 97%.
  Remaining ✗ share one pattern — *suggesting something the learner already uses* (a chunk already in the essay, a structure example identical to the original, an alternative containing the over-used word) — plus 5 truncated quotes in N/W items.
  Cost ~12.4k in / 5k out tokens, 2 calls (≈ +50% vs v2).
- **Caveat:** four rounds tuned on the same 5 essays → needs confirmation on new essays.
- **Decision:** keep — tagged **`v0.1`**.

## v4.1 — 2026-10-09 · `ielts_v4 + verify_v1 + filters`
- **Change:** no prompt change. `core/filters.py` drops learning suggestions in code: structure examples identical to the original; chunks already in the essay (whole-word match) or examples changing ≤ 1 word; alternatives (for repetition issues) that contain a word repeated ≥ 3 times. Truncated quotes in N/W are counted (`truncated_quotes`), not rewritten.
- **Result (re-run on v4 outputs, no API calls):** caught **3/3** teacher-✗ items with **0** teacher-✓ items dropped; detected **4/4** truncated quotes.
  Two fixes along the way: the first alternatives filter also dropped 4 good suggestions → narrowed to repetition issues only; the first version *repaired* truncated quotes, which would have shown learners half of their own sentence as "deleted" and broke the comparison step — caught by a unit test, replaced by counting.
- **Decision:** keep. Next measurement comes from the live pilot.

---

## Next: live pilot
Students rate items 👍/👎 and can flag "I think this isn't wrong"; teacher reviewers use the same ✓/~/✗ scheme in the app. `evaluation/pull_sheet.py` converts live data to this review format and reports inter-rater agreement. Results will be logged here as `live-*` rounds.
