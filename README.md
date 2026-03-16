# NHL Web API Reference

_Last updated: 2026-03-09 | Unofficial / Community-Maintained_

> **Important:** These APIs are not officially documented by the NHL. Treat them as "works-now" endpoints that may change without notice. The NHL updated several endpoints around 2024–2025, so older scripts may need migration. Always validate JSON keys, expect missing fields, and handle fallback values.

---

## 1. Base URLs

```text
NHL_URL            = https://www.nhl.com/
NHL_API_URL        = https://api-web.nhle.com/
NHL_API_URL_V1     = https://api-web.nhle.com/v1/
NHL_PLAYER_API_URL = https://api-web.nhle.com/v1/player/
NHL_STATS_API_URL  = https://api.nhle.com/stats/rest/en/
NHL_ASSET_API_URL  = https://assets.nhle.com/
```

| Base URL | Purpose |
|---|---|
| `api-web.nhle.com/v1/` | Modern game, player, score, and schedule endpoints |
| `api.nhle.com/stats/rest/en/` | Stats metadata, glossary, team/country lookups |
| `assets.nhle.com/` | Static assets — logos, player headshots |
| `www.nhl.com/` | Human-facing site links (e.g. gamecenter pages) |

### Browser / CORS note

When making requests from a browser-side app, you'll need a CORS proxy:

```js
const PROXY = 'https://corsproxy.io/?';
const API   = 'https://api-web.nhle.com/v1';

const url = PROXY + encodeURIComponent(API + pathWithQuery);
```

---

## 2. Typical Workflow

Most NHL dashboards follow this pattern:

1. Query the daily scoreboard → `GET /v1/score/{date}`
2. Extract `game_id` values from the response
3. Fetch rich game data → `GET /v1/gamecenter/{game_id}/landing`
4. Parse scoring events, clock state, and player data
5. Render UI — scoreboard, goal summaries, player cards

---

## 3. Score / Scoreboard Endpoints

### Daily scoreboard

```
GET https://api-web.nhle.com/v1/score/{date}
GET https://api-web.nhle.com/v1/score/now        ← alias for today
```

**Example:**
```
https://api-web.nhle.com/v1/score/2026-03-08
```

Returns the daily scoreboard including scheduled, live, and final games.

**Key top-level fields:** `currentDate`, `prevDate`, `nextDate`, `gameWeek`, `games`

**Key per-game fields:**

| Field | Description |
|---|---|
| `id` | Game ID used in other endpoints |
| `gameState` | e.g. `LIVE`, `FINAL`, `PRE` |
| `startTimeUTC` | ISO timestamp |
| `awayTeam` / `homeTeam` | Team info including abbrev, score, logo |
| `clock.timeRemaining` | e.g. `"12:34"` |
| `clock.secondsRemaining` | Integer seconds |
| `clock.running` | Boolean |
| `period` | Current period number |
| `periodDescriptor.number` | Period number |
| `periodDescriptor.periodType` | e.g. `REG`, `OT`, `SO` |
| `gameOutcome.lastPeriodType` | How the game ended |
| `tvBroadcasts` | Broadcast network info |
| `gameCenterLink` | Link to NHL.com game page |
| `goals` | Lightweight goals array |
| `threeMinRecap` / `condensedGame` | Highlight video links |

**Python example:**
```python
import requests

url = "https://api-web.nhle.com/v1/score/2026-03-08"
data = requests.get(url, timeout=30).json()

for game in data.get("games", []):
    away = game["awayTeam"]["abbrev"]
    home = game["homeTeam"]["abbrev"]
    print(away, "@", home)
```

### Scoreboard (alternative)

```
GET https://api-web.nhle.com/v1/scoreboard/now
```

A lighter scoreboard view, useful for quick polling.

---

## 4. Game Center (Landing) Endpoint

```
GET https://api-web.nhle.com/v1/gamecenter/{game_id}/landing
```

**Example:**
```
https://api-web.nhle.com/v1/gamecenter/2025020910/landing
```

The richest single-game endpoint. Prefer this for detailed game cards, scoring breakdowns, and live state.

**Key fields:** `gameState`, `clock`, `periodDescriptor`, `summary`, `scoring`, `tvBroadcasts`, `threeMinRecap`, `condensedGame`

**Per-goal fields inside `scoring[*].goals[*]`:**

