
from __future__ import annotations

import html
import time
import textwrap
from typing import Any

import pandas as pd
import requests
import streamlit as st

LEAGUE_ID = "1382737164013436928"
MY_TEAM_NAME = "7 toes & the other cheek"
SLEEPER_BASE = "https://api.sleeper.app/v1"
FANTASYCALC_URL = (
    "https://api.fantasycalc.com/values/current"
    "?isDynasty=true&numQbs=1&numTeams=12&ppr=1"
)

st.set_page_config(
    page_title="Fantasy Football Front Office",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def render_html(markup: str) -> None:
    """Render generated HTML as one continuous block.

    Markdown interprets indented lines and blank-separated fragments as code
    blocks. Flattening the generated markup prevents player and summary cards
    from appearing as raw HTML.
    """
    flattened = "".join(
        line.strip()
        for line in textwrap.dedent(markup).splitlines()
        if line.strip()
    )
    st.markdown(flattened, unsafe_allow_html=True)


st.markdown(
    """
    <style>
    :root {
      --bg:#0a0d12;
      --sidebar:#10141b;
      --panel:#151a22;
      --panel2:#1b222d;
      --border:#283242;
      --text:#f8fafc;
      --muted:#98a2b3;
      --orange:#f59e0b;
      --qb:#19c7a3;
      --rb:#169bd5;
      --wr:#ff3d73;
      --te:#d837f2;
      --pick:#ffb000;
      --green:#22c55e;
      --red:#ef4444;
      --blue:#3b82f6;
    }

    .stApp { background:var(--bg); color:var(--text); }
    [data-testid="stSidebar"] {
      background:var(--sidebar);
      border-right:1px solid var(--border);
    }
    .block-container {
      max-width:1800px;
      padding-top:1rem;
      padding-bottom:2rem;
    }
    .brand {
      display:flex; align-items:center; gap:.85rem; margin-bottom:1rem;
    }
    .brand-badge {
      width:44px; height:44px; border-radius:12px;
      display:grid; place-items:center;
      background:linear-gradient(135deg,#f8fafc 0 34%,var(--orange) 34% 68%,#111827 68%);
      border:1px solid var(--border);
      font-weight:900; color:#111827;
    }
    .brand h1 { margin:0; font-size:1.65rem; }
    .brand p { margin:.15rem 0 0; color:var(--muted); font-size:.9rem; }

    .panel {
      background:var(--panel);
      border:1px solid var(--border);
      border-radius:18px;
      padding:1rem;
      margin-bottom:1rem;
    }
    .league-header {
      display:flex; align-items:center; gap:.8rem;
      background:var(--panel);
      border:1px solid var(--border);
      border-radius:16px;
      padding:.9rem 1rem;
      margin-bottom:1rem;
    }
    .league-avatar {
      width:36px; height:36px; border-radius:10px;
      display:grid; place-items:center; background:#1fc7b5; color:#082f2f; font-weight:900;
    }
    .league-title { font-weight:800; font-size:1.05rem; }
    .league-sub { color:var(--muted); font-size:.82rem; }
    .window {
      margin-left:auto;
      padding:.25rem .65rem;
      border-radius:999px;
      background:#2d2a16;
      color:#fde68a;
      font-size:.78rem;
      font-weight:800;
    }

    .summary-grid {
      display:grid;
      grid-template-columns:repeat(5,minmax(0,1fr));
      gap:.75rem;
      margin-bottom:1rem;
    }
    .summary-card {
      background:var(--panel);
      border:1px solid var(--border);
      border-radius:14px;
      padding:.9rem;
    }
    .summary-label { color:var(--muted); font-size:.78rem; }
    .summary-value { font-size:1.45rem; font-weight:900; margin-top:.2rem; }
    .summary-note { color:var(--muted); font-size:.75rem; margin-top:.15rem; }

    .roster-strip {
      display:flex;
      overflow-x:auto;
      gap:.65rem;
      padding:.15rem 0 .75rem;
      scrollbar-width:thin;
    }
    .player-card {
      min-width:126px;
      max-width:126px;
      background:var(--panel2);
      border:1px solid var(--border);
      border-radius:15px;
      overflow:hidden;
      position:relative;
    }
    .player-status {
      text-align:center;
      padding:.25rem;
      font-size:.7rem;
      font-weight:800;
      letter-spacing:.02em;
    }
    .starter { background:#0d2b17; color:#4ade80; }
    .bench { background:#2b2811; color:#fde047; }
    .ir { background:#321a1a; color:#fca5a5; }
    .taxi { background:#1d2637; color:#93c5fd; }
    .player-photo {
      height:105px;
      display:flex;
      align-items:flex-end;
      justify-content:center;
      background:linear-gradient(180deg,#202a39,#111827);
      overflow:hidden;
    }
    .player-photo img {
      width:100%;
      height:100%;
      object-fit:contain;
      object-position:center bottom;
    }
    .player-card-body { padding:.55rem; }
    .player-card-name {
      font-size:.82rem;
      font-weight:800;
      white-space:nowrap;
      overflow:hidden;
      text-overflow:ellipsis;
    }
    .player-card-meta {
      display:flex;
      justify-content:space-between;
      margin-top:.35rem;
      font-size:.72rem;
    }
    .pos-pill {
      padding:.15rem .35rem;
      border-radius:6px;
      color:#081018;
      font-weight:900;
    }
    .qb-bg{background:var(--qb)}
    .rb-bg{background:var(--rb)}
    .wr-bg{background:var(--wr)}
    .te-bg{background:var(--te)}
    .pick{background:var(--pick)}
    .idp-bg{background:#94a3b8}
    .rank-chip {
      background:#0b0f15;
      border:1px solid var(--border);
      border-radius:7px;
      padding:.12rem .3rem;
      color:#fff;
      font-weight:800;
    }

    .position-header {
      display:flex;
      justify-content:space-between;
      align-items:center;
      color:#081018;
      font-weight:900;
      padding:.55rem .7rem;
      border-radius:10px 10px 0 0;
    }
    .position-row {
      display:grid;
      grid-template-columns:32px 1fr auto auto;
      gap:.45rem;
      align-items:center;
      background:var(--panel2);
      border-left:1px solid var(--border);
      border-right:1px solid var(--border);
      border-bottom:1px solid var(--border);
      padding:.52rem .55rem;
      font-size:.79rem;
    }
    .position-row:last-child { border-radius:0 0 10px 10px; }
    .mini-photo {
      width:28px; height:28px; border-radius:50%;
      object-fit:cover; background:#111827;
    }
    .name-clip {
      white-space:nowrap;
      overflow:hidden;
      text-overflow:ellipsis;
    }
    .value { color:#d7dce3; font-variant-numeric:tabular-nums; }
    .small-rank {
      min-width:30px;
      text-align:center;
      border-radius:6px;
      padding:.18rem .3rem;
      background:#0c1118;
      font-weight:900;
    }

    .power-row {
      background:var(--panel);
      border:1px solid var(--border);
      border-radius:14px;
      padding:.8rem;
      margin-bottom:.65rem;
    }
    .power-top {
      display:grid;
      grid-template-columns:38px 170px 1fr auto;
      gap:.65rem;
      align-items:center;
    }
    .team-rank {
      width:34px; height:34px; border-radius:10px;
      display:grid; place-items:center; background:#0d1219;
      border:1px solid var(--border); font-weight:900;
    }
    .team-name { font-weight:800; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .power-bar {
      height:16px; border-radius:999px; overflow:hidden;
      display:flex; background:#0d1219;
      border:1px solid var(--border);
    }
    .seg-qb{background:var(--qb)}
    .seg-rb{background:var(--rb)}
    .seg-wr{background:var(--wr)}
    .seg-te{background:var(--te)}
    .seg-pick{background:var(--pick)}
    .status-tag {
      padding:.22rem .5rem;
      border-radius:999px;
      font-size:.72rem;
      font-weight:800;
      background:#1c2733;
      color:#bfdbfe;
    }
    .power-meta {
      margin-top:.5rem;
      color:var(--muted);
      font-size:.76rem;
      display:flex; gap:.8rem; flex-wrap:wrap;
    }

    .section-title {
      display:flex; align-items:center; justify-content:space-between;
      margin:.2rem 0 .7rem;
    }
    .section-title h3 { margin:0; }

    .gm-card {
      background:linear-gradient(135deg,rgba(245,158,11,.12),rgba(59,130,246,.08));
      border:1px solid var(--border);
      border-radius:16px;
      padding:1rem;
      margin-bottom:1rem;
    }

    [data-testid="stMetric"] {
      background:var(--panel);
      border:1px solid var(--border);
      border-radius:14px;
      padding:12px;
    }
    div[data-testid="stDataFrame"] {
      border:1px solid var(--border);
      border-radius:12px;
      overflow:hidden;
    }

    [data-testid="stExpander"] {
      background:var(--panel);
      border:1px solid var(--border);
      border-radius:14px;
      margin-bottom:.7rem;
      overflow:hidden;
    }
    [data-testid="stExpander"] details summary {
      padding:.82rem 1rem;
      font-weight:800;
      background:var(--panel);
    }
    [data-testid="stExpander"] details summary:hover {
      background:var(--panel2);
    }
    [data-testid="stExpander"] details[open] summary {
      border-bottom:1px solid var(--border);
    }

    .league-accordion { display:flex; flex-direction:column; gap:.8rem; }
    .franchise-details {
      background:transparent;
      border-bottom:1px solid rgba(255,255,255,.05);
      padding-bottom:.8rem;
    }
    .franchise-details > summary { list-style:none; cursor:pointer; display:block; }
    .franchise-details > summary::-webkit-details-marker { display:none; }
    .franchise-summary {
      display:grid;
      grid-template-columns:44px 190px 1fr auto;
      gap:.75rem;
      align-items:center;
      padding:.55rem .25rem;
    }
    .franchise-rank {
      width:36px; height:36px; display:grid; place-items:center;
      border-radius:10px; background:#11161e;
      border:1px solid var(--border); font-weight:900;
    }
    .franchise-name {
      font-weight:850; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    }
    .franchise-subline {
      display:flex; gap:.65rem; flex-wrap:wrap;
      color:var(--muted); font-size:.74rem;
      padding:.15rem 0 .45rem 3.8rem;
    }
    .franchise-status {
      border-radius:999px; padding:.24rem .55rem;
      background:#163125; color:#7ef0a6;
      font-size:.72rem; font-weight:800;
    }
    .franchise-details[open] .franchise-status {
      background:#2d2614; color:#fde68a;
    }
    .franchise-body { padding:.55rem 0 .2rem 3.8rem; }
    .roster-grid {
      display:grid;
      grid-template-columns:1fr 1fr 1.15fr 1fr 1.05fr;
      gap:.75rem;
      align-items:start;
    }
    .position-stack { min-width:0; }
    .position-title {
      display:flex; align-items:center; justify-content:space-between;
      padding:.58rem .68rem; border-radius:9px 9px 0 0;
      color:#071018; font-weight:900;
    }
    .asset-row {
      display:grid;
      grid-template-columns:28px minmax(0,1fr) auto auto;
      gap:.42rem; align-items:center;
      min-height:38px; padding:.36rem .45rem;
      background:#181d25; border-bottom:1px solid #252d39;
      font-size:.78rem;
    }
    .asset-row:last-child { border-radius:0 0 9px 9px; }
    .asset-row img {
      width:26px; height:26px; border-radius:50%;
      object-fit:cover; background:#111827;
    }
    .asset-name { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .asset-value { color:#c9d0da; }
    .asset-rank {
      min-width:28px; text-align:center;
      padding:.16rem .28rem; border-radius:6px;
      background:#0d1118; font-weight:850;
    }
    .team-gm-line {
      margin-top:.75rem; color:var(--muted); font-size:.78rem;
    }
    .power-segment {
      display:flex;
      align-items:center;
      justify-content:center;
      min-width:28px;
      color:#071018;
      font-size:.72rem;
      font-weight:950;
      text-shadow:0 1px 0 rgba(255,255,255,.18);
    }

    @media (max-width: 1100px) {
      .summary-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
      .power-top { grid-template-columns:34px 130px 1fr; }
      .status-tag { display:none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


class DataError(RuntimeError):
    pass


def get_json(url: str, timeout: int = 30) -> Any:
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Fantasy-Football-Front-Office/Milestone-2"},
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise DataError(f"Could not load {url}: {exc}") from exc
    except ValueError as exc:
        raise DataError(f"Invalid JSON returned by {url}.") from exc


@st.cache_data(ttl=900, show_spinner=False)
def load_sleeper_bundle(league_id: str) -> dict[str, Any]:
    return {
        "league": get_json(f"{SLEEPER_BASE}/league/{league_id}"),
        "users": get_json(f"{SLEEPER_BASE}/league/{league_id}/users"),
        "rosters": get_json(f"{SLEEPER_BASE}/league/{league_id}/rosters"),
        "traded_picks": get_json(f"{SLEEPER_BASE}/league/{league_id}/traded_picks"),
        "players": get_json(f"{SLEEPER_BASE}/players/nfl"),
    }


@st.cache_data(ttl=3600, show_spinner=False)
def load_fantasycalc() -> list[dict[str, Any]]:
    data = get_json(FANTASYCALC_URL)
    if not isinstance(data, list):
        raise DataError("FantasyCalc returned an unexpected response.")
    return data


def team_name(user: dict[str, Any]) -> str:
    metadata = user.get("metadata") or {}
    return (
        metadata.get("team_name")
        or user.get("display_name")
        or user.get("username")
        or "Unnamed Team"
    )


def normalise_fc(row: dict[str, Any]) -> dict[str, Any]:
    player = row.get("player") or {}
    sleeper_id = (
        player.get("sleeperId")
        or player.get("sleeper_id")
        or row.get("sleeperId")
        or row.get("sleeper_id")
        or ""
    )
    return {
        "sleeper_id": str(sleeper_id),
        "value": int(row.get("value") or 0),
        "rank": row.get("overallRank") or row.get("rank"),
        "position_rank": row.get("positionRank"),
        "trend": int(row.get("trend30Day") or row.get("trend30") or 0),
        "age": player.get("age") or row.get("age"),
    }


def player_image_url(player: dict[str, Any]) -> str:
    espn_id = player.get("espn_id")
    if espn_id:
        return f"https://a.espncdn.com/i/headshots/nfl/players/full/{espn_id}.png"
    sleeper_id = player.get("player_id")
    if sleeper_id:
        return f"https://sleepercdn.com/content/nfl/players/{sleeper_id}.jpg"
    return "https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png"


def build_players(bundle: dict[str, Any], fc_rows: list[dict[str, Any]]) -> pd.DataFrame:
    users = {str(u.get("user_id")): u for u in bundle["users"]}
    fc_by_id = {
        row["sleeper_id"]: row
        for row in (normalise_fc(x) for x in fc_rows)
        if row["sleeper_id"]
    }

    rows: list[dict[str, Any]] = []
    for roster in bundle["rosters"]:
        owner = users.get(str(roster.get("owner_id")), {})
        roster_team = team_name(owner)
        starters = {str(x) for x in roster.get("starters") or []}
        reserve = {str(x) for x in roster.get("reserve") or []}
        taxi = {str(x) for x in roster.get("taxi") or []}

        for raw_id in roster.get("players") or []:
            pid = str(raw_id)
            p = bundle["players"].get(pid, {}) or {}
            p["player_id"] = pid
            fc = fc_by_id.get(pid, {})
            name = (
                p.get("full_name")
                or " ".join(filter(None, [p.get("first_name"), p.get("last_name")]))
                or pid
            )
            status = "Starter" if pid in starters else "Bench"
            if pid in reserve:
                status = "IR"
            elif pid in taxi:
                status = "Taxi"

            rows.append(
                {
                    "Team": roster_team,
                    "Roster ID": int(roster["roster_id"]),
                    "Player": name,
                    "Position": p.get("position") or "NA",
                    "NFL Team": p.get("team") or "FA",
                    "Age": p.get("age") or fc.get("age"),
                    "Status": status,
                    "Value": int(fc.get("value") or 0),
                    "Overall Rank": fc.get("rank"),
                    "Position Rank": fc.get("position_rank"),
                    "Trend": fc.get("trend") or 0,
                    "Sleeper ID": pid,
                    "Image": player_image_url(p),
                }
            )
    return pd.DataFrame(rows)


def build_picks(bundle: dict[str, Any]) -> pd.DataFrame:
    league = bundle["league"]
    users = {str(u.get("user_id")): team_name(u) for u in bundle["users"]}
    roster_to_team = {
        int(r["roster_id"]): users.get(str(r.get("owner_id")), f"Roster {r['roster_id']}")
        for r in bundle["rosters"]
    }
    current_season = int(league.get("season") or 2026)
    rounds = int((league.get("settings") or {}).get("draft_rounds") or 3)

    traded_seasons = {
        int(pick.get("season"))
        for pick in bundle["traded_picks"]
        if str(pick.get("season", "")).isdigit()
    }
    # Always show the current three-year horizon, while also retaining any
    # additional seasons already represented in Sleeper traded-pick records.
    seasons = sorted(
        {current_season, current_season + 1, current_season + 2}
        | traded_seasons
    )

    ownership: dict[tuple[int, int, int], int] = {}
    for season in seasons:
        for original in roster_to_team:
            for rnd in range(1, rounds + 1):
                ownership[(season, rnd, original)] = original

    for pick in bundle["traded_picks"]:
        try:
            key = (int(pick["season"]), int(pick["round"]), int(pick["roster_id"]))
            if key in ownership:
                ownership[key] = int(pick["owner_id"])
        except (KeyError, TypeError, ValueError):
            continue

    year_factor = {current_season: 1.0, current_season + 1: 0.88, current_season + 2: 0.76}
    round_base = {1: 4300, 2: 1800, 3: 800, 4: 350, 5: 150}
    rows = []
    for (season, rnd, original), owner in ownership.items():
        rows.append(
            {
                "Season": season,
                "Round": rnd,
                "Original Team": roster_to_team.get(original, str(original)),
                "Current Owner": roster_to_team.get(owner, str(owner)),
                "Value": round(round_base.get(rnd, 75) * year_factor.get(season, .70)),
                "Traded": owner != original,
            }
        )
    return pd.DataFrame(rows)


def build_teams(players: pd.DataFrame, picks: pd.DataFrame) -> pd.DataFrame:
    pos = players.groupby(["Team", "Position"])["Value"].sum().unstack(fill_value=0)
    base = (
        players.groupby("Team", as_index=False)
        .agg(
            Player_Value=("Value", "sum"),
            Avg_Age=("Age", "mean"),
            Trend=("Trend", "sum"),
            Player_Count=("Player", "count"),
        )
    )
    pick_values = (
        picks.groupby("Current Owner", as_index=False)["Value"]
        .sum()
        .rename(columns={"Current Owner": "Team", "Value": "Pick_Value"})
    )
    base = base.merge(pick_values, on="Team", how="left")
    base["Pick_Value"] = base["Pick_Value"].fillna(0).astype(int)
    base["Total_Value"] = base["Player_Value"] + base["Pick_Value"]
    base["Avg_Age"] = base["Avg_Age"].round(1)

    for p in ["QB", "RB", "WR", "TE"]:
        if p not in pos.columns:
            pos[p] = 0
    base = base.merge(pos[["QB", "RB", "WR", "TE"]].reset_index(), on="Team", how="left")

    for p in ["QB", "RB", "WR", "TE"]:
        base[f"{p}_Rank"] = base[p].rank(ascending=False, method="min").astype(int)
    base["Pick_Rank"] = base["Pick_Value"].rank(ascending=False, method="min").astype(int)
    base["Overall_Rank"] = base["Total_Value"].rank(ascending=False, method="min").astype(int)

    med_age = base["Avg_Age"].median()
    hi = base["Player_Value"].quantile(.65)
    lo = base["Player_Value"].quantile(.35)
    pick_hi = base["Pick_Value"].quantile(.65)

    def classify(row: pd.Series) -> str:
        if row["Player_Value"] >= hi and row["Avg_Age"] <= med_age + .4:
            return "Contender"
        if row["Player_Value"] >= hi:
            return "Win-now"
        if row["Player_Value"] <= lo and row["Pick_Value"] >= pick_hi:
            return "Rebuilding"
        if row["Avg_Age"] < med_age and row["Pick_Value"] >= base["Pick_Value"].median():
            return "Ascending"
        return "Balanced"

    base["Window"] = base.apply(classify, axis=1)
    return base.sort_values(["Overall_Rank", "Team"])


def find_my_team(names: list[str]) -> str | None:
    exact = next((x for x in names if x.casefold() == MY_TEAM_NAME.casefold()), None)
    return exact or next((x for x in names if "7 toes" in x.casefold()), None)


def clean(value: Any) -> str:
    return html.escape(str(value))


def status_class(status: str) -> str:
    return status.lower().replace(" ", "-")


def pos_class(pos: str) -> str:
    pos = pos.upper()
    return {
        "QB": "qb-bg",
        "RB": "rb-bg",
        "WR": "wr-bg",
        "TE": "te-bg",
    }.get(pos, "idp-bg")


def render_brand(title: str, subtitle: str) -> None:
    render_html(
        f"""
        <div class="brand">
          <div class="brand-badge">FO</div>
          <div>
            <h1>{clean(title)}</h1>
            <p>{clean(subtitle)}</p>
          </div>
        </div>
        """
    )


def render_player_card(row: pd.Series) -> str:
    position_rank = "—" if pd.isna(row["Position Rank"]) else int(row["Position Rank"])
    return f"""
    <div class="player-card">
      <div class="player-status {status_class(row["Status"])}">{clean(row["Status"])}</div>
      <div class="player-photo">
        <img src="{clean(row["Image"])}"
             onerror="this.onerror=null;this.src='https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png';">
      </div>
      <div class="player-card-body">
        <div class="player-card-name">{clean(row["Player"])}</div>
        <div class="player-card-meta">
          <span class="pos-pill {pos_class(row["Position"])}">{clean(row["Position"])}</span>
          <span class="rank-chip">{position_rank}</span>
        </div>
      </div>
    </div>
    """


def render_position_column(roster: pd.DataFrame, pos: str, rank: int, color_class: str) -> None:
    render_html(
        f'<div class="position-header {color_class}"><span>{pos} Rank</span><span>{rank}</span></div>'
    )
    data = roster[roster["Position"] == pos].sort_values("Value", ascending=False).head(9)
    if data.empty:
        render_html(
            '<div class="position-row"><span></span><span>No players</span><span></span><span></span></div>'
        )
        return
    for _, row in data.iterrows():
        p_rank = "—" if pd.isna(row["Position Rank"]) else int(row["Position Rank"])
        render_html(
            f"""
            <div class="position-row">
              <img class="mini-photo" src="{clean(row["Image"])}"
                   onerror="this.onerror=null;this.src='https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png';">
              <span class="name-clip">{clean(row["Player"])}</span>
              <span class="value">{int(row["Value"])}</span>
              <span class="small-rank">{p_rank}</span>
            </div>
            """
        )


def render_pick_column(picks: pd.DataFrame, team: str, rank: int) -> None:
    render_html(
        f'<div class="position-header pick"><span>PICKS</span><span>{rank}</span></div>'
    )
    data = picks[picks["Current Owner"] == team].sort_values(
        ["Season", "Round", "Original Team"]
    )
    if data.empty:
        render_html(
            """
            <div class="position-row">
              <span style="font-size:1.15rem">📋</span>
              <span class="name-clip">No future picks found</span>
              <span class="value">—</span>
              <span class="small-rank">—</span>
            </div>
            """
        )
        return

    for _, row in data.head(12).iterrows():
        label = f'{int(row["Season"])} R{int(row["Round"])}'
        if row["Traded"]:
            label += f' ({str(row["Original Team"])[:12]})'
        render_html(
            f"""
            <div class="position-row">
              <span style="font-size:1.15rem">📋</span>
              <span class="name-clip">{clean(label)}</span>
              <span class="value">{int(row["Value"])}</span>
              <span class="small-rank">↔</span>
            </div>
            """
        )


def render_summary_cards(row: pd.Series) -> None:
    cards = [
        ("Overall Rank", f'#{int(row["Overall_Rank"])}', "League-wide franchise rank"),
        ("Player Value", f'{int(row["Player_Value"]):,}', "Current roster market value"),
        ("Pick Value", f'{int(row["Pick_Value"]):,}', "Future draft capital"),
        ("Average Age", f'{row["Avg_Age"]:.1f}', "Roster age profile"),
        ("30-Day Trend", f'{int(row["Trend"]):+d}', "Recent market movement"),
    ]
    html_cards = "".join(
        f"""
        <div class="summary-card">
          <div class="summary-label">{label}</div>
          <div class="summary-value">{value}</div>
          <div class="summary-note">{note}</div>
        </div>
        """
        for label, value, note in cards
    )
    render_html(f'<div class="summary-grid">{html_cards}</div>')


def render_team_review(teams: pd.DataFrame, players: pd.DataFrame, picks: pd.DataFrame, league_name: str) -> None:
    render_brand("My Team", "Front-office view of your roster and league position")
    my_team = find_my_team(teams["Team"].tolist()) or teams.iloc[0]["Team"]
    selected = st.selectbox("League / Team", teams["Team"].tolist(), index=teams["Team"].tolist().index(my_team))
    row = teams[teams["Team"] == selected].iloc[0]
    roster = players[players["Team"] == selected].sort_values(["Status", "Value"], ascending=[True, False])

    render_html(
        f"""
        <div class="league-header">
          <div class="league-avatar">WW</div>
          <div>
            <div class="league-title">{clean(league_name)}</div>
            <div class="league-sub">{clean(selected)}</div>
          </div>
          <div class="window">{clean(row["Window"])}</div>
        </div>
        """
    )

    render_summary_cards(row)

    render_html('<div class="section-title"><h3>Roster</h3><span style="color:#98a2b3">Scroll horizontally</span></div>')
    cards = "".join(render_player_card(r) for _, r in roster.head(18).iterrows())
    render_html(f'<div class="roster-strip">{cards}</div>')

    render_html('<div class="section-title"><h3>Roster Construction</h3></div>')
    cols = st.columns([1, 1, 1.2, 1, 1.1], gap="small")
    with cols[0]:
        render_position_column(roster, "QB", int(row["QB_Rank"]), "qb-bg")
    with cols[1]:
        render_position_column(roster, "RB", int(row["RB_Rank"]), "rb-bg")
    with cols[2]:
        render_position_column(roster, "WR", int(row["WR_Rank"]), "wr-bg")
    with cols[3]:
        render_position_column(roster, "TE", int(row["TE_Rank"]), "te-bg")
    with cols[4]:
        render_pick_column(picks, selected, int(row["Pick_Rank"]))

    pos_ranks = {
        "QB": int(row["QB_Rank"]),
        "RB": int(row["RB_Rank"]),
        "WR": int(row["WR_Rank"]),
        "TE": int(row["TE_Rank"]),
    }
    strongest = min(pos_ranks, key=pos_ranks.get)
    weakest = max(pos_ranks, key=pos_ranks.get)
    render_html(
        f"""
        <div class="gm-card">
          <b>GM Review:</b> {clean(selected)} currently profiles as <b>{clean(row["Window"])}</b>.
          The strongest room is <b>{strongest}</b> (#{pos_ranks[strongest]}), while the largest
          positional gap is <b>{weakest}</b> (#{pos_ranks[weakest]}). The franchise ranks
          <b>#{int(row["Overall_Rank"])}</b> overall when roster value and draft capital are combined.
        </div>
        """
    )



def render_power_rankings(
    teams: pd.DataFrame,
    players: pd.DataFrame,
    picks: pd.DataFrame,
) -> None:
    render_brand(
        "League",
        "League-wide power rankings with expandable franchise detail"
    )

    render_html(
        '''
        <div class="gm-card">
          <b>League view:</b> each franchise summary is the dropdown. Open as many
          teams as needed to compare positional rankings, roster construction and
          draft capital without leaving the page.
        </div>
        '''
    )

    def position_stack(team_roster: pd.DataFrame, pos: str, rank: int, css_class: str) -> str:
        rows = []
        data = (
            team_roster[team_roster["Position"] == pos]
            .sort_values("Value", ascending=False)
            .head(10)
        )
        if data.empty:
            rows.append(
                '<div class="asset-row"><span></span><span class="asset-name">No players</span>'
                '<span class="asset-value">—</span><span class="asset-rank">—</span></div>'
            )
        else:
            for _, player in data.iterrows():
                p_rank = "—" if pd.isna(player["Position Rank"]) else int(player["Position Rank"])
                rows.append(
                    f'''
                    <div class="asset-row">
                      <img src="{clean(player["Image"])}"
                           onerror="this.onerror=null;this.src='https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png';">
                      <span class="asset-name">{clean(player["Player"])}</span>
                      <span class="asset-value">{int(player["Value"])}</span>
                      <span class="asset-rank">{p_rank}</span>
                    </div>
                    '''
                )
        return (
            f'<div class="position-stack">'
            f'<div class="position-title {css_class}"><span>{pos} Rank</span><span>{rank}</span></div>'
            + "".join(rows)
            + "</div>"
        )

    def pick_stack(team: str, rank: int) -> str:
        rows = []
        data = picks[picks["Current Owner"] == team].sort_values(
            ["Season", "Round", "Original Team"]
        )
        if data.empty:
            rows.append(
                '<div class="asset-row"><span>📋</span><span class="asset-name">No future picks</span>'
                '<span class="asset-value">—</span><span class="asset-rank">—</span></div>'
            )
        else:
            for _, pick in data.head(12).iterrows():
                label = f'{int(pick["Season"])} R{int(pick["Round"])}'
                if pick["Traded"]:
                    label += f' ({str(pick["Original Team"])[:12]})'
                rows.append(
                    f'''
                    <div class="asset-row">
                      <span style="font-size:1rem">📋</span>
                      <span class="asset-name">{clean(label)}</span>
                      <span class="asset-value">{int(pick["Value"])}</span>
                      <span class="asset-rank">↔</span>
                    </div>
                    '''
                )
        return (
            '<div class="position-stack">'
            f'<div class="position-title pick"><span>PICKS</span><span>{rank}</span></div>'
            + "".join(rows)
            + "</div>"
        )

    cards = []
    my_team = find_my_team(teams["Team"].tolist())
    total_max = max(float(teams["Total_Value"].max()), 1)

    for _, row in teams.iterrows():
        team = row["Team"]
        roster = players[players["Team"] == team].copy()

        qb_w = max(3, row["QB"] / total_max * 100)
        rb_w = max(3, row["RB"] / total_max * 100)
        wr_w = max(3, row["WR"] / total_max * 100)
        te_w = max(3, row["TE"] / total_max * 100)
        pk_w = max(3, row["Pick_Value"] / total_max * 100)
        total = qb_w + rb_w + wr_w + te_w + pk_w

        pos_ranks = {
            "QB": int(row["QB_Rank"]),
            "RB": int(row["RB_Rank"]),
            "WR": int(row["WR_Rank"]),
            "TE": int(row["TE_Rank"]),
        }
        strongest = min(pos_ranks, key=pos_ranks.get)
        weakest = max(pos_ranks, key=pos_ranks.get)
        open_attr = " open" if team == my_team else ""

        cards.append(
            f'''
            <details class="franchise-details"{open_attr}>
              <summary>
                <div class="franchise-summary">
                  <div class="franchise-rank">{int(row["Overall_Rank"])}</div>
                  <div class="franchise-name">{clean(team)}</div>
                  <div class="power-bar">
                    <div class="seg-qb power-segment" style="width:{qb_w/total*100:.1f}%">{int(row["QB_Rank"])}</div>
                    <div class="seg-rb power-segment" style="width:{rb_w/total*100:.1f}%">{int(row["RB_Rank"])}</div>
                    <div class="seg-wr power-segment" style="width:{wr_w/total*100:.1f}%">{int(row["WR_Rank"])}</div>
                    <div class="seg-te power-segment" style="width:{te_w/total*100:.1f}%">{int(row["TE_Rank"])}</div>
                    <div class="seg-pick power-segment" style="width:{pk_w/total*100:.1f}%">{int(row["Pick_Rank"])}</div>
                  </div>
                  <div class="franchise-status">{clean(row["Window"])}</div>
                </div>
                <div class="franchise-subline">
                  <span>Total {int(row["Total_Value"]):,}</span>
                  <span>QB #{int(row["QB_Rank"])}</span>
                  <span>RB #{int(row["RB_Rank"])}</span>
                  <span>WR #{int(row["WR_Rank"])}</span>
                  <span>TE #{int(row["TE_Rank"])}</span>
                  <span>Picks #{int(row["Pick_Rank"])}</span>
                  <span>Age {row["Avg_Age"]:.1f}</span>
                </div>
              </summary>

              <div class="franchise-body">
                <div class="roster-grid">
                  {position_stack(roster, "QB", int(row["QB_Rank"]), "qb-bg")}
                  {position_stack(roster, "RB", int(row["RB_Rank"]), "rb-bg")}
                  {position_stack(roster, "WR", int(row["WR_Rank"]), "wr-bg")}
                  {position_stack(roster, "TE", int(row["TE_Rank"]), "te-bg")}
                  {pick_stack(team, int(row["Pick_Rank"]))}
                </div>
                <div class="team-gm-line">
                  <b>GM profile:</b> strongest room {strongest} (#{pos_ranks[strongest]});
                  largest weakness {weakest} (#{pos_ranks[weakest]});
                  draft capital rank #{int(row["Pick_Rank"])}.
                </div>
              </div>
            </details>
            '''
        )

    render_html('<div class="league-accordion">' + "".join(cards) + "</div>")

def render_rankings(players: pd.DataFrame) -> None:
    render_brand("Player Rankings", "Search and compare the live dynasty market")
    c1, c2 = st.columns([2, 1])
    with c1:
        query = st.text_input("Search for a player, franchise or NFL team")
    with c2:
        positions = st.multiselect("Position", sorted(players["Position"].dropna().unique()))

    view = players.copy()
    if query:
        q = query.casefold()
        view = view[
            view["Player"].str.casefold().str.contains(q, na=False)
            | view["Team"].str.casefold().str.contains(q, na=False)
            | view["NFL Team"].astype(str).str.casefold().str.contains(q, na=False)
        ]
    if positions:
        view = view[view["Position"].isin(positions)]

    st.dataframe(
        view.sort_values("Value", ascending=False)[
            ["Player", "Position", "NFL Team", "Team", "Age", "Value", "Overall Rank", "Position Rank", "Trend"]
        ],
        hide_index=True,
        use_container_width=True,
        height=760,
    )


def render_trade_calculator(players: pd.DataFrame, picks: pd.DataFrame, teams: pd.DataFrame) -> None:
    render_brand("Trade Centre", "Build and compare trade packages")
    st.caption("Rough-draft calculator using FantasyCalc player values and estimated draft-pick values.")

    player_options = {
        f'{row["Player"]} — {row["Team"]} ({int(row["Value"]):,})': int(row["Value"])
        for _, row in players.sort_values("Value", ascending=False).iterrows()
    }
    pick_options = {
        f'{int(row["Season"])} R{int(row["Round"])} — {row["Current Owner"]} ({int(row["Value"]):,})': int(row["Value"])
        for _, row in picks.iterrows()
    }
    all_options = {**player_options, **pick_options}

    left, right = st.columns(2, gap="large")
    with left:
        render_html("### They Receive")
        give = st.multiselect("Add assets", list(all_options.keys()), key="give")
        give_value = sum(all_options[x] for x in give)
        st.metric("Package Value", f"{give_value:,}")
    with right:
        render_html("### I Receive")
        receive = st.multiselect("Add assets", list(all_options.keys()), key="receive")
        receive_value = sum(all_options[x] for x in receive)
        st.metric("Package Value", f"{receive_value:,}")

    difference = receive_value - give_value
    if give or receive:
        if abs(difference) <= max(500, int((give_value + receive_value) * .05)):
            st.success(f"Approximately balanced. Difference: {difference:+,}")
        elif difference > 0:
            st.info(f"Your side receives about {difference:,} more value.")
        else:
            st.warning(f"Your side gives about {abs(difference):,} more value.")


def render_draft(picks: pd.DataFrame, teams: pd.DataFrame) -> None:
    render_brand("Draft Capital", "Review future pick ownership across the league")
    owner = st.selectbox("Current owner", ["All teams"] + teams["Team"].tolist())
    view = picks.copy()
    if owner != "All teams":
        view = view[view["Current Owner"] == owner]

    summary = (
        view.groupby("Current Owner", as_index=False)
        .agg(
            Total_Picks=("Round", "count"),
            Firsts=("Round", lambda x: int((x == 1).sum())),
            Seconds=("Round", lambda x: int((x == 2).sum())),
            Thirds=("Round", lambda x: int((x == 3).sum())),
            Estimated_Value=("Value", "sum"),
        )
        .sort_values("Estimated_Value", ascending=False)
    )
    st.dataframe(summary, hide_index=True, use_container_width=True)
    st.dataframe(
        view.sort_values(["Season", "Round", "Current Owner", "Original Team"]),
        hide_index=True,
        use_container_width=True,
    )


def main() -> None:
    st.sidebar.markdown("## 🏈 Front Office")
    page = st.sidebar.radio(
        "Navigation",
        ["My Team", "League", "Rankings", "Trade Centre", "Draft Capital"],
        label_visibility="collapsed",
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Weekend Warriors")
    st.sidebar.caption(MY_TEAM_NAME)
    if st.sidebar.button("Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    try:
        with st.spinner("Loading Sleeper and FantasyCalc data..."):
            bundle = load_sleeper_bundle(LEAGUE_ID)
            fc_rows = load_fantasycalc()
            players = build_players(bundle, fc_rows)
            picks = build_picks(bundle)
            teams = build_teams(players, picks)
    except Exception as exc:
        st.error("The live application could not load.")
        st.exception(exc)
        st.stop()

    if page == "My Team":
        render_team_review(teams, players, picks, bundle["league"].get("name", "Weekend Warriors"))
    elif page == "League":
        render_power_rankings(teams, players, picks)
    elif page == "Rankings":
        render_rankings(players)
    elif page == "Trade Centre":
        render_trade_calculator(players, picks, teams)
    else:
        render_draft(picks, teams)


if __name__ == "__main__":
    main()
