# NHL API Reference Notes (focused on your dashboard)

Prepared from:
- your uploaded `index.html` dashboard file
- your follow-up endpoint notes and code patterns
- live checks against `https://api-web.nhle.com/v1/...` where possible
- community-maintained reference material used to expand endpoint coverage

## 1) Base URLs

```text
NHL_URL              = https://www.nhl.com/
NHL_API_URL          = https://api-web.nhle.com/
NHL_API_URL_V1       = https://api-web.nhle.com/v1/
NHL_PLAYER_API_URL   = https://api-web.nhle.com/v1/player/
NHL_STATS_API_URL    = https://api.nhle.com/stats/rest/en/
NHL_ASSET_API_URL    = https://assets.nhle.com/
```

Practical mental model:
- `api-web.nhle.com/v1/...` = modern web/game/player endpoints
- `api.nhle.com/stats/rest/en/...` = stats / lookup / glossary-style endpoints
- `assets.nhle.com/...` = logos, mugs, and other static assets
- `www.nhl.com/...` = human-facing site links such as gamecenter pages

For browser-side fetches behind a permissive proxy, your dashboard uses:

```js
const PROXY = 'https://corsproxy.io/?';
const API = 'https://api-web.nhle.com/v1';

const url = PROXY + encodeURIComponent(API + pathWithQuery);
```

---

## 2) Core endpoints used by your dashboard

### Scores by date
```text
GET /v1/score/{date}
Example: /v1/score/2026-03-08
```
Notes:
- Returns `currentDate`, `prevDate`, `nextDate`, `gameWeek`, `oddsPartners`, and `games`.
- Each game commonly includes team names, abbrevs, scores, SOG, logos, broadcasts, clock, period, `periodDescriptor`, `gameCenterLink`, recap links, and a lightweight `goals` array.
- `GET /v1/score/now` behaves like a convenience alias to a dated scoreboard.

Example Python:
```python
import requests

url = "https://api-web.nhle.com/v1/score/2026-03-08"
data = requests.get(url, timeout=30).json()
games = data.get("games", [])
```

### Game landing / gamecenter payload
```text
GET /v1/gamecenter/{game_id}/landing
Example: /v1/gamecenter/2025020910/landing
```
Notes:
- Best single endpoint for a rich game card.
- Commonly contains game metadata, clock, period information, `summary`, `scoring`, player headshots, highlight links, assists, team-side flags, and more.
- This is the endpoint you are already using for scorer cards.

Example Python:
```python
import requests

game_id = 2025020910
url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/landing"
landing = requests.get(url, timeout=30).json()
scoring = landing.get("scoring", [])
```

### Standings
```text
GET /v1/standings/now
GET /v1/standings/{date}
Example: /v1/standings/2026-03-08
```
Notes:
- Includes records like `teamName`, `teamCommonName`, `teamAbbrev`, `teamLogo`, `points`, `pointPctg`, `wins`, `losses`, `otLosses`, streak data, division / conference sequence ranks, wildcard sequence, and more.

Example Python:
```python
import requests

standings = requests.get("https://api-web.nhle.com/v1/standings/now", timeout=30).json()
teams = standings.get("standings", [])
```

### Playoff bracket
```text
GET /v1/playoff-bracket/{year}
Example: /v1/playoff-bracket/2025
```
Notes:
- Community references still document this with a single playoff year.
- If your runtime code prefers a season-form path like `20242025`, validate that behavior before standardizing.

### Playoff series schedule
```text
GET /v1/schedule/playoff-series/{season}/{series_letter}
Example: /v1/schedule/playoff-series/20242025/a
```

---

## 3) Player-specific endpoints

### Player landing
```text
GET /v1/player/{player_id}/landing
Example: /v1/player/8478402/landing
```
Use cases:
- rich player profile page data
- current team / biographical / season context
- often easier than piecing together player identity from boxscore payloads alone

Example Python:
```python
import requests

pid = 8478402
url = f"https://api-web.nhle.com/v1/player/{pid}/landing"
player = requests.get(url, timeout=30).json()
```

### Team roster by season
```text
GET /v1/roster/{team_tricode}/{season}
Example: /v1/roster/TOR/20242025
```
Use cases:
- fetch a club roster for a specific season
- map player IDs for mugshots / player landing links
- useful for prebuilding team dictionaries in local cache

Example Python:
```python
import requests

team_tri_code = "TOR"
season = "20242025"
url = f"https://api-web.nhle.com/v1/roster/{team_tri_code}/{season}"
roster = requests.get(url, timeout=30).json()
```

---

## 4) Stats API (`api.nhle.com/stats/rest/en/`)

