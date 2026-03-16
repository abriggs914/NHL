"""
NHL Prediction Performance Dashboard
Run with: streamlit run nhl_dashboard.py
"""

import os
import math
import time
import json
import base64
import requests
import warnings
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from plotly.subplots import make_subplots
from streamlit_pills import pills
from datetime import datetime, timedelta

from colour_utility import Colour
from json_utility import peek_json
import nhl_api_reference_examples as api_ref

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────
# DATA SOURCE — local Excel workbook
# ─────────────────────────────────────────────────────────
path_excel_predictions       = r"C:\\Users\\abrig\\Documents\\Coding_Practice\\Python\\Jerseys\\NHLGamePredictions_2526_copy.xlsx"
path_excel_jerseys           = r"C:\\Users\\abrig\\Documents\\Coding_Practice\\Python\\Jerseys\\Jerseys_20260309.xlsx"
path_jersey_images           = r"D:\\NHL jerseys\\Jerseys 20250927"
path_image_dir               = r"C:\Users\abrig\Documents\Coding_Practice\Python\DataVisualizer"
path_stanley_cup_appearances = r"C:\Users\abrig\Documents\Coding_Practice\Python\DataVisualizer\dataset_nhl_team_apperances.json"
path_stanley_cup_wins        = r"C:\Users\abrig\Documents\Coding_Practice\Python\DataVisualizer\dataset_nhl_team_wins.json"
path_stanley_cup_losses      = r"C:\Users\abrig\Documents\Coding_Practice\Python\DataVisualizer\dataset_nhl_team_losses.json"

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NHL Prediction Dashboard",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

# ═══════════════════════════════════════════════════════════
# JERSEY COLLECTION MODULE
# ═══════════════════════════════════════════════════════════

