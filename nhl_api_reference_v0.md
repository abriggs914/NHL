# NHL API Reference Notes (focused on your dashboard)

Prepared from:
- your uploaded `index.html` dashboard file
- live checks against `https://api-web.nhle.com/v1/...`
- an unofficial community reference used only to expand endpoint coverage

## 1) Base URL

```text
https://api-web.nhle.com/v1
```

For browser-side fetches behind a permissive proxy, your dashboard uses:

```js
const PROXY = 'https://corsproxy.io/?';
const API = 'https://api-web.nhle.com/v1';

const url = PROXY + encodeURIComponent(API + pathWithQuery);
```

---

## 2) Endpoints used directly by your uploaded dashboard

### Scores by date
```text
GET /v1/score/{date}
Example: /v1/score/2026-03-08
```
Notes:
- Returns `currentDate`, `prevDate`, `nextDate`, `gameWeek`, `oddsPartners`, and `games`.
- Each game commonly includes team names, abbrevs, scores, SOG, logos, broadcasts, clock, period, periodDescriptor, gameCenterLink, recap links, and a lightweight `goals` array.
- `GET /v1/score/now` currently redirects to the dated form.

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
- Best endpoint for a rich single-game view.
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
- `standings/now` currently redirects to the dated form.
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
- Community references still document the bracket endpoint with a single playoff year.
- Your HTML currently calls `/playoff-bracket/{season}` with a season string like `20242025`; verify this against live behavior before standardizing.
- The same dashboard falls back to building a projection from standings if bracket data is unavailable.

### Playoff series schedule
```text
GET /v1/schedule/playoff-series/{season}/{series_letter}
Example: /v1/schedule/playoff-series/20242025/a
```

---

## 3) Closely related endpoints worth keeping handy

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
Examples:
```text
/v1/scoreboard/now
/v1/where-to-watch
/v1/network/tv-schedule/2026-03-06
/v1/partner-game/US/now
```

### Additional single-game endpoints
```text
GET /v1/gamecenter/{game_id}/play-by-play
GET /v1/gamecenter/{game_id}/boxscore
GET /v1/wsc/game-story/{game_id}
GET /v1/wsc/play-by-play/{game_id}
```
Examples:
```text
/v1/gamecenter/2025020910/play-by-play
/v1/gamecenter/2025020910/boxscore
/v1/wsc/game-story/2025020910
```

### Standings / club-level extras
```text
GET /v1/standings-season
GET /v1/club-stats/{team}/now
GET /v1/club-stats/{team}/{season}/{game_type}
```
Examples:
```text
/v1/standings-season
/v1/club-stats/TOR/now
```

### Miscellaneous metadata
```text
GET /v1/meta
GET /v1/meta/game/{game_id}
GET /v1/location
GET /v1/meta/playoff-series/{year}/{series_letter}
```
Examples:
```text
/v1/meta?players=8478402&teams=EDM,TOR
/v1/meta/game/2025020910
/v1/location
```

### Seasons and draft
```text
GET /v1/season
GET /v1/draft/rankings/now
GET /v1/draft/rankings/{season}/{prospect_category}
GET /v1/draft-tracker/picks/now
GET /v1/draft/picks/now
GET /v1/draft/picks/{season}/{round}
```

---

## 4) Payload fields that matter most for your current project

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
- per-goal fields inside `scoring[*].goals[*]`:
  - `situationCode`
  - `eventId`
  - `strength`
  - `playerId`
  - `firstName.default`
  - `lastName.default`
  - `name.default`
  - `teamAbbrev.default` or `teamAbbrev`
  - `headshot`
  - `highlightClipSharingUrl`
  - `goalsToDate`
  - `awayScore`, `homeScore`
  - `timeInPeriod`
  - `shotType`
  - `goalModifier`
  - `pptReplayUrl`
  - `isHome`
  - `assists[]`

