"""
NHL Prediction Performance Dashboard
Run with: streamlit run nhl_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NHL Prediction Dashboard",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded",
)


path_excel_predictions = r"C:\Users\abrig\Documents\Coding_Practice\Python\Jerseys\NHLGamePredictions_2526_copy.xlsx"


# ─────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background: #0a0e1a; }

.nhl-header {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d2137 50%, #0a0e1a 100%);
    border-bottom: 3px solid #c8a84b;
    padding: 24px 32px;
    margin-bottom: 24px;
    border-radius: 0 0 12px 12px;
}
.nhl-header h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.8rem;
    letter-spacing: 4px;
    color: #c8a84b;
    margin: 0;
    text-shadow: 0 0 30px rgba(200,168,75,0.3);
}
.nhl-header p { color: #8899aa; margin: 4px 0 0; font-size: 0.9rem; }

.metric-card {
    background: linear-gradient(135deg, #0d1f35, #0a1828);
    border: 1px solid #1e3a5a;
    border-left: 4px solid #c8a84b;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 4px;
}
.metric-card .value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.2rem;
    color: #c8a84b;
    line-height: 1;
}
.metric-card .label { color: #8899aa; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }

.section-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    letter-spacing: 3px;
    color: #c8a84b;
    border-bottom: 2px solid #1e3a5a;
    padding-bottom: 8px;
    margin: 24px 0 16px;
}

.team-logo { width: 48px; height: 48px; object-fit: contain; }

.stSelectbox > div > div { background: #0d1f35; border-color: #1e3a5a; }
.stMultiSelect > div > div { background: #0d1f35; border-color: #1e3a5a; }

div[data-testid="stMetricValue"] { color: #c8a84b !important; font-family: 'Bebas Neue', sans-serif; font-size: 2rem !important; }
div[data-testid="stMetricLabel"] { color: #8899aa !important; }

.gauntlet-card {
    background: #0d1f35;
    border: 1px solid #1e3a5a;
    border-radius: 8px;
    padding: 16px;
    margin: 8px 0;
}
.gauntlet-title { font-family: 'Bebas Neue', sans-serif; color: #c8a84b; font-size: 1.2rem; letter-spacing: 2px; }

.correct-badge { background: #0d3321; color: #2ecc71; border-radius: 4px; padding: 2px 8px; font-size: 0.8rem; font-weight: 600; }
.incorrect-badge { background: #330d0d; color: #e74c3c; border-radius: 4px; padding: 2px 8px; font-size: 0.8rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# NHL TEAM METADATA
# ─────────────────────────────────────────────────────────
TEAM_META = {
    "ANA": {"name": "Anaheim Ducks",       "conf": "Western", "div": "Pacific",    "id": 24},
    "ARI": {"name": "Utah Hockey Club",     "conf": "Western", "div": "Central",    "id": 53},
    "UTA": {"name": "Utah Hockey Club",     "conf": "Western", "div": "Central",    "id": 59},
    "BOS": {"name": "Boston Bruins",        "conf": "Eastern", "div": "Atlantic",   "id": 6},
    "BUF": {"name": "Buffalo Sabres",       "conf": "Eastern", "div": "Atlantic",   "id": 7},
    "CGY": {"name": "Calgary Flames",       "conf": "Western", "div": "Pacific",    "id": 20},
    "CAR": {"name": "Carolina Hurricanes",  "conf": "Eastern", "div": "Metropolitan","id": 12},
    "CHI": {"name": "Chicago Blackhawks",   "conf": "Western", "div": "Central",    "id": 16},
    "COL": {"name": "Colorado Avalanche",   "conf": "Western", "div": "Central",    "id": 21},
    "CBJ": {"name": "Columbus Blue Jackets","conf": "Eastern", "div": "Metropolitan","id": 29},
    "DAL": {"name": "Dallas Stars",         "conf": "Western", "div": "Central",    "id": 25},
    "DET": {"name": "Detroit Red Wings",    "conf": "Eastern", "div": "Atlantic",   "id": 17},
    "EDM": {"name": "Edmonton Oilers",      "conf": "Western", "div": "Pacific",    "id": 22},
    "FLA": {"name": "Florida Panthers",     "conf": "Eastern", "div": "Atlantic",   "id": 13},
    "LAK": {"name": "Los Angeles Kings",    "conf": "Western", "div": "Pacific",    "id": 26},
    "MIN": {"name": "Minnesota Wild",       "conf": "Western", "div": "Central",    "id": 30},
    "MTL": {"name": "Montréal Canadiens",   "conf": "Eastern", "div": "Atlantic",   "id": 8},
    "NSH": {"name": "Nashville Predators",  "conf": "Western", "div": "Central",    "id": 18},
    "NJD": {"name": "New Jersey Devils",    "conf": "Eastern", "div": "Metropolitan","id": 1},
    "NYI": {"name": "New York Islanders",   "conf": "Eastern", "div": "Metropolitan","id": 2},
    "NYR": {"name": "New York Rangers",     "conf": "Eastern", "div": "Metropolitan","id": 3},
    "OTT": {"name": "Ottawa Senators",      "conf": "Eastern", "div": "Atlantic",   "id": 9},
    "PHI": {"name": "Philadelphia Flyers",  "conf": "Eastern", "div": "Metropolitan","id": 4},
    "PIT": {"name": "Pittsburgh Penguins",  "conf": "Eastern", "div": "Metropolitan","id": 5},
    "SJS": {"name": "San Jose Sharks",      "conf": "Western", "div": "Pacific",    "id": 28},
    "SEA": {"name": "Seattle Kraken",       "conf": "Western", "div": "Pacific",    "id": 55},
    "STL": {"name": "St. Louis Blues",      "conf": "Western", "div": "Central",    "id": 19},
    "TBL": {"name": "Tampa Bay Lightning",  "conf": "Eastern", "div": "Atlantic",   "id": 14},
    "TOR": {"name": "Toronto Maple Leafs",  "conf": "Eastern", "div": "Atlantic",   "id": 10},
    "VAN": {"name": "Vancouver Canucks",    "conf": "Western", "div": "Pacific",    "id": 23},
    "VGK": {"name": "Vegas Golden Knights", "conf": "Western", "div": "Pacific",    "id": 54},
    "WSH": {"name": "Washington Capitals",  "conf": "Eastern", "div": "Metropolitan","id": 15},
    "WPG": {"name": "Winnipeg Jets",        "conf": "Western", "div": "Central",    "id": 52},
}

GAUNTLETS = {
    "California Swing 🌴": {
        "teams": ["ANA", "LAK", "SJS", "VGK"],
        "desc": "West Coast swing through California & Vegas",
        "region": "Pacific Coast"
    },
    "Canada West 🍁": {
        "teams": ["CGY", "EDM", "VAN"],
        "desc": "Western Canadian road trip",
        "region": "Western Canada"
    },
    "Canada East 🍁": {
        "teams": ["MTL", "OTT", "TOR"],
        "desc": "Eastern Canadian road trip",
        "region": "Eastern Canada"
    },
    "Metro NY Gauntlet 🗽": {
        "teams": ["NYR", "NYI", "NJD"],
        "desc": "New York metro area tri-team swing",
        "region": "Greater New York"
    },
    "Florida Sunshine Tour ☀️": {
        "teams": ["FLA", "TBL"],
        "desc": "Florida peninsula back-to-back",
        "region": "Florida"
    },
    "Pennsylvania Turnpike 🛣️": {
        "teams": ["PIT", "PHI"],
        "desc": "Keystone State rivalry gauntlet",
        "region": "Pennsylvania"
    },
    "Central Midwest Swing 🌾": {
        "teams": ["CHI", "STL", "NSH", "MIN"],
        "desc": "Central division midwest road stretch",
        "region": "Midwest"
    },
    "Texas Two-Step 🤠": {
        "teams": ["DAL", "COL"],
        "desc": "Southern plains to mountain road trip",
        "region": "South-Central"
    },
    "Pacific Northwest 🌲": {
        "teams": ["VAN", "SEA"],
        "desc": "Cascadia coastal road trip",
        "region": "Pacific Northwest"
    },
    "Original Six Heritage 🏆": {
        "teams": ["BOS", "MTL", "TOR", "DET", "NYR", "CHI"],
        "desc": "Classic Original Six matchups",
        "region": "Historic Rivalry"
    },
}

# ─────────────────────────────────────────────────────────
# DATA LOADING & ENRICHMENT
# ─────────────────────────────────────────────────────────
@st.cache_data
def load_data(filepath: str, **kwargs) -> pd.DataFrame:
    if filepath.lower().endswith(".csv"):
        df = pd.read_csv(filepath, encoding="utf-8-sig")
    elif filepath.lower().endswith(".xlsx"):
        df = pd.read_excel(filepath, **kwargs)
    df.columns = df.columns.str.strip()

    # Drop the unnamed first column if it exists
    if df.columns[0] == "" or df.columns[0].startswith("Unnamed"):
        df = df.iloc[:, 1:]

    # Date parsing
    for col in ["GameDate", "PredictionDate"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Normalize Y/N/1/0 columns
    yn_cols = ["GameIsOver", "CorrectWinnerPrediction", "CorrectAwayScorePrediction",
               "CorrectHomeScorePrediction", "WatchedGame", "GameHasShutOut",
               "AwayWon", "HomeWon_", "InterConf", "InterDiv",
               "SameConfDiffDiv", "CrossConf", "CanadianTeamPlays",
               "OriginalSixPlays", "THG_TonyTiger", "THG_80sGame",
               "THG_Extermination", "THG_ChessMatch"]
    for col in yn_cols:
        if col in df.columns:
            df[col] = df[col].map(
                lambda x: True if str(x).strip().upper() in ["Y", "YES", "1", "TRUE"] else False
            )

    # Numeric
    for col in ["ActualAwayScore", "ActualHomeScore", "PredictedAwayScore", "PredictedHomeScore",
                "GamePredictionScore", "GamePredictionScore2", "NewPointsAway", "NewPointsHome",
                "GameCost", "AwayTeamPays", "HomeTeamPays"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Enrich with team metadata
    df["AwayConf"] = df["AwayTeam"].map(lambda t: TEAM_META.get(t, {}).get("conf", "Unknown"))
    df["HomeConf"] = df["HomeTeam"].map(lambda t: TEAM_META.get(t, {}).get("conf", "Unknown"))
    df["AwayDiv"]  = df["AwayTeam"].map(lambda t: TEAM_META.get(t, {}).get("div", "Unknown"))
    df["HomeDiv"]  = df["HomeTeam"].map(lambda t: TEAM_META.get(t, {}).get("div", "Unknown"))

    # Week/Month/DayOfWeek
    if "GameDate" in df.columns:
        df["Month"]     = df["GameDate"].dt.month_name()
        df["MonthNum"]  = df["GameDate"].dt.month
        df["Week"]      = df["GameDate"].dt.isocalendar().week.astype(int)
        df["DayOfWeek"] = df["GameDate"].dt.day_name()
        df["WeekStart"] = df["GameDate"].dt.to_period("W").apply(lambda p: p.start_time)

    # Back-to-back detection (same team plays on consecutive days)
    df = detect_back_to_back(df)

    # Road trip / homestand tracking
    df = detect_road_trips(df)

    # Won/lost last game
    df = detect_last_game_result(df)

    # Gauntlet detection
    df = detect_gauntlets(df)

    return df


def detect_back_to_back(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("GameDate").reset_index(drop=True)
    df["AwayB2B"] = False
    df["HomeB2B"] = False

    all_teams = set(df["AwayTeam"].dropna()) | set(df["HomeTeam"].dropna())
    for team in all_teams:
        mask_away = df["AwayTeam"] == team
        mask_home = df["HomeTeam"] == team
        team_games = df[mask_away | mask_home][["GameDate"]].copy()
        team_games = team_games.sort_values("GameDate")
        team_games["PrevDate"] = team_games["GameDate"].shift(1)
        team_games["IsB2B"] = (team_games["GameDate"] - team_games["PrevDate"]).dt.days == 1

        b2b_dates = set(team_games[team_games["IsB2B"]]["GameDate"])
        df.loc[mask_away & df["GameDate"].isin(b2b_dates), "AwayB2B"] = True
        df.loc[mask_home & df["GameDate"].isin(b2b_dates), "HomeB2B"] = True

    df["EitherB2B"] = df["AwayB2B"] | df["HomeB2B"]
    return df


def detect_road_trips(df: pd.DataFrame) -> pd.DataFrame:
    """Track consecutive away games (road trips) and home games (homestands) per team."""
    df = df.sort_values("GameDate").reset_index(drop=True)
    df["AwayRoadTripGame"] = 0  # which game in road trip (0 = not on road trip)
    df["HomeHomestandGame"] = 0

    all_teams = set(df["AwayTeam"].dropna()) | set(df["HomeTeam"].dropna())
    for team in all_teams:
        away_idx = df[df["AwayTeam"] == team].index.tolist()
        home_idx = df[df["HomeTeam"] == team].index.tolist()

        all_idx = sorted(away_idx + home_idx)
        streak_away = 0
        streak_home = 0
        for idx in all_idx:
            if idx in df.index:
                if df.loc[idx, "AwayTeam"] == team:
                    streak_away += 1
                    streak_home = 0
                    if streak_away >= 2:
                        # Mark this game as part of road trip
                        df.loc[idx, "AwayRoadTripGame"] = streak_away
                else:
                    streak_home += 1
                    streak_away = 0
                    if streak_home >= 2:
                        df.loc[idx, "HomeHomestandGame"] = streak_home

    df["OnRoadTrip"]  = df["AwayRoadTripGame"] >= 2
    df["OnHomeStand"] = df["HomeHomestandGame"] >= 2
    return df


def detect_last_game_result(df: pd.DataFrame) -> pd.DataFrame:
    """For each game, did the away/home team win or lose their last game?"""
    df = df.sort_values("GameDate").reset_index(drop=True)
    df["AwayWonLast"] = None
    df["HomeWonLast"] = None

    all_teams = set(df["AwayTeam"].dropna()) | set(df["HomeTeam"].dropna())
    for team in all_teams:
        mask_away = df["AwayTeam"] == team
        mask_home = df["HomeTeam"] == team
        combined = pd.concat([
            df[mask_away][["GameDate", "ActualWinner"]].assign(side="away", idx=df[mask_away].index),
            df[mask_home][["GameDate", "ActualWinner"]].assign(side="home", idx=df[mask_home].index),
        ]).sort_values("GameDate")

        combined["TeamWon"] = combined["ActualWinner"] == team
        combined["TeamWonLast"] = combined["TeamWon"].shift(1)

        for _, row in combined.iterrows():
            if pd.isna(row["TeamWonLast"]):
                continue
            if row["side"] == "away":
                df.loc[row["idx"], "AwayWonLast"] = row["TeamWonLast"]
            else:
                df.loc[row["idx"], "HomeWonLast"] = row["TeamWonLast"]

    return df


def detect_gauntlets(df: pd.DataFrame) -> pd.DataFrame:
    """Detect when away team is on a gauntlet swing."""
    df = df.sort_values("GameDate").reset_index(drop=True)
    df["GauntletName"] = ""

    all_teams = set(df["AwayTeam"].dropna())
    for team in all_teams:
        away_games = df[df["AwayTeam"] == team][["GameDate", "HomeTeam"]].sort_values("GameDate")

        # Sliding window: look for gauntlet patterns in consecutive away games
        if len(away_games) < 2:
            continue

        away_games = away_games.reset_index()

        for gauntlet_name, g_info in GAUNTLETS.items():
            g_teams = set(g_info["teams"])
            for i in range(len(away_games)):
                # Look up to len(g_teams) ahead
                window = away_games.iloc[i:i+len(g_teams)]
                opponents = set(window["HomeTeam"].values)
                # Check if at least 2 gauntlet teams are in consecutive away window
                overlap = opponents & g_teams
                if len(overlap) >= 2:
                    # Check dates are within 10 days
                    if len(window) > 1:
                        span = (window["GameDate"].max() - window["GameDate"].min()).days
                        if span <= 14:
                            idxs = window["index"].tolist()
                            for idx in idxs:
                                if df.loc[idx, "HomeTeam"] in g_teams:
                                    if df.loc[idx, "GauntletName"] == "":
                                        df.loc[idx, "GauntletName"] = gauntlet_name
                                    elif gauntlet_name not in df.loc[idx, "GauntletName"]:
                                        df.loc[idx, "GauntletName"] += f", {gauntlet_name}"
    return df


@st.cache_data
def get_team_logo(team_abbr: str) -> str:
    """Get NHL team logo URL from NHL API."""
    team_id = TEAM_META.get(team_abbr, {}).get("id")
    if team_id:
        return f"https://assets.nhle.com/logos/nhl/svg/{team_abbr}_dark.svg"
    return ""


# ─────────────────────────────────────────────────────────
# PLOTTING HELPERS
# ─────────────────────────────────────────────────────────
DARK_THEME = dict(
    paper_bgcolor="#0a0e1a",
    plot_bgcolor="#0d1f35",
    font=dict(color="#ccd6e0", family="Inter"),
    xaxis=dict(gridcolor="#1e3a5a", linecolor="#1e3a5a"),
    yaxis=dict(gridcolor="#1e3a5a", linecolor="#1e3a5a"),
)
GOLD = "#c8a84b"
ICE_BLUE = "#4ab3f4"
RED = "#e74c3c"
GREEN = "#2ecc71"


def accuracy_bar(group_col, label, df_completed):
    """Bar chart of prediction accuracy by a grouping column."""
    grouped = (
        df_completed.groupby(group_col)["CorrectWinnerPrediction"]
        .agg(["sum", "count"])
        .reset_index()
    )
    grouped.columns = [group_col, "Correct", "Total"]
    grouped["Accuracy"] = (grouped["Correct"] / grouped["Total"] * 100).round(1)
    grouped = grouped.sort_values("Accuracy", ascending=True)

    fig = px.bar(
        grouped, x="Accuracy", y=group_col, orientation="h",
        text="Accuracy", color="Accuracy",
        color_continuous_scale=[[0, RED], [0.5, "#f39c12"], [1, GREEN]],
        labels={"Accuracy": "Accuracy %", group_col: label},
        title=f"Prediction Accuracy by {label}",
        custom_data=["Correct", "Total"]
    )
    fig.update_traces(
        texttemplate="%{text:.1f}%", textposition="outside",
        hovertemplate=f"<b>%{{y}}</b><br>Accuracy: %{{x:.1f}}%<br>Correct: %{{customdata[0]}} / %{{customdata[1]}}<extra></extra>"
    )
    fig.update_layout(**DARK_THEME, coloraxis_showscale=False, height=max(300, len(grouped)*35 + 80))
    fig.update_traces(marker_line_width=0)
    return fig, grouped


def correct_incorrect_pie(correct_count, total_count):
    incorrect = total_count - correct_count
    fig = go.Figure(go.Pie(
        labels=["Correct ✓", "Incorrect ✗"],
        values=[correct_count, incorrect],
        hole=0.65,
        marker_colors=[GREEN, RED],
        textinfo="label+percent",
        hovertemplate="%{label}: %{value}<extra></extra>"
    ))
    fig.update_layout(
        **DARK_THEME,
        showlegend=False,
        annotations=[dict(
            text=f"<b>{correct_count/total_count*100:.1f}%</b>",
            x=0.5, y=0.5, font_size=24, font_color=GOLD, showarrow=False
        )],
        height=280,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    return fig


def rolling_accuracy_chart(df_team, team_abbr):
    df_team = df_team.sort_values("GameDate").copy()
    df_team["CumCorrect"] = df_team["CorrectWinnerPrediction"].cumsum()
    df_team["CumTotal"] = range(1, len(df_team) + 1)
    df_team["CumAccuracy"] = df_team["CumCorrect"] / df_team["CumTotal"] * 100
    df_team["Roll7"] = (
        df_team["CorrectWinnerPrediction"]
        .rolling(7, min_periods=3)
        .mean() * 100
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_team["GameDate"], y=df_team["CumAccuracy"],
        name="Cumulative Accuracy", line=dict(color=GOLD, width=2),
        mode="lines"
    ))
    fig.add_trace(go.Scatter(
        x=df_team["GameDate"], y=df_team["Roll7"],
        name="7-Game Rolling Avg", line=dict(color=ICE_BLUE, width=2, dash="dot"),
        mode="lines"
    ))
    fig.add_hline(y=50, line_dash="dash", line_color="#555", annotation_text="50%")
    fig.update_layout(
        **DARK_THEME,
        title=f"Prediction Accuracy Trend — {team_abbr}",
        xaxis_title="Game Date",
        yaxis_title="Accuracy %",
        yaxis_range=[0, 105],
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=350
    )
    return fig


def game_by_game_scatter(df_team, team_abbr):
    df_team = df_team.sort_values("GameDate").copy()
    df_team["GameNum"] = range(1, len(df_team) + 1)
    df_team["Result"] = df_team["CorrectWinnerPrediction"].map({True: "Correct", False: "Incorrect"})
    df_team["Opponent"] = df_team.apply(
        lambda r: r["HomeTeam"] if r["AwayTeam"] == team_abbr else r["AwayTeam"], axis=1
    )
    df_team["Side"] = df_team.apply(
        lambda r: "Away" if r["AwayTeam"] == team_abbr else "Home", axis=1
    )

    fig = px.scatter(
        df_team, x="GameDate", y="GamePredictionScore",
        color="Result", symbol="Side",
        color_discrete_map={"Correct": GREEN, "Incorrect": RED},
        hover_data=["Opponent", "ActualResult", "PredictedResult"],
        title=f"Game-by-Game Prediction Quality — {team_abbr}",
        labels={"GamePredictionScore": "Prediction Score", "GameDate": "Date"}
    )
    fig.update_layout(**DARK_THEME, height=350)
    return fig


def compare_two_groups(df_completed, group_col, label):
    """Side-by-side comparison chart."""
    g = (
        df_completed.groupby(group_col)["CorrectWinnerPrediction"]
        .agg(["sum", "count"]).reset_index()
    )
    g.columns = [group_col, "Correct", "Total"]
    g["Incorrect"] = g["Total"] - g["Correct"]
    g["Accuracy"] = (g["Correct"] / g["Total"] * 100).round(1)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Correct", x=g[group_col], y=g["Correct"],
        marker_color=GREEN, text=g["Accuracy"].apply(lambda x: f"{x}%"),
        textposition="outside"
    ))
    fig.add_trace(go.Bar(
        name="Incorrect", x=g[group_col], y=g["Incorrect"],
        marker_color=RED
    ))
    fig.update_layout(
        **DARK_THEME,
        barmode="stack",
        title=f"Correct vs Incorrect by {label}",
        xaxis_title=label,
        yaxis_title="Games",
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    return fig


# ─────────────────────────────────────────────────────────
# PREDICTION MODEL (SIMPLE STATS-BASED)
# ─────────────────────────────────────────────────────────
def build_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """Predict future games using historical win rates from this dataset."""
    completed = df[df["GameIsOver"] == True].copy()
    future    = df[df["GameIsOver"] == False].copy()

    if len(future) == 0:
        return pd.DataFrame()

    # Build team stats: overall win rate (as away), win rate (as home)
    away_stats = (
        completed.groupby("AwayTeam")["AwayWon"]
        .agg(["mean", "count"]).rename(columns={"mean": "AwayWinRate", "count": "AwayGames"})
    )
    home_stats = (
        completed.groupby("HomeTeam")["HomeWon_"]
        .agg(["mean", "count"]).rename(columns={"mean": "HomeWinRate", "count": "HomeGames"})
    )

    # Home ice advantage boost: historically ~55% home win rate in NHL
    HOME_BOOST = 0.04

    results = []
    for _, row in future.iterrows():
        away = row["AwayTeam"]
        home = row["HomeTeam"]

        away_wr = away_stats.loc[away, "AwayWinRate"] if away in away_stats.index else 0.45
        home_wr = home_stats.loc[home, "HomeWinRate"] if home in home_stats.index else 0.50

        # Combined score: blend away team's road win rate with home team's home win rate
        home_prob = (home_wr + HOME_BOOST + (1 - away_wr)) / 2
        home_prob = max(0.1, min(0.9, home_prob))
        away_prob = 1 - home_prob

        predicted_winner = home if home_prob > 0.5 else away
        confidence = max(home_prob, away_prob)

        results.append({
            "GameDate": row["GameDate"],
            "AwayTeam": away,
            "HomeTeam": home,
            "PredictedWinner": predicted_winner,
            "AwayWinProb": round(away_prob * 100, 1),
            "HomeWinProb": round(home_prob * 100, 1),
            "Confidence": round(confidence * 100, 1),
            "GameID": row.get("GameID", ""),
        })

    return pd.DataFrame(results)


# ─────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────
def main():
    # Header
    st.markdown("""
    <div class="nhl-header">
        <h1>🏒 NHL PREDICTION DASHBOARD</h1>
        <p>Analyze your game prediction performance across teams, divisions, conferences, and scheduling patterns</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ─────────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🗂️ Navigation")
        page = st.radio("", [
            "📊 Overview & Accuracy",
            "👥 By Team",
            "🗓️ Trends Over Time",
            "🌍 Travel & Gauntlets",
            "🔮 Future Predictions",
        ], label_visibility="collapsed")
        
    try:
        df = load_data(path_excel_predictions, skiprows=1)
        st.sidebar.success(f"✅ Using bundled dataset ({path_excel_predictions})")
    except Exception as e:
        st.error(f"No data found. Please upload your CSV. Error: {e}")
        return

    completed = df[df["GameIsOver"] == True].copy()
    future    = df[df["GameIsOver"] == False].copy()

    total      = len(completed)
    n_correct  = completed["CorrectWinnerPrediction"].sum()
    accuracy   = n_correct / total * 100 if total > 0 else 0

    # ── PAGE: OVERVIEW ───────────────────────────────────
    if page == "📊 Overview & Accuracy":
        st.markdown('<div class="section-header">OVERALL PERFORMANCE</div>', unsafe_allow_html=True)

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Total Games", f"{total}")
        with c2:
            st.metric("Correct", f"{int(n_correct)}")
        with c3:
            st.metric("Incorrect", f"{int(total - n_correct)}")
        with c4:
            st.metric("Win Rate", f"{accuracy:.1f}%")
        with c5:
            avg_score = completed["GamePredictionScore"].mean()
            st.metric("Avg Pred Score", f"{avg_score:.2f}" if not pd.isna(avg_score) else "N/A")

        col_pie, col_info = st.columns([1, 2])
        with col_pie:
            st.plotly_chart(correct_incorrect_pie(int(n_correct), total), use_container_width=True)
        with col_info:
            st.markdown('<div class="section-header" style="font-size:1.1rem">QUICK FACTS</div>', unsafe_allow_html=True)
            if "WatchedGame" in completed.columns:
                watched = completed["WatchedGame"].sum()
                st.metric("Games Watched", f"{int(watched)} / {total}")
            if "GameHasShutOut" in completed.columns:
                shutouts = completed["GameHasShutOut"].sum()
                st.metric("Shutouts in Dataset", f"{int(shutouts)}")
            if "ActualResult" in completed.columns:
                ots = completed[completed["ActualResult"].isin(["OT", "SO"])].shape[0]
                st.metric("OT/SO Games", f"{int(ots)}")

        st.markdown('<div class="section-header">ACCURACY BY GROUPING</div>', unsafe_allow_html=True)

        grouping_options = {
            "Conference": "AwayConf",
            "Division (Away Team)": "AwayDiv",
            "Division (Home Team)": "HomeDiv",
            "Day of Week": "DayOfWeek",
            "Month": "Month",
            "Home Team": "HomeTeam",
            "Away Team": "AwayTeam",
            "Actual Result Type": "ActualResult",
        }

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            g1 = st.selectbox("Group by (Chart 1)", list(grouping_options.keys()), index=0)
        with col_g2:
            g2 = st.selectbox("Group by (Chart 2)", list(grouping_options.keys()), index=2)

        tab1, tab2 = st.tabs([f"📊 {g1}", f"📊 {g2}"])
        with tab1:
            fig, tbl = accuracy_bar(grouping_options[g1], g1, completed)
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("View data table"):
                st.dataframe(tbl.sort_values("Accuracy", ascending=False), use_container_width=True)

        with tab2:
            fig2, tbl2 = accuracy_bar(grouping_options[g2], g2, completed)
            st.plotly_chart(fig2, use_container_width=True)
            with st.expander("View data table"):
                st.dataframe(tbl2.sort_values("Accuracy", ascending=False), use_container_width=True)

        # Stacked comparison
        st.markdown('<div class="section-header">SIDE-BY-SIDE COMPARISON</div>', unsafe_allow_html=True)
        cmp_col = st.selectbox("Compare by", list(grouping_options.keys()), index=6)
        fig_cmp = compare_two_groups(completed, grouping_options[cmp_col], cmp_col)
        st.plotly_chart(fig_cmp, use_container_width=True)

        # Back-to-back accuracy
        st.markdown('<div class="section-header">BACK-TO-BACK PERFORMANCE</div>', unsafe_allow_html=True)
        b2b_df = completed.copy()
        b2b_df["Situation"] = "Standard"
        b2b_df.loc[b2b_df["AwayB2B"], "Situation"] = "Away B2B"
        b2b_df.loc[b2b_df["HomeB2B"], "Situation"] = "Home B2B"
        b2b_df.loc[b2b_df["AwayB2B"] & b2b_df["HomeB2B"], "Situation"] = "Both B2B"

        fig_b2b, _ = accuracy_bar("Situation", "Back-to-Back Situation", b2b_df)
        st.plotly_chart(fig_b2b, use_container_width=True)

    # ── PAGE: BY TEAM ────────────────────────────────────
    elif page == "👥 By Team":
        st.markdown('<div class="section-header">TEAM PERFORMANCE EXPLORER</div>', unsafe_allow_html=True)

        all_teams = sorted(set(completed["AwayTeam"].dropna()) | set(completed["HomeTeam"].dropna()))
        selected_team = st.selectbox("Select Team", all_teams)

        team_logo_url = get_team_logo(selected_team)
        team_name = TEAM_META.get(selected_team, {}).get("name", selected_team)

        col_logo, col_title = st.columns([1, 6])
        with col_logo:
            if team_logo_url:
                st.image(team_logo_url, width=80)
        with col_title:
            st.markdown(f"### {team_name} ({selected_team})")
            meta = TEAM_META.get(selected_team, {})
            st.caption(f"{meta.get('conf','?')} Conference · {meta.get('div','?')} Division")

        # Filter conditions
        st.markdown("#### 🔍 Filter Conditions")
        filter_cols = st.columns(3)
        filter_opts = {
            "Away Games Only": None,
            "Home Games Only": None,
            "Playing Back-to-Back": None,
            "On Road Trip": None,
            "On Home Stand": None,
            "Team Won Last Game": None,
            "Team Lost Last Game": None,
        }
        selected_filters = []
        for i, (label, _) in enumerate(filter_opts.items()):
            with filter_cols[i % 3]:
                if st.checkbox(label):
                    selected_filters.append(label)

        # Build team dataframe
        team_away = completed[completed["AwayTeam"] == selected_team].copy()
        team_home = completed[completed["HomeTeam"] == selected_team].copy()
        team_all  = pd.concat([team_away, team_home]).sort_values("GameDate").drop_duplicates()

        # Apply filters
        fdf = team_all.copy()
        for f in selected_filters:
            if f == "Away Games Only":
                fdf = fdf[fdf["AwayTeam"] == selected_team]
            elif f == "Home Games Only":
                fdf = fdf[fdf["HomeTeam"] == selected_team]
            elif f == "Playing Back-to-Back":
                fdf = fdf[
                    ((fdf["AwayTeam"] == selected_team) & fdf["AwayB2B"]) |
                    ((fdf["HomeTeam"] == selected_team) & fdf["HomeB2B"])
                ]
            elif f == "On Road Trip":
                fdf = fdf[(fdf["AwayTeam"] == selected_team) & fdf["OnRoadTrip"]]
            elif f == "On Home Stand":
                fdf = fdf[(fdf["HomeTeam"] == selected_team) & fdf["OnHomeStand"]]
            elif f == "Team Won Last Game":
                fdf = fdf[
                    ((fdf["AwayTeam"] == selected_team) & (fdf["AwayWonLast"] == True)) |
                    ((fdf["HomeTeam"] == selected_team) & (fdf["HomeWonLast"] == True))
                ]
            elif f == "Team Lost Last Game":
                fdf = fdf[
                    ((fdf["AwayTeam"] == selected_team) & (fdf["AwayWonLast"] == False)) |
                    ((fdf["HomeTeam"] == selected_team) & (fdf["HomeWonLast"] == False))
                ]

        n_t = len(fdf)
        n_c = fdf["CorrectWinnerPrediction"].sum() if n_t > 0 else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Games (filtered)", n_t)
        m2.metric("Correct", int(n_c))
        m3.metric("Accuracy", f"{n_c/n_t*100:.1f}%" if n_t > 0 else "—")
        m4.metric("Home/Away Split", f"{len(fdf[fdf['HomeTeam']==selected_team])}H / {len(fdf[fdf['AwayTeam']==selected_team])}A")

        if n_t > 0:
            st.plotly_chart(rolling_accuracy_chart(fdf, selected_team), use_container_width=True)
            st.plotly_chart(game_by_game_scatter(fdf, selected_team), use_container_width=True)

            # Game-by-game table
            st.markdown("#### Game Log")
            display_cols = ["GameDate", "AwayTeam", "HomeTeam", "PredictedWinner", "ActualWinner",
                            "CorrectWinnerPrediction", "ActualResult", "GamePredictionScore"]
            display_cols = [c for c in display_cols if c in fdf.columns]
            log_df = fdf[display_cols].sort_values("GameDate", ascending=False).copy()
            log_df["CorrectWinnerPrediction"] = log_df["CorrectWinnerPrediction"].map(
                {True: "✅", False: "❌"}
            )
            st.dataframe(log_df, use_container_width=True, height=320)
        else:
            st.warning("No games match the selected filters.")

        # Home vs Away breakdown
        st.markdown('<div class="section-header">HOME VS AWAY BREAKDOWN</div>', unsafe_allow_html=True)
        col_hv, col_av = st.columns(2)

        for col_w, subset, label in [(col_hv, team_home, "Home"), (col_av, team_away, "Away")]:
            with col_w:
                n = len(subset)
                c = subset["CorrectWinnerPrediction"].sum() if n > 0 else 0
                st.metric(f"{label} Games", n)
                st.metric(f"{label} Accuracy", f"{c/n*100:.1f}%" if n > 0 else "—")
                if n > 0:
                    st.plotly_chart(correct_incorrect_pie(int(c), n), use_container_width=True)

    # ── PAGE: TRENDS OVER TIME ────────────────────────────
    elif page == "🗓️ Trends Over Time":
        st.markdown('<div class="section-header">PREDICTION TRENDS OVER TIME</div>', unsafe_allow_html=True)

        # Overall cumulative accuracy
        overall = completed.sort_values("GameDate").copy()
        overall["CumAcc"] = overall["CorrectWinnerPrediction"].expanding().mean() * 100
        overall["Roll14"] = overall["CorrectWinnerPrediction"].rolling(14, min_periods=5).mean() * 100

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=overall["GameDate"], y=overall["CumAcc"],
            name="Cumulative Accuracy", line=dict(color=GOLD, width=2),
        ))
        fig_trend.add_trace(go.Scatter(
            x=overall["GameDate"], y=overall["Roll14"],
            name="14-Game Rolling Avg", line=dict(color=ICE_BLUE, width=2, dash="dot"),
        ))
        fig_trend.add_hline(y=50, line_dash="dash", line_color="#555", annotation_text="50%")
        fig_trend.update_layout(
            **DARK_THEME,
            title="Overall Prediction Accuracy Over Time",
            xaxis_title="Date", yaxis_title="Accuracy %",
            yaxis_range=[0, 105], height=380
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # By week
        st.markdown('<div class="section-header">WEEKLY BREAKDOWN</div>', unsafe_allow_html=True)
        weekly = (
            completed.groupby("WeekStart")["CorrectWinnerPrediction"]
            .agg(["sum", "count"]).reset_index()
        )
        weekly.columns = ["Week", "Correct", "Total"]
        weekly["Accuracy"] = weekly["Correct"] / weekly["Total"] * 100

        fig_wk = go.Figure()
        fig_wk.add_trace(go.Bar(
            x=weekly["Week"], y=weekly["Accuracy"],
            marker_color=[GREEN if a >= 50 else RED for a in weekly["Accuracy"]],
            text=weekly["Accuracy"].round(1), texttemplate="%{text:.1f}%",
            textposition="outside",
            hovertemplate="Week of %{x}<br>Accuracy: %{y:.1f}%<br>Games: %{customdata}<extra></extra>",
            customdata=weekly["Total"]
        ))
        fig_wk.add_hline(y=50, line_dash="dash", line_color="#888")
        fig_wk.update_layout(**DARK_THEME, title="Accuracy by Week", yaxis_range=[0, 110], height=380)
        st.plotly_chart(fig_wk, use_container_width=True)

        # By month
        st.markdown('<div class="section-header">MONTHLY BREAKDOWN</div>', unsafe_allow_html=True)
        monthly = (
            completed.groupby(["MonthNum", "Month"])["CorrectWinnerPrediction"]
            .agg(["sum", "count"]).reset_index().sort_values("MonthNum")
        )
        monthly.columns = ["MonthNum", "Month", "Correct", "Total"]
        monthly["Accuracy"] = monthly["Correct"] / monthly["Total"] * 100

        fig_mo = px.bar(
            monthly, x="Month", y="Accuracy",
            color="Accuracy",
            color_continuous_scale=[[0, RED], [0.5, "#f39c12"], [1, GREEN]],
            text=monthly["Accuracy"].round(1),
            title="Accuracy by Month"
        )
        fig_mo.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_mo.update_layout(**DARK_THEME, coloraxis_showscale=False, yaxis_range=[0, 110], height=380)
        st.plotly_chart(fig_mo, use_container_width=True)

        # Day of week heatmap
        st.markdown('<div class="section-header">DAY OF WEEK HEATMAP</div>', unsafe_allow_html=True)
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow = (
            completed.groupby("DayOfWeek")["CorrectWinnerPrediction"]
            .agg(["sum", "count"]).reset_index()
        )
        dow.columns = ["Day", "Correct", "Total"]
        dow["Accuracy"] = dow["Correct"] / dow["Total"] * 100
        dow["Day"] = pd.Categorical(dow["Day"], categories=dow_order, ordered=True)
        dow = dow.sort_values("Day")

        fig_dow = px.bar(
            dow, x="Day", y="Accuracy",
            color="Accuracy",
            color_continuous_scale=[[0, RED], [0.5, "#f39c12"], [1, GREEN]],
            text=dow["Accuracy"].round(1),
            title="Accuracy by Day of Week",
            hover_data=["Correct", "Total"]
        )
        fig_dow.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig_dow.update_layout(**DARK_THEME, coloraxis_showscale=False, yaxis_range=[0, 110], height=360)
        st.plotly_chart(fig_dow, use_container_width=True)

    # ── PAGE: TRAVEL & GAUNTLETS ──────────────────────────
    elif page == "🌍 Travel & Gauntlets":
        st.markdown('<div class="section-header">TRAVEL PATTERNS & SCHEDULING GAUNTLETS</div>', unsafe_allow_html=True)

        st.markdown("""
        Scheduling gauntlets occur when an away team travels through a geographic cluster of opponents
        consecutively. Detect how well games are predicted during these grueling road swings.
        """)

        # Road trip performance
        st.markdown('<div class="section-header">ROAD TRIP PERFORMANCE</div>', unsafe_allow_html=True)

        rt_df = completed[completed["OnRoadTrip"]].copy()
        st_df = completed[~completed["OnRoadTrip"]].copy()

        col_rt1, col_rt2 = st.columns(2)
        with col_rt1:
            n_rt = len(rt_df)
            c_rt = rt_df["CorrectWinnerPrediction"].sum() if n_rt > 0 else 0
            st.metric("Road Trip Games", n_rt)
            st.metric("Road Trip Accuracy", f"{c_rt/n_rt*100:.1f}%" if n_rt > 0 else "—")
            if n_rt > 0:
                st.plotly_chart(correct_incorrect_pie(int(c_rt), n_rt), use_container_width=True)
        with col_rt2:
            n_st = len(st_df)
            c_st = st_df["CorrectWinnerPrediction"].sum() if n_st > 0 else 0
            st.metric("Standard Away Games", n_st)
            st.metric("Standard Away Accuracy", f"{c_st/n_st*100:.1f}%" if n_st > 0 else "—")
            if n_st > 0:
                st.plotly_chart(correct_incorrect_pie(int(c_st), n_st), use_container_width=True)

        # Gauntlet analysis
        st.markdown('<div class="section-header">GAUNTLET PERFORMANCE</div>', unsafe_allow_html=True)

        gauntlet_games = completed[completed["GauntletName"] != ""].copy()
        non_gauntlet   = completed[completed["GauntletName"] == ""].copy()

        if len(gauntlet_games) > 0:
            gauntlet_summary = (
                gauntlet_games.groupby("GauntletName")["CorrectWinnerPrediction"]
                .agg(["sum", "count"]).reset_index()
            )
            gauntlet_summary.columns = ["Gauntlet", "Correct", "Total"]
            gauntlet_summary["Accuracy"] = (gauntlet_summary["Correct"] / gauntlet_summary["Total"] * 100).round(1)

            fig_g = px.bar(
                gauntlet_summary.sort_values("Accuracy", ascending=True),
                x="Accuracy", y="Gauntlet", orientation="h",
                color="Accuracy",
                color_continuous_scale=[[0, RED], [0.5, "#f39c12"], [1, GREEN]],
                text="Accuracy",
                title="Prediction Accuracy During Gauntlet Swings",
                hover_data=["Correct", "Total"]
            )
            fig_g.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_g.update_layout(**DARK_THEME, coloraxis_showscale=False, height=400)
            st.plotly_chart(fig_g, use_container_width=True)

            for gauntlet_name, g_info in GAUNTLETS.items():
                g_games = gauntlet_games[gauntlet_games["GauntletName"].str.contains(gauntlet_name.split("🌴")[0].strip().split("🍁")[0].strip(), na=False)]
                if len(g_games) == 0:
                    continue
                n_g = len(g_games)
                c_g = g_games["CorrectWinnerPrediction"].sum()
                with st.expander(f"{gauntlet_name} — {n_g} games, {c_g/n_g*100:.0f}% accuracy"):
                    st.caption(g_info["desc"])
                    dcols = ["GameDate", "AwayTeam", "HomeTeam", "ActualWinner", "CorrectWinnerPrediction"]
                    dcols = [c for c in dcols if c in g_games.columns]
                    st.dataframe(g_games[dcols].sort_values("GameDate"), use_container_width=True)
        else:
            st.info("No gauntlet patterns detected in completed games yet. As the season progresses, patterns will emerge from consecutive away game groupings.")

        # Show gauntlet definitions
        st.markdown('<div class="section-header">GAUNTLET DEFINITIONS</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, (name, info) in enumerate(GAUNTLETS.items()):
            with cols[i % 2]:
                teams_str = " · ".join([
                    f'<img src="{get_team_logo(t)}" width="24" style="vertical-align:middle"> {t}'
                    for t in info["teams"]
                ])
                st.markdown(f"""
                <div class="gauntlet-card">
                    <div class="gauntlet-title">{name}</div>
                    <div style="color:#8899aa; font-size:0.85rem; margin-top:4px">{info["desc"]}</div>
                    <div style="margin-top:8px; font-size:0.8rem; color:#ccd6e0">{", ".join(info["teams"])}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── PAGE: FUTURE PREDICTIONS ──────────────────────────
    elif page == "🔮 Future Predictions":
        st.markdown('<div class="section-header">FUTURE GAME PREDICTIONS</div>', unsafe_allow_html=True)

        pred_df = build_predictions(df)

        if len(pred_df) == 0:
            st.info("🎉 All games in your dataset have been completed! No future games to predict.")
            st.markdown("Upload a dataset with upcoming games (GameIsOver = N/False) to see predictions.")
            return

        st.markdown(f"Found **{len(pred_df)}** upcoming games to predict using statistical win rates from your dataset.")

        # Team win rate stats used for predictions
        completed_copy = completed.copy()
        away_stats = (
            completed_copy.groupby("AwayTeam")["AwayWon"]
            .agg(["mean", "count"]).reset_index()
        )
        away_stats.columns = ["Team", "AwayWinRate", "AwayGames"]
        home_stats = (
            completed_copy.groupby("HomeTeam")["HomeWon_"]
            .agg(["mean", "count"]).reset_index()
        )
        home_stats.columns = ["Team", "HomeWinRate", "HomeGames"]

        with st.expander("📈 Team Win Rate Statistics (basis for predictions)"):
            combined_stats = away_stats.merge(home_stats, on="Team", how="outer")
            combined_stats["OverallGames"] = combined_stats["AwayGames"].fillna(0) + combined_stats["HomeGames"].fillna(0)
            combined_stats["AwayWinRate"] = (combined_stats["AwayWinRate"] * 100).round(1)
            combined_stats["HomeWinRate"] = (combined_stats["HomeWinRate"] * 100).round(1)

            fig_stats = px.scatter(
                combined_stats.dropna(subset=["AwayWinRate", "HomeWinRate"]),
                x="AwayWinRate", y="HomeWinRate", text="Team",
                size="OverallGames", color="HomeWinRate",
                color_continuous_scale=[[0, RED], [0.5, "#f39c12"], [1, GREEN]],
                title="Team Away vs Home Win Rates",
                labels={"AwayWinRate": "Away Win Rate %", "HomeWinRate": "Home Win Rate %"}
            )
            fig_stats.update_traces(textposition="top center")
            fig_stats.update_layout(**DARK_THEME, coloraxis_showscale=False, height=450)
            st.plotly_chart(fig_stats, use_container_width=True)

        # Display predictions
        st.markdown('<div class="section-header">UPCOMING GAME PREDICTIONS</div>', unsafe_allow_html=True)

        filter_team = st.selectbox(
            "Filter by team (optional)",
            ["All Teams"] + sorted(set(pred_df["AwayTeam"]) | set(pred_df["HomeTeam"]))
        )

        display_pred = pred_df.copy()
        if filter_team != "All Teams":
            display_pred = display_pred[
                (display_pred["AwayTeam"] == filter_team) |
                (display_pred["HomeTeam"] == filter_team)
            ]

        display_pred["GameDate"] = pd.to_datetime(display_pred["GameDate"]).dt.strftime("%a %b %d")
        display_pred["Matchup"] = display_pred["AwayTeam"] + " @ " + display_pred["HomeTeam"]
        display_pred["Win Probabilities"] = (
            display_pred["AwayTeam"] + ": " + display_pred["AwayWinProb"].astype(str) + "% | " +
            display_pred["HomeTeam"] + ": " + display_pred["HomeWinProb"].astype(str) + "%"
        )
        display_pred["Confidence"] = display_pred["Confidence"].astype(str) + "%"

        st.dataframe(
            display_pred[["GameDate", "Matchup", "PredictedWinner", "Win Probabilities", "Confidence"]],
            use_container_width=True
        )

        # Confidence distribution
        fig_conf = px.histogram(
            pred_df, x="Confidence", nbins=20,
            color_discrete_sequence=[GOLD],
            title="Distribution of Prediction Confidence",
            labels={"Confidence": "Confidence %", "count": "Games"}
        )
        fig_conf.update_layout(**DARK_THEME, height=300)
        st.plotly_chart(fig_conf, use_container_width=True)

        # Predicted winners summary
        winners = pred_df["PredictedWinner"].value_counts().reset_index()
        winners.columns = ["Team", "Predicted Wins"]

        col_pw1, col_pw2 = st.columns(2)
        with col_pw1:
            fig_pw = px.bar(
                winners.head(15), x="Predicted Wins", y="Team", orientation="h",
                color="Predicted Wins", color_continuous_scale=[[0, ICE_BLUE], [1, GOLD]],
                title="Teams with Most Predicted Wins (upcoming)"
            )
            fig_pw.update_layout(**DARK_THEME, coloraxis_showscale=False, height=420)
            st.plotly_chart(fig_pw, use_container_width=True)
        with col_pw2:
            st.markdown("**Top Confident Predictions**")
            top_conf = pred_df.nlargest(10, "Confidence")[
                ["GameDate", "AwayTeam", "HomeTeam", "PredictedWinner", "Confidence"]
            ].copy()
            top_conf["GameDate"] = pd.to_datetime(top_conf["GameDate"]).dt.strftime("%b %d")
            top_conf["Confidence"] = top_conf["Confidence"].astype(str) + "%"
            st.dataframe(top_conf, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()