@st.cache_data(ttl=None)
def load_jersey_data(filepath: str) -> pd.DataFrame:
    """Load jersey Excel workbook (skiprows=1 for header offset)."""
    ext = str(filepath).lower()
    if ext.endswith(".xlsx") or ext.endswith(".xls"):
        df = pd.read_excel(filepath)
    else:
        df = pd.read_csv(filepath, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    # Drop unnamed first column if present
    if df.columns[0] == "" or df.columns[0].startswith("Unnamed"):
        df = df.iloc[:, 1:]

    # Date parsing
    for col in ["OrderDate", "ReceiveDate", "OpenDate"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    df["PriceF"] = df.apply(
        lambda r:
            (
                (
                    (
                        r["ExchangeRate"] * (
                            r["StickerPriceUS"]
                            + (r["Shipping"] if (str(r["Shipping"]).lower() not in ["nan", "0", "0.0", "none"]) else 0)
                            + (r["Tax"] if (str(r["Tax"]).lower() not in ["nan", "0", "0.0", "none"]) else 0)
                        )
                    )
                    + (r["Duty"] if (str(r["Duty"]).lower() not in ["nan", "0", "0.0", "none"]) else 0)
                    - (r["Discount"] if (str(r["Discount"]).lower() not in ["nan", "0", "0.0", "none"]) else 0)
                ) if (str(r["StickerPriceUS"]).lower() not in ["nan", "0", "0.0", "none"]) else (
                    (
                        (
                            r["StickerPriceCDN"]
                            + (r["Duty"] if (str(r["Duty"]).lower() not in ["nan", "0", "0.0", "none"]) else 0)
                            + (r["Shipping"] if (str(r["Shipping"]).lower() not in ["nan", "0", "0.0", "none"]) else 0)
                            + (r["Tax"] if (str(r["Tax"]).lower() not in ["nan", "0", "0.0", "none"]) else 0)
                        )
                        - (r["Discount"] if (str(r["Discount"]).lower() not in ["nan", "0", "0.0", "none"]) else 0)
                    ) if (str(r["StickerPriceCDN"]).lower() not in ["nan", "0", "0.0", "none"]) else -1
                )
            )
        , axis=1
    )

    # Numeric
    for col in ["PriceC", "PriceM", "PriceF", "StickerPriceCDN", "StickerPriceUS",
                "Duty", "Shipping", "Discount", "Tax", "ExchangeRate", "NHLID"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Bool
    if "Cancelled" in df.columns:
        df["Cancelled"] = df["Cancelled"].astype(str).str.lower().isin(["true", "yes", "1"])

    # Derived fields
    if "OrderDate" in df.columns and "ReceiveDate" in df.columns:
        df["DaysToReceive"] = (df["ReceiveDate"] - df["OrderDate"]).dt.days

    if "ReceiveDate" in df.columns and "OpenDate" in df.columns:
        df["DaysToOpen"] = (df["OpenDate"] - df["ReceiveDate"]).dt.days

    if "OrderDate" in df.columns:
        df["OrderYear"]  = df["OrderDate"].dt.year
        df["OrderMonth"] = df["OrderDate"].dt.to_period("M").astype(str)

    # Player name
    df["PlayerName"] = (
        df.get("PlayerFirst", pd.Series([""] * len(df))).fillna("").astype(str).str.strip()
        + " " +
        df.get("PlayerLast", pd.Series([""] * len(df))).fillna("").astype(str).str.strip()
    ).str.strip()
    # df["PlayerName"] = df["PlayerName"].replace("", pd.NA)
    df["NHLID"] = df["NHLID"].fillna(0)
    df["NHLID"] = df["NHLID"].astype(int)

    return df


@st.cache_data(ttl=86400)
def fetch_nhl_player(nhl_id: int) -> dict:
    """Fetch player bio + stats from NHL API v1."""
    try:
        # Bio
        bio_url = f"https://api-web.nhle.com/v1/player/{nhl_id}/landing"
        r = requests.get(bio_url, timeout=8)
        if r.status_code != 200:
            return {}
        data = r.json()

        bio = {
            "name":        data.get("firstName", {}).get("default", "") + " " + data.get("lastName", {}).get("default", ""),
            "headshot":    data.get("headshot", ""),
            "position":    data.get("position", ""),
            "birthCity":   data.get("birthCity", {}).get("default", "") if isinstance(data.get("birthCity"), dict) else data.get("birthCity", ""),
            "birthCountry":data.get("birthCountry", ""),
            "birthDate":   data.get("birthDate", ""),
            "nationality": data.get("nationality", ""),
            "heightFeet":  data.get("heightInFeet", ""),
            "heightInches":data.get("heightInInches", ""),
            "weightPounds":data.get("weightInPounds", ""),
            "shoots":      data.get("shootsCatches", ""),
            "draftYear":   data.get("draftDetails", {}).get("year", ""),
            "draftRound":  data.get("draftDetails", {}).get("round", ""),
            "draftPick":   data.get("draftDetails", {}).get("pickInRound", ""),
            "draftTeam":   data.get("draftDetails", {}).get("teamAbbrev", ""),
            "currentTeam": data.get("currentTeamAbbrev", ""),
            "sweaterNo":   data.get("sweaterNumber", ""),
            "isRetired":   data.get("isRetired", False),
        }

        # Career regular-season stats (last available season)
        stats_list = data.get("featuredStats", {}).get("regularSeason", {}).get("career", {})
        if not stats_list:
            stats_list = data.get("careerTotals", {}).get("regularSeason", {})

        bio["stats"] = stats_list

        # Bio blurb — try from bio block
        bio["bio"] = data.get("biography", {}).get("default", "") if isinstance(data.get("biography"), dict) else ""

        return bio
    except Exception:
        return {}


def get_jersey_image_paths(jersey_id, base_path: str) -> list:
    """Return list of local image paths for a jersey ID."""
    import os, glob
    j_folder = f"J_{int(jersey_id):03d}"
    folder = os.path.join(base_path, j_folder)
    if not os.path.isdir(folder):
        return []
    # f"{folder=}, {jersey_id=}"
    imgs = sorted(
        glob.glob(os.path.join(folder, "*.jpg")) +
        glob.glob(os.path.join(folder, "*.jpeg")) +
        glob.glob(os.path.join(folder, "*.png")) +
        glob.glob(os.path.join(folder, "*.JPG")) +
        glob.glob(os.path.join(folder, "*.JPEG"))
    )
    return list(set(imgs))


def render_jersey_card(row, base_img_path: str, show_player_data: bool = True):
    """Render a single jersey card with image, details, and optional player info."""
    jersey_id = row.get("ID", "?")
    player    = row.get("PlayerName", "")
    team      = row.get("Team", "Unknown")
    league    = row.get("League", "NHL")
    number    = row.get("Number", "")
    brand     = row.get("Brand", "")
    model     = row.get("Model", "")
    make      = row.get("Make", "")
    size      = row.get("Size", "")
    price     = row.get("PriceF", None)
    nhl_id    = row.get("NHLID", None)
    order_dt  = row.get("OrderDate", None)
    
    k_jersey: str = ''.join(map(str, [jersey_id, player, team, league, number, brand, model, make, size, price, nhl_id, order_dt]))

    # Colour chips
    colours = [str(row.get(c, "")) for c in ["Colour1", "Colour2", "Colour3"] if row.get(c, "")]
    colour_map = {
        "Red": "#c0392b", "Black": "#1a1a1a", "White": "#f0f0f0",
        "Blue": "#2980b9", "Gold": "#f1c40f", "Yellow": "#f1c40f",
        "Green": "#27ae60", "Dark Green": "#1a5e2b", "Teal": "#16a085",
        "Navy": "#1a237e", "Orange": "#e67e22", "Purple": "#8e44ad",
        "Grey": "#7f8c8d", "Silver": "#bdc3c7", "Bronze": "#cd7f32",
    }
    colour_chips = "".join([
        f'<span style="display:inline-block;width:14px;height:14px;border-radius:3px;'
        f'background:{colour_map.get(c,"#888")};border:1px solid #333;margin-right:3px;'
        f'vertical-align:middle" title="{c}"></span>'
        for c in colours if c
    ])

    # Team logo
    team_abbr = ""
    for abbr, meta in TEAM_META.items():
        # if meta["name"].lower() in team.lower() or abbr.lower() in team.lower():
        if meta["name"].lower() == team.lower():
            team_abbr = abbr
            break
    logo_html = "<div></div>"
    if team_abbr:
        logo_url = fetch_team_logo(team_abbr)
        logo_html = f'<img src="{logo_url}" width="36" style="vertical-align:middle;margin-right:8px">'

    # Jersey images
    img_paths = get_jersey_image_paths(jersey_id, base_img_path) if jersey_id != "?" else []

    markdown = f"""
    <div style="background:#0d1f35;border:1px solid #1e3a5a;border-radius:10px;padding:16px;margin-bottom:12px">
        <div style="display:flex;align-items:center;margin-bottom:8px">
            {logo_html}
            <div>
                <span style="font-family:'Bebas Neue',sans-serif;font-size:1.3rem;color:#c8a84b;letter-spacing:2px">
                    {"#" + str(int(number)) + " " if str(number).strip() not in ["","nan"] else ""}{player if player else team}
                </span>
                <span style="color:#8899aa;font-size:0.8rem;margin-left:8px">{team} · {league}</span>
            </div>
        </div>
        <div style="color:#ccd6e0;font-size:0.82rem;line-height:1.7">
            <b>ID:</b> J_{int(jersey_id):03d} &nbsp;|&nbsp;
            <b>Brand:</b> {brand} {make} &nbsp;|&nbsp;
            <b>Model:</b> {model} &nbsp;|&nbsp;
            <b>Size:</b> {size}<br>
            <b>Colours:</b> {colour_chips} {", ".join(colours)}<br>
            {"<b>Cost:</b> $" + f"{price:.2f}" + " CAD &nbsp;|&nbsp;" if pd.notna(price) else ""}
            {"<b>Ordered:</b> " + order_dt.strftime("%b %d, %Y") if pd.notna(order_dt) else ""}
        </div>
    </div>
    """
    # st.code(markdown, language="HTML", line_numbers=True)
    st.markdown(markdown, unsafe_allow_html=True)

    # Jersey photos
    if img_paths:
        if len(img_paths) > 3:
            lst_cols_to_make = [1] + [8 for _ in range(3)] + [1]
            # st.write(img_paths)
        else:
            lst_cols_to_make = [1 for _ in range(min(len(img_paths), 3))]
            
        with st.expander(f"{len(img_paths)} Jersey Images:", expanded=False):
            cols_img = st.columns(lst_cols_to_make)
            k_images_start: str = f"key_images_start_{k_jersey}"
            i_images_start = st.session_state.setdefault(k_images_start, 0)
            # st.write(f"{len(img_paths)=}, {i_images_start=}, {k_images_start=}")
            if len(img_paths) > 3:
                with cols_img[0]:
                    if st.button("<", key=f"prev_image_{k_jersey}", disabled=i_images_start==0):
                        st.session_state.update({k_images_start: max(0, i_images_start - 1)})
                        st.rerun()
                    if st.button("|<", key=f"first_image_{k_jersey}", disabled=i_images_start==0):
                        st.session_state.update({k_images_start: 0})
                        st.rerun()
                with cols_img[4]:
                    if st.button("\>", key=f"next_image_{k_jersey}", disabled=i_images_start==(len(img_paths)-3)):
                        st.session_state.update({k_images_start: max(0, i_images_start + 1)})
                        st.rerun()
                    if st.button("\>|", key=f"last_image_{k_jersey}", disabled=i_images_start==(len(img_paths)-3)):
                        st.session_state.update({k_images_start: len(img_paths)-3})
                        st.rerun()
            for i, p in enumerate(img_paths[i_images_start: i_images_start + 3]):
                with cols_img[i + int(bool(len(img_paths) > 3))]:
                    try:
                        st.image(p, use_container_width=True, caption=f"{i_images_start+i+1} / {len(img_paths)} -- '{p}'")
                    except Exception:
                        st.caption(f"📷 {p.split('/')[-1].split(chr(92))[-1]}")
    else:
        st.caption("📷 No local images found for this jersey.")

    # Player data
    if show_player_data and pd.notna(nhl_id) and league in ("NHL", "PWHL"):
        nhl_id_int = int(nhl_id)
        player_data = fetch_nhl_player(nhl_id_int)
        if player_data:
            render_player_panel(player_data, league)


def render_player_panel(pd_data: dict, league: str):
    """Render player bio and stats panel."""
    headshot = pd_data.get("headshot", "")
    name     = pd_data.get("name", "").strip()
    birth    = pd_data.get("birthDate", "")
    city     = pd_data.get("birthCity", "")
    country  = pd_data.get("birthCountry", "")
    stats    = pd_data.get("stats", {})
    bio_text = pd_data.get("bio", "")

    # Age calculation
    age_str = ""
    try:
        bd = datetime.strptime(birth, "%Y-%m-%d")
        age = (datetime.now() - bd).days // 365
        age_str = f"{age} years old"
    except Exception:
        age_str = ""

    col_hs, col_bio = st.columns([1, 4])
    with col_hs:
        if headshot:
            st.image(headshot, width=90)
    with col_bio:
        retired = pd_data.get("isRetired", False)
        badge = "🏒 Active" if not retired else "🎽 Retired"
        draft_info = ""
        if pd_data.get("draftYear"):
            draft_info = f"  |  Drafted {pd_data['draftYear']} Rd {pd_data.get('draftRound','')} #{pd_data.get('draftPick','')} by {pd_data.get('draftTeam','')}"

        st.markdown(f"""
        <div style="background:#081420;border-left:3px solid #c8a84b;padding:10px 14px;border-radius:0 6px 6px 0;margin-bottom:6px">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.1rem;color:#c8a84b">{name} <span style="font-size:0.75rem;color:#8899aa">{badge}</span></div>
            <div style="color:#aabbcc;font-size:0.8rem">
                {pd_data.get('position','').upper()} · {pd_data.get('shoots','')} · 
                {str(pd_data.get('heightFeet',''))}\'{str(pd_data.get('heightInches',''))}\" · 
                {pd_data.get('weightPounds','')} lbs
            </div>
            <div style="color:#8899aa;font-size:0.78rem;margin-top:2px">
                📍 {city}{", " + country if country else ""} · 🎂 {birth} ({age_str}){draft_info}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Career stats
    if stats:
        pos = pd_data.get("position", "G").upper()
        if pos == "G":
            stat_items = [
                ("GP", stats.get("gamesPlayed", "—")),
                ("W",  stats.get("wins", "—")),
                ("L",  stats.get("losses", "—")),
                ("OTL",stats.get("otLosses", "—")),
                ("GAA",f"{stats.get('goalsAgainstAvg', 0):.2f}" if stats.get('goalsAgainstAvg') else "—"),
                ("SV%",f"{stats.get('savePctg', 0):.3f}" if stats.get('savePctg') else "—"),
                ("SO", stats.get("shutouts", "—")),
            ]
        else:
            stat_items = [
                ("GP",  stats.get("gamesPlayed", "—")),
                ("G",   stats.get("goals", "—")),
                ("A",   stats.get("assists", "—")),
                ("PTS", stats.get("points", "—")),
                ("+/-", stats.get("plusMinus", "—")),
                ("PIM", stats.get("pim", "—")),
                ("PPG", stats.get("powerPlayGoals", "—")),
                ("SHG", stats.get("shorthandedGoals", "—")),
            ]
        cols_s = st.columns(len(stat_items))
        for i, (label, val) in enumerate(stat_items):
            with cols_s[i]:
                st.markdown(f"""
                <div style="text-align:center;background:#0a1828;border:1px solid #1e3a5a;border-radius:5px;padding:5px 3px">
                    <div style="font-family:'Bebas Neue';font-size:1.2rem;color:#c8a84b">{val}</div>
                    <div style="font-size:0.65rem;color:#8899aa">{label}</div>
                </div>
                """, unsafe_allow_html=True)

    # Bio blurb
    if bio_text and len(bio_text) > 20:
        with st.expander("📖 Player Bio"):
            st.markdown(f'<div style="color:#aabbcc;font-size:0.82rem;line-height:1.6">{bio_text}</div>', unsafe_allow_html=True)


def page_jersey_collection(df_jerseys: pd.DataFrame, base_img_path: str):
    """Full Jersey Collection page."""
    st.markdown('<div class="section-header">🧥 JERSEY COLLECTION</div>', unsafe_allow_html=True)
    
    # st.write("df_jerseys")
    # st.dataframe(df_jerseys)
    # st.write("'" + ("', '".join(df_jerseys["PlayerName"].values)) + "'")

    active = df_jerseys[df_jerseys.get("Cancelled", pd.Series([False]*len(df_jerseys))).fillna(False) != True].copy()
    
    # st.write("active")
    # st.dataframe(active)
    # st.write("'" + ("', '".join(active["PlayerName"].values)) + "'")
    
    active["ImagePaths"] = active["ID"].apply(lambda id_: get_jersey_image_paths(id_, base_img_path))
    
    st.write(f"active")
    st.write(active)
    
    total_jerseys = len(active)
    total_value   = active["PriceF"].sum() if "PriceF" in active.columns else 0
    with_player   = (~active["PlayerName"].str.strip().isin(["nan", "none", ""])).sum()
    blank_jerseys = total_jerseys - with_player
    # with_images   = sum(1 for _, r in active.iterrows() if get_jersey_image_paths(r.get("ID", -1), base_img_path))
    # need_images = active.loc[bool(len(get_jersey_image_paths(active.get("ID", -1), base_img_path)))]
    # need_images = active.loc[len(np.where(get_jersey_image_paths(active.get("ID", -1), base_img_path)) > 0)]
    # need_images = active.loc[(pd.isna(active["ImagePaths"])) | (len(active["ImagePaths"]) == 0)]
    need_images = active.loc[active["ImagePaths"].map(len) == 0]
    st.write(f"need_images")
    st.write(need_images)
    with_images   = len(active) - len(need_images)
    missing_price = len(active) - len(active[active["PriceF"] > 0])

    # Top KPIs
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Jerseys", total_jerseys)
    k2.metric("Collection Value", f"${total_value:,.0f} CAD" if total_value > 0 else "—")
    k3.metric("Player Jerseys", with_player)
    k4.metric("Blank Jerseys", blank_jerseys)
    k5.metric("With Photos", with_images)
    k6.metric("Missing Price", missing_price)

    st.markdown("---")
    
    options_pills_jersey_collection_mode = [
        "📊 Collection Stats",
        "🔍 Browse Jerseys",
        "📅 Timeline",
        "💰 Cost Analysis",
    ]
    k_pills_jersey_collection_mode: str = "key_pills_jersey_collection_mode"
    st.session_state.setdefault(k_pills_jersey_collection_mode, 0)
    pills_jersey_collection_mode = pills(
        label="Mode",
        options=options_pills_jersey_collection_mode,
        key=k_pills_jersey_collection_mode,
        index=0,
        label_visibility="hidden"
    )

    # ══════════════════════════════════════════════
    # TAB 1: COLLECTION STATS
    # ══════════════════════════════════════════════
    if pills_jersey_collection_mode == options_pills_jersey_collection_mode[0]:
        # 📊 Collection Stats
        st.markdown('<div class="section-header" style="font-size:1.2rem">COLLECTION STATISTICS</div>', unsafe_allow_html=True)

        col_l, col_r = st.columns(2)

        # By League
        with col_l:
            if "League" in active.columns:
                league_cnt = active["League"].value_counts().reset_index()
                league_cnt.columns = ["League", "Count"]
                fig_league = px.pie(
                    league_cnt, names="League", values="Count",
                    title="By League", hole=0.5,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig_league.update_layout(**DARK_THEME, height=300, margin=dict(l=10,r=10,t=40,b=10))
                st.plotly_chart(fig_league, use_container_width=True)

        # By Brand
        with col_r:
            if "Brand" in active.columns:
                brand_cnt = active["Brand"].fillna("Unknown").value_counts().reset_index()
                brand_cnt.columns = ["Brand", "Count"]
                fig_brand = px.bar(
                    brand_cnt, x="Count", y="Brand", orientation="h",
                    title="By Brand / Manufacturer",
                    color="Count", color_continuous_scale=[[0, ICE_BLUE], [1, GOLD]],
                    text="Count"
                )
                fig_brand.update_traces(textposition="outside")
                fig_brand.update_layout(**DARK_THEME, coloraxis_showscale=False,
                                        height=300, margin=dict(l=10,r=10,t=40,b=10))
                st.plotly_chart(fig_brand, use_container_width=True)

        col_l2, col_r2 = st.columns(2)

        # By Team
        with col_l2:
            if "Team" in active.columns:
                team_cnt = active["Team"].fillna("Unknown").value_counts().head(20).reset_index()
                team_cnt.columns = ["Team", "Count"]
                fig_team = px.bar(
                    team_cnt, x="Count", y="Team", orientation="h",
                    title="Top Teams in Collection",
                    color="Count", color_continuous_scale=[[0, RED], [0.5, GOLD], [1, GREEN]],
                    text="Count"
                )
                fig_team.update_traces(textposition="outside")
                fig_team.update_layout(**DARK_THEME, coloraxis_showscale=False,
                                       height=max(300, len(team_cnt)*28 + 60))
                st.plotly_chart(fig_team, use_container_width=True)

        # By Jersey Type / Model
        with col_r2:
            if "Model" in active.columns:
                model_cnt = active["Model"].fillna("Unknown").value_counts().reset_index()
                model_cnt.columns = ["Model", "Count"]
                fig_model = px.pie(
                    model_cnt, names="Model", values="Count",
                    title="By Jersey Model / Type", hole=0.45,
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                fig_model.update_layout(**DARK_THEME, height=350, margin=dict(l=10,r=10,t=40,b=10))
                st.plotly_chart(fig_model, use_container_width=True)

        col_l3, col_r3 = st.columns(2)

        # By Make (PrimeGreen, Blue-Line etc)
        with col_l3:
            if "Make" in active.columns:
                make_cnt = active["Make"].fillna("Unknown").value_counts().reset_index()
                make_cnt.columns = ["Make", "Count"]
                fig_make = px.bar(
                    make_cnt, x="Make", y="Count",
                    title="By Make / Tier",
                    color="Count", color_continuous_scale=[[0, ICE_BLUE], [1, GOLD]],
                    text="Count"
                )
                fig_make.update_traces(textposition="outside")
                fig_make.update_layout(**DARK_THEME, coloraxis_showscale=False, height=320)
                st.plotly_chart(fig_make, use_container_width=True)

        # By Supplier
        with col_r3:
            if "Supplier" in active.columns:
                sup_cnt = active["Supplier"].fillna("Unknown").value_counts().head(15).reset_index()
                sup_cnt.columns = ["Supplier", "Count"]
                fig_sup = px.bar(
                    sup_cnt, x="Count", y="Supplier", orientation="h",
                    title="By Supplier / Store",
                    color="Count", color_continuous_scale=[[0, "#8e44ad"], [1, GOLD]],
                    text="Count"
                )
                fig_sup.update_traces(textposition="outside")
                fig_sup.update_layout(**DARK_THEME, coloraxis_showscale=False,
                                      height=max(280, len(sup_cnt)*30 + 60))
                st.plotly_chart(fig_sup, use_container_width=True)

        # By Nationality of player
        if "Nationality" in active.columns:
            nat_cnt = active["Nationality"].dropna().value_counts().reset_index()
            nat_cnt.columns = ["Nationality", "Count"]
            fig_nat = px.bar(
                nat_cnt, x="Nationality", y="Count",
                title="Player Nationality in Collection",
                color="Count", color_continuous_scale=[[0, ICE_BLUE], [1, GOLD]],
                text="Count"
            )
            fig_nat.update_traces(textposition="outside")
            fig_nat.update_layout(**DARK_THEME, coloraxis_showscale=False, height=320)
            st.plotly_chart(fig_nat, use_container_width=True)

        # By Position
        if "Position" in active.columns:
            pos_cnt = active["Position"].dropna().value_counts().reset_index()
            pos_cnt.columns = ["Position", "Count"]
            fig_pos = px.pie(
                pos_cnt, names="Position", values="Count",
                title="Player Positions in Collection", hole=0.45,
                color_discrete_sequence=[GOLD, ICE_BLUE, GREEN, RED]
            )
            fig_pos.update_layout(**DARK_THEME, height=300)
            st.plotly_chart(fig_pos, use_container_width=True)

        # Size distribution
        if "Size" in active.columns:
            size_cnt = active["Size"].fillna("Unknown").astype(str).value_counts().reset_index()
            size_cnt.columns = ["Size", "Count"]
            fig_size = px.bar(
                size_cnt.sort_values("Count", ascending=False), x="Size", y="Count",
                title="Jersey Size Distribution",
                color="Count",
                color_continuous_scale=[[0, ICE_BLUE], [1, GOLD]],
                text="Count"
            )
            fig_size.update_xaxes(type="category")
            fig_size.update_traces(textposition="outside")
            fig_size.update_layout(**DARK_THEME, coloraxis_showscale=False, height=300)
            st.plotly_chart(fig_size, use_container_width=True)

    # ══════════════════════════════════════════════
    # TAB 2: BROWSE JERSEYS
    # ══════════════════════════════════════════════
    if pills_jersey_collection_mode == options_pills_jersey_collection_mode[1]:
        # 🔍 Browse Jerseys
        st.markdown('<div class="section-header" style="font-size:1.2rem">BROWSE & SEARCH</div>', unsafe_allow_html=True)

        # Filters
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            leagues_avail = sorted(active["League"].dropna().unique()) if "League" in active.columns else []
            sel_league = st.multiselect("League", leagues_avail, default=leagues_avail)
        with fc2:
            teams_avail = sorted(active["Team"].dropna().unique()) if "Team" in active.columns else []
            sel_team = st.multiselect("Team", teams_avail, default=[])
        with fc3:
            brands_avail = sorted(active["Brand"].dropna().unique()) if "Brand" in active.columns else []
            sel_brand = st.multiselect("Brand", brands_avail, default=[])
        with fc4:
            player_search = st.text_input("Search player name", "")

        fc5, fc6, fc7 = st.columns(3)
        has_player_filter = fc5.checkbox("Has player name", value=False)
        show_player_info  = fc6.checkbox("Load player data from NHL API", value=True,
                                        help="Fetches live data — may be slow for many jerseys")
        has_image_filter = fc7.checkbox("Has image(s)", value=False)

        # Apply filters
        filtered = active.copy()
        if sel_league:
            filtered = filtered[filtered["League"].isin(sel_league)]
        if sel_team:
            filtered = filtered[filtered["Team"].isin(sel_team)]
        if sel_brand:
            filtered = filtered[filtered["Brand"].isin(sel_brand)]
        if has_player_filter:
            filtered = filtered[filtered["PlayerName"].notna()]
        if player_search:
            filtered = filtered[
                filtered["PlayerName"].fillna("").str.lower().str.contains(player_search.lower())
            ]
        if has_image_filter:
            filtered = filtered[filtered["ImagePaths"].map(len) != 0]

        st.caption(f"Showing {len(filtered)} of {total_jerseys} jerseys")

        # Sort
        sort_col, sort_dir = st.columns([3, 1])
        with sort_col:
            sort_by = st.selectbox("Sort by", ["OrderDate", "PriceF", "Team", "PlayerLast", "League", "ID"], index=0)
        with sort_dir:
            asc = st.selectbox("Direction", ["Desc", "Asc"], index=0) == "Asc"

        if sort_by in filtered.columns:
            filtered = filtered.sort_values(sort_by, ascending=asc, na_position="last")

        # st.write(f"filtered")
        # st.write(filtered)
        # print(f"filtered")
        # print(filtered)
        
        cols_paginataion = st.columns([0.65, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05])
        k_page: str = "page_number"
        cards_per_page = 3
        n_pages = int(math.ceil(filtered.shape[0] / cards_per_page))
        page_num = st.session_state.setdefault(k_page, 0)
        with cols_paginataion[1]:
            if st.button("|<"):
                st.session_state.update({k_page: 0})
                st.rerun()
        with cols_paginataion[2]:
            if st.button(f"-{cards_per_page} <"):
                st.session_state.update({k_page: max(0, page_num - cards_per_page)})
                st.rerun()
        with cols_paginataion[3]:
            if st.button("<"):
                st.session_state.update({k_page: max(0, page_num - 1)})
                st.rerun()
        with cols_paginataion[4]:
            st.write(f"{page_num + 1} / {n_pages}")
        with cols_paginataion[5]:
            if st.button("\>"):
                st.session_state.update({k_page: min(n_pages - 1, page_num + 1)})
                st.rerun()
        with cols_paginataion[6]:
            if st.button(f"\> {cards_per_page}"):
                st.session_state.update({k_page: min(n_pages - 1, page_num + cards_per_page)})
                st.rerun()
        with cols_paginataion[7]:
            if st.button("\>|"):
                st.session_state.update({k_page: n_pages - 1})
                st.rerun()
        i_a = cards_per_page * page_num
        i_b = (cards_per_page * (page_num + 1)) - 1
        
        filtered = filtered[i_a: i_b + 1]
        
        # st.write(f"{page_num=}, {i_a=}, {i_b=}, {filtered.shape=}")

        # Render jersey cards
        for _, row in filtered.head(cards_per_page).iterrows():
            with st.container():
                # st.write(f"row")
                # st.write(row)
                # print(f"row")
                # print(row)
                render_jersey_card(row, base_img_path, show_player_data=show_player_info)
                st.markdown("---")

    # ══════════════════════════════════════════════
    # TAB 3: TIMELINE
    # ══════════════════════════════════════════════
    # with tab_timeline:
    if pills_jersey_collection_mode == options_pills_jersey_collection_mode[2]:
        # 📅 Timeline
        st.markdown('<div class="section-header" style="font-size:1.2rem">ACQUISITION TIMELINE</div>', unsafe_allow_html=True)
        
        active_timeline = active.rename(columns={
            "ID": "JerseyID",
            "Brand": "BrandName",
            "Make": "JerseyMake"
        })
        active_timeline["Colours"] = active_timeline.apply(
            lambda r:
                ", ".join([c for c in r[["Colour1", "Colour2", "Colour3"]] if str(c).lower().strip() not in ["none", "nan", ""]])
            , axis=1
        )
        cols_timeline_order_open = ["OrderDate", "OpenDate", "JerseyID"]
        # st.write("active_timeline")
        # st.write(active_timeline)
        df_timeline_order_open = active_timeline[cols_timeline_order_open]
        # st.dataframe(df_timeline_order_open)
        # df_timeline_order_receive["Event"] = df_timeline_order_receive.apply(lambda row: print(f"{row=}"))
        # df_timeline_order_receive["Event"] = df_timeline_order_receive.apply(lambda row: print(f"{row=}"))
        df_timeline_order_open = df_timeline_order_open.rename(
            columns={"OrderDate": "Start Date", "OpenDate": "End Date"})

        df_timeline_order_open['Start Date'] = pd.to_datetime(df_timeline_order_open['Start Date'])
        df_timeline_order_open["Category"] = df_timeline_order_open.apply(lambda row: "Yet To Open" if pd.isna(row["End Date"]) else "Opened", axis=1)
        df_timeline_order_open['End Date'] = pd.to_datetime(df_timeline_order_open['End Date']).fillna(pd.Timestamp.now())
        df_timeline_order_open["DDiff"] = df_timeline_order_open.apply(lambda row: (row["End Date"] - row["Start Date"]).days, axis=1)
        df_timeline_order_open["Event"] = df_timeline_order_open.apply(
            lambda row:
                ", ".join(map(str, active_timeline.loc[
                        active_timeline["JerseyID"] == row["JerseyID"],
                    ["Number", "PlayerFirst", "PlayerLast", "Team", "BrandName", "JerseyMake", "Colours"]
                    ].iloc[0].values)) + " Dates between: " + str(row["DDiff"]),
            axis=1
        )
        del df_timeline_order_open["JerseyID"]
        df_timeline_order_open.sort_values(
            by=["End Date", "DDiff"],
            inplace=True
        )

        # Create a Gantt-like timeline using Plotly
        fig_timeline_order_open = px.timeline(
            df_timeline_order_open,
            x_start='Start Date',
            x_end='End Date',
            y='Event',
            title='Time Between Order to Open date',
            color='Category',
            color_discrete_map={
                'Yet To Open': 'red',
                'Medium': 'orange',
                'Opened': 'green'
            }
        )

        # Update layout to make it more readable
        fig_timeline_order_open.update_layout(xaxis_title="Date", yaxis_title="Order Date to Open Date", height=1500)

        # Display in Streamlit
        st.plotly_chart(fig_timeline_order_open)

        # timeline_df = active.dropna(subset=["OrderDate"]).copy()
        # timeline_df["Label"] = timeline_df.apply(
        #     lambda r: (
        #         f"#{int(r['Number'])} " if str(r.get("Number","")).strip() not in ["","nan"] else ""
        #     ) + (r.get("PlayerName") or r.get("Team","?")) + f" ({r.get('Team','?')})",
        #     axis=1
        # )
        # timeline_df = timeline_df.sort_values("OrderDate")

        # # Gantt-style timeline: Order → Receive → Open
        # fig_gantt = go.Figure()
        # colours_gantt = [GOLD, ICE_BLUE, GREEN, RED, "#e67e22", "#9b59b6", "#1abc9c"]

        # for i, (_, row) in enumerate(timeline_df.iterrows()):
        #     colour = colours_gantt[i % len(colours_gantt)]
        #     label  = row["Label"]
        #     od     = row.get("OrderDate")
        #     rd     = row.get("ReceiveDate")
        #     opd    = row.get("OpenDate")
        #     price  = row.get("PriceF")
        #     hover  = (
        #         f"<b>{label}</b><br>"
        #         f"Ordered: {od.strftime('%b %d, %Y') if pd.notna(od) else '—'}<br>"
        #         f"Received: {rd.strftime('%b %d, %Y') if pd.notna(rd) else '—'}<br>"
        #         f"Opened: {opd.strftime('%b %d, %Y') if pd.notna(opd) else '—'}<br>"
        #         f"Cost: {'$' + f'{price:.0f}' + ' CAD' if pd.notna(price) else '—'}"
        #     )

        #     # Order → Receive bar
        #     if pd.notna(od) and pd.notna(rd):
        #         fig_gantt.add_trace(go.Bar(
        #             name="Order→Receive" if i == 0 else "",
        #             y=[label],
        #             x=[(rd - od).days],
        #             base=[od],
        #             orientation="h",
        #             marker_color=colour,
        #             opacity=0.85,
        #             hovertemplate=hover + "<extra>Order→Receive</extra>",
        #             showlegend=(i == 0),
        #         ))

        #     # Receive → Open bar (if both exist)
        #     if pd.notna(rd) and pd.notna(opd) and opd > rd:
        #         fig_gantt.add_trace(go.Bar(
        #             name="Receive→Open" if i == 0 else "",
        #             y=[label],
        #             x=[(opd - rd).days],
        #             base=[rd],
        #             orientation="h",
        #             marker_color=colour,
        #             opacity=0.35,
        #             hovertemplate=hover + "<extra>Receive→Open</extra>",
        #             showlegend=(i == 0),
        #         ))

        #     # Point markers for key events
        #     for event_date, marker_sym, event_label in [
        #         (od,  "circle",          "Ordered"),
        #         (rd,  "diamond",         "Received"),
        #         (opd, "star",            "Opened"),
        #     ]:
        #         if pd.notna(event_date):
        #             fig_gantt.add_trace(go.Scatter(
        #                 x=[event_date], y=[label],
        #                 mode="markers",
        #                 marker=dict(symbol=marker_sym, size=9, color=colour,
        #                             line=dict(width=1, color="#fff")),
        #                 hovertemplate=f"<b>{label}</b><br>{event_label}: {event_date.strftime('%b %d, %Y')}<extra></extra>",
        #                 showlegend=False
        #             ))

        # fig_gantt.update_layout(
        #     **DARK_THEME,
        #     barmode="overlay",
        #     title="Jersey Acquisition Timeline  ●=Ordered  ◆=Received  ★=Opened",
        #     xaxis_title="Date",
        #     # xaxis=dict(type="date", gridcolor="#1e3a5a", linecolor="#1e3a5a"),
        #     # yaxis=dict(gridcolor="#1e3a5a", linecolor="#1e3a5a", autorange="reversed"),
        #     height=max(400, len(timeline_df) * 32 + 80),
        #     legend=dict(orientation="h", yanchor="bottom", y=1.01),
        #     margin=dict(l=20, r=20, t=60, b=20),
        # )
        # st.plotly_chart(fig_gantt, use_container_width=True)

        # Days to receive + days to open distributions
        col_dtr, col_dto = st.columns(2)
        with col_dtr:
            dtr = active["DaysToReceive"].dropna() if "DaysToReceive" in active.columns else pd.Series([], dtype=float)
            if len(dtr) > 0:
                fig_dtr = px.histogram(
                    dtr, nbins=15, title="Days: Order → Receive",
                    color_discrete_sequence=[ICE_BLUE],
                    labels={"value": "Days", "count": "Jerseys"}
                )
                fig_dtr.update_layout(**DARK_THEME, height=280)
                st.plotly_chart(fig_dtr, use_container_width=True)
                st.metric("Avg Days to Receive", f"{dtr.mean():.1f}")

        with col_dto:
            dto = active["DaysToOpen"].dropna() if "DaysToOpen" in active.columns else pd.Series([], dtype=float)
            if len(dto) > 0:
                fig_dto = px.histogram(
                    dto, nbins=15, title="Days: Receive → Open",
                    color_discrete_sequence=[GREEN],
                    labels={"value": "Days", "count": "Jerseys"}
                )
                fig_dto.update_layout(**DARK_THEME, height=280)
                st.plotly_chart(fig_dto, use_container_width=True)
                st.metric("Avg Days to Open", f"{dto.mean():.1f}")

        # Orders by month bar
        if "OrderMonth" in active.columns:
            mo_cnt = active.groupby("OrderMonth").size().reset_index(name="Jerseys")
            mo_cnt = mo_cnt.sort_values("OrderMonth")
            fig_mo = px.bar(
                mo_cnt, x="OrderMonth", y="Jerseys",
                title="Jerseys Ordered by Month",
                color="Jerseys", color_continuous_scale=[[0, ICE_BLUE], [1, GOLD]],
                text="Jerseys"
            )
            fig_mo.update_traces(textposition="outside")
            fig_mo.update_layout(**DARK_THEME, coloraxis_showscale=False,
                                  xaxis_tickangle=-45, height=340)
            st.plotly_chart(fig_mo, use_container_width=True)

    # ══════════════════════════════════════════════
    # TAB 4: COST ANALYSIS
    # ══════════════════════════════════════════════
    # with tab_cost:
    if pills_jersey_collection_mode == options_pills_jersey_collection_mode[3]:
        # 💰 Cost Analysis
        st.markdown('<div class="section-header" style="font-size:1.2rem">COST ANALYSIS</div>', unsafe_allow_html=True)

        all_known = active.copy()
        n_all_jerseys = len(all_known)
        priced = active.dropna(subset=["PriceF"]).copy()
        priced = priced[priced["PriceF"] > 0]
        n_priced_jerseys = len(priced)

        if len(priced) == 0:
            st.info("No pricing data available yet.")
        else:
            # Summary KPIs
            ck1, ck2, ck3, ck4, ck5, ck6 = st.columns(6)
            
            sum_priced = priced['PriceF'].sum()
            mean_priced = priced['PriceF'].mean()
            sum_priced_extrapolated = ((mean_priced * (n_all_jerseys - n_priced_jerseys)) + sum_priced)
            first_date = active["OrderDate"].min().date()
            today = datetime.now().date()
            n_days = (today - first_date).days
            spent_per_day = sum_priced_extrapolated / n_days
            
            ck1.metric("Total Spent", f"${sum_priced:,.2f} CAD")
            ck2.metric("Total Spent (Extrapolated)", f"${sum_priced_extrapolated:,.2f} CAD")
            ck3.metric("Avg per Jersey", f"${mean_priced:,.0f} CAD")
            ck4.metric("Most Expensive", f"${priced['PriceF'].max():,.2f} CAD")
            ck5.metric("Least Expensive", f"${priced['PriceF'].min():,.2f} CAD")
            ck6.metric("Jerseys with Price", len(priced))
            
            ck1.metric("Total Days Collecting:", n_days)
            ck2.metric("Total Spent per Day:", f"${spent_per_day:,.2f} CAD")

            # Cumulative spend over time
            st.write("priced")
            st.write(priced)
            priced = pd.concat([priced, pd.DataFrame({"OrderDate": [pd.Timestamp(today)], "PriceF": [0], "PlayerName": [""], "Team": [""]})])
            priced_sorted = priced.dropna(subset=["OrderDate"]).sort_values("OrderDate").copy()
            if len(priced_sorted) > 0:
                priced_sorted["CumulativeSpend"] = priced_sorted["PriceF"].cumsum()
                priced_sorted["Label"] = priced_sorted.apply(
                    lambda r: (r.get("PlayerName") or r.get("Team","?")) + f" (${r['PriceF']:.0f})", axis=1
                )
                fig_cum = make_subplots(specs=[[{"secondary_y": True}]])
                fig_cum.add_trace(go.Scatter(
                    x=priced_sorted["OrderDate"],
                    y=priced_sorted["CumulativeSpend"],
                    mode="lines+markers",
                    line=dict(color=GOLD, width=2),
                    marker=dict(size=8, color=GOLD),
                    text=priced_sorted["Label"],
                    hovertemplate="<b>%{text}</b><br>Date: %{x|%b %d, %Y}<br>Cumulative: $%{y:,.0f} CAD<extra></extra>",
                    fill="tozeroy",
                    fillcolor="rgba(200,168,75,0.08)"
                ))

                # Convert datetime to numeric values
                x = priced_sorted["OrderDate"].map(pd.Timestamp.toordinal).to_numpy().reshape(-1, 1)
                y = priced_sorted["CumulativeSpend"].to_numpy()

                regr = LinearRegression()
                regr.fit(x, y)

                fit = regr.predict(x)

                fig_cum.add_trace(
                    go.Scatter(
                        x=priced_sorted["OrderDate"],
                        y=fit,
                        name="Trend",
                        mode="lines",
                        line=dict(dash="dash", width=2, color="white"),
                        hovertemplate="Trend: $%{y:,.0f} CAD<extra></extra>"
                    ),
                    secondary_y=False
                )       
                
                
                fig_cum.update_layout(
                    **DARK_THEME,
                    title="Cumulative Collection Spend Over Time",
                    xaxis_title="Order Date",
                    yaxis_title="Cumulative Spend (CAD $)",
                    height=380,
                    # trendline="ols"
                )
                st.plotly_chart(fig_cum, use_container_width=True)

            # Cost by team
            cost_team = priced.groupby("Team")["PriceF"].agg(["sum","mean","count"]).reset_index()
            cost_team.columns = ["Team","Total","Average","Count"]
            cost_team = cost_team.sort_values("Total", ascending=True)

            col_ct1, col_ct2 = st.columns(2)
            with col_ct1:
                fig_ct = px.bar(
                    cost_team, x="Total", y="Team", orientation="h",
                    title="Total Spend by Team",
                    color="Total", color_continuous_scale=[[0, ICE_BLUE], [1, GOLD]],
                    text=cost_team["Total"].apply(lambda x: f"${x:,.0f}")
                )
                fig_ct.update_traces(textposition="outside")
                fig_ct.update_layout(**DARK_THEME, coloraxis_showscale=False,
                                     height=max(280, len(cost_team)*28 + 60))
                st.plotly_chart(fig_ct, use_container_width=True)

            with col_ct2:
                fig_ca = px.bar(
                    cost_team.sort_values("Average", ascending=True),
                    x="Average", y="Team", orientation="h",
                    title="Avg Cost per Jersey by Team",
                    color="Average", color_continuous_scale=[[0, "#27ae60"], [1, RED]],
                    text=cost_team.sort_values("Average", ascending=True)["Average"].apply(lambda x: f"${x:,.0f}")
                )
                fig_ca.update_traces(textposition="outside")
                fig_ca.update_layout(**DARK_THEME, coloraxis_showscale=False,
                                     height=max(280, len(cost_team)*28 + 60))
                st.plotly_chart(fig_ca, use_container_width=True)

            # Cost by brand & supplier
            col_cb1, col_cb2 = st.columns(2)
            with col_cb1:
                cost_brand = priced.groupby("Brand")["PriceF"].agg(["sum","mean"]).reset_index()
                cost_brand.columns = ["Brand","Total","Average"]
                fig_cb = px.bar(
                    cost_brand.sort_values("Total"),
                    x="Total", y="Brand", orientation="h",
                    title="Total Spend by Brand",
                    color="Average", color_continuous_scale=[[0, ICE_BLUE],[1, GOLD]],
                    text=cost_brand.sort_values("Total")["Total"].apply(lambda x: f"${x:,.0f}")
                )
                fig_cb.update_traces(textposition="outside")
                fig_cb.update_layout(**DARK_THEME, coloraxis_showscale=False, height=300)
                st.plotly_chart(fig_cb, use_container_width=True)

            with col_cb2:
                cost_sup = priced.groupby("Supplier")["PriceF"].sum().reset_index()
                cost_sup.columns = ["Supplier","Total"]
                cost_sup = cost_sup.sort_values("Total", ascending=False).head(10)
                fig_cs = px.pie(
                    cost_sup, names="Supplier", values="Total",
                    title="Spend Share by Supplier (Top 10)", hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                fig_cs.update_layout(**DARK_THEME, height=300)
                st.plotly_chart(fig_cs, use_container_width=True)

            # Discount analysis
            if "Discount" in priced.columns and "StickerPriceCDN" in priced.columns:
                disc = priced.dropna(subset=["Discount","StickerPriceCDN"]).copy()
                disc = disc[disc["Discount"] > 0]
                if len(disc) > 0:
                    disc["DiscountPct"] = disc["Discount"] / disc["StickerPriceCDN"] * 100
                    fig_disc = px.scatter(
                        disc,
                        x="OrderDate", y="StickerPriceCDN", size="Discount",
                        color="DiscountPct",
                        color_continuous_scale=[[0, ICE_BLUE],[0.5, GOLD],[1, GREEN]],
                        hover_data=["Team","PlayerName","Supplier","DiscountReason"],
                        title="Discounts Over Time (bubble = $ saved, colour = % off)",
                        labels={"StickerPriceCDN":"Sticker Price (CDN $)","OrderDate":"Order Date","DiscountPct":"% Off"}
                    )
                    fig_disc.update_layout(**DARK_THEME, height=380)
                    st.plotly_chart(fig_disc, use_container_width=True)

                    avg_saving = disc["Discount"].mean()
                    total_saving = disc["Discount"].sum()
                    st.info(f"💸 You saved an avg of **${avg_saving:.0f} CAD** per discounted jersey — **${total_saving:,.0f} CAD total** across {len(disc)} discounted purchases.")

            # Price distribution scatter
            priced_label = priced.copy()
            priced_label["Label"] = priced_label.apply(
                lambda r: (r.get("PlayerName") or r.get("Team","?")) + f"\n{r.get('Brand','')} {r.get('Model','')}",
                axis=1
            )
            fig_scatter = px.scatter(
                priced_label.dropna(subset=["OrderDate"]),
                x="OrderDate", y="PriceF",
                color="League" if "League" in priced_label.columns else None,
                size="PriceF",
                hover_name="Label",
                hover_data=["Team","Brand","Model","Supplier"],
                title="Jersey Prices Over Time",
                labels={"PriceF":"Price (CAD $)","OrderDate":"Order Date"}
            )
            fig_scatter.update_layout(**DARK_THEME, height=380)
            st.plotly_chart(fig_scatter, use_container_width=True)


# ─────────────────────────────────────────────────────────
# DATA LOADING & ENRICHMENT
# ─────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────
# ENHANCED PREDICTION SCORING
# ─────────────────────────────────────────────────────────
def compute_enhanced_score(row) -> float:
    """
    NHL Prediction Score v3 — a composited heuristic across 5 dimensions.

    Max possible score: 1.00  (perfect in every dimension)
    Practical "good" score: ~0.65–0.80 (correct winner + close scores)

    Component breakdown (A+B+C+D = 1.00 on a perfect prediction):
    ┌──────────────────────────────────────────────────────┐
    │  A) Winner        — 0.55 pts  (base; most important) │
    │  B) Result type   — 0.10 pts  (REG / OT / SO match)  │
    │  C) Margin error  — 0.175 pts (spread closeness)     │
    │  D) Score error   — 0.175 pts (per-team goal delta)  │
    │  E) OT/SO credit  — ≤0.10 pts (wrong-winner bonus)   │
    └──────────────────────────────────────────────────────┘

    Design rationale vs the existing formulas:
    • GPS  gives 0.80 for correct winner — too binary; a 6-1 blowout
      and a 3-2 overtime thriller both score the same.
    • GPS2 adds OT partial credit but still ignores score quality.
    • v3 rewards *how* right you were: a correct winner AND a 1-goal
      margin error scores much higher than a correct winner with a
      6-goal margin error.  Incorrect predictions still earn partial
      credit when scores are close or OT was correctly anticipated.
    """
    try:
        correct_winner  = str(row.get("CorrectWinnerPrediction", "N")).strip().upper() in ("Y", "TRUE", "1")
        correct_away_sc = str(row.get("CorrectAwayScorePrediction", "N")).strip().upper() in ("Y", "TRUE", "1")
        correct_home_sc = str(row.get("CorrectHomeScorePrediction", "N")).strip().upper() in ("Y", "TRUE", "1")
        pred_result  = str(row.get("PredictedResult", "REG")).strip().upper()
        actual_result= str(row.get("ActualResult",   "REG")).strip().upper()

        pred_away  = float(row.get("PredictedAwayScore", 0) or 0)
        pred_home  = float(row.get("PredictedHomeScore", 0) or 0)
        act_away   = float(row.get("ActualAwayScore",   0) or 0)
        act_home   = float(row.get("ActualHomeScore",   0) or 0)

        # ── A) Winner (0.55) ─────────────────────────────────
        # Scaled to 0.55 so that components A+B+C+D sum to 1.00 on a perfect prediction.
        score_winner = 0.55 if correct_winner else 0.0

        # ── B) Result type (0.10) ─────────────────────────────
        # Exact match = 0.10.  OT/SO confusion (both extra time) = 0.06.
        # REG vs OT/SO or vice-versa = 0.
        if pred_result == actual_result:
            score_result = 0.10
        elif pred_result in ("OT", "SO") and actual_result in ("OT", "SO"):
            score_result = 0.06
        else:
            score_result = 0.0

        # ── C) Victory-margin error (0.175) ───────────────────
        # Margin = away_score − home_score.
        # Exponential decay: pts = 0.175 * exp(−|Δmargin| / 2)
        # Δmargin=0 → 0.175,  Δ=1 → 0.106,  Δ=2 → 0.064,  Δ=3 → 0.039
        pred_margin   = pred_away - pred_home
        actual_margin = act_away  - act_home
        delta_margin  = abs(pred_margin - actual_margin)
        score_margin  = 0.175 * np.exp(-delta_margin / 2.0)

        # ── D) Raw score error (0.175, split 0.0875 each side) ─
        # Exponential decay per team: pts = 0.0875 * exp(−|Δgoals| / 1.5)
        # Exact match → 0.0875,  off by 1 → 0.051,  off by 2 → 0.030
        away_goal_err = abs(pred_away - act_away)
        home_goal_err = abs(pred_home - act_home)
        score_goals = (
            0.0875 * np.exp(-away_goal_err / 1.5) +
            0.0875 * np.exp(-home_goal_err / 1.5)
        )

        # ── E) Near-miss OT/SO credit (up to 0.10) ────────────
        # Wrong winner BUT game went OT/SO AND prediction was OT/SO:
        # award up to 0.10 scaled by how close the final scores were.
        # (This component only fires on wrong-winner extra-time games,
        #  so A+B+C+D still sum to exactly 1.00 on a perfect prediction.)
        score_ot_credit = 0.0
        if not correct_winner and actual_result in ("OT", "SO") and pred_result in ("OT", "SO"):
            total_goal_err = away_goal_err + home_goal_err
            # Linear taper: 0 goal err → 0.10, ≥4 goal err → 0
            score_ot_credit = max(0.0, 0.10 * (1 - total_goal_err / 4.0))

        total = score_winner + score_result + score_margin + score_goals + score_ot_credit
        return round(min(total, 1.0), 4)

    except Exception:
        return 0.0


def apply_enhanced_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Add EnhancedScore column to completed games."""
    mask = df["GameIsOver"] == True
    df.loc[mask, "EnhancedScore"] = df[mask].apply(compute_enhanced_score, axis=1)
    return df