### From `/standings/{date}`
Useful fields for standings / playoff projection:
- `conferenceAbbrev`, `conferenceName`
- `divisionAbbrev`, `divisionName`
- `conferenceSequence`, `divisionSequence`, `wildcardSequence`, `leagueSequence`
- `teamName.default`, `teamCommonName.default`, `teamAbbrev.default`
- `teamLogo`
- `points`, `pointPctg`
- `wins`, `losses`, `otLosses`
- `regulationWins`, `regulationPlusOtWins`
- `gamesPlayed`
- `streakCode`, `streakCount`

---

## 5) Practical guidance after the 2025-era changes

### Recommended endpoint choices now
- Use `/score/{date}` for a lightweight day board and high-level goal list.
- Use `/gamecenter/{game_id}/landing` for a rich per-game panel and scoring summary.
- Use `/gamecenter/{game_id}/play-by-play` when you need the most detailed event stream.
- Use `/standings/now` or `/standings/{date}` for ranking, wildcard, and seeding logic.
- Use `/playoff-bracket/{year}` only after confirming the current expected path format in your runtime environment.

### Old vs new mental model
If you previously relied on the older `statsapi.web.nhl.com` ecosystem, the newer public web-facing feed centers much more heavily on:
- `api-web.nhle.com/v1/...`
- dated resources that often have a `/now` convenience alias
- richer gamecenter documents (`landing`, `boxscore`, `play-by-play`)
- paths that are oriented around frontend consumption rather than classic REST consistency

### Defensive coding suggestions
- Expect `/now` endpoints to redirect to dated URLs.
- Keep alias handling for field names where similar concepts appear in slightly different shapes across endpoints.
- Prefer `dict.get(...)` everywhere; some nested objects are omitted for pregame or postponed states.
- Treat playoff endpoints as the least stable part of the public surface and keep a standings-based fallback.
- Cache `landing` responses per game, but invalidate during live states.

---

## 6) Copy-paste Python examples

### Daily scores
```python
import requests

DATE = "2026-03-08"
url = f"https://api-web.nhle.com/v1/score/{DATE}"
data = requests.get(url, timeout=30).json()

for game in data.get("games", []):
    away = game.get("awayTeam", {})
    home = game.get("homeTeam", {})
    print(
        game.get("id"),
        away.get("abbrev"), away.get("score"),
        home.get("abbrev"), home.get("score"),
        game.get("gameState")
    )
```

### Landing + scoring summary
```python
import requests

GAME_ID = 2025020910
url = f"https://api-web.nhle.com/v1/gamecenter/{GAME_ID}/landing"
landing = requests.get(url, timeout=30).json()

for period_block in landing.get("scoring", []):
    pd = period_block.get("periodDescriptor", {})
    print("Period", pd.get("number"), pd.get("periodType"))
    for goal in period_block.get("goals", []):
        scorer = goal.get("name", {}).get("default")
        t = goal.get("timeInPeriod")
        strength = goal.get("strength")
        print(f"  {t} {scorer} [{strength}]")
```

### Standings snapshot
```python
import requests

url = "https://api-web.nhle.com/v1/standings/now"
standings = requests.get(url, timeout=30).json().get("standings", [])

for team in standings[:5]:
    print(
        team.get("teamAbbrev", {}).get("default"),
        team.get("points"),
        team.get("wildcardSequence"),
        team.get("streakCode"),
        team.get("streakCount"),
    )
```

### Your current dashboard fetch helper pattern
```python
import requests
from urllib.parse import quote

PROXY = "https://corsproxy.io/?"
API = "https://api-web.nhle.com/v1"

path = "/score/2026-03-08"
url = PROXY + quote(API + path, safe="")
resp = requests.get(url, timeout=30)
resp.raise_for_status()
data = resp.json()
```

---

## 7) Short checklist for your project

- Keep using `/score/{date}` for the multi-game scoreboard.
- Keep using `/gamecenter/{game_id}/landing` for goal cards and detailed scoring.
- Add `/gamecenter/{game_id}/play-by-play` if you want richer live event cards.
- Use `/standings/now` for the standings tab and projection fallback.
- Re-test playoff bracket pathing before hard-coding one format.
- Preserve your field-alias layer, because the feed is not perfectly uniform.