This is the league stats / metadata family you called out. It is separate from `api-web.nhle.com/v1/...`.

### Country lookup
```text
GET /stats/rest/en/country
```
Use cases:
- country metadata
- useful when normalizing player nationality or building flag references

Example Python:
```python
import requests

countries = requests.get("https://api.nhle.com/stats/rest/en/country", timeout=30).json()
```

### Glossary
```text
GET /stats/rest/en/glossary
```
Use cases:
- stat term descriptions
- helpful when documenting advanced fields or exposing hover tooltips

Example Python:
```python
import requests

glossary = requests.get("https://api.nhle.com/stats/rest/en/glossary", timeout=30).json()
```

### Team metadata
```text
GET /stats/rest/en/team
```
Use cases:
- franchise and team identity lookup
- current and historical tricodes / franchise IDs / names
- useful join table for mapping team IDs to `triCode`

Example Python:
```python
import requests

teams = requests.get("https://api.nhle.com/stats/rest/en/team", timeout=30).json()
rows = teams.get("data", [])
```

Practical note:
- this endpoint includes current clubs and historical identities, so filter carefully if you only want active modern NHL teams.

---

## 5) Asset URL patterns

These are not JSON endpoints, but they are extremely useful in dashboards.

### Team logos
```text
https://assets.nhle.com/logos/nhl/svg/{TEAM}_dark.svg
```
Example:
```text
https://assets.nhle.com/logos/nhl/svg/TOR_dark.svg
```

Common usage pattern:
```python
def team_logo_url(team_abbr: str) -> str:
    return f"https://assets.nhle.com/logos/nhl/svg/{team_abbr}_dark.svg"
```

### Player mugs / headshots
```text
https://assets.nhle.com/mugs/nhl/{season}/{teamAbbr}/{playerId}.png
```
Example:
```text
https://assets.nhle.com/mugs/nhl/20242025/TOR/8478402.png
```

Common usage pattern from your JS note:
```js
const url = `https://assets.nhle.com/mugs/nhl/${season}/${teamAbbr}/${playerId}.png`;
```

Practical note:
- this pattern is convenient when you already know season, team tricode, and player ID.
- for in-game goal cards, the landing endpoint often already provides `headshot`, which can save you from constructing the URL manually.

### Country flags
There was not a direct flag asset pattern in your supplied code, but with `stats/rest/en/country` available, country metadata can be used to derive or map flag assets in your own layer if needed.

---

## 6) Other related web endpoints worth keeping handy

### Schedule
```text
GET /v1/schedule/now
GET /v1/schedule/{date}
GET /v1/schedule-calendar/now
GET /v1/schedule-calendar/{date}
```
Examples:
```text
/v1/schedule/2026-03-08
/v1/schedule-calendar/2026-03-08
```

### Scoreboard / viewing / TV
```text
GET /v1/scoreboard/now
GET /v1/where-to-watch
GET /v1/network/tv-schedule/now
GET /v1/network/tv-schedule/{date}
GET /v1/partner-game/{country_code}/now
```

### Additional single-game endpoints
```text
GET /v1/gamecenter/{game_id}/play-by-play
GET /v1/gamecenter/{game_id}/boxscore
GET /v1/gamecenter/{game_id}/right-rail
GET /v1/wsc/game-story/{game_id}
GET /v1/wsc/play-by-play/{game_id}
```

### Standings / club-level extras
```text
GET /v1/standings-season
GET /v1/club-stats/{team}/now
GET /v1/club-stats/{team}/{season}/{game_type}
```

### Metadata / utility
```text
GET /v1/meta
GET /v1/meta/game/{game_id}
GET /v1/location
GET /v1/meta/playoff-series/{year}/{series_letter}
GET /v1/season
```

Examples:
```text
/v1/meta?players=8478402&teams=EDM,TOR
/v1/meta/game/2025020910
/v1/location
```

---

## 7) Payload fields that matter most for your current project

### From `/score/{date}`
Useful top-level fields:
- `currentDate`, `prevDate`, `nextDate`
- `gameWeek`
- `games`

Useful per-game fields:
- `id`
- `gameState`
- `gameScheduleState`
- `startTimeUTC`
- `tvBroadcasts`
- `awayTeam`, `homeTeam`
- `clock.timeRemaining`
- `clock.secondsRemaining`
- `clock.running`
- `period`
- `periodDescriptor.number`
- `periodDescriptor.periodType`
- `gameOutcome.lastPeriodType`
- `gameCenterLink`
- `threeMinRecap`, `condensedGame`
- `goals`

### From `/gamecenter/{game_id}/landing`
Useful fields for your scorer carousel / detail panel:
- `gameState`
- `clock`
- `periodDescriptor`
- `summary`
- `scoring`
- `tvBroadcasts`
- `threeMinRecap`, `condensedGame`

Useful per-goal fields inside `scoring[*].goals[*]`:
- `situationCode`
- `eventId`
- `strength`
- `playerId`
- `firstName.default`
- `lastName.default`
- `name.default`
- `teamAbbrev.default`
- `headshot`
- `highlightClipSharingUrl`
- `highlightClip`
- `discreteClip`, `discreteClipFr`
- `goalsToDate`
- `awayScore`, `homeScore`
- `leadingTeamAbbrev.default`
- `timeInPeriod`
- `shotType`
- `goalModifier`
- `pptReplayUrl`
- `homeTeamDefendingSide`
- `isHome`
- `assists[*].playerId`
- `assists[*].name.default`
- `assists[*].assistsToDate`
- `assists[*].sweaterNumber`

### From `/v1/player/{player_id}/landing`
Useful player-level fields to look for:
- identity / naming fields
- current team name or full team name
- handedness / position fields
- season and career split blocks
- profile imagery or mug references depending on payload version

### From `stats/rest/en/team`
Useful join keys:
- `id`
- `franchiseId`
- `fullName`
- `rawTricode`
- `triCode`

---

## 8) Example snippets you can re-use

### A) Load daily scores
```python
import requests