def peek_rows(filepath: str) -> int:
    """If copy file was made manually, need to skip 1 row. If it was done by the sidebar button, none need to be skipped."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Could not find '{filepath}'")
    n = 3
    ext = str(filepath).lower()
    if ext.endswith(".xlsx") or ext.endswith(".xls"):
        df = pd.read_excel(filepath, nrows=n)
    else:
        df = pd.read_csv(filepath, encoding="utf-8-sig", nrows=n)
    cols = df.columns.tolist()
    read = [cols] + [list(df.iloc[i].values) for i in range(n)]
    for i, row in enumerate(read):
        vals = "".join(map(str, [v for v in row if (not pd.isna(v)) and bool(v)])).strip()
        if vals:
            return i
    raise ValueError(f"peek_rows could not determine hoe many rows to skip in '{filepath}'")
    

@st.cache_data
def load_data(filepath: str) -> pd.DataFrame:
    ext = str(filepath).lower()
    if ext.endswith(".xlsx") or ext.endswith(".xls"):
        df = pd.read_excel(filepath, skiprows=peek_rows(filepath))
    else:
        df = pd.read_csv(filepath, encoding="utf-8-sig")
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
                lambda x: str(x).strip().upper().replace(".0", "") in ["Y", "YES", "1", "TRUE"]
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

    # Enhanced scoring
    df = apply_enhanced_scores(df)

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
def fetch_team_logo(team_abbr: str) -> str:
    """Get NHL team logo URL from NHL API."""
    team_id = TEAM_META.get(team_abbr, {}).get("id")
    if team_id:
        return f"https://assets.nhle.com/logos/nhl/svg/{team_abbr}_dark.svg"
    return ""


@st.cache_data(ttl=60)
def fetch_game_landing(g_id) -> dict:
    """Load NHL game landing for given game ID"""
    try:
        url = f"https://api-web.nhle.com/v1/gamecenter/{g_id}/landing"
        return requests.get(url).json()
    except Exception:
        return {}


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
# PREDICTION MODEL — enhanced with scores & result type
# ─────────────────────────────────────────────────────────
def build_predictions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Predict future games using team-specific stats from completed games.
    Outputs: winner, win probabilities, predicted scores, result type, confidence.

    Methodology:
      1. Win probability — blends each team's contextual win rates
         (home/away, last-5 form, B2B penalty, OT tendency).
      2. Predicted scores — team's avg goals scored/allowed in context,
         with a small regression to the NHL mean (~3.0 gpg).
      3. Predicted result — if |predicted_margin| < 0.60 predict OT/SO
         (closer to 0 → SO, 0.3-0.6 → OT), else REG.
    """
    completed = df[df["GameIsOver"] == True].copy()
    future    = df[df["GameIsOver"] == False].copy()

    if len(future) == 0:
        return pd.DataFrame()

    NHL_AVG_GPG   = 3.05   # league avg goals per team per game (~6.1 total)
    HOME_BOOST    = 0.04   # home-ice advantage
    REGRESSION_W  = 0.25   # weight toward league mean for small samples

    # ── team-level stats from completed games ────────────────────────────
    def weighted_mean(series, league_mean, n_min=10):
        """Shrink estimate toward league mean for small samples."""
        n = len(series)
        w = min(n / n_min, 1.0) * (1 - REGRESSION_W)
        return w * series.mean() + (1 - w) * league_mean

    # Goals scored / allowed, split by home vs away
    away_gf = completed.groupby("AwayTeam")["ActualAwayScore"].apply(
        lambda s: weighted_mean(s, NHL_AVG_GPG))
    away_ga = completed.groupby("AwayTeam")["ActualHomeScore"].apply(
        lambda s: weighted_mean(s, NHL_AVG_GPG))
    home_gf = completed.groupby("HomeTeam")["ActualHomeScore"].apply(
        lambda s: weighted_mean(s, NHL_AVG_GPG))
    home_ga = completed.groupby("HomeTeam")["ActualAwayScore"].apply(
        lambda s: weighted_mean(s, NHL_AVG_GPG))

    # Win rates
    away_wr = completed.groupby("AwayTeam")["AwayWon"].mean()
    home_wr = completed.groupby("HomeTeam")["HomeWon_"].mean()

    # OT/SO tendency per team
    ot_rate = {}
    for team in set(completed["AwayTeam"]) | set(completed["HomeTeam"]):
        tm = completed[(completed["AwayTeam"]==team) | (completed["HomeTeam"]==team)]
        ot_rate[team] = (tm["ActualResult"].isin(["OT","SO"])).mean() if len(tm) > 0 else 0.23

    # Last-5 form (win rate in last 5 games per team)
    def last5_wr(team):
        tm = completed[(completed["AwayTeam"]==team) | (completed["HomeTeam"]==team)]
        tm = tm.sort_values("GameDate").tail(5)
        if len(tm) == 0:
            return 0.5
        wins = ((tm["AwayTeam"]==team) & tm["AwayWon"] |
                (tm["HomeTeam"]==team) & tm["HomeWon_"])
        return wins.mean()

    last5 = {t: last5_wr(t) for t in set(completed["AwayTeam"]) | set(completed["HomeTeam"])}

    results = []
    for _, row in future.iterrows():
        away = row["AwayTeam"]
        home = row["HomeTeam"]

        # ── win probability ─────────────────────────────────────────────
        aw_wr   = away_wr.get(away, 0.45)
        hw_wr   = home_wr.get(home, 0.50)
        aw_l5   = last5.get(away, 0.5)
        hw_l5   = last5.get(home, 0.5)

        # Blend: 50% season rate, 30% contextual (home/away), 20% last-5 form
        away_prob_raw = 0.50 * aw_wr + 0.30 * (1 - hw_wr) + 0.20 * aw_l5
        home_prob_raw = 0.50 * hw_wr + HOME_BOOST + 0.30 * (1 - aw_wr) + 0.20 * hw_l5

        # Back-to-back penalty (if data available)
        if row.get("AwayB2B", False):
            away_prob_raw *= 0.93
        if row.get("HomeB2B", False):
            home_prob_raw *= 0.93

        # Normalise to sum to 1
        total_p = away_prob_raw + home_prob_raw
        away_prob = away_prob_raw / total_p
        home_prob = home_prob_raw / total_p
        away_prob = max(0.10, min(0.90, away_prob))
        home_prob = 1 - away_prob

        # ── score prediction ────────────────────────────────────────────
        # Predicted goals = avg of (attacker's GF) and (defender's GA)
        away_gf_est = away_gf.get(away, NHL_AVG_GPG)
        away_ga_est = away_ga.get(away, NHL_AVG_GPG)
        home_gf_est = home_gf.get(home, NHL_AVG_GPG)
        home_ga_est = home_ga.get(home, NHL_AVG_GPG)

        pred_away_raw = (away_gf_est + home_ga_est) / 2
        pred_home_raw = (home_gf_est + away_ga_est) / 2

        # Nudge scores toward the predicted winner slightly
        margin_factor = abs(away_prob - home_prob)
        if away_prob > home_prob:
            pred_away_raw += 0.3 * margin_factor * 5
        else:
            pred_home_raw += 0.3 * margin_factor * 5

        # Round to nearest integer (NHL scores are whole numbers)
        pred_away_score = max(0, round(pred_away_raw))
        pred_home_score = max(0, round(pred_home_raw))

        # Avoid ties in regulation; break with OT/SO logic below
        if pred_away_score == pred_home_score:
            if away_prob >= home_prob:
                pred_away_score += 1
            else:
                pred_home_score += 1

        # ── result type prediction ──────────────────────────────────────
        # Use combined OT/SO tendency & margin closeness
        margin     = abs(away_prob - home_prob)
        avg_ot     = (ot_rate.get(away, 0.23) + ot_rate.get(home, 0.23)) / 2
        ot_thresh  = avg_ot * 1.3   # boost threshold when teams are well-matched

        if margin < 0.06 and avg_ot >= 0.20:
            pred_result = "SO"
        elif margin < ot_thresh:
            pred_result = "OT"
        else:
            pred_result = "REG"

        # Reflect OT/SO in scores: tighten gap to 1 or 0
        if pred_result in ("OT", "SO"):
            diff = abs(pred_away_score - pred_home_score)
            if diff > 1:
                if pred_away_score > pred_home_score:
                    pred_away_score = pred_home_score + 1
                else:
                    pred_home_score = pred_away_score + 1

        predicted_winner = away if away_prob > home_prob else home
        confidence       = max(away_prob, home_prob)

        results.append({
            "GameDate":           row["GameDate"],
            "AwayTeam":           away,
            "HomeTeam":           home,
            "PredictedWinner":    predicted_winner,
            "PredictedAwayScore": int(pred_away_score),
            "PredictedHomeScore": int(pred_home_score),
            "PredictedResult":    pred_result,
            "AwayWinProb":        round(away_prob * 100, 1),
            "HomeWinProb":        round(home_prob * 100, 1),
            "Confidence":         round(confidence * 100, 1),
            "GameID":             row.get("GameID", ""),
        })

    return pd.DataFrame(results)