| Field | Description |
|---|---|
| `playerId` | Scorer's player ID |
| `firstName.default` / `lastName.default` | Name parts |
| `name.default` | Full name |
| `teamAbbrev.default` | Team abbreviation |
| `headshot` | Headshot URL (use this before constructing manually) |
| `strength` | e.g. `PPG`, `EV`, `SHG` |
| `situationCode` | Situation at time of goal |
| `timeInPeriod` | e.g. `"14:23"` |
| `shotType` | e.g. `wrist`, `slap` |
| `goalModifier` | e.g. `empty-net` |
| `goalsToDate` | Scorer's season total |
| `awayScore` / `homeScore` | Score after this goal |
| `leadingTeamAbbrev.default` | Team in the lead |
| `highlightClip` / `highlightClipSharingUrl` | Clip links |
| `assists[*].playerId` | Assisting player IDs |
| `assists[*].name.default` | Assisting player names |
| `assists[*].assistsToDate` | Season assist total |
| `assists[*].sweaterNumber` | Jersey number |

**Python example:**
```python
import requests

GAME_ID = 2025020910
landing = requests.get(
    f"https://api-web.nhle.com/v1/gamecenter/{GAME_ID}/landing",
    timeout=30,
).json()

for period_block in landing.get("scoring", []):
    period_num = period_block.get("periodDescriptor", {}).get("number")
    for goal in period_block.get("goals", []):
        scorer   = goal.get("name", {}).get("default")
        strength = goal.get("strength")
        t        = goal.get("timeInPeriod")
        print(period_num, t, scorer, strength)
```

### Additional single-game endpoints

```
GET /v1/gamecenter/{game_id}/play-by-play
GET /v1/gamecenter/{game_id}/boxscore
GET /v1/gamecenter/{game_id}/right-rail
GET /v1/wsc/game-story/{game_id}
GET /v1/wsc/play-by-play/{game_id}
```

---

## 5. Standings Endpoints

```
GET https://api-web.nhle.com/v1/standings/now
GET https://api-web.nhle.com/v1/standings/{date}
GET https://api-web.nhle.com/v1/standings-season
```

**Example:**
```
https://api-web.nhle.com/v1/standings/2026-03-08
```

**Key per-team fields:** `teamName`, `teamCommonName`, `teamAbbrev`, `teamLogo`, `points`, `pointPctg`, `wins`, `losses`, `otLosses`, streak data, division rank, conference rank, wildcard sequence.

**Python example:**
```python
import requests

standings = requests.get(
    "https://api-web.nhle.com/v1/standings/now",
    timeout=30,
).json()
teams = standings.get("standings", [])
```

---

## 6. Player Endpoints

### Player landing

```
GET https://api-web.nhle.com/v1/player/{player_id}/landing
```

**Example:**
```
https://api-web.nhle.com/v1/player/8478402/landing
```

Returns a rich player profile including biography, current team, position, handedness, season and career stats, and headshot references.

**Python example:**
```python
import requests

PLAYER_ID = 8478402
player = requests.get(
    f"https://api-web.nhle.com/v1/player/{PLAYER_ID}/landing",
    timeout=30,
).json()
print(player.keys())
```

### Team roster by season

```
GET https://api-web.nhle.com/v1/roster/{team_tricode}/{season}
```

**Example:**
```
https://api-web.nhle.com/v1/roster/TOR/20242025
```

Returns player IDs, jersey numbers, positions, and roster status for the given team and season. Useful for pre-building team dictionaries and mapping player IDs to mugshot URLs.

**Python example:**
```python
import requests

roster = requests.get(
    "https://api-web.nhle.com/v1/roster/TOR/20242025",
    timeout=30,
).json()
print(roster.keys())
```

---

## 7. Schedule Endpoints

```
GET /v1/schedule/now
GET /v1/schedule/{date}
GET /v1/schedule-calendar/now
GET /v1/schedule-calendar/{date}
```

**Examples:**
```
https://api-web.nhle.com/v1/schedule/2026-03-08
https://api-web.nhle.com/v1/schedule-calendar/2026-03-08
```

---

## 8. Playoff Endpoints

```
GET /v1/playoff-bracket/{year}
GET /v1/schedule/playoff-series/{season}/{series_letter}
GET /v1/meta/playoff-series/{year}/{series_letter}
```

