
from __future__ import annotations

import time
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

st.markdown(
    """
    <style>
    :root {
        --bg: #0f0f12;
        --panel: #17171c;
        --panel-2: #1d1d23;
        --border: #2b2b34;
        --muted: #9c9ca7;
        --text: #f4f4f5;
        --orange: #ff9f1c;
        --qb: #1fd1b0;
        --rb: #1aa7ec;
        --wr: #ff3b77;
        --te: #cf3cff;
        --pick: #ffb000;
    }

    .stApp { background: var(--bg); color: var(--text); }
    .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1800px; }
    [data-testid="stSidebar"] { background: #141419; border-right: 1px solid var(--border); }
    [data-testid="stSidebar"] .block-container { padding-top: 1rem; }

    .topbar {
        display:flex; align-items:center; justify-content:space-between;
        margin-bottom: 1rem;
    }
    .brand {
        display:flex; align-items:center; gap:.8rem;
    }
    .brand-mark {
        width:42px; height:42px; border-radius:10px;
        background:linear-gradient(135deg,#fff 0 35%,#ff9f1c 35% 65%,#111 65%);
        border:1px solid var(--border);
    }
    .brand h1 { margin:0; font-size:1.75rem; }
    .brand p { margin:.1rem 0 0; color:var(--muted); }

    .panel {
        background:var(--panel); border:1px solid var(--border);
        border-radius:16px; padding:1rem; margin-bottom:1rem;
    }
    .metric-card {
        background:var(--panel); border:1px solid var(--border);
        border-radius:14px; padding:1rem;
    }
    .metric-label { color:var(--muted); font-size:.82rem; }
    .metric-value { font-size:1.65rem; font-weight:800; margin-top:.25rem; }
    .metric-sub { font-size:.8rem; color:var(--muted); margin-top:.2rem; }

    .position-header {
        display:flex; align-items:center; justify-content:space-between;
        padding:.65rem .75rem; border-radius:10px 10px 0 0;
        font-weight:800; color:#0b0b0e;
    }
    .qb { background:var(--qb); }
    .rb { background:var(--rb); }
    .wr { background:var(--wr); }
    .te { background:var(--te); }
    .pick { background:var(--pick); }

    .player-row, .pick-row {
        display:grid; grid-template-columns: 1fr auto auto;
        gap:.5rem; align-items:center;
        padding:.58rem .7rem;
        border-left:1px solid var(--border);
        border-right:1px solid var(--border);
        border-bottom:1px solid var(--border);
        background:var(--panel-2);
        font-size:.9rem;
    }
    .player-row:last-child, .pick-row:last-child { border-radius:0 0 10px 10px; }
    .player-name { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .rank-box {
        min-width:34px; text-align:center; padding:.2rem .35rem;
        border-radius:7px; background:#0e0e12; color:#f5f5f5; font-weight:700;
    }
    .value-box { color:#d5d5dc; font-variant-numeric:tabular-nums; }

    .league-strip {
        display:flex; align-items:center; gap:.65rem;
        padding:.75rem 1rem; background:var(--panel);
        border:1px solid var(--border); border-radius:14px; margin-bottom:1rem;
    }
    .league-dot { width:12px; height:12px; border-radius:50%; background:#4be0d0; }
    .window-tag {
        margin-left:auto; background:#2b2b21; color:#e6d75f;
        padding:.2rem .55rem; border-radius:999px; font-size:.76rem; font-weight:700;
    }

    .pill {
        display:inline-block; border:1px solid var(--border); background:var(--panel-2);
        padding:.35rem .7rem; border-radius:999px; margin-right:.35rem; color:#d7d7dd;
        font-size:.82rem;
    }

    [data-testid="stMetric"] {
        background:var(--panel); border:1px solid var(--border);
        border-radius:14px; padding:12px;
    }

    div[data-testid="stDataFrame"] {
        border:1px solid var(--border); border-radius:12px; overflow:hidden;
    }

    .gm-note {
        padding:1rem; border-radius:14px; border:1px solid var(--border);
        background:linear-gradient(135deg,rgba(255,159,28,.12),rgba(78,205,196,.08));
    }

    .small-muted { color:var(--muted); font-size:.82rem; }
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
            headers={"User-Agent": "Fantasy-Football-Front-Office/0.3"},
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
        raise DataError("FantasyCalc returned an unexpected response shape.")
    return data


def owner_name(user: dict[str, Any]) -> str:
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
        "name": player.get("name") or row.get("name") or "Unknown",
        "value": int(row.get("value") or 0),
        "rank": row.get("overallRank") or row.get("rank"),
        "position_rank": row.get("positionRank"),
        "trend": row.get("trend30Day") or row.get("trend30") or 0,
        "age": player.get("age") or row.get("age"),
    }


def build_player_table(bundle: dict[str, Any], fc_rows: list[dict[str, Any]]) -> pd.DataFrame:
    users = {str(u.get("user_id")): u for u in bundle["users"]}
    fc_by_id = {
        row["sleeper_id"]: row
        for row in (normalise_fc(x) for x in fc_rows)
        if row["sleeper_id"]
    }

    records: list[dict[str, Any]] = []
    for roster in bundle["rosters"]:
        user = users.get(str(roster.get("owner_id")), {})
        team = owner_name(user)
        starters = {str(x) for x in (roster.get("starters") or [])}
        reserve = {str(x) for x in (roster.get("reserve") or [])}
        taxi = {str(x) for x in (roster.get("taxi") or [])}

        for raw_id in roster.get("players") or []:
            pid = str(raw_id)
            sleeper_player = bundle["players"].get(pid, {}) or {}
            fc = fc_by_id.get(pid, {})
            name = (
                sleeper_player.get("full_name")
                or " ".join(filter(None, [sleeper_player.get("first_name"), sleeper_player.get("last_name")]))
                or fc.get("name")
                or pid
            )
            status = "Starter" if pid in starters else "Bench"
            if pid in reserve:
                status = "IR"
            elif pid in taxi:
                status = "Taxi"

            records.append(
                {
                    "Team": team,
                    "Roster ID": int(roster["roster_id"]),
                    "Player": name,
                    "Position": sleeper_player.get("position") or "NA",
                    "NFL Team": sleeper_player.get("team") or "FA",
                    "Age": sleeper_player.get("age") or fc.get("age"),
                    "Status": status,
                    "FantasyCalc Value": int(fc.get("value") or 0),
                    "Overall Rank": fc.get("rank"),
                    "Position Rank": fc.get("position_rank"),
                    "30-Day Trend": int(fc.get("trend") or 0),
                    "Sleeper ID": pid,
                }
            )
    return pd.DataFrame(records)


def build_pick_inventory(bundle: dict[str, Any]) -> pd.DataFrame:
    league = bundle["league"]
    users = {str(u.get("user_id")): owner_name(u) for u in bundle["users"]}
    roster_to_team = {
        int(r["roster_id"]): users.get(str(r.get("owner_id")), f"Roster {r['roster_id']}")
        for r in bundle["rosters"]
    }

    current_season = int(league.get("season") or 2026)
    rounds = int((league.get("settings") or {}).get("draft_rounds") or 3)
    seasons = [current_season, current_season + 1, current_season + 2]
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

    year_factor = {current_season: 1.00, current_season + 1: 0.88, current_season + 2: 0.76}
    round_base = {1: 4300, 2: 1800, 3: 800, 4: 350, 5: 150}
    rows = []
    for (season, rnd, original), current_owner in ownership.items():
        rows.append(
            {
                "Season": season,
                "Round": rnd,
                "Original Team": roster_to_team.get(original, str(original)),
                "Current Owner": roster_to_team.get(current_owner, str(current_owner)),
                "Estimated Value": round(round_base.get(rnd, 75) * year_factor.get(season, .70)),
                "Traded": current_owner != original,
            }
        )
    return pd.DataFrame(rows)


def build_team_table(players: pd.DataFrame, picks: pd.DataFrame) -> pd.DataFrame:
    position_values = players.groupby(["Team", "Position"])["FantasyCalc Value"].sum().unstack(fill_value=0)
    team_df = (
        players.groupby("Team", as_index=False)
        .agg(
            Player_Value=("FantasyCalc Value", "sum"),
            Avg_Age=("Age", "mean"),
            Trend_30d=("30-Day Trend", "sum"),
            Player_Count=("Player", "count"),
        )
    )
    pick_values = (
        picks.groupby("Current Owner", as_index=False)["Estimated Value"]
        .sum()
        .rename(columns={"Current Owner": "Team", "Estimated Value": "Pick_Value"})
    )
    team_df = team_df.merge(pick_values, on="Team", how="left")
    team_df["Pick_Value"] = team_df["Pick_Value"].fillna(0).astype(int)
    team_df["Total_Value"] = team_df["Player_Value"] + team_df["Pick_Value"]
    team_df["Avg_Age"] = team_df["Avg_Age"].round(1)

    for pos in ["QB", "RB", "WR", "TE"]:
        if pos not in position_values.columns:
            position_values[pos] = 0
    team_df = team_df.merge(position_values[["QB", "RB", "WR", "TE"]].reset_index(), on="Team", how="left")

    for pos in ["QB", "RB", "WR", "TE"]:
        team_df[f"{pos}_Rank"] = team_df[pos].rank(ascending=False, method="min").astype(int)

    team_df["Overall_Rank"] = team_df["Total_Value"].rank(ascending=False, method="min").astype(int)
    team_df["Player_Rank"] = team_df["Player_Value"].rank(ascending=False, method="min").astype(int)
    team_df["Pick_Rank"] = team_df["Pick_Value"].rank(ascending=False, method="min").astype(int)

    median_age = team_df["Avg_Age"].median()
    hi = team_df["Player_Value"].quantile(.65)
    lo = team_df["Player_Value"].quantile(.35)
    pick_hi = team_df["Pick_Value"].quantile(.65)

    def window(row: pd.Series) -> str:
        if row["Player_Value"] >= hi and row["Avg_Age"] <= median_age + .4:
            return "Contender"
        if row["Player_Value"] >= hi:
            return "Win-now"
        if row["Player_Value"] <= lo and row["Pick_Value"] >= pick_hi:
            return "Rebuilding"
        if row["Avg_Age"] < median_age and row["Pick_Value"] >= team_df["Pick_Value"].median():
            return "Ascending"
        return "Balanced"

    team_df["Window"] = team_df.apply(window, axis=1)
    return team_df.sort_values(["Overall_Rank", "Team"])


def find_my_team(names: list[str]) -> str | None:
    exact = next((x for x in names if x.casefold() == MY_TEAM_NAME.casefold()), None)
    return exact or next((x for x in names if "7 toes" in x.casefold()), None)


def fmt(value: float | int) -> str:
    return f"{int(value):,}"


def percentile_rank(team_df: pd.DataFrame, team: str, column: str) -> int:
    value = float(team_df.loc[team_df["Team"] == team, column].iloc[0])
    return int(round((team_df[column] <= value).mean() * 100))


def render_brand() -> None:
    st.markdown(
        """
        <div class="topbar">
            <div class="brand">
                <div class="brand-mark"></div>
                <div>
                    <h1>Front Office</h1>
                    <p>League portfolio and GM intelligence</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_player_column(roster: pd.DataFrame, pos: str, css_class: str, team_rank: int) -> None:
    data = roster[roster["Position"] == pos].sort_values("FantasyCalc Value", ascending=False).head(8)
    st.markdown(
        f'<div class="position-header {css_class}"><span>{pos} Rank</span><span>{team_rank}</span></div>',
        unsafe_allow_html=True,
    )
    if data.empty:
        st.markdown('<div class="player-row"><span class="player-name">No players</span><span></span><span></span></div>', unsafe_allow_html=True)
        return
    for _, row in data.iterrows():
        p_rank = row["Position Rank"]
        p_rank_text = "—" if pd.isna(p_rank) else str(int(p_rank))
        st.markdown(
            f"""
            <div class="player-row">
                <span class="player-name">{row["Player"]}</span>
                <span class="value-box">{int(row["FantasyCalc Value"])}</span>
                <span class="rank-box">{p_rank_text}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_pick_column(picks: pd.DataFrame, team: str, pick_rank: int) -> None:
    data = picks[picks["Current Owner"] == team].sort_values(["Season", "Round"]).head(9)
    st.markdown(
        f'<div class="position-header pick"><span>PICKS</span><span>{pick_rank}</span></div>',
        unsafe_allow_html=True,
    )
    for _, row in data.iterrows():
        label = f'{int(row["Season"])} R{int(row["Round"])}'
        if row["Traded"]:
            label += f' ({row["Original Team"][:10]})'
        st.markdown(
            f"""
            <div class="pick-row">
                <span class="player-name">{label}</span>
                <span class="value-box">{int(row["Estimated Value"])}</span>
                <span class="rank-box">↔</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_portfolio(team_df: pd.DataFrame, players: pd.DataFrame, picks: pd.DataFrame, league_name: str) -> None:
    render_brand()
    my_team = find_my_team(team_df["Team"].tolist()) or team_df.iloc[0]["Team"]
    row = team_df[team_df["Team"] == my_team].iloc[0]
    roster = players[players["Team"] == my_team].copy()

    st.markdown(
        f"""
        <div class="league-strip">
            <div class="league-dot"></div>
            <strong>{league_name}</strong>
            <span class="small-muted">View League →</span>
            <span class="window-tag">{row["Window"]}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([2.8, 1.15], gap="large")
    with left:
        cols = st.columns([1, 1, 1.25, 1, 1.1], gap="small")
        with cols[0]:
            render_player_column(roster, "QB", "qb", int(row["QB_Rank"]))
        with cols[1]:
            render_player_column(roster, "RB", "rb", int(row["RB_Rank"]))
        with cols[2]:
            render_player_column(roster, "WR", "wr", int(row["WR_Rank"]))
        with cols[3]:
            render_player_column(roster, "TE", "te", int(row["TE_Rank"]))
        with cols[4]:
            render_pick_column(picks, my_team, int(row["Pick_Rank"]))

        st.markdown("### GM Summary")
        pos_ranks = {
            "QB": int(row["QB_Rank"]),
            "RB": int(row["RB_Rank"]),
            "WR": int(row["WR_Rank"]),
            "TE": int(row["TE_Rank"]),
        }
        strongest = min(pos_ranks, key=pos_ranks.get)
        weakest = max(pos_ranks, key=pos_ranks.get)
        st.markdown(
            f"""
            <div class="gm-note">
                <b>{my_team}</b> profiles as <b>{row["Window"]}</b>.
                The strongest room is <b>{strongest}</b> (#{pos_ranks[strongest]}),
                while the clearest need is <b>{weakest}</b> (#{pos_ranks[weakest]}).
                Overall franchise value ranks <b>#{int(row["Overall_Rank"])}</b> in the league.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        avg_pct = round(
            sum(percentile_rank(team_df, my_team, c) for c in ["QB", "RB", "WR", "TE", "Pick_Value"]) / 5
        )
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Avg. percentile</div>
                <div class="metric-value">Top {100-avg_pct}%</div>
                <div class="metric-sub">{row["Window"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Positional percentiles")
        chart = pd.DataFrame(
            {
                "Category": ["QB", "RB", "WR", "TE", "Picks"],
                "Percentile": [
                    percentile_rank(team_df, my_team, "QB"),
                    percentile_rank(team_df, my_team, "RB"),
                    percentile_rank(team_df, my_team, "WR"),
                    percentile_rank(team_df, my_team, "TE"),
                    percentile_rank(team_df, my_team, "Pick_Value"),
                ],
            }
        ).set_index("Category")
        st.bar_chart(chart)

        st.markdown("### Portfolio exposure")
        top = roster.sort_values("FantasyCalc Value", ascending=False).head(12)
        st.dataframe(
            top[["Player", "Position", "FantasyCalc Value"]],
            hide_index=True,
            use_container_width=True,
        )


def render_league(team_df: pd.DataFrame) -> None:
    render_brand()
    st.subheader("League Power Board")
    show = team_df.rename(
        columns={
            "Overall_Rank": "Rank",
            "Total_Value": "Total",
            "Player_Value": "Players",
            "Pick_Value": "Picks",
            "Avg_Age": "Avg Age",
        }
    )
    st.dataframe(
        show[["Rank", "Team", "Window", "Total", "Players", "Picks", "Avg Age", "QB_Rank", "RB_Rank", "WR_Rank", "TE_Rank"]],
        hide_index=True,
        use_container_width=True,
    )


def render_franchise_review(team_df: pd.DataFrame, players: pd.DataFrame, picks: pd.DataFrame) -> None:
    render_brand()
    team = st.selectbox("Franchise", team_df["Team"].tolist())
    row = team_df[team_df["Team"] == team].iloc[0]
    roster = players[players["Team"] == team].copy()

    st.markdown(f"## {team}")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Overall rank", f'#{int(row["Overall_Rank"])}')
    c2.metric("Player value", fmt(row["Player_Value"]))
    c3.metric("Pick value", fmt(row["Pick_Value"]))
    c4.metric("Average age", f'{row["Avg_Age"]:.1f}')
    c5.metric("Window", row["Window"])

    cols = st.columns([1, 1, 1.25, 1, 1.1], gap="small")
    with cols[0]: render_player_column(roster, "QB", "qb", int(row["QB_Rank"]))
    with cols[1]: render_player_column(roster, "RB", "rb", int(row["RB_Rank"]))
    with cols[2]: render_player_column(roster, "WR", "wr", int(row["WR_Rank"]))
    with cols[3]: render_player_column(roster, "TE", "te", int(row["TE_Rank"]))
    with cols[4]: render_pick_column(picks, team, int(row["Pick_Rank"]))


def render_trade_lab(team_df: pd.DataFrame, players: pd.DataFrame) -> None:
    render_brand()
    st.subheader("Trade Lab")
    my_team = find_my_team(team_df["Team"].tolist())
    my_row = team_df[team_df["Team"] == my_team].iloc[0]

    ranks = {"QB": my_row["QB_Rank"], "RB": my_row["RB_Rank"], "WR": my_row["WR_Rank"], "TE": my_row["TE_Rank"]}
    needs = sorted(ranks, key=ranks.get, reverse=True)[:2]
    strengths = sorted(ranks, key=ranks.get)[:2]

    targets = players[
        (players["Team"] != my_team)
        & (players["Position"].isin(needs))
        & (players["FantasyCalc Value"] >= 2500)
    ].sort_values(["FantasyCalc Value", "30-Day Trend"], ascending=[False, False])

    st.markdown(
        f'<span class="pill">Needs: {" / ".join(needs)}</span>'
        f'<span class="pill">Strengths: {" / ".join(strengths)}</span>',
        unsafe_allow_html=True,
    )
    st.dataframe(
        targets[["Player", "Position", "Team", "Age", "FantasyCalc Value", "30-Day Trend"]].head(30),
        hide_index=True,
        use_container_width=True,
    )


def render_draft(picks: pd.DataFrame, team_df: pd.DataFrame) -> None:
    render_brand()
    st.subheader("Draft Capital")
    owner = st.selectbox("Current owner", ["All teams"] + team_df["Team"].tolist())
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
            Estimated_Value=("Estimated Value", "sum"),
        )
        .sort_values("Estimated_Value", ascending=False)
    )
    st.dataframe(summary, hide_index=True, use_container_width=True)
    st.dataframe(
        view.sort_values(["Season", "Round", "Current Owner", "Original Team"]),
        hide_index=True,
        use_container_width=True,
    )


def render_market(players: pd.DataFrame) -> None:
    render_brand()
    st.subheader("Market")
    query = st.text_input("Search player, franchise, or NFL team")
    positions = st.multiselect("Positions", sorted(players["Position"].dropna().unique()))
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
        view.sort_values("FantasyCalc Value", ascending=False)[
            ["Player", "Position", "NFL Team", "Team", "Age", "FantasyCalc Value", "Overall Rank", "30-Day Trend"]
        ],
        hide_index=True,
        use_container_width=True,
    )


def main() -> None:
    st.sidebar.markdown("## 🏈 Front Office")
    page = st.sidebar.radio(
        "Navigation",
        ["Portfolio", "League", "Franchise Review", "Trade Lab", "Draft", "Market"],
        label_visibility="collapsed",
    )
    st.sidebar.markdown("---")
    st.sidebar.caption("Weekend Warriors")
    st.sidebar.caption(MY_TEAM_NAME)
    if st.sidebar.button("Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    try:
        with st.spinner("Loading live league and market data..."):
            bundle = load_sleeper_bundle(LEAGUE_ID)
            fc_rows = load_fantasycalc()
            players = build_player_table(bundle, fc_rows)
            picks = build_pick_inventory(bundle)
            teams = build_team_table(players, picks)
    except Exception as exc:
        st.error("The application could not load live data.")
        st.exception(exc)
        st.stop()

    if page == "Portfolio":
        render_portfolio(teams, players, picks, bundle["league"].get("name", "Weekend Warriors"))
    elif page == "League":
        render_league(teams)
    elif page == "Franchise Review":
        render_franchise_review(teams, players, picks)
    elif page == "Trade Lab":
        render_trade_lab(teams, players)
    elif page == "Draft":
        render_draft(picks, teams)
    else:
        render_market(players)


if __name__ == "__main__":
    main()
