import pandas as pd

import streamlit as st


"""
Extensive NHL API endpoint map
Uses example variables requested by user.

Notes:
- api-web.nhle.com is the main modern web API surface.
- api.nhle.com/stats/rest is the separate stats/reporting surface.
- Some endpoints support both season/gameType and "now" variants.
- Some endpoints are stable and widely used; others are less documented and may change.
"""


sections = {
    "a": "LEAGUE / DATE-BASED SCHEDULE & SCORE",
    "b": "TEAM SCHEDULE / ROSTER / CLUB DATA",
    "c": "PLAYER DATA",
    "d": "LEAGUE LEADERS",
    "e": "GAMECENTER CORE",
    "f": "GAME MEDIA / REPLAYS / WATCH / ODDS / NETWORK",
    "g": "PLAYOFFS",
    "h": "DRAFT",
    "i": "META / MISC",
    "j": "NHL EDGE - TEAM",
    "k": "NHL EDGE - SKATER",
    "l": "NHL EDGE - GOALIE",
    "m": "STATS REST API - PLAYERS / LEADERS / REPORTS",
    "n": "STATS REST API - TEAMS / FRANCHISE / GAME / MISC",
    "o": "ASSETS - MUGSHOTS"
}


def contents(**data) -> pd.DataFrame:
    data_1 = dict(
        playerID = 8471675,
        teamAbbr = "PIT",
        date = "2026-01-31",
        season = "20252026",
        gameID = 2025021032,
        draftYear = 2025,
        year = 2025,
        gameType = 2,   # 2 = regular season, 3 = playoffs
        base = "https://api-web.nhle.com/v1",
        stats_base = "https://api.nhle.com/stats/rest/en",
        assets_base = "https://assets.nhle.com/mugs/nhl",
    )
    for k, v in data_1.items():
        data.setdefault(k, v)
    
    playerID = data["playerID"]
    teamAbbr = data["teamAbbr"]
    date = data["date"]
    season = data["season"]
    gameID = data["gameID"]
    draftYear = data["draftYear"]
    year = data["year"] if "year" in data else data["draftYear"]
    base = data["base"]
    gameType = data["gameType"]
    stats_base = data["stats_base"]
    assets_base = data["assets_base"]
        
    data.update(dict(
        
        url_score_by_date = ('a', '{base}/score/{date}', [base, date], 'Daily score feed for a specific date', {'base': base, 'date': date}),
        url_score_now = ('a', '{base}/score/now', [base], 'Current score feed as-of-now variant', {'base': base}),
        url_schedule_by_date = ('a', '{base}/schedule/{date}', [base, date], 'Schedule payload centered around a specific date', {'base': base, 'date': date}),
        url_schedule_now = ('a', '{base}/schedule/now', [base], 'Current schedule snapshot', {'base': base}),
        url_schedule_calendar_by_date = ('a', '{base}/schedule-calendar/{date}', [base, date], 'Calendar view of available schedule dates', {'base': base, 'date': date}),
        url_schedule_calendar_now = ('a', '{base}/schedule-calendar/now', [base], 'Calendar view as of now', {'base': base}),
        url_standings_by_date = ('a', '{base}/standings/{date}', [base, date], 'League standings snapshot for a specific date', {'base': base, 'date': date}),
        url_standings_now = ('a', '{base}/standings/now', [base], 'Current standings snapshot', {'base': base}),
        url_seasons = ('a', '{base}/season', [base], 'List of available seasons / season metadata', {'base': base}),
        url_team_week_schedule = ('b', '{base}/club-schedule/{teamAbbr}/week/{date}', [base, teamAbbr, date], 'Team week schedule for the requested date anchor', {'base': base, 'teamAbbr': teamAbbr, 'date': date}),
        url_team_week_schedule_now = ('b', '{base}/club-schedule/{teamAbbr}/week/now', [base, teamAbbr], 'Team week schedule as-of-now', {'base': base, 'teamAbbr': teamAbbr}),
        url_team_month_schedule = ('b', '{base}/club-schedule/{teamAbbr}/month/{date}', [base, teamAbbr, date], 'Team month schedule for date anchor', {'base': base, 'teamAbbr': teamAbbr, 'date': date}),       
        url_team_month_schedule_now = ('b', '{base}/club-schedule/{teamAbbr}/month/now', [base, teamAbbr], 'Team month schedule as-of-now', {'base': base, 'teamAbbr': teamAbbr}),
        url_team_season_schedule = ('b', '{base}/club-schedule-season/{teamAbbr}/{season}', [base, season, teamAbbr], 'Team season schedule for a specific season', {'base': base, 'season': season, 'teamAbbr': teamAbbr}),
        url_team_season_schedule_now = ('b', '{base}/club-schedule-season/{teamAbbr}/now', [base, teamAbbr], 'Team season schedule as-of-now', {'base': base, 'teamAbbr': teamAbbr}),
        url_team_roster_current = ('b', '{base}/roster/{teamAbbr}/current', [base, teamAbbr], 'Current team roster', {'base': base, 'teamAbbr': teamAbbr}),
        url_team_roster_season = ('b', '{base}/roster/{teamAbbr}/{season}', [base, teamAbbr, season], 'Team roster for a specific season', {'base': base, 'teamAbbr': teamAbbr, 'season': season}),
        url_team_roster_seasons = ('b', '{base}/roster-season/{teamAbbr}', [base, teamAbbr], 'Available roster seasons for the team', {'base': base, 'teamAbbr': teamAbbr}),
        url_team_prospects = ('b', '{base}/prospects/{teamAbbr}', [base, teamAbbr], 'Team prospects', {'base': base, 'teamAbbr': teamAbbr}),
        url_club_stats_now = ('b', '{base}/club-stats/{teamAbbr}/now', [base, teamAbbr], 'Current team stats snapshot', {'base': base, 'teamAbbr': teamAbbr}),
        url_club_stats_season = ('b', '{base}/club-stats/{teamAbbr}/{season}/{gameType}', [base, teamAbbr, season, gameType], 'Team stats for a season and game type', {'base': base, 'teamAbbr': teamAbbr, 'season': season, 'gameType': gameType}),
        url_team_scoreboard = ('b', '{base}/club-scoreboard/{teamAbbr}/{date}', [base, teamAbbr, date], 'Team-focused scoreboard for a given date', {'base': base, 'teamAbbr': teamAbbr, 'date': date}),
        url_player_landing = ('c', '{base}/player/{playerID}/landing', [base, playerID], 'Player landing/profile page data', {'base': base, 'playerID': playerID}),
        url_player_game_log = ('c', '{base}/player/{playerID}/game-log/{season}/{gameType}', [base, playerID, season, gameType], 'Player game log for season and game type', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_player_game_log_now = ('c', '{base}/player/{playerID}/game-log/now', [base, playerID], 'Player game log as-of-now variant', {'base': base, 'playerID': playerID}),
        url_skater_leaders_current = ('d', '{base}/skater-stats-leaders/current?categories=goals,assists,points&limit=10', [base], ' Current skater leaders by selected categories', {'base': base}),
        url_skater_leaders_season = ('d', '{base}/skater-stats-leaders/{season}/{gameType}?categories=goals,assists,points&limit=10', [base, season, gameType], ' Season-specific skater leaders', {'base': base, 'season': season, 'gameType': gameType}),
        url_goalie_leaders_current = ('d', '{base}/goalie-stats-leaders/current?categories=wins,gaa,savePct,shutouts&limit=10', [base], ' Current goalie leaders by selected categories', {'base': base}),        
        url_goalie_leaders_season = ('d', '{base}/goalie-stats-leaders/{season}/{gameType}?categories=wins,gaa,savePct,shutouts&limit=10', [base, season, gameType], ' Season-specific goalie leaders', {'base': base, 'season': season, 'gameType': gameType}),
        url_spotlight_players = ('d', '{base}/player-spotlight', [base], 'Player spotlight / featured player feed', {'base': base}),
        url_game_landing = ('e', '{base}/gamecenter/{gameID}/landing', [base, gameID], 'Main gamecenter landing endpoint', {'base': base, 'gameID': gameID}),
        url_game_play_by_play = ('e', '{base}/gamecenter/{gameID}/play-by-play', [base, gameID], 'Full play-by-play event stream', {'base': base, 'gameID': gameID}),
        url_game_boxscore = ('e', '{base}/gamecenter/{gameID}/boxscore', [base, gameID], 'Boxscore with player/team stats', {'base': base, 'gameID': gameID}),
        url_game_story = ('e', '{base}/gamecenter/{gameID}/story', [base, gameID], 'Story / recap style game content', {'base': base, 'gameID': gameID}),
        url_game_right_rail = ('e', '{base}/gamecenter/{gameID}/right-rail', [base, gameID], 'Sidebar / companion gamecenter data', {'base': base, 'gameID': gameID}),
        url_game_replay_goal = ('f', '{base}/gamecenter/{gameID}/replay/goal/1', [base, gameID], 'Goal replay payload for a game event example', {'base': base, 'gameID': gameID}),
        url_game_replay_play = ('f', '{base}/gamecenter/{gameID}/replay/play/1', [base, gameID], 'Generic play replay payload for a game event example', {'base': base, 'gameID': gameID}),
        url_where_to_watch = ('f', '{base}/where-to-watch/{gameID}', [base, gameID], 'Streaming / watch availability for a game', {'base': base, 'gameID': gameID}),
        url_tv_schedule_by_date = ('f', '{base}/network/tv-schedule/{date}', [base, date], 'TV schedule for a date', {'base': base, 'date': date}),
        url_tv_schedule_now = ('f', '{base}/network/tv-schedule/now', [base], 'Current TV schedule', {'base': base}),
        url_partner_game_odds = ('f', '{base}/partner-game/{gameID}/odds', [base, gameID], 'Partner odds for a game', {'base': base, 'gameID': gameID}),
        url_wsc_play_by_play = ('f', '{base}/gamecenter/{gameID}/play-by-play/wsc', [base, gameID], 'WSC-linked play-by-play / media-adjacent game feed', {'base': base, 'gameID': gameID}),
        url_playoff_carousel = ('g', '{base}/playoff-series/carousel/{season}', [base, season], 'Playoff series carousel overview', {'base': base, 'season': season}),
        url_playoff_schedule = ('g', '{base}/schedule/playoff-series/{season}/{date}', [base, season, date], 'Playoff series schedule for a date', {'base': base, 'season': season, 'date': date}),
        url_playoff_bracket = ('g', '{base}/playoff-bracket/{season}', [base, season], 'Playoff bracket for a season', {'base': base, 'season': season}),
        url_playoff_metadata = ('g', '{base}/meta/playoff-series/{season}', [base, season], 'Playoff series metadata', {'base': base, 'season': season}),
        url_draft_rankings = ('h', '{base}/draft/rankings/{draftYear}', [base, draftYear], 'Draft rankings for a draft year', {'base': base, 'draftYear': draftYear}),
        url_draft_rankings_by_date = ('h', '{base}/draft/rankings/{date}', [base, date], 'Draft rankings by date anchor', {'base': base, 'date': date}),
        url_draft_tracker_now = ('h', '{base}/draft-tracker/now', [base], 'Current draft tracker', {'base': base}),
        url_draft_picks_now = ('h', '{base}/draft/picks/now', [base], 'Current draft picks feed', {'base': base}),
        url_draft_picks_by_year = ('h', '{base}/draft/picks/{draftYear}', [base, draftYear], 'Draft picks for a draft year', {'base': base, 'draftYear': draftYear}),
        url_meta = ('i', '{base}/meta', [base], 'General meta information', {'base': base}),
        url_meta_game = ('i', '{base}/meta/game/{gameID}', [base, gameID], 'Game metadata', {'base': base, 'gameID': gameID}),
        url_meta_location = ('i', '{base}/location', [base], 'Location metadata / locale info', {'base': base}),
        url_postal_lookup = ('i', '{base}/postal-lookup/10001', [base], 'Postal code lookup example', {'base': base}),
        url_openapi_guess = ('i', 'https://api-web.nhle.com/model/v1/openapi.json', [], 'Referenced openapi spec path; public reference notes it appears to return 404', {}),
        url_edge_team_details = ('j', '{base}/edge/team/details/{teamAbbr}', [base, teamAbbr], 'Team Edge details', {'base': base, 'teamAbbr': teamAbbr}),
        url_edge_team_landing = ('j', '{base}/edge/team/landing/{teamAbbr}', [base, teamAbbr], 'Team Edge landing page', {'base': base, 'teamAbbr': teamAbbr}),
        url_edge_team_comparison = ('j', '{base}/edge/team/comparison/{teamAbbr}/{season}/{gameType}', [base, teamAbbr, season, gameType], 'Team comparison metrics', {'base': base, 'teamAbbr': teamAbbr, 'season': season, 'gameType': gameType}),
        url_edge_team_skating_distance_top10 = ('j', '{base}/edge/team/skating-distance/{teamAbbr}/{season}/{gameType}', [base, teamAbbr, season, gameType], 'Team skating distance top-level summary', {'base': base, 'teamAbbr': teamAbbr, 'season': season, 'gameType': gameType}),
        url_edge_team_skating_distance_detail = ('j', '{base}/edge/team/skating-distance-detail/{teamAbbr}/{season}/{gameType}', [base, teamAbbr, season, gameType], 'Team skating distance details', {'base': base, 'teamAbbr': teamAbbr, 'season': season, 'gameType': gameType}),
        url_edge_team_skating_speed_top10 = ('j', '{base}/edge/team/skating-speed/{teamAbbr}/{season}/{gameType}', [base, teamAbbr, season, gameType], 'Team skating speed summary', {'base': base, 'teamAbbr': teamAbbr, 'season': season, 'gameType': gameType}),
        url_edge_team_skating_speed_detail = ('j', '{base}/edge/team/skating-speed-detail/{teamAbbr}/{season}/{gameType}', [base, teamAbbr, season, gameType], 'Team skating speed details', {'base': base, 'teamAbbr': teamAbbr, 'season': season, 'gameType': gameType}),
        url_edge_team_zone_time_top10 = ('j', '{base}/edge/team/zone-time/{teamAbbr}/{season}/{gameType}', [base, teamAbbr, season, gameType], 'Team zone time summary', {'base': base, 'teamAbbr': teamAbbr, 'season': season, 'gameType': gameType}),
        url_edge_team_zone_time_detail = ('j', '{base}/edge/team/zone-time-detail/{teamAbbr}/{season}/{gameType}', [base, teamAbbr, season, gameType], 'Team zone time details', {'base': base, 'teamAbbr': teamAbbr, 'season': season, 'gameType': gameType}),
        url_edge_team_shot_speed_top10 = ('j', '{base}/edge/team/shot-speed/{teamAbbr}/{season}/{gameType}', [base, teamAbbr, season, gameType], 'Team shot speed summary', {'base': base, 'teamAbbr': teamAbbr, 'season': season, 'gameType': gameType}),
        url_edge_team_shot_speed_detail = ('j', '{base}/edge/team/shot-speed-detail/{teamAbbr}/{season}/{gameType}', [base, teamAbbr, season, gameType], 'Team shot speed details', {'base': base, 'teamAbbr': teamAbbr, 'season': season, 'gameType': gameType}),
        url_edge_team_shot_location_top10 = ('j', '{base}/edge/team/shot-location/{teamAbbr}/{season}/{gameType}', [base, teamAbbr, season, gameType], 'Team shot location summary', {'base': base, 'teamAbbr': teamAbbr, 'season': season, 'gameType': gameType}),
        url_edge_team_shot_location_detail = ('j', '{base}/edge/team/shot-location-detail/{teamAbbr}/{season}/{gameType}', [base, teamAbbr, season, gameType], 'Team shot location details', {'base': base, 'teamAbbr': teamAbbr, 'season': season, 'gameType': gameType}),
        url_edge_skater_detail = ('k', '{base}/edge/skater-detail/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Skater Edge detail', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_skater_landing = ('k', '{base}/edge/skater-landing/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Skater Edge landing', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_skater_comparison = ('k', '{base}/edge/skater-comparison/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Skater Edge comparison', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_skater_distance_top10 = ('k', '{base}/edge/skater-skating-distance/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Skater distance summary', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_skater_distance_detail = ('k', '{base}/edge/skater-skating-distance-detail/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Skater distance detail', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_skater_speed_top10 = ('k', '{base}/edge/skater-skating-speed/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Skater speed summary', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_skater_speed_detail = ('k', '{base}/edge/skater-skating-speed-detail/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Skater speed detail', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_skater_zone_time_top10 = ('k', '{base}/edge/skater-zone-time/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Skater zone time summary', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_skater_zone_time_detail = ('k', '{base}/edge/skater-zone-time-detail/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Skater zone time detail', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_skater_shot_speed_top10 = ('k', '{base}/edge/skater-shot-speed/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Skater shot speed summary', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_skater_shot_speed_detail = ('k', '{base}/edge/skater-shot-speed-detail/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Skater shot speed detail', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_skater_shot_location_top10 = ('k', '{base}/edge/skater-shot-location/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Skater shot location summary', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_skater_shot_location_detail = ('k', '{base}/edge/skater-shot-location-detail/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Skater shot location detail', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_cat_edge_skater_detail = ('k', '{base}/cat/edge/skater-detail/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'CAT-style skater detail rollup', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_goalie_detail = ('l', '{base}/edge/goalie-detail/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Goalie Edge detail', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_goalie_landing = ('l', '{base}/edge/goalie-landing/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Goalie Edge landing', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_goalie_comparison = ('l', '{base}/edge/goalie-comparison/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Goalie comparison rollup', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_goalie_5v5_top10 = ('l', '{base}/edge/goalie-5v5/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Goalie 5v5 summary', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_goalie_5v5_detail = ('l', '{base}/edge/goalie-5v5-detail/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Goalie 5v5 detail', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_goalie_shot_location_top10 = ('l', '{base}/edge/goalie-shot-location/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Goalie shot location summary', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_goalie_shot_location_detail = ('l', '{base}/edge/goalie-shot-location-detail/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Goalie shot location detail', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_goalie_save_pct_top10 = ('l', '{base}/edge/goalie-save-percentage/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Goalie save percentage summary', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_goalie_save_pct_detail = ('l', '{base}/edge/goalie-save-percentage-detail/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'Goalie save percentage detail', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_cat_edge_goalie_detail = ('l', '{base}/cat/edge/goalie-detail/{playerID}/{season}/{gameType}', [base, playerID, season, gameType], 'CAT-style goalie detail rollup', {'base': base, 'playerID': playerID, 'season': season, 'gameType': gameType}),
        url_edge_by_the_numbers = ('l', '{base}/edge/by-the-numbers', [base], 'Miscellaneous Edge endpoint noted in public reference', {'base': base}),
        url_stats_players = ('m', '{stats_base}/players', [stats_base], 'Basic player list / lookup surface', {'stats_base': stats_base}),
        url_stats_skater_leaders = ('m', '{stats_base}/leaders/skaters/points', [stats_base], 'Stats REST skater leaders by attribute', {'stats_base': stats_base}),
        url_stats_goalie_leaders = ('m', '{stats_base}/leaders/goalies/gaa', [stats_base], 'Stats REST goalie leaders by attribute', {'stats_base': stats_base}),
        url_stats_skater_milestones = ('m', '{stats_base}/milestones/skaters', [stats_base], 'Skater milestones', {'stats_base': stats_base}),
        url_stats_goalie_milestones = ('m', '{stats_base}/milestones/goalies', [stats_base], 'Goalie milestones', {'stats_base': stats_base}),
        url_stats_skater_summary = ('m', '{stats_base}/skater/summary?isAggregate=false&isGame=false&sort=[{{"property":"points","direction":"DESC"}}]&start=0&limit=10&cayenneExp=seasonId={season}', [stats_base, season], 'Detailed skater report query', {'stats_base': stats_base, 'season': season}),
        url_stats_goalie_summary = ('m', '{stats_base}/goalie/summary?isAggregate=false&isGame=false&sort=[{{"property":"wins","direction":"DESC"}}]&start=0&limit=10&cayenneExp=seasonId={season}', [stats_base, season], 'Detailed goalie report query', {'stats_base': stats_base, 'season': season}),
        url_stats_skater_realtime = ('m', '{stats_base}/skater/realtime?isAggregate=false&isGame=false&sort=[{{"property":"hits","direction":"DESC"}}]&start=0&limit=10&cayenneExp=seasonId={season}', [stats_base, season], 'Realtime-style skater report', {'stats_base': stats_base, 'season': season}),
        url_stats_skater_scoringpergame = ('m', '{stats_base}/skater/scoringpergame?isAggregate=false&isGame=false&start=0&limit=10&cayenneExp=seasonId={season}', [stats_base, season], 'Skater scoring-per-gamereport', {'stats_base': stats_base, 'season': season}),
        url_stats_skater_timeonice = ('m', '{stats_base}/skater/timeonice?isAggregate=false&isGame=false&start=0&limit=10&cayenneExp=seasonId={season}', [stats_base, season], 'Skater time on ice report', {'stats_base': stats_base, 'season': season}),
        url_stats_goalie_advanced = ('m', '{stats_base}/goalie/advanced?isAggregate=false&isGame=false&start=0&limit=10&cayenneExp=seasonId={season}', [stats_base, season], 'Goalie advanced report', {'stats_base': stats_base, 'season': season}),
        url_stats_teams = ('n', '{stats_base}/team', [stats_base], 'Team information', {'stats_base': stats_base}),
        url_stats_team_by_id = ('n', '{stats_base}/team/1', [stats_base], 'Team by numeric ID example', {'stats_base': stats_base}),
        url_stats_team_summary = ('n', '{stats_base}/team/summary?isAggregate=false&isGame=false&start=0&limit=10&cayenneExp=seasonId={season}', [stats_base, season], 'Team summary report', {'stats_base': stats_base, 'season': season}),
        url_stats_franchise = ('n', '{stats_base}/franchise', [stats_base], 'Franchise information', {'stats_base': stats_base}),
        url_stats_draft = ('n', '{stats_base}/draft', [stats_base], 'Draft information', {'stats_base': stats_base}),
        url_stats_season = ('n', '{stats_base}/season', [stats_base], 'Season information', {'stats_base': stats_base}),
        url_stats_component_season = ('n', '{stats_base}/componentSeason', [stats_base], 'Component season info', {'stats_base': stats_base}),
        url_stats_game = ('n', '{stats_base}/game', [stats_base], 'Game information', {'stats_base': stats_base}),
        url_stats_game_meta = ('n', '{stats_base}/game-meta', [stats_base], 'Game metadata', {'stats_base': stats_base}),
        url_stats_config = ('n', '{stats_base}/config', [stats_base], 'Configuration endpoint', {'stats_base': stats_base}),
        url_stats_ping = ('n', '{stats_base}/ping', [stats_base], 'Ping / health-style endpoint', {'stats_base': stats_base}),
        url_stats_country = ('n', '{stats_base}/country', [stats_base], 'Country information', {'stats_base': stats_base}),
        url_stats_shiftcharts = ('n', '{stats_base}/shiftcharts?cayenneExp=gameId={gameID}', [stats_base, gameID], 'Shift charts from the stats REST side', {'stats_base': stats_base, 'gameID': gameID}),        
        url_stats_glossary = ('n', '{stats_base}/glossary', [stats_base], 'Glossary endpoint', {'stats_base': stats_base}),
        url_stats_content_module = ('n', '{stats_base}/content/module/overview', [stats_base], 'Content module endpoint', {'stats_base': stats_base}),
        url_assets_mugshot = ('o', '{assets_base}/{season}/{teamAbbr}/{playerID}.png', [assets_base, season, teamAbbr, playerID], 'Player mugshot, redirects to default skater if not found.', {'assets_base': assets_base, 'season': season, 'teamAbbr': teamAbbr, 'playerID': playerID}),
        
        # # ============================================================
        # # LEAGUE / DATE-BASED SCHEDULE & SCORE
        # # ============================================================

        # url_score_by_date = ("a", f"{base}/score/{date}", "Daily score feed for a specific date"),

        # url_score_now = ("a", f"{base}/score/now", "Current score feed as-of-now variant"),

        # url_schedule_by_date = ("a", f"{base}/schedule/{date}", "Schedule payload centered around a specific date"),

        # url_schedule_now = ("a", f"{base}/schedule/now", "Current schedule snapshot"),

        # url_schedule_calendar_by_date = ("a", f"{base}/schedule-calendar/{date}", "Calendar view of available schedule dates"),

        # url_schedule_calendar_now = ("a", f"{base}/schedule-calendar/now", "Calendar view as of now"),

        # url_standings_by_date = ("a", f"{base}/standings/{date}", "League standings snapshot for a specific date"),

        # url_standings_now = ("a", f"{base}/standings/now", "Current standings snapshot"),

        # url_seasons = ("a", f"{base}/season", "List of available seasons / season metadata"),

        # # ============================================================
        # # TEAM SCHEDULE / ROSTER / CLUB DATA
        # # ============================================================

        # url_team_week_schedule = ("b", f"{base}/club-schedule/{teamAbbr}/week/{date}", "Team week schedule for the requested date anchor"),

        # url_team_week_schedule_now = ("b", f"{base}/club-schedule/{teamAbbr}/week/now", "Team week schedule as-of-now"),

        # url_team_month_schedule = ("b", f"{base}/club-schedule/{teamAbbr}/month/{date}", "Team month schedule for date anchor"),

        # url_team_month_schedule_now = ("b", f"{base}/club-schedule/{teamAbbr}/month/now", "Team month schedule as-of-now"),

        # url_team_season_schedule = ("b", f"{base}/club-schedule-season/{teamAbbr}/{season}", "Team season schedule for a specific season"),

        # url_team_season_schedule_now = ("b", f"{base}/club-schedule-season/{teamAbbr}/now", "Team season schedule as-of-now"),

        # url_team_roster_current = ("b", f"{base}/roster/{teamAbbr}/current", "Current team roster"),

        # url_team_roster_season = ("b", f"{base}/roster/{teamAbbr}/{season}", "Team roster for a specific season"),

        # url_team_roster_seasons = ("b", f"{base}/roster-season/{teamAbbr}", "Available roster seasons for the team"),

        # url_team_prospects = ("b", f"{base}/prospects/{teamAbbr}", "Team prospects"),

        # url_club_stats_now = ("b", f"{base}/club-stats/{teamAbbr}/now", "Current team stats snapshot"),

        # url_club_stats_season = ("b", f"{base}/club-stats/{teamAbbr}/{season}/{gameType}", "Team stats for a season and game type"),

        # url_team_scoreboard = ("b", f"{base}/club-scoreboard/{teamAbbr}/{date}", "Team-focused scoreboard for a given date"),

        # # ============================================================
        # # PLAYER DATA
        # # ============================================================

        # url_player_landing = ("c", f"{base}/player/{playerID}/landing", "Player landing/profile page data"),

        # url_player_game_log = ("c", f"{base}/player/{playerID}/game-log/{season}/{gameType}", "Player game log for season and game type"),

        # url_player_game_log_now = ("c", f"{base}/player/{playerID}/game-log/now", "Player game log as-of-now variant"),

        # # ============================================================
        # # LEAGUE LEADERS
        # # ============================================================

        # url_skater_leaders_current = ("d", f"{base}/skater-stats-leaders/current?categories=goals,assists,points&limit=10", " Current skater leaders by selected categories"),

        # url_skater_leaders_season =  ("d", f"{base}/skater-stats-leaders/{season}/{gameType}?categories=goals,assists,points&limit=10", " Season-specific skater leaders"),

        # url_goalie_leaders_current = ("d", f"{base}/goalie-stats-leaders/current?categories=wins,gaa,savePct,shutouts&limit=10", " Current goalie leaders by selected categories"),

        # url_goalie_leaders_season =  ("d", f"{base}/goalie-stats-leaders/{season}/{gameType}?categories=wins,gaa,savePct,shutouts&limit=10", " Season-specific goalie leaders"),

        # url_spotlight_players = ("d", f"{base}/player-spotlight", "Player spotlight / featured player feed"),

        # # ============================================================
        # # GAMECENTER CORE
        # # ============================================================

        # url_game_landing = ("e", f"{base}/gamecenter/{gameID}/landing", "Main gamecenter landing endpoint"),

        # url_game_play_by_play = ("e", f"{base}/gamecenter/{gameID}/play-by-play", "Full play-by-play event stream"),

        # url_game_boxscore = ("e", f"{base}/gamecenter/{gameID}/boxscore", "Boxscore with player/team stats"),

        # url_game_story = ("e", f"{base}/gamecenter/{gameID}/story", "Story / recap style game content"),

        # url_game_right_rail = ("e", f"{base}/gamecenter/{gameID}/right-rail", "Sidebar / companion gamecenter data"),

        # # ============================================================
        # # GAME MEDIA / REPLAYS / WATCH / ODDS / NETWORK
        # # ============================================================

        # url_game_replay_goal = ("f", f"{base}/gamecenter/{gameID}/replay/goal/1", "Goal replay payload for a game event example"),

        # url_game_replay_play = ("f", f"{base}/gamecenter/{gameID}/replay/play/1", "Generic play replay payload for a game event example"),

        # url_where_to_watch = ("f", f"{base}/where-to-watch/{gameID}", "Streaming / watch availability for a game"),

        # url_tv_schedule_by_date = ("f", f"{base}/network/tv-schedule/{date}", "TV schedule for a date"),

        # url_tv_schedule_now = ("f", f"{base}/network/tv-schedule/now", "Current TV schedule"),

        # url_partner_game_odds = ("f", f"{base}/partner-game/{gameID}/odds", "Partner odds for a game"),

        # url_wsc_play_by_play = ("f", f"{base}/gamecenter/{gameID}/play-by-play/wsc", "WSC-linked play-by-play / media-adjacent game feed"),

        # # ============================================================
        # # PLAYOFFS
        # # ============================================================

        # url_playoff_carousel = ("g", f"{base}/playoff-series/carousel/{season}", "Playoff series carousel overview"),

        # url_playoff_schedule = ("g", f"{base}/schedule/playoff-series/{season}/{date}", "Playoff series schedule for a date"),

        # url_playoff_bracket = ("g", f"{base}/playoff-bracket/{season}", "Playoff bracket for a season"),

        # url_playoff_metadata = ("g", f"{base}/meta/playoff-series/{season}", "Playoff series metadata"),

        # # ============================================================
        # # DRAFT
        # # ============================================================

        # url_draft_rankings = ("h", f"{base}/draft/rankings/{draftYear}", "Draft rankings for a draft year"),

        # url_draft_rankings_by_date = ("h", f"{base}/draft/rankings/{date}", "Draft rankings by date anchor"),

        # url_draft_tracker_now = ("h", f"{base}/draft-tracker/now", "Current draft tracker"),

        # url_draft_picks_now = ("h", f"{base}/draft/picks/now", "Current draft picks feed"),

        # url_draft_picks_by_year = ("h", f"{base}/draft/picks/{draftYear}", "Draft picks for a draft year"),

        # # ============================================================
        # # META / MISC
        # # ============================================================

        # url_meta = ("i", f"{base}/meta", "General meta information"),

        # url_meta_game = ("i", f"{base}/meta/game/{gameID}", "Game metadata"),

        # url_meta_location = ("i", f"{base}/location", "Location metadata / locale info"),

        # url_postal_lookup = ("i", f"{base}/postal-lookup/10001", "Postal code lookup example"),

        # url_openapi_guess = ("i", "https://api-web.nhle.com/model/v1/openapi.json", "Referenced openapi spec path; public reference notes it appears to return 404"),

        # # ============================================================
        # # NHL EDGE - TEAM
        # # ============================================================

        # url_edge_team_details = ("j", f"{base}/edge/team/details/{teamAbbr}", "Team Edge details"),

        # url_edge_team_landing = ("j", f"{base}/edge/team/landing/{teamAbbr}", "Team Edge landing page"),

        # url_edge_team_comparison = ("j", f"{base}/edge/team/comparison/{teamAbbr}/{season}/{gameType}", "Team comparison metrics"),

        # url_edge_team_skating_distance_top10 = ("j", f"{base}/edge/team/skating-distance/{teamAbbr}/{season}/{gameType}", "Team skating distance top-level summary"),

        # url_edge_team_skating_distance_detail = ("j", f"{base}/edge/team/skating-distance-detail/{teamAbbr}/{season}/{gameType}", "Team skating distance details"),

        # url_edge_team_skating_speed_top10 = ("j", f"{base}/edge/team/skating-speed/{teamAbbr}/{season}/{gameType}", "Team skating speed summary"),

        # url_edge_team_skating_speed_detail = ("j", f"{base}/edge/team/skating-speed-detail/{teamAbbr}/{season}/{gameType}", "Team skating speed details"),

        # url_edge_team_zone_time_top10 = ("j", f"{base}/edge/team/zone-time/{teamAbbr}/{season}/{gameType}", "Team zone time summary"),

        # url_edge_team_zone_time_detail = ("j", f"{base}/edge/team/zone-time-detail/{teamAbbr}/{season}/{gameType}", "Team zone time details"),

        # url_edge_team_shot_speed_top10 = ("j", f"{base}/edge/team/shot-speed/{teamAbbr}/{season}/{gameType}", "Team shot speed summary"),

        # url_edge_team_shot_speed_detail = ("j", f"{base}/edge/team/shot-speed-detail/{teamAbbr}/{season}/{gameType}", "Team shot speed details"),

        # url_edge_team_shot_location_top10 = ("j", f"{base}/edge/team/shot-location/{teamAbbr}/{season}/{gameType}", "Team shot location summary"),

        # url_edge_team_shot_location_detail = ("j", f"{base}/edge/team/shot-location-detail/{teamAbbr}/{season}/{gameType}", "Team shot location details"),

        # # ============================================================
        # # NHL EDGE - SKATER
        # # ============================================================

        # url_edge_skater_detail = ("k", f"{base}/edge/skater-detail/{playerID}/{season}/{gameType}", "Skater Edge detail"),

        # url_edge_skater_landing = ("k", f"{base}/edge/skater-landing/{playerID}/{season}/{gameType}", "Skater Edge landing"),

        # url_edge_skater_comparison = ("k", f"{base}/edge/skater-comparison/{playerID}/{season}/{gameType}", "Skater Edge comparison"),

        # url_edge_skater_distance_top10 = ("k", f"{base}/edge/skater-skating-distance/{playerID}/{season}/{gameType}", "Skater distance summary"),

        # url_edge_skater_distance_detail = ("k", f"{base}/edge/skater-skating-distance-detail/{playerID}/{season}/{gameType}", "Skater distance detail"),

        # url_edge_skater_speed_top10 = ("k", f"{base}/edge/skater-skating-speed/{playerID}/{season}/{gameType}", "Skater speed summary"),

        # url_edge_skater_speed_detail = ("k", f"{base}/edge/skater-skating-speed-detail/{playerID}/{season}/{gameType}", "Skater speed detail"),

        # url_edge_skater_zone_time_top10 = ("k", f"{base}/edge/skater-zone-time/{playerID}/{season}/{gameType}", "Skater zone time summary"),

        # url_edge_skater_zone_time_detail = ("k", f"{base}/edge/skater-zone-time-detail/{playerID}/{season}/{gameType}", "Skater zone time detail"),

        # url_edge_skater_shot_speed_top10 = ("k", f"{base}/edge/skater-shot-speed/{playerID}/{season}/{gameType}", "Skater shot speed summary"),

        # url_edge_skater_shot_speed_detail = ("k", f"{base}/edge/skater-shot-speed-detail/{playerID}/{season}/{gameType}", "Skater shot speed detail"),

        # url_edge_skater_shot_location_top10 = ("k", f"{base}/edge/skater-shot-location/{playerID}/{season}/{gameType}", "Skater shot location summary"),

        # url_edge_skater_shot_location_detail = ("k", f"{base}/edge/skater-shot-location-detail/{playerID}/{season}/{gameType}", "Skater shot location detail"),

        # url_cat_edge_skater_detail = ("k", f"{base}/cat/edge/skater-detail/{playerID}/{season}/{gameType}", "CAT-style skater detail rollup"),

        # # ============================================================
        # # NHL EDGE - GOALIE
        # # ============================================================

        # url_edge_goalie_detail = ("l", f"{base}/edge/goalie-detail/{playerID}/{season}/{gameType}", "Goalie Edge detail"),

        # url_edge_goalie_landing = ("l", f"{base}/edge/goalie-landing/{playerID}/{season}/{gameType}", "Goalie Edge landing"),

        # url_edge_goalie_comparison = ("l", f"{base}/edge/goalie-comparison/{playerID}/{season}/{gameType}", "Goalie comparison rollup"),

        # url_edge_goalie_5v5_top10 = ("l", f"{base}/edge/goalie-5v5/{playerID}/{season}/{gameType}", "Goalie 5v5 summary"),

        # url_edge_goalie_5v5_detail = ("l", f"{base}/edge/goalie-5v5-detail/{playerID}/{season}/{gameType}", "Goalie 5v5 detail"),

        # url_edge_goalie_shot_location_top10 = ("l", f"{base}/edge/goalie-shot-location/{playerID}/{season}/{gameType}", "Goalie shot location summary"),

        # url_edge_goalie_shot_location_detail = ("l", f"{base}/edge/goalie-shot-location-detail/{playerID}/{season}/{gameType}", "Goalie shot location detail"),

        # url_edge_goalie_save_pct_top10 = ("l", f"{base}/edge/goalie-save-percentage/{playerID}/{season}/{gameType}", "Goalie save percentage summary"),

        # url_edge_goalie_save_pct_detail = ("l", f"{base}/edge/goalie-save-percentage-detail/{playerID}/{season}/{gameType}", "Goalie save percentage detail"),

        # url_cat_edge_goalie_detail = ("l", f"{base}/cat/edge/goalie-detail/{playerID}/{season}/{gameType}", "CAT-style goalie detail rollup"),

        # url_edge_by_the_numbers = ("l", f"{base}/edge/by-the-numbers", "Miscellaneous Edge endpoint noted in public reference"),

        # # ============================================================
        # # STATS REST API - PLAYERS / LEADERS / REPORTS
        # # ============================================================

        # url_stats_players = ("m", f"{stats_base}/players", "Basic player list / lookup surface"),

        # url_stats_skater_leaders = ("m", f"{stats_base}/leaders/skaters/points", "Stats REST skater leaders by attribute"),

        # url_stats_goalie_leaders = ("m", f"{stats_base}/leaders/goalies/gaa", "Stats REST goalie leaders by attribute"),

        # url_stats_skater_milestones = ("m", f"{stats_base}/milestones/skaters", "Skater milestones"),

        # url_stats_goalie_milestones = ("m", f"{stats_base}/milestones/goalies", "Goalie milestones"),

        # url_stats_skater_summary = ("m", f'{stats_base}/skater/summary?isAggregate=false&isGame=false&sort=[{{"property":"points","direction":"DESC"}}]&start=0&limit=10&cayenneExp=seasonId={season}', "Detailed skater report query"),

        # url_stats_goalie_summary = ("m", f'{stats_base}/goalie/summary?isAggregate=false&isGame=false&sort=[{{"property":"wins","direction":"DESC"}}]&start=0&limit=10&cayenneExp=seasonId={season}', "Detailed goalie report query"),

        # url_stats_skater_realtime = ("m", f'{stats_base}/skater/realtime?isAggregate=false&isGame=false&sort=[{{"property":"hits","direction":"DESC"}}]&start=0&limit=10&cayenneExp=seasonId={season}', "Realtime-style skater report"),

        # url_stats_skater_scoringpergame = ("m", f'{stats_base}/skater/scoringpergame?isAggregate=false&isGame=false&start=0&limit=10&cayenneExp=seasonId={season}', "Skater scoring-per-game report"),

        # url_stats_skater_timeonice = ("m", f'{stats_base}/skater/timeonice?isAggregate=false&isGame=false&start=0&limit=10&cayenneExp=seasonId={season}', "Skater time on ice report"),

        # url_stats_goalie_advanced = ("m", f'{stats_base}/goalie/advanced?isAggregate=false&isGame=false&start=0&limit=10&cayenneExp=seasonId={season}', "Goalie advanced report"),
        
        # # ============================================================
        # # STATS REST API - TEAMS / FRANCHISE / GAME / MISC
        # # ============================================================

        # url_stats_teams = ("n", f"{stats_base}/team", "Team information"),

        # url_stats_team_by_id = ("n", f"{stats_base}/team/{1}", "Team by numeric ID example"),

        # url_stats_team_summary = ("n", f'{stats_base}/team/summary?isAggregate=false&isGame=false&start=0&limit=10&cayenneExp=seasonId={season}', "Team summary report"),

        # url_stats_franchise = ("n", f"{stats_base}/franchise", "Franchise information"),

        # url_stats_draft = ("n", f"{stats_base}/draft", "Draft information"),

        # url_stats_season = ("n", f"{stats_base}/season", "Season information"),

        # url_stats_component_season = ("n", f"{stats_base}/componentSeason", "Component season info"),

        # url_stats_game = ("n", f"{stats_base}/game", "Game information"),

        # url_stats_game_meta = ("n", f"{stats_base}/game-meta", "Game metadata"),

        # url_stats_config = ("n", f"{stats_base}/config", "Configuration endpoint"),

        # url_stats_ping = ("n", f"{stats_base}/ping", "Ping / health-style endpoint"),

        # url_stats_country = ("n", f"{stats_base}/country", "Country information"),

        # url_stats_shiftcharts = ("n", f"{stats_base}/shiftcharts?cayenneExp=gameId={gameID}", "Shift charts from the stats REST side"),

        # url_stats_glossary = ("n", f"{stats_base}/glossary", "Glossary endpoint"),

        # url_stats_content_module = ("n", f"{stats_base}/content/module/overview", "Content module endpoint"),
        
        # # ============================================================
        # # ASSETS API - MUGSHOTS
        # # ============================================================
        
        # url_assets_mugshot = ("o", f"{assets_base}/{season}/{teamAbbr}/{playerID}.png", "Player mugshot, redirects to default skater if not found.")
    ))
    
    columns = ["section", "url", "order", "description", "data"]
    # columns = ["section", "url", "description"]
    # data_params={k: v for k, v in data.items() if not isinstance(v, (list, tuple))}
    data={k: dict(zip(columns, v)) for k, v in data.items() if isinstance(v, (list, tuple))}
    df = pd.DataFrame(data).transpose()
    df["section"] = df["section"].apply(lambda s: sections[s])
    # i_, j_ = 0, 0
    # for k, v in data.items():
    #     s = v["section"]
    #     u = v["url"]
    #     d = v["description"]
    #     u_og = u
    #     u = u.replace("{", "{{").replace("}", "}}")
    #     params = []
    #     for k_, v_ in data_params.items():
    #         k_s, v_s = str(k_).lower(), str(v_).lower()
    #         if i_ == 0:
    #             print(f"{k_s=}, {v_s=}", end=" ")
    #         if len(v_s) > 8:
    #             if i_ == 0:
    #                 print("a", end="")
    #             if v_s in u.lower():
    #                 if i_ == 0:
    #                     print("b", end="")
    #                 # u = u.replace(v_, str(len(params)))
    #                 u = u.replace(str(v_), "{" + k_ + "}")
    #                 params.append(k_)
    #         else:
    #             if i_ == 0:
    #                 print("c", end="")
    #             if (f"{v_s}" in u.lower()) or (f"{v_s}" in u.lower()):
    #                 if i_ == 0:
    #                     print("d", end="")
    #                 # u = u.replace(v_, str(len(params)))
    #                 u = u.replace(str(v_), "{" + k_ + "}")
    #                 params.append(k_)
            
    #         if i_ == 0:
    #             print("")
    #         # print(f"{params=}, {u=}")
    #         params.sort(key=lambda p: u.index(p))
    #         j_ += 1
    #     i_ += 1
    #     values = []
    #     param_dict = {}
    #     param_dict_s = "{"
    #     for p in params:
    #         # values.append(f"{p}='{data_params[p]}'")
    #         values.append(f"{p}={p},")
    #         # param_dict[p] = data_params[p]
    #         param_dict[p] = p
    #         param_dict_s += f"'{p}': {p}, "
    #     param_dict_s = param_dict_s.removesuffix(", ")
    #     param_dict_s += "}"
    #     if values:
    #         values[-1].removesuffix(",")
    #     # print(f"{k} = ('{s}', '{u}'.format({''.join(values)}), [{', '.join(params)}], '{d}', {param_dict_s}),")
    #     print(f"{k} = ('{s}', '{u}', [{', '.join(params)}], '{d}', {param_dict_s}),")
    
    return df


if __name__ == "__main__":
    
    df = contents()
    print(df)