**Examples:**
```
https://api-web.nhle.com/v1/playoff-bracket/2025
https://api-web.nhle.com/v1/schedule/playoff-series/20242025/a
```

> Note: Some community references use a single playoff year; others use the full season format (e.g. `20242025`). Validate the format at runtime before standardizing.

---

## 9. Stats Metadata API (`api.nhle.com`)

These endpoints are served from a separate base URL:
```
https://api.nhle.com/stats/rest/en/
```

### Country lookup

```
GET https://api.nhle.com/stats/rest/en/country
```

Country metadata for player nationality, useful for building flag references or normalizing country fields.

### Glossary

```
GET https://api.nhle.com/stats/rest/en/glossary
```

Definitions for statistical terms. Helpful for hover tooltips or documenting advanced fields.

### Team metadata

```
GET https://api.nhle.com/stats/rest/en/team
```

Franchise and team identity lookup. Returns current and historical teams.

**Key fields:** `id`, `franchiseId`, `fullName`, `rawTricode`, `triCode`

> Filter carefully — this endpoint includes historical franchise identities, not just currently active teams.

**Python example:**
```python
import requests

teams = requests.get(
    "https://api.nhle.com/stats/rest/en/team",
    timeout=30,
).json()
rows = teams.get("data", [])
```

**Club-level stats:**

```
GET /v1/club-stats/{team}/now
GET /v1/club-stats/{team}/{season}/{game_type}
```

---

## 10. Broadcast / TV / Location Endpoints

```
GET /v1/where-to-watch
GET /v1/network/tv-schedule/now
GET /v1/network/tv-schedule/{date}
GET /v1/partner-game/{country_code}/now
GET /v1/location
```

The `/v1/location` endpoint returns geographic information used for broadcast restrictions and region-specific content.

---

## 11. Metadata / Utility Endpoints

```
GET /v1/meta
GET /v1/meta/game/{game_id}
GET /v1/season
```

**Examples:**
```
https://api-web.nhle.com/v1/meta?players=8478402&teams=EDM,TOR
https://api-web.nhle.com/v1/meta/game/2025020910
```

---

## 12. Asset URL Patterns

Assets are hosted at `https://assets.nhle.com/` and follow predictable URL patterns. These are not JSON endpoints.

### Team logos

```
https://assets.nhle.com/logos/nhl/svg/{TEAM}_dark.svg
```

**Example:**
```
https://assets.nhle.com/logos/nhl/svg/TOR_dark.svg
```

```python
def team_logo_url(team_abbr: str) -> str:
    return f"https://assets.nhle.com/logos/nhl/svg/{team_abbr}_dark.svg"
```

### Player headshots (mugshots)

```
https://assets.nhle.com/mugs/nhl/{season}/{teamAbbr}/{playerId}.png
```

**Example:**
```
https://assets.nhle.com/mugs/nhl/20242025/TOR/8479318.png
```

```python
def player_mug_url(season: str, team_abbr: str, player_id: int | str) -> str:
    return f"https://assets.nhle.com/mugs/nhl/{season}/{team_abbr}/{player_id}.png"
```

> **Tip:** The `gamecenter/landing` payload often already includes a `headshot` field. Use it directly rather than constructing the URL manually — the manual pattern is a useful fallback when the field is absent.

```js
// JavaScript
const mugUrl = `https://assets.nhle.com/mugs/nhl/${season}/${teamAbbr}/${playerId}.png`;
```

---

## 13. Migration from Pre-2025 APIs

| Legacy Pattern | Current Replacement |
|---|---|
| Scoreboard | `GET /v1/score/{date}` |
| Game data | `GET /v1/gamecenter/{id}/landing` |
| Roster | `GET /v1/roster/{team}/{season}` |
| Player data | `GET /v1/player/{id}/landing` |

---

## 14. Stability & Best Practices

- **Validate all JSON keys** — fields may be absent for in-progress or postponed games.
- **Avoid strict schemas** — use `.get()` in Python or optional chaining in JS.
- **Cache responses** where possible — especially rosters, standings, and metadata that change infrequently.
- **Treat asset URLs as patterns** — not guaranteed contractual interfaces.
- **`.../now` endpoints** often behave as aliases or redirectors — validate at runtime.
- **Schema drift is real** — the 2024–2025 migration changed multiple endpoints; older community examples may be outdated.
- **Use `stats/rest/en/team`** as a stable join table when team identity fields differ across endpoints.
