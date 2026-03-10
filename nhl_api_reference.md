# Unofficial NHL Web API Reference (2025+)

_Last generated: 2026-03-09 22:58 UTC_

This document provides an **instructional reference** for the NHL public web APIs currently used by dashboards and analytics tools.

These endpoints are **not officially documented by the NHL** and should be treated as a **“works-now” API** that may change. The NHL modified several endpoints around **2024–2025**, so older scripts may require updates.

---

# 1. Base URL Constants

These base URLs appear throughout NHL web applications and scripts.

```python
NHL_ASSET_API_URL = "https://assets.nhle.com/"
NHL_STATS_API_URL = "https://api.nhle.com/stats/rest/en/"
NHL_API_URL = "https://api-web.nhle.com/"
NHL_API_URL_V1 = f"{NHL_API_URL}v1/"
NHL_PLAYER_API_URL = f"{NHL_API_URL_V1}player/"
NHL_URL = "https://www.nhl.com/"
```

| Base URL | Purpose |
|--------|--------|
| api-web.nhle.com | Primary modern NHL web API |
| api.nhle.com/stats | Structured stats endpoints |
| assets.nhle.com | Static media assets |
| nhl.com | NHL website frontend |

---

# 2. Scoreboard Endpoint

### Endpoint

```
GET https://api-web.nhle.com/v1/score/{date}
```

### Example

```
https://api-web.nhle.com/v1/score/2025-03-01
```

### Description

Returns the **daily scoreboard** including:

- scheduled games
- live games
- final scores
- team information
- broadcast networks
- game IDs

### Python Example

```python
import requests

url = "https://api-web.nhle.com/v1/score/2025-03-01"
data = requests.get(url).json()

games = data["games"]
```

---

# 3. Game Landing Endpoint

### Endpoint

```
GET https://api-web.nhle.com/v1/gamecenter/{game_id}/landing
```

### Example

```
https://api-web.nhle.com/v1/gamecenter/2025020910/landing
```

### Description

Returns the **complete dataset for a game**, used by the NHL website.

Includes:

- scoreboard state
- game clock
- scoring events
- highlight clips
- player data
- team metadata
- broadcast information

### Example

```python
url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/landing"
data = requests.get(url).json()

scoring = data["scoring"]
```

---

# 4. Player API

### Endpoint

```
GET https://api-web.nhle.com/v1/player/{player_id}/landing
```

### Example

```
https://api-web.nhle.com/v1/player/8478402/landing
```

### Description

Returns player information including:

- biography
- current team
- stats summary
- headshot URLs
- season statistics

### Python Example

```python
url = "https://api-web.nhle.com/v1/player/8478402/landing"
player = requests.get(url).json()
```

---

# 5. Team Roster Endpoint

### Endpoint

```
GET https://api-web.nhle.com/v1/roster/{team_abbrev}/{season}
```

### Example

```
https://api-web.nhle.com/v1/roster/CGY/20242025
```

### Description

Returns the roster for a team in a given season.

Includes:

- player IDs
- jersey numbers
- positions
- roster status

### Python Example

```python
url = f"https://api-web.nhle.com/v1/roster/{team}/{season}"
roster = requests.get(url).json()
```

---

# 6. Standings Endpoint

### Endpoint

```
GET https://api-web.nhle.com/v1/standings/now
```

### Description

Returns league standings including:

- division rankings
- conference rankings
- games played
- wins / losses / OT losses
- points

---

# 7. Stats Metadata API

These endpoints are served from:

```
https://api.nhle.com/stats/rest/en/
```

These APIs provide **reference metadata used across the NHL ecosystem**.

## Countries

```
GET https://api.nhle.com/stats/rest/en/country
```

Returns country metadata used for player nationality.

## Glossary

```
GET https://api.nhle.com/stats/rest/en/glossary
```

Returns definitions for statistical terms.

## Teams

```
GET https://api.nhle.com/stats/rest/en/team
```

Returns franchise metadata including:

- team IDs
- abbreviations
- franchise history

Useful for building **lookup tables**.

---

# 8. Asset URLs

Assets used by the NHL site are hosted on:

```
https://assets.nhle.com/
```

These are **pattern-based URLs**.

## Player Mugshots

```
https://assets.nhle.com/mugs/nhl/{season}/{team_abbr}/{player_id}.png
```

Example

```
https://assets.nhle.com/mugs/nhl/20242025/TOR/8478402.png
```

Used for:

- player headshots
- roster displays
- scoreboard UI

## Team Logos

```
https://assets.nhle.com/logos/nhl/svg/{team_abbr}_dark.svg
```

Example

```
https://assets.nhle.com/logos/nhl/svg/CGY_dark.svg
```

SVG logos are used by the NHL web interface.

---

# 9. Location Endpoint

### Endpoint

```
GET https://api-web.nhle.com/v1/location
```

### Description

Returns geographic information used by the NHL site to determine:

- broadcast restrictions
- localization
- region-specific content

---

# 10. Typical Data Workflow

Most NHL dashboards follow this pattern:

### 1. Query daily scoreboard

```
/v1/score/{date}
```

### 2. Extract game IDs

### 3. Query game landing data

```
/v1/gamecenter/{game_id}/landing
```

### 4. Parse scoring events and player data

### 5. Render UI components

- scoreboard
- goal summaries
- player cards

---

# 11. Migration Notes (Pre‑2025 API)

Older scripts referencing legacy APIs should migrate to the following endpoints.

| Legacy Pattern | Replacement |
|---------------|-------------|
Scoreboard | `/v1/score/{date}` |
Game data | `/v1/gamecenter/{id}/landing` |
Roster | `/v1/roster/{team}/{season}` |
Player data | `/v1/player/{id}/landing` |

---

# 12. Stability Notes

These APIs are **not officially supported**.

Recommended practices:

- Always validate JSON keys
- Expect missing fields
- Avoid strict schemas
- Handle fallback values
- Cache responses where possible

---

# Suggested Repository Structure

To maintain clear documentation:

```
docs/
    nhl_api_reference.md
    endpoint_examples.md
    landing_schema.md
```

Possible additions:

- JSON schema for `gamecenter/landing`
- scoring event structure
- asset URL patterns
- migration guides for older scripts