DATE = "2026-03-08"
url = f"https://api-web.nhle.com/v1/score/{DATE}"
data = requests.get(url, timeout=30).json()
for game in data.get("games", []):
    away = game.get("awayTeam", {}).get("abbrev", {}).get("default")
    home = game.get("homeTeam", {}).get("abbrev", {}).get("default")
    print(away, "@", home)
```

### B) Load landing and flatten scoring
```python
import requests

GAME_ID = 2025020910
landing = requests.get(
    f"https://api-web.nhle.com/v1/gamecenter/{GAME_ID}/landing",
    timeout=30,
).json()

for period_block in landing.get("scoring", []):
    period_desc = period_block.get("periodDescriptor", {})
    period_num = period_desc.get("number")
    for goal in period_block.get("goals", []):
        scorer = goal.get("name", {}).get("default")
        strength = goal.get("strength")
        t = goal.get("timeInPeriod")
        print(period_num, t, scorer, strength)
```

### C) Load player landing
```python
import requests

PLAYER_ID = 8478402
player = requests.get(
    f"https://api-web.nhle.com/v1/player/{PLAYER_ID}/landing",
    timeout=30,
).json()
print(player.keys())
```

### D) Load team roster for a season
```python
import requests

TEAM = "TOR"
SEASON = "20242025"
roster = requests.get(
    f"https://api-web.nhle.com/v1/roster/{TEAM}/{SEASON}",
    timeout=30,
).json()
print(roster.keys())
```

### E) Load stats glossary
```python
import requests

glossary = requests.get(
    "https://api.nhle.com/stats/rest/en/glossary",
    timeout=30,
).json()
print(glossary.keys() if isinstance(glossary, dict) else type(glossary))
```

### F) Build common asset URLs
```python
def team_logo_url(team_abbr: str) -> str:
    return f"https://assets.nhle.com/logos/nhl/svg/{team_abbr}_dark.svg"


def player_mug_url(season: str, team_abbr: str, player_id: int | str) -> str:
    return f"https://assets.nhle.com/mugs/nhl/{season}/{team_abbr}/{player_id}.png"
```

---

## 9) Practical notes for your own codebase

- Prefer `gamecenter/{game_id}/landing` for rich game detail cards and scoring breakdowns.
- Prefer `/score/{date}` for listing many simultaneous games quickly.
- Use `stats/rest/en/team` as a stable helper table when team identity fields differ across endpoints.
- Use `/v1/player/{player_id}/landing` when you need player-centric context beyond a single game.
- When a landing payload already includes a headshot URL, use it first; fall back to the `assets.nhle.com/mugs/...` pattern only when needed.
- Treat some community-documented endpoints as observed rather than formally versioned documentation; runtime validation is still wise.

---

## 10) Known caveats

- The NHL web APIs are not documented like a polished public developer product, so schema drift does happen.
- The 2025-era changes you mentioned are real enough that older mental models from pre-`api-web.nhle.com` or early migration examples can mislead.
- Some endpoints behave like aliases or redirectors, especially `.../now` patterns.
- Asset URL patterns are very useful, but they should still be treated as implementation patterns rather than guaranteed contractual interfaces.