@st.cache_data()
def load_index_html() -> str:
    # index_html = ""
    # with open("index.html", "r", encoding="utf-8-sig") as f:
    #     index_html = "".join(f.read())
    # return index_html
    return Path("index.html").read_text(encoding="utf-8")


def load_jersey_workbook():
    # Load jersey workbook
    try:
        return load_jersey_data(path_excel_jerseys)
    except FileNotFoundError:
        st.error(f"❌ Jersey workbook not found:\n\n`{path_excel_jerseys}`\n\nCheck the path at the top of the script.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Could not load jersey workbook: {e}")
        return pd.DataFrame()


def verify_scores(df):
    """Slow process to check every game landing against every game prediction in the prediction file."""
    game_ids = df["GameID"].tolist()
    st.write(game_ids)
    to_reconcile = []
    for g_id in game_ids:
        results = fetch_game_landing(g_id)
        if results:
            # all_results.append(results)
            df_game = df.loc[df["GameID"] == g_id]
            if not df_game.empty:
                ser_game = df_game.reset_index().iloc[0]
                
                my_away_name = ser_game["AwayTeam"]
                my_home_name = ser_game["HomeTeam"]
                my_away_score = ser_game["ActualAwayScore"]
                my_home_score = ser_game["ActualHomeScore"]
                my_result = ser_game["ActualResult"]
                
                away = results.get("awayTeam", {})
                home = results.get("homeTeam", {})
                away_name = away.get("abbrev", "")
                home_name = home.get("abbrev", "")
                away_score = int(away.get("score", "0"))
                home_score = int(home.get("score", "0"))
                game_result = results.get("periodDescriptor", {}).get("periodType", "REG")
                
                if any([
                    my_away_name != away_name,
                    my_home_name != home_name,
                    my_away_score != away_score,
                    my_home_score != home_score,
                    my_result != game_result,
                ]):
                    to_reconcile.append(dict(
                        g_id=g_id, away=away_name, home=home_name,
                        my_away_score=my_away_score, my_home_score=my_home_score,
                        away_score=away_score, home_score=home_score,
                        my_result=my_result, game_result=game_result
                    ))
        
        # time.sleep(0.08)
        
    return to_reconcile
        

