# Research Quality Measurement

Use this skill to grade bug research only after checking every claim, snippet,
and repository-relative `file:line` reference against the current source.

## Levels

| Level | Criteria |
| --- | --- |
| `EXCELLENT` | Every material claim and reference is correct, snippets are exact, scope is complete, and no discrepancy affects planning. |
| `GOOD` | At least 90% of claims are correct and any discrepancy is minor, explicit, and does not change the proposed fix. |
| `NEEDS_IMPROVEMENT` | One or more material claims are incomplete or incorrect, but verified evidence is still sufficient to continue after the planner excludes disputed claims. |
| `UNRELIABLE` | References are missing or fabricated, fewer than 70% of material claims verify, or the evidence cannot support a safe implementation plan. |

## Measurement Procedure

1. List every factual claim and reference in the source research.
2. Open the referenced file and inspect the cited line and surrounding context.
3. Compare quoted snippets character-for-character, allowing indentation-only
   differences when meaning is unchanged.
4. Record verified and disputed claims separately.
5. Select the lowest level whose criteria the complete research satisfies.
6. Stop the pipeline when the result is `UNRELIABLE`.

## Required Report Format

`verified-research.md` must contain:

- `Verification Summary`: pass/fail, counts, and selected Research Quality level.
- `Verified Claims`: claim, evidence, and checked `file:line`.
- `Discrepancies Found`: every mismatch or `None`.
- `Research Quality Assessment`: level and concrete reasoning.
- `References`: all inspected paths.
