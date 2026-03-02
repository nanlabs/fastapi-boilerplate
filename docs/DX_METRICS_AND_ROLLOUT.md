# DX Metrics and Rollout

Use this guide to validate whether Dev Container + Git + pre-commit decisions are improving or hurting daily developer experience.

## Success metrics

Track weekly:

- Onboarding time
  - Target: first successful run in <= 15 minutes.
- Local commit latency
  - Target: fast local hooks (ideally < 5s for common commits).
- Environment-related failures
  - Target: close to zero issues caused by host/container mismatch.
- CI duration and reliability
  - Target: stable CI runtime and low flaky-job rate.

## How to measure

- Onboarding time:
  - measure from clone to first green `make test` in Dev Container.
- Local commit latency:
  - sample 10 commits and track pre-commit duration.
- Environment-related failures:
  - count issues/PR comments caused by line endings, missing tools, hook mismatch, or auth.
- CI health:
  - track average run time and rerun rate per workflow.

## Rollout plan

### Week 1

- Communicate Host vs Container contract.
- Enable fast local hooks strategy.
- Capture baseline metrics.

### Week 2

- Keep strict CI gates (`full-quality`, `tests`).
- Optionally enable `mega-linter` by setting repository variable:
  - `ENABLE_MEGA_LINTER=true`
- Compare CI times against baseline.

### Week 3

- Evaluate friction points with real team feedback.
- Tune hook scope and CI parallelization if needed.
- Decide whether mega-linter stays mandatory for all PRs.

## Decision checklist

- If local commit flow feels slow, move more checks from local hooks to CI.
- If CI becomes too slow, split jobs further and optimize cache.
- If onboarding fails repeatedly, improve docs before adding more automation.
