# Evidence-Based Coding Checklist

Use this checklist when implementation, review, or refactor work touches code quality concerns such as magic values, complexity, duplication, naming, or shared abstractions.

Canonical standard: `docs/ai/standards/evidence-based-coding-standards.md`.

## Review Steps

1. Confirm scope.
- Apply this checklist to changed code and directly affected helpers only.
- Do not rewrite unrelated legacy code to satisfy the checklist.

2. Check named values.
- By default, name business thresholds, protocol/status codes, timeouts, retries, sizes, coordinates, capacities, scores, probabilities, and unit-bearing values.
- Allow obvious literals such as `0`, `1`, `-1`, simple loop increments, and local test fixture data.
- Prefer names with units: `_ms`, `_px`, `_count`, `_limit`, `_ratio`.

3. Check complexity.
- Flag deep nesting, long condition chains, wide `match/case`, repeated branch bodies, and functions that are hard to cover.
- Prefer early returns, lookup tables, smaller functions, or clear strategy boundaries.
- Do not add an abstraction if it requires many flags or hides a simple rule.

4. Check size and responsibility.
- Use existing code-shape budgets as the first signal.
- When a function or class grows, identify whether I/O, parsing, rules, validation, rendering, persistence, and reporting are mixed.
- Split only along a real responsibility boundary.

5. Check duplication.
- Extract only when the duplicate represents the same domain concept, will change together, and has at least two real call sites.
- Keep intentional duplication when it isolates protocols, reduces coupling, or the similar shapes have different meanings.
- If preserving a non-obvious duplicate, leave a short local comment or final-review note.

6. Check naming.
- Names should explain intent, not implementation trivia.
- Avoid vague reusable buckets such as `common`, `util`, `helper`, `manager`, `data`, `info`, or `tmp` unless the surrounding scope makes them precise.

7. Check public abstraction triggers.
- Public helpers/classes need at least two real call sites, one shared domain concept, consistent change direction, simpler dependencies after extraction, and test or smoke coverage.
- Boundary abstractions for external APIs, schema contracts, framework lifecycle hooks, or cross-process protocols may appear before two call sites, but require an explicit boundary rationale.
- Prefer local direct code when only one call site exists or when extraction increases branching.

## Severity

- High: correctness, security, permissions, money, protocols, persistence, release, user-visible behavior, or repeated bugfix risk.
- Medium: core-path readability, public API/schema naming, unit semantics, responsibility boundary, or test maintainability.
- Low: local readability, weak local names, fixture literals, small duplication, or polish.

## Closeout

- Treat this checklist as `review-required`.
- Summarize outcomes as `checked`, `fixed`, `deferred with rationale`, or `no material issue`.
- Mark Low-only comments as `nit` / non-blocking unless they accumulate into real maintainability risk.
- Do not enable new Ruff or ESLint rules as part of ordinary implementation.
- Record durable exceptions in status or ADR only when the exception will affect future tasks.
