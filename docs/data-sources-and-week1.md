# Pep's reign: free data sources and week-1 status

Checked 25 Nov 2026. Scope: Man City, Premier League, 2016/17 to 2024/25 (Pep's nine seasons).

## Verdict on the attachment's source list

The attachment is a good starting point, but three claims need correcting:

1. **FBref is no longer a usable xG source.** Sports Reference removed FBref's advanced statistics on 20 January 2026, after Opta ended the arrangement. Basic scores, tables and goal tallies remain, but xG, progressive passes and shot-creating actions are gone. Do not build the project on FBref.
2. **FBref's terms are stricter than the attachment implies.** Sports Reference's data-use page says not to create websites or tools based on scraped data, and not to use its data to train generative AI without permission. Even the basic pages are not a safe scrape target.
3. **Free event data for Pep's era does not exist.** StatsBomb's open data includes only the 2015/16 Premier League (checked against its competitions.json). That is a baseline for method checks, not part of the Pep analysis.

## Source inventory

| Source | What it gives | Status for this project | Access from my sandbox |
|---|---|---|---|
| **openfootball/england** (GitHub, public domain) | PL match results and scores | **Use as the results spine.** Downloaded all 9 seasons, 380 matches each, 3,420 total | Reachable |
| **Football-Data.co.uk** | Results, shots, shots on target, corners, fouls, cards, betting odds, per season as CSV | **Use.** Free CSVs, long history, plus a bookmaker-implied strength benchmark | Blocked (proxy 403). Download on your own machine |
| **Understat** | Shot-level xG with x/y coordinates, match xG, PPDA, team season totals | **Use for xG and shot maps.** No official API, so scrape politely and cache once. xG is Understat's own model | Blocked (proxy 403). Run locally |
| **ClubElo** (api.clubelo.com) | Team Elo ratings over time, free CSV endpoint | **Use as an independent strength baseline** (did City's rating move with results?) | Blocked. Run locally |
| **StatsBomb open data** | Event data | **Method check only.** The only free PL coverage is 2015/16 | Reachable (GitHub) |
| **FBref** | Basic tables only since Jan 2026 | **Drop** for xG. Terms restrict scraping | Blocked |
| **Premier League official stats** | Team stats, official xG from 2012/13 (per attachment) | **Spot-check only.** Scraping is restricted | Not tested |

## What I built this session

- `pl_matches_2016_25.csv`: 3,420 PL matches parsed from openfootball, with season, home and away team, and full-time goals.
- `pl_tables_2016_25_computed.csv`: league tables for each season, computed from those matches.
- `man_city_season_summary.csv`: City's season line, with the champion's points for comparison.

Validation: the computed tables reproduce City's known points and goals in the seasons I checked: 2017/18 (100 pts, 106 GF, 27 GA), 2018/19 (98 pts, 95 GF, 23 GA), 2019/20 (81 pts, 102 GF, 35 GA), and 2024/25 (71 pts, 3rd). Champion points also match. **I checked these against my own recollection of published tables, not against premierleague.com, which I could not reach.** Please spot-check two or three seasons against the official table before you rely on them.

Known gap: the team names differ between sources ("Manchester City" vs "Manchester City FC"). I normalised them in `build_tables.py`, but this mapping needs to be built properly before joining to Understat or Football-Data.

## Week 1, revised

1. **Local machine:** install soccerdata (`pip install soccerdata`). In my sandbox, its import failed on a missing `fasteners` dependency, so check it works before you rely on it.
2. **Understat:** pull City's match and shot data for 2016 to 2024 with soccerdata's Understat class, and cache it. Check the team-name mapping.
3. **Football-Data.co.uk:** download the E0 CSV for each season from 2016/17 to 2024/25 and save it locally.
4. **Join:** match openfootball results to Football-Data and Understat on date and team. Check that the scores agree.
5. **Minimum tier:** build the season table (points, goals, xG, xGA, possession if available) and check points against the official table.
6. **Decide on the xG model** only after the minimum tier works. The attachment's point about needing several seasons of training data still holds.

## Still to decide

- Primary metric: points per game, xG difference, or trophies. Pick one, with two secondary metrics.
- End point: the attachment says 2024/25 is Pep's final season. Confirm this before you start.
- Publication: publish derived numbers only, not raw data dumps, and cache each source once.
