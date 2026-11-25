# Project plan

## Goal

Measure how good Manchester City were under Pep Guardiola (2016/17 to 2024/25), with a clear primary metric, reproducible code, and a short write-up a hiring manager can read in five minutes.

## Definition of "good"

- **Primary:** points per game.
- **Secondary:** xG difference per game (Understat) and goal difference per game.
- **Context:** Elo rating (ClubElo) as an independent strength baseline.

Trophies are reported as context, not as a metric.

## Scope tiers

| Tier | Deliverable | Status |
|---|---|---|
| Minimum | Season table 2016/17 to 2024/25: points, goals, GD, position, points per game. Checked against official tables. | Pipeline and tests in place. Official check still to do. |
| Standard | Add xG per game, shot quality, PPDA, comparison with the league average and with City's pre-Pep baseline. Shot map dashboard from Understat coordinates. | Not started. Needs Understat and Football-Data pulls. |
| Ambitious | Own xG model, finishing over/under-performance, season style clustering, effect of key absences. | Not started. Needs several seasons of training data. |

## Milestones

1. **Data ingestion.** Results from openfootball, plus Understat, Football-Data.co.uk and ClubElo, cached once, each with a schema check.
2. **Minimum tier.** Season table, validated against official points and goals.
3. **Standard tier.** xG and comparisons. Dashboard published.
4. **Modelling (optional).** Baseline models in scikit-learn, then XGBoost, tracked with MLflow.
5. **Write-up.** README results section plus a short post. Publish derived numbers only.

## Working agreements

- Every pipeline stage validates its output with pandera.
- Tests use small fixtures, not full downloads. CI runs without network access.
- Notebooks explore. Anything that feeds a result moves into `src/` with a test.
- One branch per milestone, merged through pull requests with CI passing.

## Open decisions

- Confirm 2024/25 as the final season (Pep's last game as City manager). The plan assumes it is.
- Team name mapping for Understat and Football-Data. Build the alias table before joining.
- Whether to commit `pl_tables.csv` as a sample, so the dashboard runs without re-ingesting.