@st.cache_data
def load_stanley_cup_jsons():
    d_a = json.load(open(path_stanley_cup_appearances, "r"))
    d_w = json.load(open(path_stanley_cup_wins, "r"))
    d_l = json.load(open(path_stanley_cup_losses, "r"))
    datas = {
        "appearances": d_a,
        "wins": d_w,
        "losses": d_l
    }
    for k, data in datas.items():
        for k_ in ["colour", "border_colour", "font_colour", "font_back_colour"]:
            # st.write(f"{k=}, {k_=}")
            # st.write(data["ENTITIES"])
            for t, t_data in data["ENTITIES"].items():
                t_data[k_] = Colour(t_data[k_]).hex_code
    return datas


def img_to_uri(path, abbr, path_image_dir=path_image_dir):
    
    # logo = fetch_team_logo(abbr)
    logo = ""
    
    if not logo:    
        path = Path(os.path.join(path_image_dir, path))
        if not path.exists():
            return None
        ext = path.suffix.lower().replace(".", "")
        mime = "png" if ext == "png" else "jpeg"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f"data:image/{mime};base64,{b64}"
    else:
        return logo


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
        st.markdown("### 🗂️ Navigation")
        page = st.radio("", [
            "⚡ Scores",
            "📊 Overview & Accuracy",
            "👥 By Team",
            "🗓️ Trends Over Time",
            "🌍 Travel & Gauntlets",
            "🔮 Future Predictions",
            "🧥 Jersey Collection",
            "Stanley Cup",
            "Explore API",
        ], label_visibility="collapsed")
        st.markdown("---")
        st.caption(f"📂 `{path_excel_predictions.split(chr(92))[-1]}`")
        
        if st.button(
            "Update predictions copy"
        ):
            path_predictions_2526 = r"C:\Users\abrig\Documents\Coding_Practice\Python\Jerseys\NHLGamePredictions2526.xlsx"
            if os.path.exists(path_predictions_2526):
                try:
                    df_new = pd.read_excel(path_predictions_2526, skiprows=1)
                    df_new.to_excel(path_excel_predictions, index=False)
                    load_data.clear()
                except PermissionError:
                    print("Excel file is currently open.")

    # Load data
    try:
        df = load_data(path_excel_predictions)
    except FileNotFoundError:
        st.error(f"❌ Workbook not found:\n\n`{path_excel_predictions}`\n\nCheck the path at the top of the script.")
        return
    except Exception as e:
        st.error(f"❌ Could not load workbook: {e}")
        return

    completed = df[df["GameIsOver"] == True].copy()
    future    = df[df["GameIsOver"] == False].copy()

    total      = len(completed)
    n_correct  = completed["CorrectWinnerPrediction"].sum()
    accuracy   = n_correct / total * 100 if total > 0 else 0
    
    if page == "Explore API":
        
        df_jerseys = load_jersey_workbook()
        
        if not df_jerseys.empty:
            
            lst_player_ids = df_jerseys["NHLID"].dropna().unique().tolist()
            if 0 in lst_player_ids:
                lst_player_ids.remove(0)
            lst_player_ids.sort()
            
            # playerID = data["playerID"]
            # teamAbbr = data["teamAbbr"]
            # date = data["date"]
            # season = data["season"]
            # gameType = data["gameType"]
            # gameID = data["gameID"]
            # draftYear = data["draftYear"]
            
            k_selectbox_player_id = "key_selectbox_player_id"
            st.session_state.setdefault(k_selectbox_player_id, 8471675)  # Sidney Crosby
            selectbox_player_id = st.selectbox(
                label="Player ID",
                options=lst_player_ids,
                key=k_selectbox_player_id,
                help="PlayerIDs list is sourced from Jersey Collection spreadsheet"
            )
            
            k_datepicker_date = "key_datepicker_date"
            st.session_state.setdefault(k_datepicker_date, datetime.now().date())  # Today
            datepicker_date = st.date_input(
                label="Date",
                key=k_datepicker_date
            )
            
            start_year = 1900
            lst_seasons = [f"{start_year+i}{start_year+i+1}" for i in range(2026-start_year)]
            lst_seasons.sort(reverse=True)
            k_selectbox_season = "key_selectbox_season"
            st.session_state.setdefault(k_selectbox_season, lst_seasons[0])  # Current season
            selectbox_season = st.selectbox(
                label="Season",
                options=lst_seasons,
                key=k_selectbox_season,
                help="Season of play. Seasons start in the Fall and end in Spring / Summer, spanning ~250 days over 2 calendar years."
            )
            
            lst_team_abbrs = list(TEAM_META.keys())
            k_selectbox_team = "key_selectbox_team"
            st.session_state.setdefault(k_selectbox_team, "PIT")  # Sidney Crosby's team
            lst_team_abbrs.sort()
            selectbox_team = st.selectbox(
                label="Team",
                options=lst_team_abbrs,
                key=k_selectbox_team
            )
            
            params = {
                "playerID": selectbox_player_id,
                "date": datepicker_date,
                "season": selectbox_season,
                "teamAbbr": selectbox_team,
            }
            
            df_contents_og = api_ref.contents(**params)
            df_contents = df_contents_og.copy()
            df_contents[["url", "key_order"]] = df_contents.apply(
                lambda r:
                    pd.Series([
                        r["url"].format(**r["data"]),
                        [{v: k_ for k_, v in r["data"].items()}[k] for k in r["order"]]
                    ])
                , axis=1
            )
            df_contents.drop(columns=["order", "data"], inplace=True)
            
            lst_sections = df_contents["section"].dropna().unique().tolist()
            lst_sections.sort()
            k_multiselect_sections = "key_multiselect_sections"
            st.session_state.setdefault(k_multiselect_sections, lst_sections)  # All
            selectbox_player_id = st.multiselect(
                label="Sections:",
                options=lst_sections,
                key=k_multiselect_sections
            )
            
            df_contents = df_contents[df_contents["section"].isin(selectbox_player_id)]
            
            k_sel_url = "key_sel_url"
            stdf_contents = st.dataframe(
                df_contents,
                selection_mode="single-row",
                on_select="rerun"
            )
            
            if not stdf_contents:
                stdf_contents = st.session_state.get(k_sel_url)
            
            if stdf_contents:
                df_sel_contents: pd.DataFrame = df_contents.iloc[stdf_contents.get("selection", {}).get("rows", [])]
                if not df_sel_contents.empty:
                    ser_sel_contents = df_sel_contents.reset_index().iloc[0]
                    sel_url = ser_sel_contents["url"]
                    section = ser_sel_contents["section"]
                    description = ser_sel_contents["description"]
                    is_image = str(sel_url).lower().strip().endswith(".png")
                    st.session_state.update({k_sel_url: stdf_contents})
                    result = None
                    cont_info = st.container(horizontal=True)
                    cols_info = st.columns(2)
                    try:
                        if not is_image:
                            result = requests.get(sel_url)
                            if result.status_code == 200:
                                result = result.json()
                            else:
                                st.write(f":red[Invalid HTML status code] {result.status_code=}")
                        else:
                            result = None
                        with cont_info:
                            # st.write(ser_sel_contents["section"])
                            # st.write(ser_sel_contents["description"])
                            st.metric(
                                ser_sel_contents["section"],
                                ser_sel_contents["description"]
                            )
                            st.link_button(label=sel_url, url=sel_url)
                            with st.container():
                                st.write("raw")
                                st.code(sel_url)
                            
                            proxy_prefix = "https://corsproxy.io/?url="
                            replace_chars = {
                                ":": "%3A",
                                "/": "%2F",
                                "?": "%3F",
                                "=": "%3D",
                                ",": "%2C",
                                "&": "%26",
                            }
                            sel_url_cors = f"{sel_url}"
                            for c, v in replace_chars.items():
                                sel_url_cors = sel_url_cors.replace(c, v)
                            sel_url_cors = f"{proxy_prefix}{sel_url_cors}"
                            with st.container():
                                st.write(f"cors")
                                st.code(sel_url_cors)
                        if not is_image:
                            with cols_info[1]:
                                k_checkbox_expand_actual = "key_checkbox_expand_actual"
                                checkbox_expand_actual = st.checkbox(
                                    "expand?",
                                    key=k_checkbox_expand_actual,
                                    value=False
                                )
                                st.subheader(f"Actual ({len(str(result))} characters)")
                                st.json(result, expanded=checkbox_expand_actual)
                    except Exception as e:
                        st.error(e)
                        raise e
                    with cols_info[0]:
                        st.write(df_contents_og[(df_contents_og["section"] == section) & (df_contents_og["description"] == description)].iloc[0])
                        if is_image:
                            st.image(sel_url, caption=sel_url)
                        else:
                            if result:
                                k_checkbox_expand_sampled = "key_checkbox_expand_sampled"
                                checkbox_expand_sampled = st.checkbox(
                                    "expand?",
                                    key=k_checkbox_expand_sampled,
                                    value=False
                                )
                                peek_results = peek_json(result)
                                st.subheader(f"Sampled ({len(str(peek_results))} characters)")
                                st.json(peek_results, expanded=checkbox_expand_sampled)
            
    # ── PAGE: Stanley Cup ───────────────────────────────────
    elif page == "Stanley Cup":
        
        datas = load_stanley_cup_jsons()
        data_appearances = datas["appearances"].copy()
        data_wins = datas["wins"].copy()
        data_losses = datas["losses"].copy()
        
        entities = data_appearances.pop("ENTITIES", {})

        rows = []
        first_season = list(data_appearances)[0]
        teams = list(data_appearances[first_season])
        data_appearances[int(first_season) - 1] = {t: 0 for t in teams}
        data_wins[int(first_season) - 1] = {t: 0 for t in teams}
        data_losses[int(first_season) - 1] = {t: 0 for t in teams}
        
        for season, season_data_a in data_appearances.items():
            season_data_w = data_wins[season]
            season_data_l = data_losses[season]
            for team, total in season_data_a.items():
                season_data_w_t = season_data_w[team]
                season_data_l_t = season_data_l[team]
                rows.append({
                    "Season": int(season),
                    "Team": team,
                    "Appearances": total,
                    "Wins": season_data_w_t,
                    "Losses": season_data_l_t
                })

        df = pd.DataFrame(rows)
        df.sort_values(by=["Season", "Team"], inplace=True)

        # Optional historical name cleanup
        df["Team"] = df["Team"].replace({
            "Chicago Black Hawks": "Chicago Blackhawks",
            "Mighty Ducks of Anaheim": "Anaheim Ducks",
        })

        # User choice of metric to animate
        metric = st.radio(
            "Animate by:",
            ["Appearances", "Wins", "Losses"],
            horizontal=True,
            index=0
        )

        top_n = st.slider("Top teams to display", 5, 20, 12)

        # Build label text for bars
        df["BarText"] = df.apply(
            lambda r: f"{r[metric]}  (W:{r['Wins']} L:{r['Losses']})",
            axis=1
        )

        # Keep top N teams per season based on chosen metric
        df_plot = (
            df.sort_values(["Season", metric], ascending=[True, False])
            .groupby("Season", group_keys=False)
            .head(top_n)
            .copy()
        )

        color_map = {
            team: meta.get("colour", "#888888")
            for team, meta in entities.items()
            if isinstance(meta, dict)
        }

        title_map = {
            "Appearances": "Stanley Cup Final Appearances by Team Over Time",
            "Wins": "Stanley Cup Wins by Team Over Time",
            "Losses": "Stanley Cup Final Losses by Team Over Time"
        }

        fig = px.bar(
            df_plot,
            x=metric,
            y="Team",
            animation_frame="Season",
            orientation="h",
            color="Team",
            color_discrete_map=color_map,
            text="BarText",
            range_x=[0, df[metric].max() + 1],
            title=title_map[metric],
            hover_data={
                "Appearances": True,
                "Wins": True,
                "Losses": True,
                "BarText": False
            }
        )

        fig.update_layout(
            height=700,
            showlegend=False,
            yaxis=dict(categoryorder="total ascending")
        )

        fig.update_traces(
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Season: %{frame}<br>"
                f"{metric}: %{{x}}<br>"
                "Wins: %{customdata[1]}<br>"
                "Losses: %{customdata[2]}<extra></extra>"
            )
        )
        
        logo_uri_map = {
            team: img_to_uri(meta.get("image_path", ""), meta.get("abbr", ""))
            for team, meta in entities.items()
            if isinstance(meta, dict)
        }
        
        for frame in fig.frames:
            season = int(frame.name)
            frame_df = (
                df_plot[df_plot["Season"] == season]
                .sort_values(metric, ascending=False)
                .head(top_n)
                .copy()
            )

            images = []
            for _, row in frame_df.iterrows():
                team = row["Team"]
                logo_uri = logo_uri_map.get(team)

                if not logo_uri:
                    continue

                images.append(dict(
                    source=logo_uri,
                    xref="x",
                    yref="y",
                    x=row[metric],
                    y=team,
                    sizex=max(df[metric].max() * 0.03, 0.6),
                    sizey=0.8,
                    xanchor="left",
                    yanchor="middle",
                    sizing="contain",
                    layer="above",
                    opacity=1
                ))

            frame.layout = dict(images=images)
        
        initial_season = df_plot["Season"].min()
        initial_df = (
            df_plot[df_plot["Season"] == initial_season]
            .sort_values(metric, ascending=False)
            .head(top_n)
            .copy()
        )

        fig.update_layout(
            images=[
                dict(
                    source=logo_uri_map[row["Team"]],
                    xref="x",
                    yref="y",
                    x=row[metric],
                    y=row["Team"],
                    sizex=max(df[metric].max() * 0.03, 0.6),
                    sizey=0.8,
                    xanchor="left",
                    yanchor="middle",
                    sizing="contain",
                    layer="above",
                    opacity=1
                )
                for _, row in initial_df.iterrows()
                if logo_uri_map.get(row["Team"])
            ]
        )

        st.plotly_chart(fig, use_container_width=True)
    
    # ── PAGE: Scores ───────────────────────────────────
    elif page == "⚡ Scores":
        st.markdown('<div class="section-header">Scores</div>', unsafe_allow_html=True)
        # index_html = load_index_html()
        # st.code(index_html, language="html", line_numbers=True)
        # st.markdown(index_html, unsafe_allow_html=True)
        # st.html("index.html")
        index_html = load_index_html()
        components.html(
            index_html,
            height=2400,
            scrolling=True,
        )
        st.subheader(f"Coming soon")
        if st.button(
            "Verify My Records?"
        ):
            game_ids = completed["GameID"].tolist()
            st.write(game_ids)
            to_reconcile = verify_scores(completed)
            st.write(to_reconcile)

    # ── PAGE: OVERVIEW ───────────────────────────────────
    elif page == "📊 Overview & Accuracy":
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
            avg_score = completed["EnhancedScore"].mean() if "EnhancedScore" in completed.columns else completed["GamePredictionScore"].mean()
            st.metric("Avg Enhanced Score", f"{avg_score:.3f}" if not pd.isna(avg_score) else "N/A",
                      help="v3 heuristic: Winner(0.50) + ResultType(0.10) + MarginError(0.15) + ScoreError(0.15) + OT/SO credit(0.10)")

        # Score comparison section
        if "EnhancedScore" in completed.columns and "GamePredictionScore" in completed.columns:
            with st.expander("📐 Scoring System Comparison — GPS v1 vs v2 vs Enhanced v3", expanded=False):
                sc_cols = st.columns(3)
                gps1_avg = completed["GamePredictionScore"].mean()
                gps2_avg = completed["GamePredictionScore2"].mean() if "GamePredictionScore2" in completed.columns else None
                gps3_avg = completed["EnhancedScore"].mean()
                sc_cols[0].metric("GPS v1 Mean", f"{gps1_avg:.3f}", help="0.8×winner + 0.1×awayScore + 0.1×homeScore")
                if gps2_avg is not None:
                    sc_cols[1].metric("GPS v2 Mean", f"{gps2_avg:.3f}", help="v1 + OT/SO partial credit (0.85/0.95)")
                sc_cols[2].metric("Enhanced v3 Mean", f"{gps3_avg:.3f}", help="Winner(0.55) + ResultType(0.10) + MarginErr(0.175) + ScoreErr(0.175) + OT/SO bonus(≤0.10). Perfect = 1.00")

                score_compare_df = completed[["GameDate","AwayTeam","HomeTeam",
                    "CorrectWinnerPrediction","ActualResult","PredictedResult",
                    "GamePredictionScore","GamePredictionScore2","EnhancedScore"]].copy() \
                    if "GamePredictionScore2" in completed.columns \
                    else completed[["GameDate","AwayTeam","HomeTeam",
                    "CorrectWinnerPrediction","ActualResult","PredictedResult",
                    "GamePredictionScore","EnhancedScore"]].copy()
                score_compare_df["GameDate"] = score_compare_df["GameDate"].dt.strftime("%b %d")

                # Distribution comparison chart
                fig_sc = go.Figure()
                fig_sc.add_trace(go.Histogram(
                    x=completed["GamePredictionScore"], name="GPS v1",
                    opacity=0.65, marker_color=ICE_BLUE, nbinsx=20
                ))
                if "GamePredictionScore2" in completed.columns:
                    fig_sc.add_trace(go.Histogram(
                        x=completed["GamePredictionScore2"], name="GPS v2",
                        opacity=0.65, marker_color="#f39c12", nbinsx=20
                    ))
                fig_sc.add_trace(go.Histogram(
                    x=completed["EnhancedScore"], name="Enhanced v3",
                    opacity=0.65, marker_color=GREEN, nbinsx=20
                ))
                fig_sc.update_layout(
                    **DARK_THEME, barmode="overlay",
                    title="Score Distribution Comparison",
                    xaxis_title="Score (0–1.0)", yaxis_title="Games",
                    height=300,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02)
                )
                st.plotly_chart(fig_sc, use_container_width=True)
                st.dataframe(score_compare_df.sort_values("GameDate", ascending=False), use_container_width=True)

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
            fig, tbl = accuracy_bar(grouping_options[g1], g1, completed)
            st.plotly_chart(fig, use_container_width=True)
            with st.expander("View data table"):
                st.dataframe(tbl.sort_values("Accuracy", ascending=False), use_container_width=True)
        with col_g2:
            g2 = st.selectbox("Group by (Chart 2)", list(grouping_options.keys()), index=2)
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

        team_logo_url = fetch_team_logo(selected_team)
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
                    f'<img src="{fetch_team_logo(t)}" width="24" style="vertical-align:middle"> {t}'
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
        display_pred["Predicted Score"] = (
            display_pred["PredictedAwayScore"].astype(str) + " – " +
            display_pred["PredictedHomeScore"].astype(str)
        )
        display_pred["Win Probabilities"] = (
            display_pred["AwayTeam"] + ": " + display_pred["AwayWinProb"].astype(str) + "% | " +
            display_pred["HomeTeam"] + ": " + display_pred["HomeWinProb"].astype(str) + "%"
        )
        display_pred["Conf %"] = display_pred["Confidence"].astype(str) + "%"

        st.dataframe(
            display_pred[["GameDate", "Matchup", "PredictedWinner",
                          "Predicted Score", "PredictedResult",
                          "Win Probabilities", "Conf %"]],
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
                ["GameDate", "AwayTeam", "HomeTeam", "PredictedWinner",
                 "PredictedAwayScore", "PredictedHomeScore", "PredictedResult", "Confidence"]
            ].copy()
            top_conf["Predicted Score"] = (
                top_conf["PredictedAwayScore"].astype(str) + " – " +
                top_conf["PredictedHomeScore"].astype(str)
            )
            top_conf = top_conf.drop(columns=["PredictedAwayScore","PredictedHomeScore"])
            top_conf["GameDate"] = pd.to_datetime(top_conf["GameDate"]).dt.strftime("%b %d")
            top_conf["Confidence"] = top_conf["Confidence"].astype(str) + "%"
            st.dataframe(top_conf, use_container_width=True, hide_index=True)



    # ── PAGE: JERSEY COLLECTION ───────────────────────────
    elif page == "🧥 Jersey Collection":
        
        df_jerseys = load_jersey_workbook()
        if not df_jerseys.empty:        
            page_jersey_collection(df_jerseys, path_jersey_images)


if __name__ == "__main__":
    main()