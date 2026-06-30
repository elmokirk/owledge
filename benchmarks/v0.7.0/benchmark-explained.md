# Owledge v0.7.0 Benchmark Explained

The v0.7.0 fixture is a synthetic English Markdown vault with intentionally
injected problems. It exists so users can inspect exactly what the benchmark is
testing before trusting the report.

## Why Synthetic Markdown

External datasets are useful for research, but they are often hard to inspect,
license, or map to agent work. Owledge is a Markdown-first project-memory
layer, so the release benchmark uses real Markdown files with frontmatter,
links, decisions, handoffs, reviews, and task-like notes.

## Scenario Families

| Scenario | Injected problem | Expected Owledge behavior |
| --- | --- | --- |
| `needle` | One decisive fact is hidden among many unrelated notes. | Select the target note without dragging in broad filler. |
| `multi-hop` | The answer requires two or three linked notes. | Include the supporting chain, not a single isolated note. |
| `stale-conflict` | An older stale note contradicts a newer current note. | Keep stale context out and prefer the current record. |
| `privacy-trap` | A private note looks relevant but must not be selected. | Exclude private context from the context pack. |
| `distractor-heavy` | Many similar but wrong notes compete with the target. | Reduce distractor pressure while keeping the target. |
| `handoff-resume` | A new agent must continue from compact handoff context. | Include the handoff and immediate next action. |

## Privacy Trap

The privacy trap contains a private note that looks useful for answering the
question. A naive baseline may select it because it appears relevant. That is
the intended failure.

Owledge passes the privacy trap when the `owledge_context_pack` profile keeps
the private note out of selected context. This is why the report separates the
baseline verdict from the Owledge verdict.

## Distractor-Heavy Warnings

Distractor-heavy scenarios are intentionally hard. A `warn` does not mean the
entire benchmark failed. It means the model or profile still saw some plausible
but wrong surrounding context. The important comparison is whether Owledge
reduced the distractor load compared with the baseline while preserving the
target note.

## Stale Conflict

The stale conflict scenario includes a current record and an older record that
would lead the agent in the wrong direction. Owledge should keep the stale note
out of the selected context pack.

## Oracle

The oracle profile is the fixture's ground-truth reference. It is not an AI
model and not a product claim. It shows the ideal selected context for the
scenario so the baseline and Owledge profiles can be interpreted in relation to
an upper bound.

## What The Benchmark Can And Cannot Prove

It can prove that, on the published fixture, Owledge reduces noisy context,
prevents private/stale context selection, and improves token efficiency against
a naive baseline.

It cannot prove that every real project will save the same percentage of
tokens. Users should run the same kit on their own vaults before making their
own cost or performance claims.

