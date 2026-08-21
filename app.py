
from __future__ import annotations

import html
import math
import random
import time
import textwrap
from typing import Any

import pandas as pd
import requests
import streamlit as st

LEAGUE_ID = "1382737164013436928"
MY_TEAM_NAME = "what up dough"
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
    .cornerstone { background:#5b21b6; color:#e9d5ff; }
    .target { background:#075985; color:#bae6fd; }
    .surplus { background:#7c2d12; color:#fed7aa; }
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
    .pick-bg{background:var(--pick)}
    .player-card-value {
      margin-top:.35rem;
      font-size:.78rem;
      font-weight:900;
      color:var(--text);
    }
    .player-card-sub {
      margin-top:.2rem;
      font-size:.66rem;
      font-weight:700;
      color:var(--muted);
      white-space:nowrap;
      overflow:hidden;
      text-overflow:ellipsis;
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
    .trend-up { color:#3ddc84; font-weight:800; }
    .trend-down { color:#ff6b6b; font-weight:800; }
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
    .small-muted { color:var(--muted); font-size:.72rem; font-weight:600; }
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
    .trade-card {
      background:var(--panel); border:1px solid var(--border);
      border-radius:16px; padding:1rem; margin-bottom:.8rem;
    }
    .trade-card-top {
      display:flex; justify-content:space-between; gap:.75rem;
      align-items:center; margin-bottom:.7rem;
    }
    .trade-grid {
      display:grid; grid-template-columns:1fr 44px 1fr;
      gap:.75rem; align-items:center;
    }
    .trade-side {
      background:var(--panel2); border:1px solid var(--border);
      border-radius:12px; padding:.75rem;
    }
    .trade-side-title {
      color:var(--muted); font-size:.72rem; text-transform:uppercase;
      margin-bottom:.4rem;
    }
    .trade-asset {
      display:flex; justify-content:space-between; gap:.6rem;
      padding:.34rem 0; border-bottom:1px solid rgba(255,255,255,.05);
      font-size:.8rem;
    }
    .trade-arrow { text-align:center; color:var(--orange); font-size:1.4rem; }
    .trade-multi-grid {
      display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr));
      gap:.6rem;
    }
    .fit-badge {
      padding:.22rem .55rem; border-radius:999px;
      background:#123322; color:#86efac;
      font-size:.72rem; font-weight:900;
    }
    .partner-row {
      display:grid; grid-template-columns:1.25fr .5fr .7fr .6fr 1.35fr;
      gap:.5rem; align-items:center; padding:.55rem .65rem;
      background:var(--panel); border-bottom:1px solid var(--border);
      font-size:.78rem;
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

    .draft-round-grid {
      display:grid;
      grid-template-columns:repeat(auto-fill,minmax(148px,1fr));
      gap:.65rem;
      margin-bottom:1.15rem;
    }
    .draft-pick-card {
      background:var(--panel2);
      border:1px solid var(--border);
      border-radius:15px;
      overflow:hidden;
      position:relative;
    }
    .draft-pick-top {
      display:flex; justify-content:space-between; align-items:center;
      padding:.35rem .5rem;
    }
    .draft-pick-overall { font-weight:900; font-size:.76rem; color:var(--muted); }
    .draft-pick-photo {
      height:95px;
      display:flex; align-items:flex-end; justify-content:center;
      background:linear-gradient(180deg,#202a39,#111827);
      overflow:hidden;
    }
    .draft-pick-photo img {
      width:100%; height:100%; object-fit:contain; object-position:center bottom;
    }
    .draft-pick-body { padding:.55rem; }
    .draft-pick-name {
      font-size:.82rem; font-weight:800;
      white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    }
    .draft-pick-team {
      font-size:.72rem; color:var(--muted); margin-top:.1rem;
      white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
    }
    .draft-pick-reason {
      font-size:.68rem; color:#93c5fd; margin-top:.35rem;
      line-height:1.25;
    }
    .draftboard-scroll {
      overflow-x:auto;
      margin-bottom:1.2rem;
      padding-bottom:.3rem;
    }
    .draftboard-grid {
      display:grid;
      gap:.35rem;
      min-width:max-content;
    }
    .draftboard-head {
      background:var(--panel2);
      border:1px solid var(--border);
      border-radius:10px;
      padding:.4rem .3rem;
      text-align:center;
      font-size:.72rem;
      font-weight:900;
      color:var(--muted);
      white-space:nowrap;
      overflow:hidden;
      text-overflow:ellipsis;
    }
    .draftboard-cell {
      display:flex;
      align-items:stretch;
      border-radius:12px;
      overflow:hidden;
      height:64px;
      box-sizing:border-box;
      color:#081018;
      position:relative;
    }
    .draftboard-cell.empty {
      background:var(--panel2);
      color:var(--muted);
      align-items:center;
      justify-content:center;
      text-align:center;
    }
    .draftboard-text {
      flex:1;
      min-width:0;
      padding:.3rem .5rem;
      display:flex;
      flex-direction:column;
      justify-content:center;
      gap:.08rem;
    }
    .draftboard-row1 {
      display:flex;
      justify-content:space-between;
      align-items:baseline;
      gap:.35rem;
    }
    .draftboard-player {
      font-size:.8rem;
      font-weight:900;
      white-space:nowrap;
      overflow:hidden;
      text-overflow:ellipsis;
      min-width:0;
    }
    .draftboard-pick-no {
      font-size:.66rem;
      font-weight:800;
      opacity:.75;
      flex-shrink:0;
    }
    .draftboard-meta {
      font-size:.66rem;
      font-weight:700;
      opacity:.85;
      white-space:nowrap;
      overflow:hidden;
      text-overflow:ellipsis;
    }
    .draftboard-arrow {
      font-size:.62rem;
      font-weight:800;
      opacity:.9;
      white-space:nowrap;
      overflow:hidden;
      text-overflow:ellipsis;
      margin-top:.05rem;
    }
    .draftboard-photo {
      width:44px;
      flex-shrink:0;
      overflow:hidden;
      background:rgba(0,0,0,.18);
    }
    .draftboard-photo img {
      width:100%;
      height:100%;
      object-fit:cover;
      object-position:center top;
      display:block;
    }
    .analyzer-table {
      border:1px solid var(--border);
      border-radius:12px;
      overflow:hidden;
      margin-bottom:1rem;
    }
    .analyzer-row {
      display:grid;
      grid-template-columns:34px 1fr 42px;
      gap:.4rem;
      align-items:center;
      padding:.32rem .55rem;
      background:var(--panel);
      border-bottom:1px solid var(--border);
      font-size:.74rem;
    }
    .analyzer-row:last-child { border-bottom:none; }
    .analyzer-team-name {
      white-space:nowrap;
      overflow:hidden;
      text-overflow:ellipsis;
      min-width:0;
    }
    .analyzer-head {
      background:var(--panel2);
      font-weight:900;
      font-size:.66rem;
      color:var(--muted);
      text-transform:uppercase;
    }
    .analyzer-row-selected {
      background:rgba(59,130,246,.18);
      font-weight:900;
    }
    .rank-bar-row {
      display:grid;
      grid-template-columns:56px 1fr 44px;
      align-items:center;
      gap:.5rem;
      padding:.3rem 0;
      font-size:.78rem;
    }
    .rank-bar-track {
      background:var(--panel2);
      border-radius:6px;
      height:18px;
      overflow:hidden;
    }
    .rank-bar-fill {
      height:100%;
      border-radius:6px;
      display:flex;
      align-items:center;
      justify-content:flex-end;
      padding-right:.4rem;
      box-sizing:border-box;
    }
    .tier-good { background:#3ddc84; }
    .tier-mid { background:#4d9fff; }
    .tier-bad { background:#ff6b6b; }
    .tier-flat { background:#6b7280; }
    .lineup-bar-strip {
      display:flex;
      align-items:flex-end;
      gap:.55rem;
      overflow-x:auto;
      padding:.2rem .1rem .4rem;
    }
    .lineup-bar-col {
      display:flex;
      flex-direction:column;
      align-items:center;
      width:56px;
      flex-shrink:0;
    }
    .lineup-bar-rank {
      font-size:.7rem;
      font-weight:900;
      margin-bottom:.25rem;
    }
    .lineup-bar-track {
      width:32px;
      height:150px;
      display:flex;
      align-items:flex-end;
      background:var(--panel2);
      border-radius:8px 8px 0 0;
      overflow:hidden;
    }
    .lineup-bar-fill {
      width:100%;
      border-radius:8px 8px 0 0;
    }
    .lineup-bar-photo {
      width:42px;
      height:42px;
      border-radius:50%;
      overflow:hidden;
      margin-top:-21px;
      border:2px solid var(--panel);
      background:var(--panel2);
    }
    .lineup-bar-photo img {
      width:100%;
      height:100%;
      object-fit:cover;
      object-position:center top;
    }
    .lineup-bar-slot {
      font-size:.6rem;
      font-weight:900;
      color:var(--muted);
      margin-top:.3rem;
      text-transform:uppercase;
    }
    .dash-stat-row {
      display:flex;
      gap:.6rem;
      margin-bottom:1rem;
      flex-wrap:wrap;
    }
    .dash-stat-card {
      flex:1;
      min-width:130px;
      background:var(--panel);
      border:1px solid var(--border);
      border-radius:12px;
      padding:.7rem .9rem;
    }
    .dash-stat-label {
      font-size:.68rem;
      color:var(--muted);
      font-weight:800;
      text-transform:uppercase;
    }
    .dash-stat-value {
      font-size:1.35rem;
      font-weight:900;
      margin-top:.2rem;
    }
    .matchup-card {
      background:var(--panel);
      border:1px solid var(--border);
      border-radius:14px;
      padding:1rem;
    }
    .matchup-row {
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:.6rem;
    }
    .matchup-team {
      display:flex;
      flex-direction:column;
      align-items:center;
      gap:.35rem;
      width:110px;
      text-align:center;
    }
    .matchup-team img {
      width:48px;
      height:48px;
      border-radius:50%;
      object-fit:cover;
      background:var(--panel2);
    }
    .matchup-score { font-size:1.6rem; font-weight:900; }
    .matchup-proj { font-size:.68rem; color:var(--muted); font-weight:700; margin-top:.15rem; }
    .matchup-prob-row {
      display:flex;
      align-items:center;
      gap:.5rem;
      margin-top:.6rem;
      padding-top:.5rem;
      border-top:1px solid var(--border);
    }
    .matchup-prob-pct { font-size:.72rem; font-weight:800; width:2.4rem; text-align:center; }
    .matchup-prob-track {
      flex:1;
      height:6px;
      border-radius:999px;
      overflow:hidden;
      display:flex;
      background:var(--panel2);
    }
    .matchup-prob-fill-a { background:#3ddc84; height:100%; }
    .matchup-prob-fill-b { background:#ff6b6b; height:100%; }
    .lineup-compare-row {
      display:grid;
      grid-template-columns: 1fr 60px 1fr;
      gap:.5rem;
      align-items:center;
      padding:.4rem 0;
      border-bottom:1px solid var(--border);
      font-size:.78rem;
    }
    .lineup-compare-row:last-child { border-bottom:none; }
    .lineup-compare-side { display:flex; flex-direction:column; }
    .lineup-compare-side.right { text-align:right; align-items:flex-end; }
    .lineup-compare-name { font-weight:800; }
    .lineup-compare-meta { font-size:.66rem; color:var(--muted); }
    .lineup-compare-pts { font-weight:900; font-size:.85rem; margin-top:.1rem; }
    .lineup-compare-slot {
      text-align:center;
      font-size:.62rem;
      font-weight:900;
      color:var(--muted);
      background:var(--panel2);
      border-radius:6px;
      padding:.25rem 0;
    }
    .matchup-label { font-size:.68rem; color:var(--muted); font-weight:700; }
    .matchup-winner .matchup-label { color:#3ddc84; }
    .matchup-winner .matchup-score { color:#3ddc84; }
    .matchup-vs {
      width:32px;
      height:32px;
      border-radius:50%;
      background:#081018;
      color:#fff;
      display:flex;
      align-items:center;
      justify-content:center;
      font-size:.65rem;
      font-weight:900;
      flex-shrink:0;
    }
    .accuracy-ring {
      width:120px;
      height:120px;
      border-radius:50%;
      margin:.4rem auto;
      display:flex;
      align-items:center;
      justify-content:center;
    }
    .accuracy-ring-inner {
      width:94px;
      height:94px;
      border-radius:50%;
      background:var(--panel);
      display:flex;
      flex-direction:column;
      align-items:center;
      justify-content:center;
    }
    .accuracy-ring-pct { font-size:1.15rem; font-weight:900; }
    .accuracy-ring-label { font-size:.62rem; color:var(--muted); font-weight:700; }
    .dash-list-row {
      display:flex;
      align-items:center;
      gap:.6rem;
      padding:.4rem .1rem;
      border-bottom:1px solid var(--border);
      font-size:.78rem;
    }
    .dash-list-row:last-child { border-bottom:none; }
    .dash-list-row img {
      width:32px;
      height:32px;
      border-radius:50%;
      object-fit:cover;
      background:var(--panel2);
      flex-shrink:0;
    }
    .dash-list-main { flex:1; min-width:0; }
    .dash-list-name {
      font-weight:800;
      white-space:nowrap;
      overflow:hidden;
      text-overflow:ellipsis;
    }
    .dash-list-sub { font-size:.68rem; color:var(--muted); }
    .dash-list-tag {
      font-size:.68rem;
      font-weight:800;
      padding:.15rem .5rem;
      border-radius:999px;
      background:var(--panel2);
      flex-shrink:0;
      white-space:nowrap;
    }
    .blueprint-chip-row {
      display:flex;
      gap:.5rem;
      flex-wrap:wrap;
      margin-bottom:.8rem;
    }
    .blueprint-chip {
      background:var(--panel2);
      border:1px solid var(--border);
      border-radius:10px;
      padding:.4rem .8rem;
      text-align:center;
      min-width:76px;
    }
    .blueprint-chip-label {
      font-size:.6rem;
      color:var(--muted);
      font-weight:800;
      text-transform:uppercase;
    }
    .blueprint-chip-value { font-size:1rem; font-weight:900; margin-top:.1rem; }
    .grade-wrap { text-align:center; }
    .grade-circle {
      width:60px;
      height:60px;
      border-radius:50%;
      display:flex;
      align-items:center;
      justify-content:center;
      font-size:1.25rem;
      font-weight:900;
      color:#081018;
      margin:0 auto;
    }
    .grade-label {
      font-size:.64rem;
      color:var(--muted);
      font-weight:800;
      margin-top:.35rem;
      text-transform:uppercase;
    }
    .gradient-scale-wrap { padding:1.4rem .8rem .6rem; }
    .gradient-scale-track {
      height:14px;
      border-radius:999px;
      background:linear-gradient(90deg, #3ddc84, #4d9fff, #f5b942, #ff6b6b);
      position:relative;
    }
    .gradient-scale-marker {
      position:absolute;
      top:-7px;
      width:28px;
      height:28px;
      border-radius:50%;
      background:var(--panel);
      border:3px solid #081018;
      transform:translateX(-50%);
    }
    .gradient-scale-labels {
      display:flex;
      justify-content:space-between;
      font-size:.66rem;
      color:var(--muted);
      font-weight:800;
      margin-top:.4rem;
      text-transform:uppercase;
    }
    .outlook-row { display:flex; gap:.5rem; }
    .outlook-chip {
      flex:1;
      text-align:center;
      background:var(--panel2);
      border:1px solid var(--border);
      border-radius:10px;
      padding:.5rem .3rem;
    }
    .outlook-chip-year { font-size:.62rem; color:var(--muted); font-weight:800; }
    .outlook-chip-label { font-size:.85rem; font-weight:900; margin-top:.15rem; }
    .share-card {
      border-radius:16px;
      padding:1rem 1.1rem;
      text-align:center;
      flex:1;
    }
    .share-card.production {
      background:linear-gradient(160deg, #3b1764, #1a0b33);
      border:1px solid #7c3aed;
    }
    .share-card.value {
      background:linear-gradient(160deg, #7c2d12, #451a03);
      border:1px solid #ea580c;
    }
    .share-card-icon { font-size:1.3rem; margin-bottom:.15rem; }
    .share-card-label {
      font-size:.66rem;
      font-weight:900;
      letter-spacing:.05em;
      color:#e9d5ff;
      text-transform:uppercase;
    }
    .share-card.value .share-card-label { color:#fed7aa; }
    .share-card-pct {
      font-size:1.9rem;
      font-weight:900;
      color:#fff;
      margin:.15rem 0;
    }
    .share-card-rank {
      font-size:.64rem;
      font-weight:800;
      color:rgba(255,255,255,.7);
      text-transform:uppercase;
    }
    .share-card-row { display:flex; gap:.6rem; margin-bottom:.6rem; }
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


# Calibrated from published dynasty market patterns (Footballguys, DynastyProcess,
# KeepTradeCut, DraftSharks, etc.): early 1st picks (1.01-1.03) sit in a near-elite
# tier worth roughly 3x a late 1st, 2nd-round picks decay more gently, and 3rd+
# rounds flatten out toward "depth" value. (start_mult, end_mult, curve_power) —
# start = 1st pick in the round, end = last pick, power > 1 gives a steeper drop
# early and a flatter tail late, matching how the real market actually prices picks.
DRAFT_SLOT_CURVES = {
    1: (1.65, 0.55, 1.6),
    2: (1.40, 0.70, 1.4),
    3: (1.25, 0.80, 1.3),
}
DEFAULT_SLOT_CURVE = (1.15, 0.85, 1.2)


def slot_value_multipliers(total_slots: int, round_no: int) -> dict[int, float]:
    """Smoothly declining value multiplier by pick slot within a round, normalized so
    the round's average multiplier is 1.0 — this redistributes value realistically
    within a round without changing the round's overall calibration."""
    start, end, power = DRAFT_SLOT_CURVES.get(round_no, DEFAULT_SLOT_CURVE)
    if total_slots <= 1:
        return {1: 1.0}
    raw = {}
    for slot in range(1, total_slots + 1):
        frac = (total_slots - slot) / (total_slots - 1)
        raw[slot] = end + (start - end) * (frac ** power)
    mean_raw = sum(raw.values()) / len(raw)
    return {slot: v / mean_raw for slot, v in raw.items()}


def historical_win_pct(bundle: dict[str, Any], lookback_seasons: int = 3) -> dict[str, float]:
    """Average win% per manager (by stable Sleeper user_id, not team name — names
    change) across their last few completed seasons. Used to make future draft
    slot estimates reflect actual team quality over time, not just whatever a
    team's live record happens to be right now — which can be a tiny, noisy
    sample early in a season or completely uninformative in the preseason.
    """
    league_id = str(bundle["league"].get("league_id") or LEAGUE_ID)
    history = load_draft_history(league_id)
    per_uid: dict[str, list[float]] = {}
    for entry in history[: lookback_seasons + 1]:
        for r in entry.get("rosters") or []:
            settings = r.get("settings") or {}
            wins = int(settings.get("wins") or 0)
            losses = int(settings.get("losses") or 0)
            ties = int(settings.get("ties") or 0)
            games = wins + losses + ties
            if games == 0:
                continue
            uid = str(r.get("owner_id"))
            per_uid.setdefault(uid, []).append(wins / games)
    return {uid: sum(v) / len(v) for uid, v in per_uid.items()}


def resolve_slot_order(bundle: dict[str, Any], season: int, roster_to_team: dict[int, str]) -> dict[str, int]:
    """Best-known 1-indexed slot per team for a season's rookie draft: the official
    Sleeper draft order if the commissioner has set one, otherwise a standings-based
    estimate (worst record picks first) — blending real season history with the
    current live record, so an early-season small sample doesn't dominate.
    """
    league_id = str(bundle["league"].get("league_id") or LEAGUE_ID)
    drafts = load_league_drafts(league_id)
    users = {str(u.get("user_id")): team_name(u) for u in bundle["users"]}
    official = official_draft_order(drafts, season, users)
    if official:
        return {t: i + 1 for i, t in enumerate(official)}

    hist_win_pct = historical_win_pct(bundle)

    rows = []
    for r in bundle["rosters"]:
        settings = r.get("settings") or {}
        wins = int(settings.get("wins") or 0)
        losses = int(settings.get("losses") or 0)
        ties = int(settings.get("ties") or 0)
        fpts = float(settings.get("fpts") or 0) + float(settings.get("fpts_decimal") or 0) / 100
        games = wins + losses + ties
        current_pct = wins / games if games > 0 else None
        uid = str(r.get("owner_id"))
        hist_pct = hist_win_pct.get(uid)

        if current_pct is not None and hist_pct is not None:
            blended = 0.5 * current_pct + 0.5 * hist_pct
        elif hist_pct is not None:
            blended = hist_pct
        elif current_pct is not None:
            blended = current_pct
        else:
            blended = 0.5  # no data at all — treat as a coin flip, not last or first

        team = roster_to_team.get(int(r["roster_id"]))
        if team:
            rows.append((team, blended, fpts))
    rows.sort(key=lambda x: (x[1], x[2]))
    return {team: i + 1 for i, (team, _, _) in enumerate(rows)}


def build_picks(bundle: dict[str, Any]) -> pd.DataFrame:
    league = bundle["league"]
    users = {str(u.get("user_id")): team_name(u) for u in bundle["users"]}
    roster_to_team = {
        int(r["roster_id"]): users.get(str(r.get("owner_id")), f"Roster {r['roster_id']}")
        for r in bundle["rosters"]
    }
    current_season = int(league.get("season") or 2026)
    base_rounds = int((league.get("settings") or {}).get("draft_rounds") or 3)

    # If this season's rookie draft has already completed, those picks have
    # already been used — converted into real rostered players — and
    # shouldn't still show up as available/tradeable draft capital.
    #
    # Don't anchor this to league.season at all — that field isn't always
    # bumped to the new year immediately once a season rolls over, and if
    # it's stale, comparing against it would silently miss a draft that
    # already happened. Instead, check every draft object Sleeper has for
    # this league on its own terms (its own "season" field), and cross-verify
    # completion against real pick results, not just a status string.
    league_id = str(league.get("league_id") or LEAGUE_ID)
    total_teams = len(roster_to_team) or 12
    drafted_seasons: set[int] = set()
    for d in load_league_drafts(league_id):
        try:
            d_season = int(d.get("season"))
        except (TypeError, ValueError):
            continue
        is_complete = d.get("status") == "complete"
        if not is_complete:
            draft_id = d.get("draft_id")
            if draft_id:
                try:
                    picks_raw = get_json(f"{SLEEPER_BASE}/draft/{draft_id}/picks")
                except DataError:
                    picks_raw = []
                expected_rounds = int((d.get("settings") or {}).get("rounds") or 0)
                expected_total = expected_rounds * total_teams
                is_complete = bool(picks_raw) and bool(expected_total) and len(picks_raw) >= expected_total
        if is_complete:
            drafted_seasons.add(d_season)

    traded_seasons = {
        int(pick.get("season"))
        for pick in bundle["traded_picks"]
        if str(pick.get("season", "")).isdigit()
    }
    traded_rounds = {
        int(pick.get("round"))
        for pick in bundle["traded_picks"]
        if str(pick.get("round", "")).isdigit()
    }
    # Always show the current three-year horizon, while also retaining any
    # additional seasons already represented in Sleeper traded-pick records.
    seasons = sorted(
        {current_season, current_season + 1, current_season + 2}
        | traded_seasons
    )
    if drafted_seasons:
        # Those drafts already happened — drop them regardless of whether old
        # trade records still reference them, and top the window back up to a
        # full three forward-looking seasons.
        seasons = [s for s in seasons if s not in drafted_seasons]
        candidate = (max(seasons) if seasons else current_season) + 1
        while len(seasons) < 3:
            if candidate not in seasons and candidate not in drafted_seasons:
                seasons.append(candidate)
            candidate += 1
        seasons = sorted(seasons)
    # A trade can reference a round beyond the league's current draft_rounds
    # setting (e.g. a 4th/5th-round rookie pick changing hands even though
    # the league currently runs a 3-round draft) — the grid needs to cover
    # whichever is larger, or that pick silently has nowhere to land.
    rounds = max(base_rounds, max(traded_rounds, default=0))

    ownership: dict[tuple[int, int, int], int] = {}
    for season in seasons:
        for original in roster_to_team:
            for rnd in range(1, rounds + 1):
                ownership[(season, rnd, original)] = original

    for pick in bundle["traded_picks"]:
        try:
            pick_season = int(pick["season"])
            key = (pick_season, int(pick["round"]), int(pick["roster_id"]))
            owner = int(pick["owner_id"])
        except (KeyError, TypeError, ValueError):
            continue
        if pick_season in drafted_seasons:
            # That draft already happened — this pick has been spent, so
            # don't let old trade history resurrect it onto the board.
            continue
        # Apply every other real trade unconditionally — don't require the
        # key to already exist in the grid, or genuine trades silently vanish.
        ownership[key] = owner

    year_factor = {current_season: 1.0, current_season + 1: 0.88, current_season + 2: 0.76}
    round_base = {1: 4300, 2: 1800, 3: 800, 4: 350, 5: 150}
    total_slots = len(roster_to_team) or 12

    # Resolve a slot order per season once, reusing the official Sleeper order
    # when the commissioner has set one, or a standings-based estimate otherwise.
    slot_orders: dict[int, dict[str, int]] = {
        season: resolve_slot_order(bundle, season, roster_to_team) for season in seasons
    }

    rows = []
    for (season, rnd, original), owner in ownership.items():
        original_team = roster_to_team.get(original, str(original))
        slot = slot_orders.get(season, {}).get(original_team)
        multiplier = slot_value_multipliers(total_slots, rnd).get(slot, 1.0) if slot else 1.0
        value = round(round_base.get(rnd, 75) * year_factor.get(season, .70) * multiplier)
        rows.append(
            {
                "Season": season,
                "Round": rnd,
                "Slot": slot,
                "Original Team": original_team,
                "Current Owner": roster_to_team.get(owner, str(owner)),
                "Value": value,
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
    return exact or next((x for x in names if "what up" in x.casefold()), None)


def ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def tier_class(rank: int, good_max: int, mid_max: int) -> str:
    if rank <= good_max:
        return "tier-good"
    if rank <= mid_max:
        return "tier-mid"
    return "tier-bad"


def rank_bar_html(label: str, rank: int, total: int) -> str:
    tier = tier_class(rank, max(1, round(total / 3)), max(1, round(total * 2 / 3)))
    width = max(6, round((total - rank + 1) / total * 100))
    return (
        f'<div class="rank-bar-row"><b>{clean(label)}</b>'
        f'<div class="rank-bar-track"><div class="rank-bar-fill {tier}" style="width:{width}%"></div></div>'
        f'<span>{ordinal(rank)}</span></div>'
    )


def positional_value_ranks(players: pd.DataFrame, status: str | None = None) -> pd.DataFrame:
    """Per-team rank (1=best) at QB/RB/WR/TE, optionally scoped to a roster Status
    (e.g. "Starter" or "Bench") rather than the whole roster."""
    pool = players if status is None else players[players["Status"] == status]
    sums = pool.groupby(["Team", "Position"])["Value"].sum().unstack(fill_value=0)
    for p in ["QB", "RB", "WR", "TE"]:
        if p not in sums.columns:
            sums[p] = 0
    ranks = sums[["QB", "RB", "WR", "TE"]].rank(ascending=False, method="min").astype(int)
    return ranks.reset_index()


def build_starting_lineup(bundle: dict[str, Any], players: pd.DataFrame, team: str) -> pd.DataFrame:
    """A team's actual configured starting lineup, in real slot order (QB, RB, RB,
    WR, WR, TE, FLEX, ..., K, DL, LB, DB — whatever the league is set up as).

    Each starter is ranked against every OTHER rostered player at that position
    in this specific league (not the whole NFL) — a QB ranked #9 here means
    9th-most-valuable QB currently rostered across your 12 teams.
    """
    users = {str(u.get("user_id")): team_name(u) for u in bundle["users"]}
    roster = next(
        (r for r in bundle["rosters"] if users.get(str(r.get("owner_id"))) == team), None
    )
    if not roster:
        return pd.DataFrame()

    slot_labels = [
        s for s in (bundle["league"].get("roster_positions") or []) if s not in ("BN", "IR", "TAXI")
    ]
    starters = [str(x) for x in (roster.get("starters") or [])]
    player_by_id = {row["Sleeper ID"]: row for _, row in players.iterrows()}

    priced = players[players["Value"] > 0].copy()
    priced["League Pos Rank"] = (
        priced.groupby("Position")["Value"].rank(ascending=False, method="min").astype(int)
    )
    priced["League Pos Pool"] = priced.groupby("Position")["Value"].transform("count").astype(int)
    rank_lookup = priced.set_index("Sleeper ID")[["League Pos Rank", "League Pos Pool"]].to_dict("index")

    rows = []
    for slot, pid in zip(slot_labels, starters):
        if not pid or pid == "0":
            rows.append(
                {"Slot": slot, "Player": "Empty", "Position": slot,
                 "League Pos Rank": None, "League Pos Pool": None, "Image": ""}
            )
            continue
        p = player_by_id.get(pid)
        if p is None:
            continue
        info = rank_lookup.get(pid, {})
        rows.append(
            {
                "Slot": slot, "Player": p["Player"], "Position": p["Position"],
                "League Pos Rank": info.get("League Pos Rank"),
                "League Pos Pool": info.get("League Pos Pool"),
                "Image": p["Image"],
            }
        )
    return pd.DataFrame(rows)


def lineup_bar_html(row: pd.Series) -> str:
    rank = row.get("League Pos Rank")
    pool = row.get("League Pos Pool")
    has_rank = row["Position"] in {"QB", "RB", "WR", "TE"} and pd.notna(rank) and pool
    img = row["Image"] or "https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png"

    if has_rank:
        rank, pool = int(rank), int(pool)
        tier = tier_class(rank, max(1, round(pool / 3)), max(1, round(pool * 2 / 3)))
        height_pct = max(14, round((pool - rank + 1) / pool * 100))
        rank_label = f"#{rank}"
        tooltip = f"{row['Player']} — {row['Position']}, ranked #{rank} of {pool} rostered {row['Position']}s in your league"
    else:
        tier = "tier-flat"
        height_pct = 35
        rank_label = "N/A"
        tooltip = f"{row['Player']} — {row['Position']} isn't priced by dynasty value tools"

    return (
        f'<div class="lineup-bar-col" title="{clean(tooltip)}">'
        f'<div class="lineup-bar-rank">{clean(rank_label)}</div>'
        f'<div class="lineup-bar-track"><div class="lineup-bar-fill {tier}" style="height:{height_pct}%"></div></div>'
        f'<div class="lineup-bar-photo"><img src="{clean(img)}"'
        f' onerror="this.onerror=null;this.src=\'https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png\';"></div>'
        f'<div class="lineup-bar-slot">{clean(row["Slot"])}</div>'
        f'</div>'
    )


def radar_svg(
    categories: list[str], series_a: list[float], series_b: list[float],
    ranks_a: list[int | None], ranks_b: list[int | None],
    label_a: str = "Starters", label_b: str = "Bench", size: int = 320,
) -> str:
    """A starters-vs-bench radar chart, hand-drawn as SVG (values 0..1 per axis),
    with hoverable vertex points showing the real rank behind each one."""
    n = len(categories)
    cx, cy = size / 2, size / 2
    radius = size / 2 - 46

    def point(value: float, i: int) -> tuple[float, float]:
        angle = -math.pi / 2 + i * (2 * math.pi / n)
        r = radius * max(0.02, min(1.0, value))
        return cx + r * math.cos(angle), cy + r * math.sin(angle)

    def polygon(vals: list[float], color: str, opacity: float) -> str:
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (point(v, i) for i, v in enumerate(vals)))
        return f'<polygon points="{pts}" fill="{color}" fill-opacity="{opacity}" stroke="{color}" stroke-width="2"/>'

    rings = "".join(
        '<polygon points="'
        + " ".join(f"{x:.1f},{y:.1f}" for x, y in (point(frac, i) for i in range(n)))
        + '" fill="none" stroke="var(--border)" stroke-width="1"/>'
        for frac in [0.25, 0.5, 0.75, 1.0]
    )
    axes = "".join(
        f'<line x1="{cx}" y1="{cy}" x2="{point(1.0, i)[0]:.1f}" y2="{point(1.0, i)[1]:.1f}" '
        f'stroke="var(--border)" stroke-width="1"/>'
        for i in range(n)
    )
    labels = "".join(
        f'<text x="{point(1.26, i)[0]:.1f}" y="{point(1.26, i)[1]:.1f}" font-size="12" '
        f'font-weight="700" fill="var(--muted)" text-anchor="middle" dominant-baseline="middle">'
        f'{clean(cat)}</text>'
        for i, cat in enumerate(categories)
    )

    def vertex_dots(vals: list[float], ranks: list[int | None], label: str, color: str) -> str:
        dots = ""
        for i, (v, cat) in enumerate(zip(vals, categories)):
            x, y = point(v, i)
            rank = ranks[i]
            text = f"{cat} Rank #{rank} ({label})" if rank else f"{cat}: no {label.lower()} rostered"
            dots += (
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{color}" stroke="var(--panel)" '
                f'stroke-width="1.5" style="cursor:pointer" '
                f"onmouseover=\"var t=document.getElementById('analyzer-radar-tip'); "
                f"if(t){{t.innerText='{text}'; t.style.left=(event.pageX+12)+'px'; "
                f"t.style.top=(event.pageY-28)+'px'; t.style.opacity=1;}}\" "
                f"onmouseout=\"var t=document.getElementById('analyzer-radar-tip'); "
                f"if(t){{t.style.opacity=0;}}\">"
                f'<title>{clean(text)}</title></circle>'
            )
        return dots

    bench_poly = polygon(series_b, "#f5b942", 0.28)
    starter_poly = polygon(series_a, "#3b82f6", 0.40)
    bench_dots = vertex_dots(series_b, ranks_b, label_b, "#f5b942")
    starter_dots = vertex_dots(series_a, ranks_a, label_a, "#3b82f6")
    legend = (
        f'<circle cx="14" cy="14" r="6" fill="#3b82f6"/><text x="26" y="18" font-size="11" '
        f'fill="var(--muted)">{clean(label_a)}</text>'
        f'<circle cx="100" cy="14" r="6" fill="#f5b942"/><text x="112" y="18" font-size="11" '
        f'fill="var(--muted)">{clean(label_b)}</text>'
    )
    tooltip_div = (
        '<div id="analyzer-radar-tip" style="position:fixed;pointer-events:none;opacity:0;'
        'background:var(--panel);color:var(--text);border:1px solid var(--border);'
        'border-radius:8px;padding:.35rem .6rem;font-size:.75rem;font-weight:700;'
        'z-index:9999;transition:opacity .12s;"></div>'
    )
    svg = (
        f'<svg viewBox="0 0 {size} {size + 10}" width="100%" height="330">'
        f'{legend}{rings}{axes}{bench_poly}{starter_poly}{bench_dots}{starter_dots}{labels}</svg>'
    )
    return tooltip_div + svg


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


def render_player_card(row: pd.Series, show_value: bool = False) -> str:
    position_rank = "—" if pd.isna(row["Position Rank"]) else int(row["Position Rank"])
    value_line = (
        f'<div class="player-card-value">{int(row["Value"]):,}</div>' if show_value else ""
    )
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
        {value_line}
      </div>
    </div>
    """


def render_asset_player_card(
    label: str,
    position: str,
    value: int,
    image: str,
    badge_text: str,
    badge_class: str,
    sub_text: str | None = None,
    position_rank: int | None = None,
) -> str:
    """Same player-card shape as the Roster/Draft Capital strips, reused for any
    list of named players (cornerstones, trade targets, surplus assets)."""
    rank_display = "—" if position_rank is None or pd.isna(position_rank) else int(position_rank)
    sub_line = f'<div class="player-card-sub">{clean(sub_text)}</div>' if sub_text else ""
    fallback = "https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png"
    return f"""
    <div class="player-card">
      <div class="player-status {badge_class}">{clean(badge_text)}</div>
      <div class="player-photo">
        <img src="{clean(image or fallback)}"
             onerror="this.onerror=null;this.src='{fallback}';">
      </div>
      <div class="player-card-body">
        <div class="player-card-name">{clean(label)}</div>
        <div class="player-card-meta">
          <span class="pos-pill {pos_class(position)}">{clean(position)}</span>
          <span class="rank-chip">{rank_display}</span>
        </div>
        <div class="player-card-value">{int(value):,}</div>
        {sub_line}
      </div>
    </div>
    """


def render_pick_card(row: pd.Series) -> str:
    """Same size/shape as a player card, for displaying an owned draft pick."""
    label = f'{int(row["Season"])} · Round {int(row["Round"])}'
    traded_line = (
        f'<div class="player-card-sub">via {clean(row["Original Team"])}</div>'
        if row.get("Traded") else ""
    )
    return f"""
    <div class="player-card">
      <div class="player-status pick">{int(row["Season"])}</div>
      <div class="player-photo pick-photo">
        <img src="https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png">
      </div>
      <div class="player-card-body">
        <div class="player-card-name">Round {int(row["Round"])}</div>
        <div class="player-card-meta">
          <span class="pos-pill pick-bg">PICK</span>
          <span class="rank-chip">{int(row["Value"]):,}</span>
        </div>
        {traded_line}
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


def render_weekly_dashboard(bundle: dict[str, Any], teams: pd.DataFrame, players: pd.DataFrame, team: str) -> None:
    league = bundle["league"]
    league_id = str(league.get("league_id") or LEAGUE_ID)
    users = {str(u.get("user_id")): team_name(u) for u in bundle["users"]}
    roster_to_team = {
        int(r["roster_id"]): users.get(str(r.get("owner_id")), f"Roster {r['roster_id']}")
        for r in bundle["rosters"]
    }
    my_roster = next((r for r in bundle["rosters"] if roster_to_team.get(int(r["roster_id"])) == team), None)

    state = load_nfl_state()
    season_type = state.get("season_type", "off")
    # During preseason, Sleeper's "week" reflects the preseason week, not
    # Week 1 of the regular season — target Week 1 explicitly so the matchup
    # lookup below finds real Week 1 pairings once they're set, rather than a
    # meaningless preseason week number.
    current_week = int(state.get("week") or 1) if season_type in {"regular", "post"} else 1
    completed_weeks = detect_completed_weeks(league_id)

    st.markdown("### Weekly Dashboard")
    st.caption(
        "Built from real Sleeper data (standings, matchups, injury flags, trending adds). "
        "Playoff Odds is our own simulation from real remaining schedule + season scoring, not a "
        "licensed odds product — treat it as directional, not a guarantee."
    )

    if not my_roster:
        st.info("Couldn't find a roster for this team.")
        return

    info = current_matchup_info(league_id, roster_to_team, my_roster, current_week)
    has_matchup = bool(info and info.get("opp_team"))
    if not has_matchup and completed_weeks == 0:
        render_html(
            '<div class="gm-card">No matchup data from Sleeper yet for this league/season — '
            "this will populate automatically once Week 1 matchups are set, even before kickoff. "
            "Scores show 0.00 until games are actually played.</div>"
        )
        return

    settings = my_roster.get("settings") or {}
    wins, losses, ties = int(settings.get("wins") or 0), int(settings.get("losses") or 0), int(settings.get("ties") or 0)
    weekly_scores = build_weekly_scores(league_id, roster_to_team, completed_weeks)
    my_scores = weekly_scores[weekly_scores["Team"] == team]
    avg_pts = my_scores["Points"].mean() if not my_scores.empty else None

    standings_rank = None
    if not weekly_scores.empty:
        wins_by_team = {
            roster_to_team.get(int(r["roster_id"])): int((r.get("settings") or {}).get("wins") or 0)
            for r in bundle["rosters"]
        }
        ranked = sorted(wins_by_team, key=lambda t: -wins_by_team.get(t, 0))
        if team in ranked:
            standings_rank = ranked.index(team) + 1

    playoff_odds = simulate_playoff_odds(bundle, weekly_scores, team, current_week) if completed_weeks > 0 else None

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value in [
        (c1, "Record", f"{wins}-{losses}" + (f"-{ties}" if ties else "")),
        (c2, "Avg Points", f"{avg_pts:.1f}" if avg_pts is not None else "—"),
        (c3, "League Rank", f"#{standings_rank}" if standings_rank else "—"),
        (c4, "Playoff Odds", f"{playoff_odds:.0f}%" if playoff_odds is not None else "—"),
    ]:
        with col:
            render_html(
                f'<div class="dash-stat-card"><div class="dash-stat-label">{clean(label)}</div>'
                f'<div class="dash-stat-value">{clean(value)}</div></div>'
            )

    colA, colB = st.columns([1.3, 1])
    with colA:
        st.markdown("#### This Week's Matchup")
        if not has_matchup:
            render_html('<div class="matchup-card">No matchup found for this week (bye week or playoffs may not include every team).</div>')
        else:
            my_pts = info["my_points"]
            opp_pts = info["opp_points"]
            my_label = f"{my_pts:.2f}" if my_pts is not None else "0.00"
            opp_label = f"{opp_pts:.2f}" if opp_pts is not None else "0.00"

            opp_roster = next(
                (r for r in bundle["rosters"] if int(r["roster_id"]) == info.get("opp_roster_id")), None
            )
            proj_season = int(state.get("season") or league.get("season") or 2026)
            scoring_settings = league.get("scoring_settings") or {}
            my_proj, my_proj_source = project_lineup_points(
                league_id, my_roster, completed_weeks, proj_season, current_week, scoring_settings
            )
            opp_proj, opp_proj_source = (
                project_lineup_points(
                    league_id, opp_roster, completed_weeks, proj_season, current_week, scoring_settings
                )
                if opp_roster else (None, "none")
            )
            my_proj_html = (
                f'<div class="matchup-proj">Proj: {my_proj:.2f}</div>' if my_proj is not None else ""
            )
            opp_proj_html = (
                f'<div class="matchup-proj">Proj: {opp_proj:.2f}</div>' if opp_proj is not None else ""
            )

            render_html(
                f'<div class="matchup-card"><div class="matchup-row">'
                f'<div class="matchup-team"><div class="matchup-label">{clean(team)}</div>'
                f'<div class="matchup-score">{my_label}</div>{my_proj_html}</div>'
                f'<div class="matchup-vs">VS</div>'
                f'<div class="matchup-team"><div class="matchup-label">{clean(info["opp_team"])}</div>'
                f'<div class="matchup-score">{opp_label}</div>{opp_proj_html}</div>'
                f'</div></div>'
            )
            proj_source = "sleeper" if "sleeper" in {my_proj_source, opp_proj_source} else my_proj_source
            if proj_source == "sleeper":
                st.caption("Proj = Sleeper's own weekly projections.")
            elif proj_source == "season_avg":
                st.caption(
                    "Sleeper's own weekly projections weren't available, so Proj falls back to each "
                    "starter's own season-average points so far, summed — a simple self-computed "
                    "sketch (no injuries, matchup, or Vegas lines factored in), not a licensed projection."
                )
            else:
                st.caption(
                    "Projections need Sleeper's projections endpoint or at least one completed week "
                    "of season data — neither is available yet."
                )

        st.markdown("#### Weekly Points — You vs. League Median")
        if weekly_scores.empty:
            st.info("No completed weeks yet.")
        else:
            median_by_week = weekly_scores.groupby("Week")["Points"].median()
            chart_df = my_scores.set_index("Week")[["Points"]].rename(columns={"Points": "You"})
            chart_df["League Median"] = chart_df.index.map(median_by_week)
            st.line_chart(chart_df)

    with colB:
        st.markdown("#### Start/Sit Accuracy")
        acc = compute_start_sit_accuracy(bundle, league_id, my_roster, completed_weeks)
        if acc is None:
            st.info("Not enough completed weeks yet to compute this.")
        else:
            pct, weeks_counted = acc
            ring_color = "#3ddc84" if pct >= 90 else ("#4d9fff" if pct >= 75 else "#ff6b6b")
            render_html(
                f'<div class="accuracy-ring" style="background:conic-gradient({ring_color} '
                f'{pct * 3.6:.0f}deg, var(--panel2) 0deg)">'
                f'<div class="accuracy-ring-inner"><div class="accuracy-ring-pct">{pct:.0f}%</div>'
                f'<div class="accuracy-ring-label">Optimal</div></div></div>'
            )
            st.caption(f"Actual starter points vs. your best possible lineup, averaged over {weeks_counted} completed week(s).")

    st.divider()
    col5, col6, col7 = st.columns(3)

    with col5:
        st.markdown("#### Lineup Suggestions")
        st.caption("Bench players out-scoring a starter at an eligible slot, by season average.")
        if my_scores.empty or completed_weeks == 0:
            st.info("Available once there's at least one completed week.")
        else:
            roster_rows = players[players["Team"] == team]
            week_pts_by_player: dict[str, list[float]] = {}
            for wk in range(1, completed_weeks + 1):
                for m in load_matchups(league_id, wk):
                    if int(m.get("roster_id", -1)) != int(my_roster["roster_id"]):
                        continue
                    for pid, pts in (m.get("players_points") or {}).items():
                        week_pts_by_player.setdefault(pid, []).append(float(pts))
            avg_by_player = {pid: sum(v) / len(v) for pid, v in week_pts_by_player.items() if v}
            starter_ids = set(str(x) for x in (my_roster.get("starters") or []) if x and x != "0")

            suggestions = []
            for _, r in roster_rows.iterrows():
                pid = r["Sleeper ID"]
                if pid in starter_ids or pid not in avg_by_player:
                    continue
                bench_avg = avg_by_player[pid]
                worse_starters = [
                    (sid, avg_by_player.get(sid, 0))
                    for sid in starter_ids
                    if avg_by_player.get(sid, 0) < bench_avg
                ]
                if worse_starters:
                    weakest_id, weakest_avg = min(worse_starters, key=lambda x: x[1])
                    weakest_row = roster_rows[roster_rows["Sleeper ID"] == weakest_id]
                    weakest_name = weakest_row.iloc[0]["Player"] if not weakest_row.empty else "a starter"
                    suggestions.append((r["Player"], r["Image"], bench_avg, weakest_name, weakest_avg))

            if not suggestions:
                st.info("No bench players are currently outscoring a starter on average.")
            else:
                rows_html = "".join(
                    f'<div class="dash-list-row"><img src="{clean(img)}" '
                    f'onerror="this.onerror=null;this.src=\'https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png\';">'
                    f'<div class="dash-list-main"><div class="dash-list-name">{clean(name)}</div>'
                    f'<div class="dash-list-sub">{avg:.1f} avg vs {clean(weak_name)} ({weak_avg:.1f})</div></div>'
                    f'</div>'
                    for name, img, avg, weak_name, weak_avg in sorted(suggestions, key=lambda x: -x[2])[:5]
                )
                render_html(rows_html)

    with col6:
        st.markdown("#### Waiver Targets")
        st.caption("Trending Sleeper adds league-wide, not currently on any roster here.")
        waivers = build_waiver_targets(bundle, players)
        if waivers.empty:
            st.info("No trending waiver data available right now.")
        else:
            rows_html = "".join(
                f'<div class="dash-list-row"><img src="{clean(r["Image"])}" '
                f'onerror="this.onerror=null;this.src=\'https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png\';">'
                f'<div class="dash-list-main"><div class="dash-list-name">{clean(r["Player"])}</div>'
                f'<div class="dash-list-sub">{clean(r["Position"])} · {clean(r["NFL Team"])}</div></div>'
                f'<span class="dash-list-tag">{int(r["Adds"]):,} adds</span></div>'
                for _, r in waivers.iterrows()
            )
            render_html(rows_html)

    with col7:
        st.markdown("#### Injury Report")
        st.caption("Real injury flags from Sleeper for your roster.")
        injuries = build_injury_report(bundle, players, team)
        if injuries.empty:
            st.info("No injury designations on your roster right now.")
        else:
            rows_html = "".join(
                f'<div class="dash-list-row"><img src="{clean(r["Image"])}" '
                f'onerror="this.onerror=null;this.src=\'https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png\';">'
                f'<div class="dash-list-main"><div class="dash-list-name">{clean(r["Player"])}</div>'
                f'<div class="dash-list-sub">{clean(r["Position"])}' + (f' · {clean(r["Note"])}' if r["Note"] else '') + '</div></div>'
                f'<span class="dash-list-tag">{clean(r["Status"])}</span></div>'
                for _, r in injuries.iterrows()
            )
            render_html(rows_html)


def render_league_projections(bundle: dict[str, Any], teams: pd.DataFrame, players: pd.DataFrame) -> None:
    render_brand(
        "League Projections",
        "Every matchup, every team, projected — plus a configurable playoff/championship simulation engine",
    )

    league = bundle["league"]
    league_id = str(league.get("league_id") or LEAGUE_ID)
    users = {str(u.get("user_id")): team_name(u) for u in bundle["users"]}
    roster_to_team = {
        int(r["roster_id"]): users.get(str(r.get("owner_id")), f"Roster {r['roster_id']}")
        for r in bundle["rosters"]
    }

    state = load_nfl_state()
    season_type = state.get("season_type", "off")
    current_week = int(state.get("week") or 1) if season_type in {"regular", "post"} else 1
    completed_weeks = detect_completed_weeks(league_id)
    proj_season = int(state.get("season") or league.get("season") or 2026)
    playoff_week_start = int((league.get("settings") or {}).get("playoff_week_start") or 15)

    st.caption(
        "Each team's projected score here is its BEST POSSIBLE lineup (optimal-lineup projection, "
        "not just whoever's currently starting) — real slot eligibility, Sleeper's own weekly "
        "projections where available, our own season-average sketch to fill any gaps. Win % assumes "
        "roughly normal score distributions around each projection. The simulation below is our own "
        "Monte Carlo model — real remaining schedule, each team's scoring mean/variance, a standard "
        "static-seed playoff bracket — not a licensed odds product. Treat everything here as "
        "directional, not a guarantee."
    )

    st.markdown("### Week-by-Week League Board")
    max_week = max(playoff_week_start + 3, current_week + 1)
    week_options = list(range(1, max_week))
    week_choice = st.selectbox(
        "Week", week_options, index=min(max(current_week - 1, 0), len(week_options) - 1)
    )

    board = build_full_week_board(bundle, week_choice, roster_to_team, proj_season, completed_weeks)
    if board.empty:
        st.info(f"No schedule data available for Week {week_choice} yet.")
    else:
        sleeper_proj = load_sleeper_projections(proj_season, week_choice, league.get("scoring_settings"))
        season_avg = build_player_avg_lookup(league_id, completed_weeks) if completed_weeks > 0 else {}
        combined_proj = {**season_avg, **sleeper_proj}
        roster_by_id = {int(r["roster_id"]): r for r in bundle["rosters"]}
        canonical_slots = [
            s for s in (league.get("roster_positions") or []) if s not in ("BN", "IR", "TAXI")
        ]

        for _, row in board.sort_values("Proj A", ascending=False, na_position="last").iterrows():
            proj_a, proj_b = row["Proj A"], row["Proj B"]
            label_a = f"{proj_a:.1f}" if proj_a is not None else "—"
            label_b = f"{proj_b:.1f}" if proj_b is not None else "—"
            win_a, win_b = row["Win % A"], row["Win % B"]
            a_favored = win_a >= win_b
            class_a = "matchup-team matchup-winner" if a_favored else "matchup-team"
            class_b = "matchup-team" if a_favored else "matchup-team matchup-winner"
            fill_left_class = "matchup-prob-fill-a" if a_favored else "matchup-prob-fill-b"
            fill_right_class = "matchup-prob-fill-b" if a_favored else "matchup-prob-fill-a"
            render_html(
                f'<div class="matchup-card"><div class="matchup-row">'
                f'<div class="{class_a}"><div class="matchup-label">{clean(row["Team A"])}</div>'
                f'<div class="matchup-score">{label_a}</div></div>'
                f'<div class="matchup-vs">VS</div>'
                f'<div class="{class_b}"><div class="matchup-label">{clean(row["Team B"])}</div>'
                f'<div class="matchup-score">{label_b}</div></div>'
                f'</div>'
                f'<div class="matchup-prob-row">'
                f'<span class="matchup-prob-pct">{win_a:.0f}%</span>'
                f'<div class="matchup-prob-track">'
                f'<div class="{fill_left_class}" style="width:{win_a:.0f}%"></div>'
                f'<div class="{fill_right_class}" style="width:{win_b:.0f}%"></div>'
                f'</div>'
                f'<span class="matchup-prob-pct">{win_b:.0f}%</span>'
                f'</div></div>'
            )

            with st.expander(f"Player-by-player: {row['Team A']} vs {row['Team B']}"):
                roster_a = roster_by_id.get(int(row["Roster ID A"])) if row["Roster ID A"] is not None else None
                roster_b = roster_by_id.get(int(row["Roster ID B"])) if row["Roster ID B"] is not None else None
                assign_a = optimal_lineup_assignment(bundle, roster_a, combined_proj) if roster_a else []
                assign_b = optimal_lineup_assignment(bundle, roster_b, combined_proj) if roster_b else []
                if not assign_a and not assign_b:
                    st.info("No projection data available to build a lineup breakdown yet.")
                else:
                    assign_a = reorder_by_canonical_slots(assign_a, canonical_slots)
                    assign_b = reorder_by_canonical_slots(assign_b, canonical_slots)
                    max_len = max(len(assign_a), len(assign_b))
                    rows_html = ""
                    for i in range(max_len):
                        a = assign_a[i] if i < len(assign_a) else {"slot": "", "name": "—", "position": "", "points": None}
                        b = assign_b[i] if i < len(assign_b) else {"slot": "", "name": "—", "position": "", "points": None}
                        slot_label = a["slot"] or b["slot"]
                        a_pts = f'{a["points"]:.1f}' if a["points"] is not None else "—"
                        b_pts = f'{b["points"]:.1f}' if b["points"] is not None else "—"
                        rows_html += (
                            f'<div class="lineup-compare-row">'
                            f'<div class="lineup-compare-side"><span class="lineup-compare-name">{clean(a["name"])}</span>'
                            f'<span class="lineup-compare-meta">{clean(a["position"])}</span>'
                            f'<span class="lineup-compare-pts">{a_pts}</span></div>'
                            f'<div class="lineup-compare-slot">{clean(slot_label)}</div>'
                            f'<div class="lineup-compare-side right"><span class="lineup-compare-name">{clean(b["name"])}</span>'
                            f'<span class="lineup-compare-meta">{clean(b["position"])}</span>'
                            f'<span class="lineup-compare-pts">{b_pts}</span></div>'
                            f'</div>'
                        )
                    render_html(rows_html)

    st.divider()
    st.markdown("### Playoff & Championship Simulation Engine")
    st.caption("Tune the knobs below, then run it. Nothing here is saved.")

    with st.expander("Simulation settings", expanded=True):
        trials = st.slider(
            "Simulation trials", min_value=100, max_value=2000, value=500, step=100,
            help="More trials = more stable odds, slower to compute.",
        )
        variance_mult = st.slider(
            "Score variance multiplier", min_value=0.5, max_value=2.0, value=1.0, step=0.1,
            help="Scale how volatile weekly scores are in the simulation — raise it to stress-test "
            "chaos/upsets, lower it to see something closer to a 'chalk' outcome.",
        )
        team_names = teams["Team"].tolist()
        boost_teams = st.multiselect(
            "Nudge specific teams' projected scoring (optional)", team_names,
            help="Model an injury, a hot streak, a big trade — anything that would shift a team's "
            "average output up or down for the rest of the season.",
        )
        mean_adjustments: dict[str, float] = {}
        for t in boost_teams:
            pct = st.slider(
                f"{t} scoring adjustment (%)", min_value=-30, max_value=30, value=0, step=5,
                key=f"proj_adj_{t}",
            )
            mean_adjustments[t] = pct

    run_clicked = st.button("Run simulation", use_container_width=True)
    if run_clicked or "league_proj_sim" not in st.session_state:
        with st.spinner("Simulating the rest of the season..."):
            weekly_scores = build_weekly_scores(league_id, roster_to_team, completed_weeks)
            st.session_state["league_proj_sim"] = simulate_full_league(
                bundle, weekly_scores, current_week,
                trials=trials, variance_mult=variance_mult, mean_adjustments=mean_adjustments,
            )

    sim = st.session_state.get("league_proj_sim")
    if sim is None or sim.empty:
        st.info("Run the simulation to see projected standings, a champion, and next year's likely top pick.")
        return

    champ_row = sim.iloc[0]
    worst_row = sim.sort_values("Avg Final Wins", ascending=True).iloc[0]
    ccol, pcol = st.columns(2)
    with ccol:
        render_html(
            f'<div class="gm-card">🏆 <b>Projected League Champion:</b><br>'
            f'<span style="font-size:1.2rem;font-weight:900">{clean(champ_row["Team"])}</span><br>'
            f'won the simulated championship in {champ_row["Champion Odds"]:.1f}% of {trials} trials.</div>'
        )
    with pcol:
        render_html(
            f'<div class="gm-card">🔻 <b>Projected #1 Pick Next Season:</b><br>'
            f'<span style="font-size:1.2rem;font-weight:900">{clean(worst_row["Team"])}</span><br>'
            f'averaged the fewest wins ({worst_row["Avg Final Wins"]:.1f}) across all simulated trials.</div>'
        )

    st.markdown("#### Projected Final Standings")
    st.caption("Sorted by championship odds — worst-to-best record is what drives next year's draft slot.")
    st.dataframe(
        sim.rename(columns={"Champion Odds": "Champion %", "Playoff Odds": "Playoff %"}),
        hide_index=True, use_container_width=True,
    )


def render_trend_breakdown(roster: pd.DataFrame) -> None:
    """Per-player 30-day value movement, sorted by magnitude — exactly which
    players are driving the team's overall 30-Day Trend stat, and by how much.
    """
    trend_df = roster[(roster["Value"] > 0) & (roster["Trend"] != 0)][
        ["Player", "Position", "Image", "Value", "Trend"]
    ].copy()
    if trend_df.empty:
        st.caption("No recent value movement recorded for this roster.")
        return
    trend_df = trend_df.sort_values("Trend", key=lambda s: s.abs(), ascending=False)

    risers = trend_df[trend_df["Trend"] > 0]
    fallers = trend_df[trend_df["Trend"] < 0]
    net = int(trend_df["Trend"].sum())
    st.caption(
        f"{len(risers)} riser(s) totaling {int(risers['Trend'].sum()):+,}, "
        f"{len(fallers)} faller(s) totaling {int(fallers['Trend'].sum()):+,} — "
        f"net {net:+,}, matching the 30-Day Trend stat above."
    )
    for _, r in trend_df.iterrows():
        is_up = r["Trend"] > 0
        arrow_class = "trend-up" if is_up else "trend-down"
        arrow = "▲" if is_up else "▼"
        render_html(
            f"""
            <div class="position-row">
              <img class="mini-photo" src="{clean(r["Image"])}"
                   onerror="this.onerror=null;this.src='https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png';">
              <span class="name-clip">{clean(r["Player"])} <span class="small-muted">{clean(r["Position"])}</span></span>
              <span class="value">{int(r["Value"]):,}</span>
              <span class="{arrow_class}">{arrow} {int(r["Trend"]):+,}</span>
            </div>
            """
        )


def render_team_review(
    bundle: dict[str, Any], teams: pd.DataFrame, players: pd.DataFrame, picks: pd.DataFrame, league_name: str
) -> None:
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

    with st.expander("Where is the 30-Day Trend coming from?", expanded=False):
        render_trend_breakdown(roster)

    render_weekly_dashboard(bundle, teams, players, selected)

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



def render_team_blueprint(
    bundle: dict[str, Any], teams: pd.DataFrame, players: pd.DataFrame, picks: pd.DataFrame
) -> None:
    render_brand(
        "Team Blueprint",
        "Your full team profile in one place — archetype, grades, cornerstones, and trade strategy",
    )

    team_names = teams["Team"].tolist()
    default_team = find_my_team(team_names) or team_names[0]
    team = st.selectbox(
        "Team", team_names, index=team_names.index(default_team), key="blueprint_team"
    )
    total_teams = len(team_names)
    row = teams[teams["Team"] == team].iloc[0]

    league = bundle["league"]
    scoring = league.get("scoring_settings") or {}
    roster_positions = league.get("roster_positions") or []
    is_sf = "SUPER_FLEX" in roster_positions
    ppr = scoring.get("rec", 0)
    tep = scoring.get("bonus_rec_te", 0)

    chips = [("TEAMS", total_teams), ("SF", "YES" if is_sf else "NO"), ("PPR", f"{ppr:g}"), ("TEP", f"{tep:g}")]
    render_html(
        '<div class="blueprint-chip-row">'
        + "".join(
            f'<div class="blueprint-chip"><div class="blueprint-chip-label">{clean(l)}</div>'
            f'<div class="blueprint-chip-value">{clean(v)}</div></div>'
            for l, v in chips
        )
        + '</div>'
    )

    pos_ranks = {
        "QB": int(row["QB_Rank"]), "RB": int(row["RB_Rank"]),
        "WR": int(row["WR_Rank"]), "TE": int(row["TE_Rank"]),
    }
    archetype = roster_archetype(pos_ranks)

    col1, col2 = st.columns(2)
    with col1:
        render_html(
            f'<div class="gm-card"><b>Value Archetype</b><br>'
            f'<span style="font-size:1.3rem;font-weight:900">{clean(row["Window"])}</span></div>'
        )
    with col2:
        render_html(
            f'<div class="gm-card"><b>Roster Archetype</b><br>'
            f'<span style="font-size:1.3rem;font-weight:900">{clean(archetype)}</span></div>'
        )

    render_html('<div class="section-title"><h3>Roster</h3></div>')
    roster = players[players["Team"] == team].sort_values(["Status", "Value"], ascending=[True, False])
    for pos, rank_col in [("QB", "QB_Rank"), ("RB", "RB_Rank"), ("WR", "WR_Rank"), ("TE", "TE_Rank")]:
        pos_players = roster[roster["Position"] == pos]
        if pos_players.empty:
            continue
        render_html(
            f'<div class="position-header {pos.lower()}-bg"><span>{clean(pos)}</span>'
            f'<span>Rank #{int(row[rank_col])}</span></div>'
        )
        cards = "".join(render_player_card(r, show_value=True) for _, r in pos_players.iterrows())
        render_html(f'<div class="roster-strip">{cards}</div>')

    st.divider()
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### Value Share")
        st.caption("Share of total league-wide dynasty value.")
        pct, rank = value_share(teams, team, "Total_Value")
        render_html(
            f'<div class="gm-card"><div style="font-size:1.6rem;font-weight:900">{pct:.1f}%</div>'
            f'League rank #{rank} of {total_teams}.</div>'
        )
    with col4:
        st.markdown("#### Starter Value Share")
        st.caption("Share of league-wide value coming from your STARTING lineup only.")
        starter_totals = (
            players[players["Status"] == "Starter"].groupby("Team")["Value"].sum()
            .reindex(teams["Team"], fill_value=0)
        )
        total_starter_value = starter_totals.sum()
        my_starter_value = starter_totals.get(team, 0)
        pct2 = round(my_starter_value / total_starter_value * 100, 1) if total_starter_value else 0.0
        rank2 = int(starter_totals.rank(ascending=False, method="min").get(team, total_teams))
        render_html(
            f'<div class="gm-card"><div style="font-size:1.6rem;font-weight:900">{pct2:.1f}%</div>'
            f'League rank #{rank2} of {total_teams}.</div>'
        )

    st.markdown("#### Multi-Year Outlook")
    labels = outlook_labels(players, team)
    render_html(
        '<div class="outlook-row">'
        + "".join(
            f'<div class="outlook-chip"><div class="outlook-chip-year">Year {i + 1}</div>'
            f'<div class="outlook-chip-label" style="color:{OUTLOOK_COLORS.get(lbl, "#fff")}">{clean(lbl)}</div></div>'
            for i, lbl in enumerate(labels)
        )
        + '</div>'
    )
    st.caption("Same aging-curve heuristic as Roster Lab — directional planning, not a forecast.")

    st.divider()
    st.markdown("#### Positional Grades")
    grade_cols = st.columns(6)
    grade_defs = [
        ("QB", grade_from_rank(int(row["QB_Rank"]), total_teams), int(row["QB_Rank"]), "var(--qb)"),
        ("RB", grade_from_rank(int(row["RB_Rank"]), total_teams), int(row["RB_Rank"]), "var(--rb)"),
        ("WR", grade_from_rank(int(row["WR_Rank"]), total_teams), int(row["WR_Rank"]), "var(--wr)"),
        ("TE", grade_from_rank(int(row["TE_Rank"]), total_teams), int(row["TE_Rank"]), "var(--te)"),
        ("PICKS", grade_from_rank(int(row["Pick_Rank"]), total_teams), int(row["Pick_Rank"]), "#f5b942"),
        ("OVERALL", grade_from_rank(int(row["Overall_Rank"]), total_teams), int(row["Overall_Rank"]), "#e5e7eb"),
    ]
    for col, (label, grade, rank, color) in zip(grade_cols, grade_defs):
        with col:
            render_html(
                f'<div class="grade-wrap"><div class="grade-circle" style="background:{color}">{grade}</div>'
                f'<div class="grade-label">{clean(label)}</div>'
                f'<div class="grade-label" style="opacity:.7;font-weight:700">#{rank} of {total_teams}</div></div>'
            )
    st.caption(
        "Overall isn't an average of the position grades — it's your rank by total dollar value "
        "(all positions + picks summed). Positions carry very different total value pools "
        "league-wide, so being moderately behind in one big-dollar position can outweigh being "
        "strong in several smaller ones."
    )

    st.markdown("#### Contend ↔ Rebuild Scale")
    marker_pos = WINDOW_SCALE_POS.get(row["Window"], 50)
    render_html(
        f'<div class="gradient-scale-wrap"><div class="gradient-scale-track">'
        f'<div class="gradient-scale-marker" style="left:{marker_pos}%"></div></div>'
        f'<div class="gradient-scale-labels"><span>Contend</span><span>Rebuild</span></div></div>'
    )

    render_html('<div class="section-title"><h3>Draft Capital — Next 3 Years</h3></div>')
    current_season = int(bundle["league"].get("season") or picks["Season"].min())
    upcoming_seasons = [s for s in sorted(picks["Season"].unique()) if s >= current_season][:3]
    my_picks = picks[(picks["Current Owner"] == team) & (picks["Season"].isin(upcoming_seasons))]
    if my_picks.empty:
        st.info("No picks currently owned in the next three seasons.")
    else:
        for season in upcoming_seasons:
            season_picks = my_picks[my_picks["Season"] == season].sort_values("Round")
            if season_picks.empty:
                continue
            render_html(f'<div class="section-title"><h4>{int(season)}</h4></div>')
            cards = "".join(render_pick_card(r) for _, r in season_picks.iterrows())
            render_html(f'<div class="roster-strip">{cards}</div>')
    render_html(
        f'<div class="gm-card" style="margin-top:.4rem">Draft capital ranks '
        f'<b>#{int(row["Pick_Rank"])}</b> of {total_teams} league-wide.</div>'
    )

    st.divider()
    st.markdown("#### Cornerstone Assets")
    st.caption("Players you've manually protected — set these in Team Needs or Trade Centre.")
    untouchables, _ = compute_effective_cornerstones(picks, team)
    my_cornerstones = players[(players["Team"] == team) & (players["Player"].isin(untouchables))]
    if my_cornerstones.empty:
        st.info("No cornerstones set for this team yet — add them in Team Needs or Trade Centre.")
    else:
        cards = "".join(
            render_asset_player_card(
                r["Player"], r["Position"], int(r["Value"]), r["Image"],
                "CORNERSTONE", "cornerstone", position_rank=r.get("Position Rank"),
            )
            for _, r in my_cornerstones.sort_values("Value", ascending=False).iterrows()
        )
        render_html(f'<div class="roster-strip">{cards}</div>')

    st.divider()
    st.markdown("#### Trade Strategy")
    strategy = build_trade_strategy(teams, players, picks, team, untouchables)
    col7, col8 = st.columns(2)
    with col7:
        st.markdown("**Look To Trade**")
        st.caption(
            "Independent options worth considering — not a package. A real trade could be just "
            "one of these for one target below, not all of them at once."
        )
        if not strategy["look_to_trade"]:
            st.info("No clear surplus assets right now.")
        else:
            cards = "".join(
                render_asset_player_card(
                    a["label"], a.get("position", "PICK"), a["value"], a.get("image"),
                    "SURPLUS", "surplus", position_rank=a.get("position_rank"),
                )
                for a in strategy["look_to_trade"]
            )
            render_html(f'<div class="roster-strip">{cards}</div>')
    with col8:
        st.markdown("**Players To Target**")
        st.caption(
            "Individual targets, not a bundle — for full control over exactly who's involved and "
            "how many pieces, use the Custom Trade Builder in Trade Centre."
        )
        if not strategy["targets"]:
            st.info("No standout targets found.")
        else:
            cards = "".join(
                render_asset_player_card(
                    a["label"], a.get("position", ""), a["value"], a.get("image"),
                    "TARGET", "target", sub_text=f'from {a["from_team"]}',
                    position_rank=a.get("position_rank"),
                )
                for a in strategy["targets"]
            )
            render_html(f'<div class="roster-strip">{cards}</div>')

    st.divider()
    st.markdown("#### Suggestions")
    strongest = min(pos_ranks, key=pos_ranks.get)
    weakest = max(pos_ranks, key=pos_ranks.get)
    pick_rank = int(row["Pick_Rank"])
    bullets = [
        f'Elite <b>{clean(strongest)}</b> room (#{pos_ranks[strongest]}) — lean on it as trade '
        f'leverage rather than a need.',
        f'Clearest gap is <b>{clean(weakest)}</b> (#{pos_ranks[weakest]}) — prioritize upgrades here.',
        f'Draft capital ranks #{pick_rank} of {total_teams} — '
        + ("use it to address needs directly." if pick_rank <= max(total_teams // 2, 1)
           else "consider packaging picks together for a proven veteran."),
    ]
    render_html('<div class="gm-card">' + "<br>".join(f"• {b}" for b in bullets) + '</div>')


def render_league_analyzer(
    bundle: dict[str, Any], teams: pd.DataFrame, players: pd.DataFrame
) -> None:
    render_brand("League Analyzer", "See where your roster stacks up across the whole league")

    team_names = teams["Team"].tolist()
    default_team = find_my_team(team_names) or team_names[0]
    team = st.selectbox(
        "Team", team_names, index=team_names.index(default_team), key="analyzer_team"
    )
    total_teams = len(team_names)

    st.caption(
        "Positional and starter rankings cover QB/RB/WR/TE — the positions FantasyCalc actually "
        "prices for dynasty value. If your league starts K/DL/LB/DB, those slots still appear in "
        "Starting Lineup below, just without a fabricated value rank next to them."
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown("### Team Power Rankings")
        lo, hi = teams["Total_Value"].min(), teams["Total_Value"].max()
        board = teams.sort_values("Overall_Rank").copy()
        board["Score"] = (100 * (board["Total_Value"] - lo) / max(hi - lo, 1)).round().astype(int)
        rows_html = "".join(
            f'<div class="analyzer-row{" analyzer-row-selected" if r["Team"] == team else ""}">'
            f'<span>#{int(r["Overall_Rank"])}</span>'
            f'<span class="analyzer-team-name">{clean(r["Team"])}</span>'
            f'<span>{int(r["Score"])}</span></div>'
            for _, r in board.iterrows()
        )
        render_html(
            '<div class="analyzer-table"><div class="analyzer-row analyzer-head">'
            '<span>RK</span><span>TEAM</span><span>SCR</span></div>'
            f'{rows_html}</div>'
        )

    with col2:
        st.markdown("### Positional Rankings")
        st.caption("Whole roster, by total dynasty value.")
        row = teams[teams["Team"] == team].iloc[0]
        for pos, rank_col in [
            ("QB", "QB_Rank"), ("RB", "RB_Rank"), ("WR", "WR_Rank"),
            ("TE", "TE_Rank"), ("PICKS", "Pick_Rank"),
        ]:
            render_html(rank_bar_html(pos, int(row[rank_col]), total_teams))

    with col3:
        st.markdown("### Starter Rankings")
        st.caption("Starting lineup only, by total dynasty value.")
        starter_ranks = positional_value_ranks(players, status="Starter")
        srow = starter_ranks[starter_ranks["Team"] == team]
        if srow.empty:
            st.info("No starters are set for this team.")
        else:
            srow = srow.iloc[0]
            for pos in ["QB", "RB", "WR", "TE"]:
                render_html(rank_bar_html(pos, int(srow[pos]), total_teams))

    st.divider()
    col4, col5 = st.columns([1, 1.6])
    with col4:
        st.markdown("### Position Strength")
        st.caption("Hover a point to see your league rank at that position.")
        starter_ranks_all = positional_value_ranks(players, status="Starter")
        bench_ranks_all = positional_value_ranks(players, status="Bench")

        def rank_or_none(ranks_df: pd.DataFrame, pos: str) -> int | None:
            r = ranks_df[ranks_df["Team"] == team]
            return int(r.iloc[0][pos]) if not r.empty else None

        def percentile(ranks_df: pd.DataFrame, pos: str) -> float:
            rank = rank_or_none(ranks_df, pos)
            if rank is None or total_teams <= 1:
                return 0.05
            return max(0.05, (total_teams - rank) / (total_teams - 1))

        cats = ["QB", "RB", "WR", "TE"]
        starter_pct = [percentile(starter_ranks_all, p) for p in cats]
        bench_pct = [percentile(bench_ranks_all, p) for p in cats]
        starter_rank_vals = [rank_or_none(starter_ranks_all, p) for p in cats]
        bench_rank_vals = [rank_or_none(bench_ranks_all, p) for p in cats]
        render_html(radar_svg(cats, starter_pct, bench_pct, starter_rank_vals, bench_rank_vals))

    with col5:
        st.markdown("### Starting Lineup")
        st.caption(
            "Your team's actual configured starting slots from Sleeper — bar height and color show "
            "how each starter ranks at their position among every rostered player in your league."
        )
        lineup = build_starting_lineup(bundle, players, team)
        if lineup.empty:
            st.info("No starting lineup data was found for this team.")
        else:
            bars = "".join(lineup_bar_html(r) for _, r in lineup.iterrows())
            render_html(f'<div class="lineup-bar-strip">{bars}</div>')


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



CORNERSTONE_AGE_CEILINGS = {"QB": 32, "RB": 26, "WR": 29, "TE": 30}


def compute_untouchables(players: pd.DataFrame, min_value: int = 2000) -> set[str]:
    """Cornerstone / foundational assets — every team's own anchor piece(s) at
    each position they roster, not just whoever ranks in some league-wide top tier.

    This mirrors how dynasty managers actually talk about untouchables: each
    team has its own foundational player(s) — the clear QB1/RB1/WR1/TE1
    building block for THAT roster — regardless of whether that specific
    player would crack a global elite tier. A player only qualifies if they
    clear a minimum value floor (so a replacement-level "QB1" on a QB-starved
    roster doesn't get tagged just for being the best of a weak group) and
    isn't already aging out of a foundational role for their position.
    """
    cornerstones: set[str] = set()
    for team in players["Team"].unique():
        roster = players[(players["Team"] == team) & (players["Value"] >= min_value)]
        for pos in ["QB", "RB", "WR", "TE"]:
            pos_players = roster[roster["Position"] == pos]
            if pos_players.empty:
                continue
            best = pos_players.sort_values("Value", ascending=False).iloc[0]
            ceiling = CORNERSTONE_AGE_CEILINGS.get(pos, 29)
            if pd.isna(best["Age"]) or best["Age"] <= ceiling:
                cornerstones.add(best["Player"])
    return cornerstones


def positional_profile(teams: pd.DataFrame, team: str) -> dict[str, int]:
    row = teams[teams["Team"] == team].iloc[0]
    return {
        "QB": int(row["QB_Rank"]),
        "RB": int(row["RB_Rank"]),
        "WR": int(row["WR_Rank"]),
        "TE": int(row["TE_Rank"]),
        "PICKS": int(row["Pick_Rank"]),
    }


def trade_partner_scores(
    teams: pd.DataFrame,
    my_team: str,
) -> pd.DataFrame:
    my_profile = positional_profile(teams, my_team)
    my_strengths = sorted(["QB", "RB", "WR", "TE"], key=lambda p: my_profile[p])[:2]
    my_needs = sorted(["QB", "RB", "WR", "TE"], key=lambda p: my_profile[p], reverse=True)[:2]

    rows = []
    for _, row in teams.iterrows():
        team = row["Team"]
        if team == my_team:
            continue

        profile = positional_profile(teams, team)
        their_needs = sorted(["QB", "RB", "WR", "TE"], key=lambda p: profile[p], reverse=True)[:2]
        their_strengths = sorted(["QB", "RB", "WR", "TE"], key=lambda p: profile[p])[:2]

        reciprocal = (
            len(set(my_strengths) & set(their_needs))
            + len(set(my_needs) & set(their_strengths))
        )
        pick_flex = max(0, 13 - int(row["Pick_Rank"]))
        score = min(
            99,
            reciprocal * 24
            + pick_flex * 2
            + sum(max(0, profile[p] - 6) for p in my_strengths)
            + sum(max(0, 7 - profile[p]) for p in my_needs)
        )

        rows.append(
            {
                "Team": team,
                "Fit Score": int(score),
                "Window": row["Window"],
                "Needs": ", ".join(their_needs),
                "Strengths": ", ".join(their_strengths),
                "Pick Rank": int(row["Pick_Rank"]),
                "Overall Rank": int(row["Overall_Rank"]),
            }
        )

    return pd.DataFrame(rows).sort_values(
        ["Fit Score", "Overall Rank"],
        ascending=[False, True],
    )


def league_needs_board(teams: pd.DataFrame) -> pd.DataFrame:
    """One row per team summarising positional strengths/needs and draft capital."""
    rows = []
    for _, row in teams.iterrows():
        team = row["Team"]
        profile = positional_profile(teams, team)
        strengths = sorted(["QB", "RB", "WR", "TE"], key=lambda p: profile[p])[:2]
        needs = sorted(["QB", "RB", "WR", "TE"], key=lambda p: profile[p], reverse=True)[:2]
        rows.append(
            {
                "Team": team,
                "Overall Rank": int(row["Overall_Rank"]),
                "Window": row["Window"],
                "Strengths": ", ".join(strengths),
                "Needs": ", ".join(needs),
                "Pick Rank": int(row["Pick_Rank"]),
            }
        )
    return pd.DataFrame(rows).sort_values("Overall Rank")


def mutual_fit(
    teams: pd.DataFrame,
    players: pd.DataFrame,
    picks: pd.DataFrame,
    my_team: str,
    max_offers: int | None = 4,
    include_picks: bool = True,
) -> list[dict[str, Any]]:
    """For every other team, work out what each side's roster could do for the other.

    'my_offers' are my_team's players at positions where the partner ranks
    weak — i.e. what I have that could plausibly fill their need — plus my
    owned draft picks (when include_picks=True), which are real trade currency
    regardless of position. 'their_offers' is the same idea from the partner's
    side. This is a needs-fit lens (who has what the other side is missing),
    not a value-balanced trade proposal like the Trade Centre scenarios.
    Untouchable cornerstone players AND protected 1st-round picks are excluded
    from both sides — a mutual fit isn't realistic if it hinges on someone
    giving up a piece they'd never actually move.
    """
    untouchables, untouchable_picks = compute_effective_cornerstones(picks, my_team)
    my_profile = positional_profile(teams, my_team)
    my_needs = sorted(["QB", "RB", "WR", "TE"], key=lambda p: my_profile[p], reverse=True)
    my_picks_all = pick_assets(picks, my_team, exclude=untouchable_picks) if include_picks else []

    partners = trade_partner_scores(teams, my_team)
    results = []
    for _, r in partners.iterrows():
        partner = r["Team"]
        their_profile = positional_profile(teams, partner)
        their_needs = sorted(["QB", "RB", "WR", "TE"], key=lambda p: their_profile[p], reverse=True)
        their_picks_all = pick_assets(picks, partner, exclude=untouchable_picks) if include_picks else []

        my_players_offer = player_assets(players, my_team, their_needs[:2], exclude=untouchables)
        their_players_offer = player_assets(players, partner, my_needs[:3], exclude=untouchables)

        my_offers_all = sorted(my_players_offer + my_picks_all, key=lambda a: -a["value"])
        their_offers_all = sorted(their_players_offer + their_picks_all, key=lambda a: -a["value"])
        # Show a balanced number of options on each side — a card with 2 on
        # one side and 1 on the other doesn't read as a real comparison.
        balanced_count = min(len(my_offers_all), len(their_offers_all))
        if max_offers is not None:
            balanced_count = min(balanced_count, max_offers)
        my_offers = my_offers_all[:balanced_count]
        their_offers = their_offers_all[:balanced_count]

        results.append(
            {
                "Team": partner,
                "Fit Score": int(r["Fit Score"]),
                "Window": r["Window"],
                "their_needs": their_needs[:2],
                "my_needs": my_needs[:3],
                "my_offers": my_offers,
                "their_offers": their_offers,
            }
        )
    return results


def player_assets(
    players: pd.DataFrame,
    team: str,
    positions: list[str] | None = None,
    exclude: set[str] | None = None,
) -> list[dict[str, Any]]:
    owned = players[players["Team"] == team].copy()
    if positions:
        owned = owned[owned["Position"].isin(positions)]
    if exclude:
        owned = owned[~owned["Player"].isin(exclude)]
    owned = owned.sort_values("Value", ascending=False)
    return [
        {
            "label": row["Player"], "value": int(row["Value"]), "type": "player",
            "position": row["Position"], "image": row.get("Image", ""),
            "position_rank": row.get("Position Rank"),
        }
        for _, row in owned.iterrows()
        if int(row["Value"]) > 0
    ]


def get_manual_untouchables(
    team: str,
) -> tuple[set[str], set[tuple[int, int, str]], set[str], set[tuple[int, int, str]]]:
    """User-specified overrides on top of the automatic cornerstone algorithm,
    scoped per team, persisting across pages within a session:
      - players/picks manually ADDED as protected (on top of the automatic list)
      - players/picks manually ALLOWED to trade (overriding an automatic flag —
        e.g. the algorithm calls Colston Loveland a cornerstone, but you're
        actually willing to move him)
    Returns (added_players, added_picks, allowed_players, allowed_picks).
    """
    added_players = set(st.session_state.get(f"manual_untouchable_players_{team}", []))
    added_picks = {tuple(p) for p in st.session_state.get(f"manual_untouchable_picks_{team}", [])}
    allowed_players = set(st.session_state.get(f"manual_allowed_players_{team}", []))
    allowed_picks = {tuple(p) for p in st.session_state.get(f"manual_allowed_picks_{team}", [])}
    return added_players, added_picks, allowed_players, allowed_picks


def apply_manual_overrides(
    team: str, auto_players: set[str], auto_picks: set[tuple[int, int, str]]
) -> tuple[set[str], set[tuple[int, int, str]]]:
    """Combine the automatic cornerstone sets with this team's manual
    overrides: anything manually added gets included, anything manually
    allowed gets removed — even if the algorithm would otherwise protect it.
    """
    added_players, added_picks, allowed_players, allowed_picks = get_manual_untouchables(team)
    players = (auto_players | added_players) - allowed_players
    picks = (auto_picks | added_picks) - allowed_picks
    return players, picks


def compute_effective_cornerstones(
    picks: pd.DataFrame, team: str
) -> tuple[set[str], set[tuple[int, int, str]]]:
    """This team's cornerstones — shared by Team Needs and Trade Centre so
    both pages always agree.

    Player cornerstones are PURELY what you choose — no automatic "best
    player at each position" guessing. That algorithm doesn't know that you
    have three good tight ends and would rather keep LaPorta than Loveland;
    only you know that, so only your manual picks count.

    Pick cornerstones default to 1st-round picks (real star-hit upside isn't
    something a trade suggestion should casually shop), plus anything you
    manually add, minus anything you manually allow.
    """
    added_players, added_picks, allowed_players, allowed_picks = get_manual_untouchables(team)
    cornerstone_players = added_players - allowed_players
    cornerstone_picks = (compute_untouchable_picks(picks) | added_picks) - allowed_picks
    return cornerstone_players, cornerstone_picks


def compute_untouchable_picks(picks: pd.DataFrame, protect_round: int = 1) -> set[tuple[int, int, str]]:
    """Draft picks treated as cornerstone/protected trade assets: 1st-round
    picks specifically, for whichever team currently owns them — the real
    star-hit upside a 1st carries doesn't disappear just because the value
    math on a trade would balance. 2nd-round picks and later are legitimate,
    tradeable draft capital, especially the lower-value/later-slot ones.
    """
    protected: set[tuple[int, int, str]] = set()
    for _, row in picks.iterrows():
        if int(row["Round"]) <= protect_round:
            protected.add((int(row["Season"]), int(row["Round"]), str(row["Original Team"])))
    return protected


def pick_assets(
    picks: pd.DataFrame, team: str, exclude: set[tuple[int, int, str]] | None = None
) -> list[dict[str, Any]]:
    owned = picks[picks["Current Owner"] == team].sort_values(["Season", "Round"])
    result = []
    for _, row in owned.iterrows():
        key = (int(row["Season"]), int(row["Round"]), str(row["Original Team"]))
        if exclude and key in exclude:
            continue
        label = f'{int(row["Season"])} R{int(row["Round"])}'
        if row["Traded"]:
            label += f' ({str(row["Original Team"])[:10]})'
        result.append(
            {
                "label": label, "value": int(row["Value"]), "type": "pick",
                "season": int(row["Season"]), "round": int(row["Round"]),
                "original_team": str(row["Original Team"]),
            }
        )
    return result


def closest_package(
    assets: list[dict[str, Any]],
    target_value: int,
    max_assets: int = 2,
) -> list[dict[str, Any]]:
    pool = assets[:18]
    if not pool:
        return []

    best = [pool[0]]
    best_gap = abs(pool[0]["value"] - target_value)

    for asset in pool:
        gap = abs(asset["value"] - target_value)
        if gap < best_gap:
            best, best_gap = [asset], gap

    if max_assets >= 2:
        for i, first in enumerate(pool):
            for second in pool[i + 1:]:
                gap = abs(first["value"] + second["value"] - target_value)
                if gap < best_gap:
                    best, best_gap = [first, second], gap
    return best


def build_trade_scenarios(
    teams: pd.DataFrame,
    players: pd.DataFrame,
    picks: pd.DataFrame,
    my_team: str,
    partner: str,
    untouchables: set[str],
) -> list[dict[str, Any]]:
    mine = positional_profile(teams, my_team)
    theirs = positional_profile(teams, partner)

    my_needs = sorted(["QB", "RB", "WR", "TE"], key=lambda p: mine[p], reverse=True)
    their_needs = sorted(["QB", "RB", "WR", "TE"], key=lambda p: theirs[p], reverse=True)

    target_positions = [p for p in my_needs if theirs[p] <= 6] or my_needs[:2]
    outgoing_positions = [p for p in their_needs if mine[p] <= 6] or sorted(
        ["QB", "RB", "WR", "TE"], key=lambda p: mine[p]
    )[:2]

    # Neither side's untouchable cornerstone pieces — players or protected
    # 1st-round picks — are realistic trade chips for an auto-generated
    # scenario, so they're excluded from both what we'd send and what we'd
    # target from the partner. Manual overrides for my_team are applied too
    # (both added protections and explicit "allow trading" exceptions).
    untouchables, untouchable_picks = apply_manual_overrides(
        my_team, untouchables, compute_untouchable_picks(picks)
    )
    targets = player_assets(players, partner, target_positions, exclude=untouchables)
    outgoing_players = player_assets(players, my_team, outgoing_positions, exclude=untouchables)
    my_picks = pick_assets(picks, my_team, exclude=untouchable_picks)
    their_picks = pick_assets(picks, partner, exclude=untouchable_picks)

    scenarios = []

    if targets:
        target = targets[0]
        package = closest_package(outgoing_players + my_picks, target["value"])
        if package:
            scenarios.append({
                "title": f"Address {target.get('position', 'roster')} need",
                "give": package,
                "receive": [target],
                "rationale": (
                    f"{partner} is relatively strong at {target.get('position', 'this position')} "
                    "while your roster ranks lower there. The outgoing package leans on a stronger "
                    "room and may use draft capital to balance value."
                ),
            })

    if their_picks and outgoing_players:
        target_pick = their_picks[0]
        package = closest_package(outgoing_players, target_pick["value"])
        scenarios.append({
            "title": "Convert roster surplus into draft capital",
            "give": package,
            "receive": [target_pick],
            "rationale": (
                f"{partner} owns useful draft capital and has positional needs that may overlap "
                "with your stronger rooms. This shifts value toward your future build."
            ),
        })

    if len(targets) > 1 and my_picks:
        target = targets[1]
        package = closest_package(my_picks + outgoing_players, target["value"])
        scenarios.append({
            "title": "Use draft capital to tier up",
            "give": package,
            "receive": [target],
            "rationale": (
                "This consolidates picks and/or a secondary player into a more valuable core asset. "
                "It fits an elite-talent strategy but should preserve your most important future first."
            ),
        })

    return scenarios[:3]


def build_simple_trades(
    players: pd.DataFrame,
    picks: pd.DataFrame,
    my_team: str,
    partner: str,
    untouchables: set[str],
    max_ideas: int = 3,
) -> list[dict[str, Any]]:
    """Straightforward single-asset-for-single-asset trade ideas.

    No multi-piece packages, no positional-need logic — just every one of my
    tradeable assets (players + picks) paired against every one of theirs,
    kept if the values are reasonably close. This is the "would you just do
    this?" layer that sits alongside the more elaborate need-based scenarios.
    """
    mine = player_assets(players, my_team, exclude=untouchables) + pick_assets(picks, my_team)
    theirs = player_assets(players, partner, exclude=untouchables) + pick_assets(picks, partner)
    if not mine or not theirs:
        return []

    ideas = []
    for give in mine[:15]:
        for receive in theirs[:15]:
            gv, rv = give["value"], receive["value"]
            if gv <= 0 or rv <= 0:
                continue
            match = max(0, 100 - int(abs(rv - gv) / max(rv, gv) * 100))
            ideas.append({"give": [give], "receive": [receive], "match": match})

    ideas.sort(key=lambda x: -x["match"])
    out, seen_give, seen_receive = [], set(), set()
    for idea in ideas:
        g_label = idea["give"][0]["label"]
        r_label = idea["receive"][0]["label"]
        if g_label in seen_give or r_label in seen_receive:
            continue
        seen_give.add(g_label)
        seen_receive.add(r_label)
        out.append(idea)
        if len(out) == max_ideas:
            break
    return out


def assets_html(assets: list[dict[str, Any]]) -> str:
    return "".join(
        f'<div class="trade-asset"><span>{clean(a["label"])}</span><span>{int(a["value"]):,}</span></div>'
        for a in assets
    ) or '<div class="trade-asset"><span>No assets</span><span>—</span></div>'



def selectable_assets(
    players: pd.DataFrame,
    picks: pd.DataFrame,
    team: str,
    untouchables: set[str] | None = None,
    untouchable_picks: set[tuple[int, int, str]] | None = None,
) -> dict[str, dict[str, Any]]:
    untouchables = untouchables or set()
    untouchable_picks = untouchable_picks or set()
    assets = {}
    for _, row in players[players["Team"] == team].sort_values("Value", ascending=False).iterrows():
        if int(row["Value"]) <= 0:
            continue
        lock = "🔒 " if row["Player"] in untouchables else ""
        key = f'{lock}{row["Player"]} · {row["Position"]} · {int(row["Value"]):,}'
        assets[key] = {"label": row["Player"], "value": int(row["Value"]), "type": "player", "position": row["Position"]}
    for _, row in picks[picks["Current Owner"] == team].sort_values(["Season", "Round"]).iterrows():
        pick_key = (int(row["Season"]), int(row["Round"]), str(row["Original Team"]))
        lock = "🔒 " if pick_key in untouchable_picks else ""
        label = f'{int(row["Season"])} R{int(row["Round"])}'
        if row["Traded"]:
            label += f' ({str(row["Original Team"])[:10]})'
        key = f'{lock}{label} · Pick · {int(row["Value"]):,}'
        assets[key] = {
            "label": label, "value": int(row["Value"]), "type": "pick",
            "season": int(row["Season"]), "round": int(row["Round"]),
            "original_team": str(row["Original Team"]),
        }
    return assets


def package_value(assets: list[dict[str, Any]]) -> int:
    return sum(int(a["value"]) for a in assets)


def labels_to_assets(labels: list[str], mapping: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    return [mapping[x] for x in labels if x in mapping]


def package_candidates(assets: list[dict[str, Any]], target: int, favourable: bool) -> list[list[dict[str, Any]]]:
    if not assets or target <= 0:
        return []
    desired = target * (0.93 if favourable else 1.0)
    pool = assets[:22]
    scored = []
    for a in pool:
        scored.append((abs(a["value"] - desired), [a]))
    for i, a in enumerate(pool):
        for b in pool[i+1:]:
            scored.append((abs(a["value"] + b["value"] - desired), [a, b]))
    for i, a in enumerate(pool[:14]):
        for j, b in enumerate(pool[i+1:14], start=i+1):
            for c in pool[j+1:14]:
                scored.append((abs(a["value"] + b["value"] + c["value"] - desired), [a, b, c]))
    scored.sort(key=lambda x: x[0])
    out, seen = [], set()
    for _, pkg in scored:
        sig = tuple(sorted(x["label"] for x in pkg))
        if sig in seen:
            continue
        seen.add(sig)
        out.append(pkg)
        if len(out) == 5:
            break
    return out


def build_asset_pool(
    players: pd.DataFrame,
    picks: pd.DataFrame,
    include_teams: list[str] | None = None,
    exclude_teams: list[str] | None = None,
    show_team_label: bool = False,
) -> dict[str, dict[str, Any]]:
    """Selectable players/picks across one or more teams, for Roster Lab's give/acquire pickers.

    include_teams restricts to just those teams (e.g. "my own assets to give up").
    exclude_teams removes teams from an otherwise league-wide pool (e.g. "anyone
    else's assets I could acquire"). show_team_label appends the owning team to
    the label, useful when the pool spans multiple teams.
    """
    pool_players = players[players["Value"] > 0]
    pool_picks = picks
    if include_teams:
        pool_players = pool_players[pool_players["Team"].isin(include_teams)]
        pool_picks = pool_picks[pool_picks["Current Owner"].isin(include_teams)]
    if exclude_teams:
        pool_players = pool_players[~pool_players["Team"].isin(exclude_teams)]
        pool_picks = pool_picks[~pool_picks["Current Owner"].isin(exclude_teams)]

    assets: dict[str, dict[str, Any]] = {}
    for _, row in pool_players.sort_values("Value", ascending=False).iterrows():
        suffix = f' · {row["Team"]}' if show_team_label else ""
        key = f'{row["Player"]} · {row["Position"]} · {int(row["Value"]):,}{suffix}'
        assets[key] = {
            "label": row["Player"], "value": int(row["Value"]), "type": "player",
            "position": row["Position"], "team": row["Team"],
        }
    for _, row in pool_picks.sort_values(["Season", "Round"]).iterrows():
        label = f'{int(row["Season"])} R{int(row["Round"])}'
        # A team can own more than one pick in the same season/round (their own
        # plus one or more acquired via trade) — without this, those picks
        # generate identical dict keys and silently collide, dropping all but
        # the last one.
        if row["Traded"]:
            label += f' (via {row["Original Team"]})'
        suffix = f' · {row["Current Owner"]}' if show_team_label else ""
        key = f'{label} · Pick · {int(row["Value"]):,}{suffix}'
        assets[key] = {
            "label": label, "value": int(row["Value"]), "type": "pick",
            "team": row["Current Owner"], "season": int(row["Season"]), "round": int(row["Round"]),
            "original_team": row["Original Team"],
        }
    return assets


def apply_roster_moves(
    players: pd.DataFrame,
    picks: pd.DataFrame,
    my_team: str,
    give_assets: list[dict[str, Any]],
    acquire_assets: list[dict[str, Any]],
    give_to_team: str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return copies of players/picks reflecting a hypothetical set of moves.

    If give_to_team is set, giving up an asset reassigns it to that specific
    partner (so both sides of the trade can be evaluated). If left as None,
    giving up an asset just removes it from the pool outright — the original
    one-sided "how does my roster change" behavior. Acquiring a real player or
    pick simply reassigns its Team/Current Owner to my_team, which correctly
    removes it from whoever previously held it too. Acquiring a devy prospect
    or an unrostered rookie appends a brand-new row instead, since neither
    exists yet as a row on any team in the players table — there's nothing to
    reassign from.
    """
    players_mod = players.copy()
    picks_mod = picks.copy()

    for a in give_assets:
        if a["type"] == "player":
            if give_to_team:
                players_mod.loc[
                    (players_mod["Team"] == my_team) & (players_mod["Player"] == a["label"]), "Team"
                ] = give_to_team
            else:
                players_mod = players_mod[
                    ~((players_mod["Team"] == my_team) & (players_mod["Player"] == a["label"]))
                ]
        else:
            mask = (
                (picks_mod["Current Owner"] == my_team)
                & (picks_mod["Season"] == a["season"])
                & (picks_mod["Round"] == a["round"])
                & (picks_mod["Original Team"] == a["original_team"])
            )
            if give_to_team:
                picks_mod.loc[mask, "Current Owner"] = give_to_team
            else:
                picks_mod = picks_mod[~mask]

    new_rows = []
    for a in acquire_assets:
        if a["type"] == "player":
            players_mod.loc[
                (players_mod["Team"] == a["team"]) & (players_mod["Player"] == a["label"]), "Team"
            ] = my_team
        elif a["type"] == "devy":
            new_rows.append(
                {
                    "Team": my_team, "Roster ID": -1, "Player": a["player_name"],
                    "Position": a["position"], "NFL Team": a.get("nfl_team", "NCAA"),
                    "Age": float("nan"), "Status": "Devy", "Value": a["value"],
                    "Overall Rank": float("nan"), "Position Rank": float("nan"), "Trend": 0,
                    "Sleeper ID": f'devy-{a["prospect_rank"]}-{a["player_name"]}',
                    "Image": a["image"],
                }
            )
        elif a["type"] == "rookie":
            new_rows.append(
                {
                    "Team": my_team, "Roster ID": -1, "Player": a["player_name"],
                    "Position": a["position"], "NFL Team": a.get("nfl_team", "FA"),
                    "Age": a.get("age", float("nan")), "Status": "Bench", "Value": a["value"],
                    "Overall Rank": float("nan"), "Position Rank": float("nan"), "Trend": 0,
                    "Sleeper ID": a["sleeper_id"], "Image": a["image"],
                }
            )
        else:
            picks_mod.loc[
                (picks_mod["Current Owner"] == a["team"])
                & (picks_mod["Season"] == a["season"])
                & (picks_mod["Round"] == a["round"])
                & (picks_mod["Original Team"] == a["original_team"]),
                "Current Owner",
            ] = my_team

    if new_rows:
        players_mod = pd.concat([players_mod, pd.DataFrame(new_rows)], ignore_index=True)

    return players_mod, picks_mod


POSITION_AGE_CURVES = {
    "QB": {"peak": 29, "growth": 0.035, "decline": 0.045},
    "RB": {"peak": 24, "growth": 0.060, "decline": 0.150},
    "WR": {"peak": 26, "growth": 0.050, "decline": 0.070},
    "TE": {"peak": 27, "growth": 0.045, "decline": 0.060},
}


def project_value(value: float, position: str, age: float | None, years_ahead: int) -> float:
    """Rough dynasty aging heuristic: value keeps climbing toward a position's
    typical peak age, then decays afterward at a position-specific rate (RBs
    fastest, QBs slowest). This is a simple directional model for planning,
    not a statistical forecast — real outcomes depend on landing spot, injury
    luck, scheme fit, and dozens of things this can't see.
    """
    if value <= 0 or age is None or pd.isna(age):
        return value
    curve = POSITION_AGE_CURVES.get(position, {"peak": 27, "growth": 0.045, "decline": 0.07})
    a, v = float(age), float(value)
    for _ in range(years_ahead):
        v *= (1 + curve["growth"]) if a < curve["peak"] else (1 - curve["decline"])
        a += 1
    return v


def project_roster_trajectory(players: pd.DataFrame, team: str, years: int = 3) -> list[float]:
    roster = players[(players["Team"] == team) & (players["Value"] > 0)]
    trajectory = [float(roster["Value"].sum())]
    for y in range(1, years + 1):
        total = sum(
            project_value(r["Value"], r["Position"], r["Age"], y) for _, r in roster.iterrows()
        )
        trajectory.append(total)
    return trajectory


WINDOW_SCALE_POS = {"Contender": 8, "Win-now": 20, "Balanced": 50, "Ascending": 65, "Rebuilding": 90}
OUTLOOK_COLORS = {"Ascend": "#3ddc84", "Contend": "#4d9fff", "Reload": "#f5b942", "Rebuild": "#ff6b6b"}


def grade_from_rank(rank: int, total: int) -> int:
    """Convert a 1..total league rank into a 1-10 grade (rank 1 -> 10)."""
    if total <= 1:
        return 10
    return max(1, round(10 - (rank - 1) / (total - 1) * 9))


def roster_archetype(pos_ranks: dict[str, int]) -> str:
    """A rough shape label for how concentrated a roster's strength is."""
    strongest = min(pos_ranks, key=pos_ranks.get)
    weakest = max(pos_ranks, key=pos_ranks.get)
    spread = pos_ranks[weakest] - pos_ranks[strongest]
    if spread <= 3:
        return "Well Rounded"
    if pos_ranks[strongest] <= 3 and spread >= 6:
        return f"{strongest}-Heavy"
    return "Top Heavy" if pos_ranks[strongest] <= 3 else "Balanced Build"


def value_share(teams: pd.DataFrame, team: str, value_col: str = "Total_Value") -> tuple[float, int]:
    """This team's share of total league-wide value in a given column, and its rank."""
    total_league_value = teams[value_col].sum()
    row = teams[teams["Team"] == team].iloc[0]
    pct = (row[value_col] / total_league_value * 100) if total_league_value else 0.0
    rank = int(teams[value_col].rank(ascending=False, method="min").loc[row.name])
    return round(pct, 1), rank


def optimal_starters_by_value(bundle: dict[str, Any], roster_df: pd.DataFrame) -> set[str]:
    """Which players on this roster WOULD start, based purely on dynasty value and real
    slot eligibility (QB/RB/WR/TE + FLEX/SUPER_FLEX/REC_FLEX) from the league's actual
    roster_positions. Used instead of Sleeper's real Status field so a hypothetical
    Roster Lab trade can be evaluated the same way before and after — a newly acquired
    or dropped player doesn't come with a real starter/bench label yet.
    """
    slot_labels = [s for s in (bundle["league"].get("roster_positions") or []) if s not in ("BN", "IR", "TAXI")]
    if not slot_labels:
        return set(roster_df[roster_df["Status"] == "Starter"]["Player"])

    pool = [
        {"label": r["Player"], "value": r["Value"], "eligible": {r["Position"]}}
        for _, r in roster_df.iterrows() if r["Value"] > 0
    ]

    def slot_eligible(slot: str, elig: set[str]) -> bool:
        if slot in elig:
            return True
        if slot == "FLEX":
            return bool(elig & {"RB", "WR", "TE"})
        if slot == "SUPER_FLEX":
            return bool(elig & {"QB", "RB", "WR", "TE"})
        if slot == "REC_FLEX":
            return bool(elig & {"WR", "TE"})
        return False

    slot_order = sorted(slot_labels, key=lambda s: sum(1 for p in pool if slot_eligible(s, p["eligible"])))
    used: set[str] = set()
    for slot in slot_order:
        candidates = [p for p in pool if p["label"] not in used and slot_eligible(slot, p["eligible"])]
        if not candidates:
            continue
        best = max(candidates, key=lambda p: p["value"])
        used.add(best["label"])
    return used


def team_optimal_starter_values(bundle: dict[str, Any], players: pd.DataFrame) -> pd.Series:
    """Total dynasty value in each team's best-possible starting lineup — the basis for
    a self-consistent Production Share, comparable across teams and before/after a trade."""
    totals = {}
    for team in players["Team"].unique():
        roster_df = players[players["Team"] == team]
        starters = optimal_starters_by_value(bundle, roster_df)
        totals[team] = float(roster_df[roster_df["Player"].isin(starters)]["Value"].sum())
    return pd.Series(totals)


def production_share(bundle: dict[str, Any], players: pd.DataFrame, team: str) -> tuple[float, int]:
    totals = team_optimal_starter_values(bundle, players)
    total_league = totals.sum()
    pct = (totals.get(team, 0) / total_league * 100) if total_league else 0.0
    rank = int(totals.rank(ascending=False, method="min").get(team, len(totals)))
    return round(pct, 1), rank


def share_card_html(label: str, icon: str, pct: float, rank: int, css_class: str) -> str:
    return (
        f'<div class="share-card {css_class}"><div class="share-card-icon">{icon}</div>'
        f'<div class="share-card-label">{clean(label)}</div>'
        f'<div class="share-card-pct">{pct:.1f}%</div>'
        f'<div class="share-card-rank">League Rank: #{rank}</div></div>'
    )


def outlook_labels(players: pd.DataFrame, team: str) -> list[str]:
    """Contend/Ascend/Reload/Rebuild label for each of the next few years, derived from
    the same aging-curve trajectory used in Roster Lab."""
    trajectory = project_roster_trajectory(players, team, years=3)
    base = trajectory[0] if trajectory[0] else 1
    labels = []
    for v in trajectory[1:]:
        ratio = v / base
        if ratio >= 1.02:
            labels.append("Ascend")
        elif ratio >= 0.92:
            labels.append("Contend")
        elif ratio >= 0.78:
            labels.append("Reload")
        else:
            labels.append("Rebuild")
    return labels


def build_trade_strategy(
    teams: pd.DataFrame, players: pd.DataFrame, picks: pd.DataFrame, team: str,
    untouchables: set[str], top_n: int = 3,
) -> dict[str, list[dict[str, Any]]]:
    """'Look to trade' (my shoppable surplus at strong positions plus tradeable
    draft capital, cornerstones excluded) and 'players to target' (best fits
    from other rosters at my weak spots, their cornerstones excluded) —
    reusing the same logic as Team Needs' mutual fit.

    1st-round picks are treated as cornerstone assets and never suggested
    here, regardless of exact value — the real star-hit upside on a 1st isn't
    something a 'balanced' trade recommendation should casually shop. 2nd+
    round picks are legitimate surplus, weighted toward suggesting the
    lower-value ones first (the "lower-end 2nd," not the best pick owned).
    """
    profile = positional_profile(teams, team)
    strengths = sorted(["QB", "RB", "WR", "TE"], key=lambda p: profile[p])[:2]

    untouchables, untouchable_picks = apply_manual_overrides(
        team, untouchables, compute_untouchable_picks(picks)
    )
    tradeable_picks = sorted(
        pick_assets(picks, team, exclude=untouchable_picks), key=lambda a: a["value"]
    )
    look_to_trade = (
        player_assets(players, team, strengths, exclude=untouchables)[: top_n - 1]
        + tradeable_picks[:1]
    )[:top_n]

    fits = mutual_fit(teams, players, picks, team, max_offers=2, include_picks=False)
    seen: set[str] = set()
    targets: list[dict[str, Any]] = []
    for f in fits:
        for offer in f["their_offers"]:
            if offer["label"] in seen:
                continue
            seen.add(offer["label"])
            targets.append({**offer, "from_team": f["Team"]})
    targets.sort(key=lambda a: -a["value"])
    return {"look_to_trade": look_to_trade, "targets": targets[:top_n]}


def render_roster_impact_panel(
    bundle: dict[str, Any], team: str,
    teams: pd.DataFrame, teams_mod: pd.DataFrame,
    players: pd.DataFrame, players_mod: pd.DataFrame,
    heading: str,
) -> None:
    current_row = teams[teams["Team"] == team].iloc[0]
    projected_row = teams_mod[teams_mod["Team"] == team].iloc[0]

    st.markdown(f"### {clean(heading)}: Before vs. After")
    cols = st.columns(2)
    for col, row, sublabel in zip(cols, [current_row, projected_row], ["Current", "Projected"]):
        with col:
            render_html(
                f'<div class="gm-card"><b>{clean(sublabel)}</b><br>'
                f'Overall Rank: #{int(row["Overall_Rank"])} · Window: {clean(row["Window"])}<br>'
                f'Total Value: {int(row["Total_Value"]):,} '
                f'(Players {int(row["Player_Value"]):,} + Picks {int(row["Pick_Value"]):,})<br>'
                f'Avg Age: {row["Avg_Age"]}<br>'
                f'QB #{int(row["QB_Rank"])} · RB #{int(row["RB_Rank"])} · '
                f'WR #{int(row["WR_Rank"])} · TE #{int(row["TE_Rank"])} · PICKS #{int(row["Pick_Rank"])}'
                f'</div>'
            )

    rank_delta = int(current_row["Overall_Rank"]) - int(projected_row["Overall_Rank"])
    if rank_delta > 0:
        st.caption(f"This move improves {heading}'s overall rank by {rank_delta} spot(s) league-wide.")
    elif rank_delta < 0:
        st.caption(f"This move drops {heading}'s overall rank by {abs(rank_delta)} spot(s) league-wide.")
    else:
        st.caption(f"This move leaves {heading}'s overall rank unchanged league-wide.")

    st.markdown(f"### {clean(heading)}: Share of League")
    st.caption(
        "Value Share = share of total league-wide dynasty value. Production Share = share of "
        "value concentrated in the best possible starting lineup (real slot eligibility, not "
        "bench) — a dynasty-value proxy, not real box-score production."
    )
    cur_prod_pct, cur_prod_rank = production_share(bundle, players, team)
    cur_val_pct, cur_val_rank = value_share(teams, team)
    proj_prod_pct, proj_prod_rank = production_share(bundle, players_mod, team)
    proj_val_pct, proj_val_rank = value_share(teams_mod, team)

    scol1, scol2 = st.columns(2)
    with scol1:
        st.markdown("**Current**")
        render_html(
            '<div class="share-card-row">'
            + share_card_html("Production Share", "⚙️", cur_prod_pct, cur_prod_rank, "production")
            + share_card_html("Value Share", "📈", cur_val_pct, cur_val_rank, "value")
            + '</div>'
        )
    with scol2:
        st.markdown("**Projected**")
        render_html(
            '<div class="share-card-row">'
            + share_card_html("Production Share", "⚙️", proj_prod_pct, proj_prod_rank, "production")
            + share_card_html("Value Share", "📈", proj_val_pct, proj_val_rank, "value")
            + '</div>'
        )


def render_team_needs(
    bundle: dict[str, Any], fc_rows: list[dict[str, Any]],
    teams: pd.DataFrame, players: pd.DataFrame, picks: pd.DataFrame,
) -> None:
    render_brand(
        "Team Needs",
        "League-wide strengths and weaknesses, a roster sandbox, and needs-driven trade concepts",
    )

    render_html('<div class="section-title"><h3>League Needs Board</h3></div>')
    board = league_needs_board(teams)
    render_html(
        '<div class="partner-row"><b>Team</b><b>Rank</b><b>Window</b><b>Strengths</b><b>Needs</b></div>'
        + "".join(
            f'<div class="partner-row"><span><b>{clean(r["Team"])}</b></span>'
            f'<span>#{int(r["Overall Rank"])}</span><span>{clean(r["Window"])}</span>'
            f'<span>{clean(r["Strengths"])}</span><span>{clean(r["Needs"])}</span></div>'
            for _, r in board.iterrows()
        )
    )
    st.caption("Strengths/needs are each team's top-2 and bottom-2 ranked positions by total FantasyCalc value.")
    st.divider()

    st.markdown("### Roster Sandbox")
    team_names = teams["Team"].tolist()
    default_team = find_my_team(team_names) or team_names[0]
    my_team = st.selectbox(
        "Your team", team_names, index=team_names.index(default_team), key="needs_my_team"
    )

    other_teams = [t for t in team_names if t != my_team]
    partner_choice = st.selectbox(
        "Trade partner (optional)",
        ["None — one-sided sandbox"] + other_teams,
        key="needs_partner",
        help=(
            "Leave as None to just see how your own roster would change, and to pick from ANY "
            "team's players below. Pick a partner to model both sides of a specific deal instead."
        ),
    )
    partner_team = None if partner_choice == "None — one-sided sandbox" else partner_choice

    render_html(
        '<div class="gm-card">Nothing here is submitted or saved anywhere — this is a sandbox. '
        "Add any player in the league (yours or anyone else's) to \"acquire,\" pull anyone off "
        "your own roster to \"give up,\" and see how your positional ranks, overall standing, and "
        "multi-year value trajectory would shift."
        + (
            " With a trade partner selected, both sides of the deal are modeled below."
            if partner_team else
            " Giving up an asset just removes it from the pool here; pick a trade partner above "
            "if you want to see the other side modeled too."
        )
        + '</div>'
    )

    reset_gen = st.session_state.get("needs_reset_gen", 0)
    give_pool = build_asset_pool(players, picks, include_teams=[my_team])
    if partner_team:
        acquire_pool = build_asset_pool(players, picks, include_teams=[partner_team], show_team_label=True)
    else:
        acquire_pool = build_asset_pool(players, picks, exclude_teams=[my_team], show_team_label=True)
    acquire_pool.update(rookie_asset_pool(bundle, fc_rows, players, 2026))
    acquire_pool.update(devy_asset_pool(2027))

    c1, c2 = st.columns(2)
    with c1:
        give_labels = st.multiselect(
            "Players/picks you'd give up", list(give_pool.keys()), key=f"needs_give_{reset_gen}"
        )
    with c2:
        acquire_labels = st.multiselect(
            "Players/picks you'd acquire (any team in the league)", list(acquire_pool.keys()),
            key=f"needs_acquire_{reset_gen}",
        )
        st.caption(
            "🆕 entries are real 2026 rookies already drafted by an NFL team but not yet "
            "rostered by anyone in this league — live Sleeper data and real FantasyCalc value. "
            "🔮 entries are 2027 devy prospects — not yet real NFL players, not owned by anyone, "
            "and valued on a much more heavily discounted scale. Adding either is a 'what if' "
            "sketch, not a real move."
        )

    if st.button("Reset simulation", key="needs_reset"):
        # Widgets can't have their session_state overwritten directly once
        # instantiated — instead, rotate to a fresh key so the multiselects
        # come back empty on rerun rather than touching the old key at all.
        st.session_state["needs_reset_gen"] = reset_gen + 1
        st.rerun()

    give_assets = labels_to_assets(give_labels, give_pool)
    acquire_assets = labels_to_assets(acquire_labels, acquire_pool)
    has_moves = bool(give_assets or acquire_assets)

    if has_moves:
        give_value = package_value(give_assets)
        acquire_value = package_value(acquire_assets)
        render_html(
            f'<div class="gm-card">Sending {give_value:,} value, receiving {acquire_value:,} value '
            f"&mdash; net {acquire_value - give_value:+,}.</div>"
        )

    players_mod, picks_mod = apply_roster_moves(
        players, picks, my_team, give_assets, acquire_assets, give_to_team=partner_team
    )
    teams_mod = build_teams(players_mod, picks_mod)

    if partner_team:
        tab1, tab2 = st.tabs([my_team, partner_team])
        with tab1:
            render_roster_impact_panel(bundle, my_team, teams, teams_mod, players, players_mod, my_team)
        with tab2:
            render_roster_impact_panel(bundle, partner_team, teams, teams_mod, players, players_mod, partner_team)
    else:
        render_roster_impact_panel(bundle, my_team, teams, teams_mod, players, players_mod, my_team)

    st.markdown("### Multi-Year Outlook")
    st.caption(
        "A simplified dynasty aging curve: RBs decline fastest after their mid-20s, WR/TE erode more "
        "gradually, QBs hold value longest, and players still climbing toward their positional peak "
        "age gain value. This is directional planning, not a statistical forecast — real outcomes "
        "depend on landing spot, injuries, and scheme fit in ways no formula captures."
    )
    years = ["Now", "+1 yr", "+2 yrs", "+3 yrs"]
    chart_df = pd.DataFrame(
        {
            "Year": years,
            "Current Roster": project_roster_trajectory(players, my_team),
            "Projected Roster": project_roster_trajectory(players_mod, my_team),
        }
    ).set_index("Year")
    st.line_chart(chart_df)

    with st.expander("Projected roster (full list)"):
        st.dataframe(
            players_mod[players_mod["Team"] == my_team][
                ["Player", "Position", "NFL Team", "Age", "Value"]
            ].sort_values("Value", ascending=False),
            hide_index=True,
            use_container_width=True,
        )

    st.divider()
    st.markdown("### Suggested Trade Concepts")
    st.caption(
        "Pick any player in the league — yours or someone else's — and we'll build a trade "
        "concept around them from team strengths and weaknesses. Independent of the sandbox "
        "above; no need to build anything there first."
    )
    roster_players = sorted(
        players[(players["Team"] == my_team) & (players["Value"] > 0)]["Player"]
    )
    st.multiselect(
        "Your cornerstone players (never suggested as a give)",
        roster_players, key=f"manual_untouchable_players_{my_team}",
    )
    team_picks_all = picks[picks["Current Owner"] == my_team].sort_values("Value", ascending=False)
    pick_label_map: dict[str, tuple[int, int, str]] = {}
    for _, row in team_picks_all.iterrows():
        label = f'{int(row["Season"])} R{int(row["Round"])}'
        if row["Traded"]:
            label += f' (via {row["Original Team"]})'
        pick_label_map[label] = (int(row["Season"]), int(row["Round"]), str(row["Original Team"]))
    chosen_pick_labels = st.multiselect(
        "Additional picks to protect (1st-rounders are already protected by default)",
        list(pick_label_map.keys()), key=f"manual_pick_labels_{my_team}",
    )
    st.session_state[f"manual_untouchable_picks_{my_team}"] = [
        pick_label_map[label] for label in chosen_pick_labels
    ]
    untouchables, untouchable_picks = compute_effective_cornerstones(picks, my_team)

    concept_pool = build_asset_pool(players, picks, show_team_label=True)
    if not concept_pool:
        st.info("No valued players or picks found in the league.")
        return
    concept_labels = st.multiselect(
        "Players/picks to build a trade concept around — any combination, any teams",
        list(concept_pool.keys()), key="needs_concept_assets",
        help=(
            "Pick only your own assets to see who'd want them and what they'd pay back. Pick only "
            "another team's assets to see what you could realistically offer for them. Pick from "
            "both sides to see that exact trade valued directly."
        ),
    )
    if not concept_labels:
        st.info("Select at least one player or pick above to see trade concepts.")
        return
    concept_assets = [concept_pool[label] for label in concept_labels]

    my_profile = positional_profile(teams, my_team)
    my_strengths = sorted(["QB", "RB", "WR", "TE"], key=lambda p: my_profile[p])[:2]
    my_needs = sorted(["QB", "RB", "WR", "TE"], key=lambda p: my_profile[p], reverse=True)[:2]

    mine = [a for a in concept_assets if a["team"] == my_team]
    theirs = [a for a in concept_assets if a["team"] != my_team]
    other_teams_involved = sorted({a["team"] for a in theirs})

    protected_selected = [
        a for a in mine
        if (a["type"] == "player" and a["label"] in untouchables)
        or (a["type"] == "pick" and (a.get("season"), a.get("round"), a.get("original_team")) in untouchable_picks)
    ]
    if protected_selected:
        st.warning(
            f"{clean(', '.join(a['label'] for a in protected_selected))} — one of these is a "
            "cornerstone. Remove it above, or un-protect it, to include it in a concept."
        )
        return

    if len(other_teams_involved) > 1:
        st.warning(
            "You've selected assets from more than one other team — a real trade only has two "
            f"sides. Pick from yourself and just one of {clean(', '.join(other_teams_involved))} at a time."
        )
        return

    if mine and theirs:
        # Both sides specified directly — just value it, no suggestion needed.
        partner = other_teams_involved[0]
        mine_value = package_value(mine)
        theirs_value = package_value(theirs)
        partner_row = teams[teams["Team"] == partner]
        window = partner_row.iloc[0]["Window"] if not partner_row.empty else ""
        render_html(
            f'<div class="trade-card">'
            f'<div class="trade-card-top"><div><b>{clean(partner)}</b>'
            f'<div class="small-muted">{clean(window)}</div></div></div>'
            f'<div class="trade-grid"><div class="trade-side">'
            f'<div class="trade-side-title">You send ({mine_value:,})</div>'
            f'{assets_html(mine)}</div>'
            f'<div class="trade-arrow">⇄</div>'
            f'<div class="trade-side"><div class="trade-side-title">You receive ({theirs_value:,})</div>'
            f'{assets_html(theirs)}</div></div>'
            f'<div class="trade-rationale">Net value: {theirs_value - mine_value:+,}.</div>'
            f'</div>'
        )

    elif mine and not theirs:
        concept_value = package_value(mine)
        mine_positions = {a["position"] for a in mine if a["type"] == "player"}
        st.caption(
            f"Your package ({concept_value:,} value) — finding teams that fit, with a "
            "value-matched return from your actual needs."
        )
        partners = trade_partner_scores(teams, my_team)
        shown = 0
        for _, partner_row in partners.iterrows():
            partner = partner_row["Team"]
            partner_profile = positional_profile(teams, partner)
            their_needs = sorted(["QB", "RB", "WR", "TE"], key=lambda p: partner_profile[p], reverse=True)[:2]
            # Picks fit any team; players only make sense to a team that
            # actually needs that position — gate on ANY overlap when the
            # package includes players at all.
            if mine_positions and not (mine_positions & set(their_needs)):
                continue
            partner_untouchables, partner_untouchable_picks = compute_effective_cornerstones(picks, partner)
            candidate_pool = (
                player_assets(players, partner, my_needs, exclude=partner_untouchables)
                + pick_assets(picks, partner, exclude=partner_untouchable_picks)
            )
            if not candidate_pool:
                continue
            return_package = closest_package(candidate_pool, concept_value, max_assets=3)
            if not return_package:
                continue
            return_value = package_value(return_package)

            fit_reason = (
                f'{clean(partner)} needs {clean("/".join(sorted(mine_positions)))} — overlapping your package'
                if mine_positions else
                f'{clean(partner)} is a strong overall fit for extra draft capital'
            )
            render_html(
                f'<div class="trade-card">'
                f'<div class="trade-card-top"><div><b>{clean(partner)}</b>'
                f'<div class="small-muted">{clean(partner_row["Window"])}</div></div>'
                f'<span class="fit-badge">{int(partner_row["Fit Score"])} fit</span></div>'
                f'<div class="trade-grid"><div class="trade-side">'
                f'<div class="trade-side-title">You send ({concept_value:,})</div>'
                f'{assets_html(mine)}</div>'
                f'<div class="trade-arrow">⇄</div>'
                f'<div class="trade-side"><div class="trade-side-title">You receive ({return_value:,})</div>'
                f'{assets_html(return_package)}</div></div>'
                f'<div class="trade-rationale">{fit_reason} — and can pay you back at '
                f'{clean("/".join(my_needs))}, your actual need.</div>'
                f'</div>'
            )
            shown += 1
            if shown >= 8:
                break
        if shown == 0:
            st.info("No value-matched fit found for this package — try adjusting your selection.")

    else:
        concept_team = other_teams_involved[0]
        concept_value = package_value(theirs)
        st.caption(
            f"{clean(concept_team)}'s package ({concept_value:,} value) — finding what you could "
            "realistically offer from your own strengths to get it."
        )
        my_candidate_pool = (
            player_assets(players, my_team, my_strengths, exclude=untouchables)
            + pick_assets(picks, my_team, exclude=untouchable_picks)
        )
        if not my_candidate_pool:
            st.info("No tradeable assets found at your strengths to build an offer.")
            return
        offer_package = closest_package(my_candidate_pool, concept_value, max_assets=3)
        if not offer_package:
            st.info("No reasonable value-matched offer found.")
            return
        offer_value = package_value(offer_package)

        render_html(
            f'<div class="trade-card">'
            f'<div class="trade-card-top"><div><b>{clean(concept_team)}</b></div></div>'
            f'<div class="trade-grid"><div class="trade-side">'
            f'<div class="trade-side-title">You send ({offer_value:,})</div>'
            f'{assets_html(offer_package)}</div>'
            f'<div class="trade-arrow">⇄</div>'
            f'<div class="trade-side"><div class="trade-side-title">You receive ({concept_value:,})</div>'
            f'{assets_html(theirs)}</div></div>'
            f'<div class="trade-rationale">Built from your strengths at {clean("/".join(my_strengths))} — '
            "the positions you'd actually have realistic surplus to offer from.</div>"
            f'</div>'
        )


def render_roster_lab(
    bundle: dict[str, Any], fc_rows: list[dict[str, Any]],
    teams: pd.DataFrame, players: pd.DataFrame, picks: pd.DataFrame,
) -> None:
    render_brand(
        "Roster Lab",
        "Plug in hypothetical moves and project your roster's rank now — and its trajectory in the coming years",
    )

    team_names = teams["Team"].tolist()
    default_team = find_my_team(team_names) or team_names[0]
    my_team = st.selectbox(
        "Your team", team_names, index=team_names.index(default_team), key="lab_my_team"
    )

    other_teams = [t for t in team_names if t != my_team]
    partner_choice = st.selectbox(
        "Trade partner (optional)",
        ["None — one-sided sandbox"] + other_teams,
        key="lab_partner",
        help=(
            "Leave as None to just see how your own roster would change. Pick a partner to also "
            "model their side: your 'give up' picks are credited to them, and 'acquire' options "
            "are limited to their real assets, so you can see Before vs. After and Share of League "
            "for both teams."
        ),
    )
    partner_team = None if partner_choice == "None — one-sided sandbox" else partner_choice

    render_html(
        '<div class="gm-card">Nothing here is submitted or saved anywhere — this is a sandbox. '
        "Add anyone in the league to \"acquire,\" pull anyone off your own roster to \"give up,\" "
        "and see how your positional ranks, overall standing, and multi-year value trajectory would "
        "shift."
        + (
            " With a trade partner selected, both sides of the deal are modeled below."
            if partner_team else
            " Giving up an asset just removes it from the pool here; pick a trade partner above "
            "if you want to see the other side modeled too."
        )
        + '</div>'
    )

    give_pool = build_asset_pool(players, picks, include_teams=[my_team])
    if partner_team:
        acquire_pool = build_asset_pool(players, picks, include_teams=[partner_team], show_team_label=True)
    else:
        acquire_pool = build_asset_pool(players, picks, exclude_teams=[my_team], show_team_label=True)
    acquire_pool.update(rookie_asset_pool(bundle, fc_rows, players, 2026))
    acquire_pool.update(devy_asset_pool(2027))

    c1, c2 = st.columns(2)
    with c1:
        give_labels = st.multiselect(
            "Players/picks you'd give up", list(give_pool.keys()), key="lab_give"
        )
    with c2:
        acquire_labels = st.multiselect(
            "Players/picks you'd acquire", list(acquire_pool.keys()), key="lab_acquire"
        )
        st.caption(
            "🆕 entries are real 2026 rookies already drafted by an NFL team but not yet "
            "rostered by anyone in this league — live Sleeper data and real FantasyCalc value. "
            "🔮 entries are 2027 devy prospects — not yet real NFL players, not owned by anyone, "
            "and valued on a much more heavily discounted scale. Adding either is a 'what if' "
            "sketch, not a real move."
        )

    if st.button("Reset simulation"):
        st.session_state["lab_give"] = []
        st.session_state["lab_acquire"] = []
        st.rerun()

    give_assets = labels_to_assets(give_labels, give_pool)
    acquire_assets = labels_to_assets(acquire_labels, acquire_pool)
    has_moves = bool(give_assets or acquire_assets)

    if has_moves:
        give_value = package_value(give_assets)
        acquire_value = package_value(acquire_assets)
        render_html(
            f'<div class="gm-card">Sending {give_value:,} value, receiving {acquire_value:,} value '
            f"&mdash; net {acquire_value - give_value:+,}.</div>"
        )

    players_mod, picks_mod = apply_roster_moves(
        players, picks, my_team, give_assets, acquire_assets, give_to_team=partner_team
    )
    teams_mod = build_teams(players_mod, picks_mod)

    if partner_team:
        tab1, tab2 = st.tabs([my_team, partner_team])
        with tab1:
            render_roster_impact_panel(bundle, my_team, teams, teams_mod, players, players_mod, my_team)
        with tab2:
            render_roster_impact_panel(bundle, partner_team, teams, teams_mod, players, players_mod, partner_team)
    else:
        render_roster_impact_panel(bundle, my_team, teams, teams_mod, players, players_mod, my_team)

    st.markdown("### Multi-Year Outlook")
    st.caption(
        "A simplified dynasty aging curve: RBs decline fastest after their mid-20s, WR/TE erode more "
        "gradually, QBs hold value longest, and players still climbing toward their positional peak "
        "age gain value. This is directional planning, not a statistical forecast — real outcomes "
        "depend on landing spot, injuries, and scheme fit in ways no formula captures."
    )
    years = ["Now", "+1 yr", "+2 yrs", "+3 yrs"]
    chart_df = pd.DataFrame(
        {
            "Year": years,
            "Current Roster": project_roster_trajectory(players, my_team),
            "Projected Roster": project_roster_trajectory(players_mod, my_team),
        }
    ).set_index("Year")
    st.line_chart(chart_df)

    with st.expander("Projected roster (full list)"):
        st.dataframe(
            players_mod[players_mod["Team"] == my_team][
                ["Player", "Position", "NFL Team", "Age", "Value"]
            ].sort_values("Value", ascending=False),
            hide_index=True,
            use_container_width=True,
        )


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


DEVY_PROSPECTS_PATH = "devy_prospects.csv"


@st.cache_data(ttl=1800, show_spinner=False)
def load_transactions(league_id: str, week: int) -> list[dict[str, Any]]:
    try:
        return get_json(f"{SLEEPER_BASE}/league/{league_id}/transactions/{week}")
    except DataError:
        return []


def load_all_trades(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    """Every completed trade across this league's full history, walking the
    same previous_league_id chain as Draft History, normalized into simple
    records tracked by stable Sleeper user_id underneath — so a manager's
    trade history stays together even if their team name changed.
    """
    league_id = str(bundle["league"].get("league_id") or LEAGUE_ID)
    history = load_draft_history(league_id)
    if not history:
        history = [
            {
                "season": bundle["league"].get("season"), "league_id": league_id,
                "users": bundle["users"], "rosters": bundle["rosters"],
            }
        ]

    player_meta = bundle["players"]
    trades = []
    for entry in history:
        season = entry.get("season")
        season_league_id = entry.get("league_id")
        if not season_league_id:
            continue
        users_map = {str(u.get("user_id")): team_name(u) for u in entry.get("users") or []}
        roster_to_uid = {
            int(r["roster_id"]): str(r.get("owner_id"))
            for r in entry.get("rosters") or []
        }

        def team_at_time(rid: int | None) -> tuple[str, str]:
            if rid is None:
                return "", "Unknown"
            uid = roster_to_uid.get(int(rid), "")
            return uid, users_map.get(uid, f"Roster {rid}")

        for week in range(1, 19):
            for tx in load_transactions(season_league_id, week):
                if tx.get("type") != "trade" or tx.get("status") != "complete":
                    continue

                roster_ids = tx.get("roster_ids") or []
                uids_involved = sorted({team_at_time(rid)[0] for rid in roster_ids if team_at_time(rid)[0]})

                adds = tx.get("adds") or {}
                drops = tx.get("drops") or {}
                players_moved = []
                for pid, to_rid in adds.items():
                    from_rid = drops.get(pid)
                    meta = player_meta.get(str(pid), {}) or {}
                    name = (
                        meta.get("full_name")
                        or " ".join(filter(None, [meta.get("first_name"), meta.get("last_name")]))
                        or str(pid)
                    )
                    to_uid, to_name = team_at_time(to_rid)
                    from_uid, from_name = team_at_time(from_rid)
                    players_moved.append(
                        {
                            "player": name, "position": meta.get("position") or "",
                            "to_uid": to_uid, "to_team": to_name,
                            "from_uid": from_uid, "from_team": from_name,
                            "image": player_image_url({"player_id": pid}),
                        }
                    )

                picks_moved = []
                for p in tx.get("draft_picks") or []:
                    to_uid, to_name = team_at_time(p.get("owner_id"))
                    from_uid, from_name = team_at_time(p.get("previous_owner_id"))
                    picks_moved.append(
                        {
                            "season": p.get("season"), "round": p.get("round"),
                            "to_uid": to_uid, "to_team": to_name,
                            "from_uid": from_uid, "from_team": from_name,
                        }
                    )

                if not players_moved and not picks_moved:
                    continue

                trades.append(
                    {
                        "season": season, "week": week, "user_ids": uids_involved,
                        "players_moved": players_moved, "picks_moved": picks_moved,
                        "timestamp": tx.get("created") or 0,
                        "transaction_id": tx.get("transaction_id"),
                    }
                )

    trades.sort(key=lambda t: t["timestamp"], reverse=True)
    return trades


def render_trade_history(bundle: dict[str, Any], teams: pd.DataFrame) -> None:
    render_brand("Trade History", "Every completed trade across this league's history")

    # Filter by the CURRENT team name (what you recognize today), but match
    # trades by the stable Sleeper user_id underneath — so if a manager has
    # renamed their team at any point, their full history still shows up
    # together instead of being split across old and new names.
    current_names_by_uid = {str(u.get("user_id")): team_name(u) for u in bundle["users"]}
    name_to_uid = {v: k for k, v in current_names_by_uid.items()}
    current_names = sorted(current_names_by_uid.values())

    team_names = teams["Team"].tolist()
    default_team = find_my_team(team_names) or (current_names[0] if current_names else None)
    default_index = current_names.index(default_team) + 1 if default_team in current_names else 0
    filter_choice = st.selectbox("Filter by team", ["All Teams"] + current_names, index=default_index)

    with st.spinner("Loading trade history from Sleeper..."):
        trades = load_all_trades(bundle)

    if filter_choice != "All Teams":
        selected_uid = name_to_uid.get(filter_choice)
        trades = [t for t in trades if selected_uid in t["user_ids"]]

    if not trades:
        st.info("No completed trades were found" + (f" for {filter_choice}." if filter_choice != "All Teams" else "."))
        return

    st.caption(f"{len(trades)} trade(s) found.")

    for t in trades:
        by_uid: dict[str, dict[str, Any]] = {
            uid: {"players": [], "picks": [], "name_then": None} for uid in t["user_ids"]
        }
        for p in t["players_moved"]:
            if p["to_uid"] in by_uid:
                by_uid[p["to_uid"]]["players"].append(p)
                by_uid[p["to_uid"]]["name_then"] = p["to_team"]
        for pk in t["picks_moved"]:
            if pk["to_uid"] in by_uid:
                by_uid[pk["to_uid"]]["picks"].append(pk)
                by_uid[pk["to_uid"]]["name_then"] = pk["to_team"]

        side_divs = []
        for uid, assets in by_uid.items():
            name_then = assets["name_then"] or current_names_by_uid.get(uid, "Unknown")
            name_now = current_names_by_uid.get(uid)
            title = clean(name_then)
            if name_now and name_now != name_then:
                title += f' <span style="opacity:.6;font-weight:600">(now {clean(name_now)})</span>'

            items_html = "".join(
                f'<div class="dash-list-row"><img src="{clean(p["image"])}" '
                'onerror="this.onerror=null;this.src=\'https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png\';">'
                f'<div class="dash-list-main"><div class="dash-list-name">{clean(p["player"])}</div>'
                f'<div class="dash-list-sub">{clean(p["position"])} · from {clean(p["from_team"])}</div></div></div>'
                for p in assets["players"]
            ) + "".join(
                f'<div class="dash-list-row"><div class="dash-list-main">'
                f'<div class="dash-list-name">{int(pk["season"])} Round {int(pk["round"])}</div>'
                f'<div class="dash-list-sub">from {clean(pk["from_team"])}</div></div></div>'
                for pk in assets["picks"]
            )
            if not items_html:
                items_html = '<div class="dash-list-sub" style="padding:.3rem 0">Nothing received</div>'
            side_divs.append(
                f'<div class="trade-side"><div class="trade-side-title">{title} received</div>'
                f'{items_html}</div>'
            )
        sides_html = (
            f'{side_divs[0]}<div class="trade-arrow">⇄</div>{side_divs[1]}'
            if len(side_divs) == 2 else "".join(side_divs)
        )

        grid_class = "trade-grid" if len(by_uid) == 2 else "trade-multi-grid"
        render_html(
            f'<div class="trade-card"><div class="trade-card-top">'
            f'<b>{clean(t["season"])} · Week {t["week"]}</b></div>'
            f'<div class="{grid_class}">{sides_html}</div></div>'
        )


def render_draft_history(bundle: dict[str, Any]) -> None:
    render_brand("Draft History", "Review past draft results, round by round")

    league_id = str(bundle["league"].get("league_id") or LEAGUE_ID)
    history = load_draft_history(league_id)
    seasons_with_drafts = [h for h in history if h.get("drafts")]

    if not seasons_with_drafts:
        st.info("No completed drafts were found in this league's history yet.")
        return

    season_labels = [str(h["season"]) for h in seasons_with_drafts]
    chosen = st.selectbox("Draft year", season_labels, index=0)
    entry = seasons_with_drafts[season_labels.index(chosen)]

    board = build_draft_board(entry)
    if board.empty:
        st.info(f"No draft picks were found for the {chosen} season.")
        return

    rounds = sorted(board["Round"].unique())
    slots = sorted(board["Slot"].unique())
    # Columns are the original owner of that draft slot — the team whose
    # turn it was, regardless of whether they later traded the pick away.
    slot_team = {
        s: board[board["Slot"] == s].sort_values("Round").iloc[0]["Original Team"]
        for s in slots
    }
    total_teams = len(slots)

    render_html(f'<div class="section-title"><h3>{clean(chosen)} Draft Board</h3></div>')

    header = "".join(f'<div class="draftboard-head">{clean(slot_team[s])}</div>' for s in slots)
    body = ""
    for rnd in rounds:
        for s in slots:
            cell = board[(board["Round"] == rnd) & (board["Slot"] == s)]
            if cell.empty:
                body += '<div class="draftboard-cell empty">—</div>'
                continue
            r = cell.iloc[0]
            pick_in_round = int(r["Pick No"]) - (int(rnd) - 1) * total_teams

            # If this pick was traded away before the draft, the column still
            # belongs to the original owner, but the arrow shows who actually
            # made the selection (they held the pick by draft day).
            arrow = (
                f'<div class="draftboard-arrow">→ {clean(r["Team"])}</div>'
                if r["Traded"] else ""
            )

            body += (
                f'<div class="draftboard-cell {pos_class(r["Position"])}">'
                f'<div class="draftboard-text">'
                f'<div class="draftboard-row1">'
                f'<span class="draftboard-player">{clean(r["Player"])}</span>'
                f'<span class="draftboard-pick-no">{int(rnd)}.{pick_in_round:02d}</span>'
                f'</div>'
                f'<div class="draftboard-meta">{clean(r["Position"])} - {clean(r["NFL Team"])}</div>'
                f'{arrow}'
                f'</div>'
                f'<div class="draftboard-photo"><img src="{clean(r["Image"])}"'
                f' onerror="this.onerror=null;this.src=\'https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png\';"></div>'
                f'</div>'
            )

    render_html(
        f'<div class="draftboard-scroll">'
        f'<div class="draftboard-grid" style="grid-template-columns:repeat({total_teams},minmax(132px,1fr))">'
        f'{header}{body}</div></div>'
    )

    st.caption(
        "Scroll horizontally to see every team. Columns show the original owner of each draft slot. "
        "The → arrow means that pick was traded away before the draft — it points to whoever actually "
        "made the selection."
    )

    with st.expander("View as a table"):
        st.dataframe(
            board[
                ["Round", "Pick No", "Original Team", "Team", "Traded",
                 "Player", "Position", "NFL Team", "Is Keeper"]
            ].rename(columns={"Team": "Actually Drafted By"})
            .sort_values(["Round", "Pick No"]),
            hide_index=True,
            use_container_width=True,
        )


@st.cache_data(ttl=3600, show_spinner=False)
def load_devy_prospects(path: str = DEVY_PROSPECTS_PATH) -> pd.DataFrame:
    """Curated devy/rookie board for draft classes too far out for Sleeper to have real players.

    Sleeper only lists actual NFL players, so a season more than ~1 year away
    is essentially empty in build_rookies. This loads a hand-maintained CSV
    aggregated from public dynasty rookie mock-draft coverage (Dynasty Nerds,
    Dynasty League Football, DraftSharks, FootballGuys forums, Roto Street
    Journal, FlurrySports, NFL Mock Draft Database) as a stand-in pool. It is
    NOT live data and will drift as the season progresses — treat it as
    directional, and refresh the CSV periodically from current mock drafts.
    """
    try:
        return pd.read_csv(path)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame()


def build_devy_pool(devy_df: pd.DataFrame, season: int) -> pd.DataFrame:
    if devy_df.empty:
        return pd.DataFrame()
    view = devy_df[devy_df["Season"] == season].copy()
    if view.empty:
        return pd.DataFrame()

    view = view.sort_values("Consensus Rank").reset_index(drop=True)
    view["Prospect Rank"] = range(1, len(view) + 1)
    top_rank = view["Consensus Rank"].max()
    view["Value"] = ((top_rank - view["Consensus Rank"] + 1) * 40).astype(int)
    view["Search Rank"] = view["Consensus Rank"]
    view["NFL Team"] = view["School"]
    view["Age"] = None
    view["Sleeper ID"] = ""
    view["Image"] = "https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png"
    return view[
        ["Player", "Position", "NFL Team", "Age", "Value", "Search Rank",
         "Sleeper ID", "Image", "Prospect Rank", "Notes"]
    ]


def devy_prospect_assets(season: int = 2027) -> list[dict[str, Any]]:
    """Speculative devy prospects as optional hypothetical trade/roster assets.

    Values are rescaled to roughly the ballpark of a discounted future rookie
    pick — NOT on the same market footing as FantasyCalc's real dynasty values,
    since these players haven't even been drafted by an NFL team yet. Any
    projection involving these is a rough directional sketch, not a real
    trade proposal or roster move Sleeper (or any market) would recognize.
    """
    pool = build_devy_pool(load_devy_prospects(), season)
    if pool.empty:
        return []
    max_rank = int(pool["Prospect Rank"].max())
    top_value = 4300 * 0.55  # discounted vs. a real, already-existing 2027 1.01
    floor_value = 400
    assets = []
    for _, row in pool.iterrows():
        frac = (max_rank - row["Prospect Rank"]) / max(max_rank - 1, 1)
        value = round(floor_value + (top_value - floor_value) * (frac ** 1.3))
        assets.append(
            {
                "label": f'🔮 {row["Player"]} · {row["Position"]} · {row["NFL Team"]} · {value:,} (2027 devy)',
                "value": value, "type": "devy", "position": row["Position"],
                "image": row["Image"], "player_name": row["Player"],
                "nfl_team": row["NFL Team"], "prospect_rank": int(row["Prospect Rank"]),
            }
        )
    return assets


def devy_asset_pool(season: int = 2027) -> dict[str, dict[str, Any]]:
    return {a["label"]: a for a in devy_prospect_assets(season)}


def unrostered_rookie_assets(
    bundle: dict[str, Any], fc_rows: list[dict[str, Any]], players: pd.DataFrame, season: int = 2026
) -> list[dict[str, Any]]:
    """Real, already-drafted NFL rookies who aren't yet on any roster in this
    league — unlike the 2027 devy class, these are live Sleeper players with real
    FantasyCalc dynasty values, just not yet added/drafted onto a team here."""
    current_season = int(bundle["league"].get("season") or season)
    rookies = build_rookies(bundle, fc_rows, season, current_season)
    if rookies.empty:
        return []
    rostered_ids = set(players["Sleeper ID"].astype(str))
    pool = rookies[~rookies["Sleeper ID"].astype(str).isin(rostered_ids) & (rookies["Value"] > 0)]
    return [
        {
            "label": (
                f'🆕 {row["Player"]} · {row["Position"]} · {row["NFL Team"]} · '
                f'{int(row["Value"]):,}'
                + (f' · {row["Age"]:.1f}y' if pd.notna(row["Age"]) else "")
                + f' ({season} rookie)'
            ),
            "value": int(row["Value"]), "type": "rookie", "position": row["Position"],
            "image": row["Image"], "player_name": row["Player"],
            "nfl_team": row["NFL Team"], "sleeper_id": str(row["Sleeper ID"]),
            "age": row["Age"] if pd.notna(row["Age"]) else float("nan"),
        }
        for _, row in pool.iterrows()
    ]


def rookie_asset_pool(
    bundle: dict[str, Any], fc_rows: list[dict[str, Any]], players: pd.DataFrame, season: int = 2026
) -> dict[str, dict[str, Any]]:
    return {a["label"]: a for a in unrostered_rookie_assets(bundle, fc_rows, players, season)}


def build_rookies(
    bundle: dict[str, Any],
    fc_rows: list[dict[str, Any]],
    season: int,
    current_season: int,
) -> pd.DataFrame:
    """Rookie-eligible skill-position players for the mock draft pool.

    Sleeper's years_exp == 0 flag means "currently in their rookie season" —
    it isn't tied to a specific future season, so it's only a valid signal
    when the requested draft season is the current one. For a season further
    out (e.g. mocking next year's class before this year's is even final),
    we instead require Sleeper's own rookie_year to match, which will
    correctly come back thin-to-empty until that class actually exists as
    real NFL players.
    """
    fc_by_id = {
        row["sleeper_id"]: row
        for row in (normalise_fc(x) for x in fc_rows)
        if row["sleeper_id"]
    }

    rows: list[dict[str, Any]] = []
    for pid, p in bundle["players"].items():
        if not isinstance(p, dict):
            continue
        position = p.get("position")
        if position not in {"QB", "RB", "WR", "TE"}:
            continue

        years_exp = p.get("years_exp")
        rookie_year = p.get("rookie_year")
        matches_target_season = bool(rookie_year) and str(rookie_year) == str(season)
        is_current_years_rookie = season == current_season and years_exp == 0
        is_rookie = matches_target_season or is_current_years_rookie
        if not is_rookie:
            continue
        if (p.get("status") or "").lower() in {"retired", "inactive"}:
            continue

        fc = fc_by_id.get(str(pid), {})
        name = (
            p.get("full_name")
            or " ".join(filter(None, [p.get("first_name"), p.get("last_name")]))
            or pid
        )
        rows.append(
            {
                "Player": name,
                "Position": position,
                "NFL Team": p.get("team") or "FA",
                "Age": p.get("age"),
                "Value": int(fc.get("value") or 0),
                "Search Rank": p.get("search_rank") or 999_999,
                "Sleeper ID": str(pid),
                "Image": player_image_url({**p, "player_id": str(pid)}),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["Has Value"] = df["Value"] > 0
    df = df.sort_values(["Has Value", "Value", "Search Rank"], ascending=[False, False, True])
    df["Prospect Rank"] = range(1, len(df) + 1)
    return df.drop(columns="Has Value").reset_index(drop=True)


@st.cache_data(ttl=900, show_spinner=False)
def load_previous_rosters(previous_league_id: str | None) -> list[dict[str, Any]]:
    if not previous_league_id or str(previous_league_id) == "0":
        return []
    try:
        return get_json(f"{SLEEPER_BASE}/league/{previous_league_id}/rosters")
    except DataError:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def load_draft_history(league_id: str) -> list[dict[str, Any]]:
    """Walk the league's previous_league_id chain, collecting each season's
    users/rosters/drafts.

    Sleeper represents each season as its own league object, linked backward
    via previous_league_id. There's no single endpoint for "all history," so
    this walks the chain until it runs out (or hits a cycle/missing league).
    """
    history: list[dict[str, Any]] = []
    current_id = league_id
    seen_ids: set[str] = set()
    while current_id and current_id != "0" and current_id not in seen_ids:
        seen_ids.add(current_id)
        try:
            league_obj = get_json(f"{SLEEPER_BASE}/league/{current_id}")
        except DataError:
            break
        if not league_obj:
            break
        try:
            users = get_json(f"{SLEEPER_BASE}/league/{current_id}/users")
        except DataError:
            users = []
        try:
            rosters = get_json(f"{SLEEPER_BASE}/league/{current_id}/rosters")
        except DataError:
            rosters = []
        try:
            drafts = get_json(f"{SLEEPER_BASE}/league/{current_id}/drafts")
        except DataError:
            drafts = []
        history.append(
            {
                "season": league_obj.get("season"),
                "league_id": current_id,
                "users": users or [],
                "rosters": rosters or [],
                "drafts": drafts or [],
            }
        )
        current_id = league_obj.get("previous_league_id")
    return history


def build_draft_board(season_entry: dict[str, Any]) -> pd.DataFrame:
    """Actual draft results for one season, one row per pick, ready for a grid view."""
    drafts = season_entry.get("drafts") or []
    draft = next((d for d in drafts if (d.get("type") or "").lower() != "auction"), None)
    if draft is None and drafts:
        draft = drafts[0]
    if not draft or not draft.get("draft_id"):
        return pd.DataFrame()

    try:
        raw_picks = get_json(f"{SLEEPER_BASE}/draft/{draft['draft_id']}/picks")
    except DataError:
        return pd.DataFrame()
    if not raw_picks:
        return pd.DataFrame()

    users = {str(u.get("user_id")): team_name(u) for u in season_entry.get("users") or []}
    rosters = season_entry.get("rosters") or []
    roster_to_team = {
        int(r["roster_id"]): users.get(str(r.get("owner_id")), f"Roster {r['roster_id']}")
        for r in rosters
    }
    user_to_roster = {
        str(r.get("owner_id")): int(r["roster_id"]) for r in rosters if r.get("owner_id")
    }

    # Resolve slot -> ORIGINAL owning roster: primary source is the draft
    # object's own slot_to_roster_id map; fall back to draft_order (user_id
    # -> slot) cross-referenced against rosters if that's missing.
    slot_to_roster_id: dict[int, int] = {}
    for slot_str, rid in (draft.get("slot_to_roster_id") or {}).items():
        try:
            slot_to_roster_id[int(slot_str)] = int(rid)
        except (TypeError, ValueError):
            continue
    if not slot_to_roster_id:
        for uid, slot in (draft.get("draft_order") or {}).items():
            rid = user_to_roster.get(str(uid))
            if rid is not None:
                try:
                    slot_to_roster_id[int(slot)] = rid
                except (TypeError, ValueError):
                    continue

    rows = []
    for p in raw_picks:
        rnd, pick_no = p.get("round"), p.get("pick_no")
        if rnd is None or pick_no is None:
            continue
        draft_slot = p.get("draft_slot")
        actual_rid = p.get("roster_id")

        original_rid = slot_to_roster_id.get(int(draft_slot)) if draft_slot is not None else None
        if original_rid is None:
            # No trade info available for this slot — best we can do is
            # assume no trade happened (original == actual drafter).
            original_rid = actual_rid
        original_team = (
            roster_to_team.get(int(original_rid), f"Roster {original_rid}")
            if original_rid is not None else "Unknown"
        )
        actual_team = (
            roster_to_team.get(int(actual_rid), f"Roster {actual_rid}")
            if actual_rid is not None else "Unknown"
        )

        meta = p.get("metadata") or {}
        player_name = " ".join(
            filter(None, [meta.get("first_name"), meta.get("last_name")])
        ) or str(p.get("player_id") or "Unknown")

        rows.append(
            {
                "Round": int(rnd),
                "Pick No": int(pick_no),
                "Slot": int(draft_slot) if draft_slot is not None else int(pick_no),
                "Original Team": original_team,
                "Team": actual_team,
                "Traded": original_team != actual_team,
                "Player": player_name,
                "Position": meta.get("position") or "",
                "NFL Team": meta.get("team") or "",
                "Image": player_image_url({"player_id": p.get("player_id")}),
                "Is Keeper": bool(p.get("is_keeper")),
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(ttl=900, show_spinner=False)
def load_league_drafts(league_id: str) -> list[dict[str, Any]]:
    try:
        return get_json(f"{SLEEPER_BASE}/league/{league_id}/drafts")
    except DataError:
        return []


@st.cache_data(ttl=1800, show_spinner=False)
def load_nfl_state() -> dict[str, Any]:
    try:
        return get_json(f"{SLEEPER_BASE}/state/nfl")
    except DataError:
        return {}


@st.cache_data(ttl=600, show_spinner=False)
def load_matchups(league_id: str, week: int) -> list[dict[str, Any]]:
    try:
        return get_json(f"{SLEEPER_BASE}/league/{league_id}/matchups/{week}")
    except DataError:
        return []


@st.cache_data(ttl=900, show_spinner=False)
def detect_completed_weeks(league_id: str, max_check: int = 18) -> int:
    """How many weeks actually have real completed scores, determined by
    checking Sleeper's matchup data directly rather than trusting
    season_type/week classification fields, which have proven unreliable —
    this is more robust to whatever exact state Sleeper's state endpoint is in.
    """
    completed = 0
    for wk in range(1, max_check + 1):
        matchups = load_matchups(league_id, wk)
        if not matchups:
            break
        has_real_points = any(
            m.get("points") is not None and float(m.get("points") or 0) > 0
            for m in matchups
        )
        if not has_real_points:
            break
        completed = wk
    return completed


@st.cache_data(ttl=3600, show_spinner=False)
def load_trending_adds(hours: int = 48, limit: int = 50) -> list[dict[str, Any]]:
    try:
        return get_json(f"{SLEEPER_BASE}/players/nfl/trending/add?lookback_hours={hours}&limit={limit}")
    except DataError:
        return []


def build_weekly_scores(league_id: str, roster_to_team: dict[int, str], through_week: int) -> pd.DataFrame:
    """Real weekly fantasy points per team for every completed week this season."""
    rows = []
    for wk in range(1, max(through_week, 0) + 1):
        for m in load_matchups(league_id, wk):
            rid, pts = m.get("roster_id"), m.get("points")
            if rid is None or pts is None:
                continue
            rows.append({"Team": roster_to_team.get(int(rid), f"Roster {rid}"), "Week": wk, "Points": float(pts)})
    # An empty list still needs real columns — pd.DataFrame([]) otherwise has
    # zero columns at all, and any downstream weekly_scores["Team"] filter
    # raises a KeyError rather than just returning nothing to work with.
    return pd.DataFrame(rows, columns=["Team", "Week", "Points"])


def current_matchup_info(
    league_id: str, roster_to_team: dict[int, str], my_roster: dict[str, Any], week: int
) -> dict[str, Any] | None:
    matchups = load_matchups(league_id, week)
    if not matchups:
        return None
    my_entry = next((m for m in matchups if int(m.get("roster_id", -1)) == int(my_roster["roster_id"])), None)
    if not my_entry:
        return None
    mid = my_entry.get("matchup_id")
    opp_entry = next(
        (m for m in matchups if m.get("matchup_id") == mid and int(m.get("roster_id", -1)) != int(my_roster["roster_id"])),
        None,
    )
    return {
        "my_points": my_entry.get("points"),
        "opp_points": opp_entry.get("points") if opp_entry else None,
        "opp_team": roster_to_team.get(int(opp_entry["roster_id"])) if opp_entry else None,
        "opp_roster_id": int(opp_entry["roster_id"]) if opp_entry else None,
        "players_points": my_entry.get("players_points") or {},
    }


@st.cache_data(ttl=1800, show_spinner=False)
def load_sleeper_raw_projections(season: int, week: int) -> dict[str, dict[str, float]]:
    """Sleeper's own weekly projections — RAW stat lines per player (pass_yd,
    pass_td, rec, rec_yd, etc.), not a pre-computed point total. This lives on
    a different URL shape than the rest of this app's Sleeper calls (no /v1
    prefix, season_type as a query param) and its exact response shape isn't
    officially documented — some sources describe a flat list of
    {player_id, stats} objects, others a dict keyed directly by player_id.
    Parsed defensively to handle either; any truly unexpected shape just
    yields an empty dict, triggering a graceful fallback to our own
    season-average sketch.

    Raw stats are kept separate from scoring on purpose: Sleeper's public
    endpoint only exposes generic pts_std/pts_half_ppr/pts_ppr, which won't
    match what Sleeper's own app displays for a league with any custom
    scoring rules (non-standard PPR value, TE premium, bonus thresholds,
    etc.) — scoring the raw stat line against this league's actual
    scoring_settings gets much closer to what you'd see in Sleeper itself.
    """
    url = f"https://api.sleeper.app/projections/nfl/{season}/{week}?season_type=regular"
    try:
        data = get_json(url)
    except DataError:
        return {}

    def extract_stat_line(entry: Any) -> dict[str, float] | None:
        stats = entry.get("stats") if isinstance(entry, dict) else None
        if not isinstance(stats, dict):
            stats = entry if isinstance(entry, dict) else None
        if not isinstance(stats, dict):
            return None
        out = {}
        for k, v in stats.items():
            try:
                out[k] = float(v)
            except (TypeError, ValueError):
                continue
        return out or None

    raw: dict[str, dict[str, float]] = {}
    if isinstance(data, list):
        for entry in data:
            if not isinstance(entry, dict):
                continue
            pid = entry.get("player_id")
            if pid is None:
                pid = (entry.get("player") or {}).get("player_id")
            stat_line = extract_stat_line(entry)
            if pid is not None and stat_line:
                raw[str(pid)] = stat_line
    elif isinstance(data, dict):
        for pid, entry in data.items():
            stat_line = extract_stat_line(entry)
            if stat_line:
                raw[str(pid)] = stat_line

    return raw


def score_stat_line(stat_line: dict[str, float], scoring_settings: dict[str, Any]) -> float | None:
    """Generic fantasy-point scorer: Sleeper's stat-line keys (pass_yd,
    pass_td, rec, rec_yd, fum_lost, etc.) line up directly with the keys in
    scoring_settings, so a plain dot-product between the two reproduces
    whatever custom scoring rules this league actually uses — the same way
    Sleeper computes it internally — rather than assuming generic full PPR.
    """
    if not stat_line or not scoring_settings:
        return None
    total = 0.0
    matched = False
    for stat_key, value in stat_line.items():
        weight = scoring_settings.get(stat_key)
        if weight is None:
            continue
        try:
            total += float(value) * float(weight)
            matched = True
        except (TypeError, ValueError):
            continue
    return total if matched else None


def load_sleeper_projections(
    season: int, week: int, scoring_settings: dict[str, Any] | None = None
) -> dict[str, float]:
    """Player -> projected points for a week, scored against this league's
    real scoring settings when available (falling back to Sleeper's generic
    full-PPR total per player if custom scoring can't be computed for them).
    """
    raw = load_sleeper_raw_projections(season, week)
    projections: dict[str, float] = {}
    for pid, stat_line in raw.items():
        pts = score_stat_line(stat_line, scoring_settings) if scoring_settings else None
        if pts is None:
            pts = stat_line.get("pts_ppr") or stat_line.get("pts_half_ppr") or stat_line.get("pts_std")
        if pts is not None:
            projections[pid] = float(pts)
    return projections


def project_lineup_points(
    league_id: str, roster: dict[str, Any], through_week: int,
    season: int | None = None, week: int | None = None,
    scoring_settings: dict[str, Any] | None = None,
) -> tuple[float | None, str]:
    """Projected total for a roster's currently configured starters.

    Tries Sleeper's own real weekly projections first (source="sleeper") —
    the same numbers Sleeper's own app shows. Falls back to a self-computed
    season-average sketch (source="season_avg") if that's not available: no
    injury news, matchup context, or Vegas lines factored in, just each
    starter's own average points across completed weeks. Returns
    (None, "none") if there's nothing to work with either way.
    """
    starter_ids = [str(x) for x in (roster.get("starters") or []) if x and x != "0"]
    if not starter_ids:
        return None, "none"

    if season is not None and week is not None:
        sleeper_proj = load_sleeper_projections(season, week, scoring_settings)
        if sleeper_proj and any(pid in sleeper_proj for pid in starter_ids):
            total = sum(sleeper_proj.get(pid, 0.0) for pid in starter_ids)
            return total, "sleeper"

    if through_week <= 0:
        return None, "none"
    week_pts_by_player: dict[str, list[float]] = {}
    for wk in range(1, through_week + 1):
        for m in load_matchups(league_id, wk):
            if int(m.get("roster_id", -1)) != int(roster["roster_id"]):
                continue
            for pid, pts in (m.get("players_points") or {}).items():
                week_pts_by_player.setdefault(pid, []).append(float(pts))
    if not week_pts_by_player:
        return None, "none"
    total, counted = 0.0, 0
    for pid in starter_ids:
        vals = week_pts_by_player.get(pid)
        if vals:
            total += sum(vals) / len(vals)
            counted += 1
    return (total, "season_avg") if counted > 0 else (None, "none")


def compute_optimal_lineup_points(bundle: dict[str, Any], roster: dict[str, Any], week_points: dict[str, float]) -> float | None:
    """Best possible starting-lineup total that week from the FULL roster, respecting
    real position eligibility — used as the 'perfect lineup' baseline for Start/Sit Accuracy."""
    slot_labels = [s for s in (bundle["league"].get("roster_positions") or []) if s not in ("BN", "IR", "TAXI")]
    if not slot_labels:
        return None
    pool = []
    for pid in (roster.get("players") or []):
        pid = str(pid)
        pts = week_points.get(pid)
        if pts is None:
            continue
        meta = bundle["players"].get(pid, {}) or {}
        pool.append({"id": pid, "points": float(pts), "eligible": set(meta.get("fantasy_positions") or [])})
    if not pool:
        return None

    def slot_eligible(slot: str, elig: set[str]) -> bool:
        if slot in elig:
            return True
        if slot == "FLEX":
            return bool(elig & {"RB", "WR", "TE"})
        if slot == "SUPER_FLEX":
            return bool(elig & {"QB", "RB", "WR", "TE"})
        if slot == "REC_FLEX":
            return bool(elig & {"WR", "TE"})
        return False

    # Fill the most position-restrictive slots first (fewest eligible pool members).
    slot_order = sorted(slot_labels, key=lambda s: sum(1 for p in pool if slot_eligible(s, p["eligible"])))
    used: set[str] = set()
    total = 0.0
    for slot in slot_order:
        candidates = [p for p in pool if p["id"] not in used and slot_eligible(slot, p["eligible"])]
        if not candidates:
            continue
        best = max(candidates, key=lambda p: p["points"])
        total += best["points"]
        used.add(best["id"])
    return total


def optimal_lineup_assignment(
    bundle: dict[str, Any], roster: dict[str, Any], player_points: dict[str, float]
) -> list[dict[str, Any]]:
    """Same slot-eligibility logic as compute_optimal_lineup_points, but
    returns the full per-slot assignment (slot, player, position, points)
    instead of just the total — used for the matchup drill-down view.
    """
    slot_labels = [s for s in (bundle["league"].get("roster_positions") or []) if s not in ("BN", "IR", "TAXI")]
    if not slot_labels:
        return []
    pool = []
    for pid in (roster.get("players") or []):
        pid = str(pid)
        pts = player_points.get(pid)
        if pts is None:
            continue
        meta = bundle["players"].get(pid, {}) or {}
        name = meta.get("full_name") or " ".join(filter(None, [meta.get("first_name"), meta.get("last_name")])) or pid
        pool.append(
            {
                "id": pid, "points": float(pts), "name": name,
                "position": meta.get("position") or "",
                "eligible": set(meta.get("fantasy_positions") or []),
            }
        )
    if not pool:
        return []

    def slot_eligible(slot: str, elig: set[str]) -> bool:
        if slot in elig:
            return True
        if slot == "FLEX":
            return bool(elig & {"RB", "WR", "TE"})
        if slot == "SUPER_FLEX":
            return bool(elig & {"QB", "RB", "WR", "TE"})
        if slot == "REC_FLEX":
            return bool(elig & {"WR", "TE"})
        return False

    slot_order = sorted(slot_labels, key=lambda s: sum(1 for p in pool if slot_eligible(s, p["eligible"])))
    used: set[str] = set()
    assignment = []
    for slot in slot_order:
        candidates = [p for p in pool if p["id"] not in used and slot_eligible(slot, p["eligible"])]
        if not candidates:
            assignment.append({"slot": slot, "name": "Empty", "position": "", "points": None})
            continue
        best = max(candidates, key=lambda p: p["points"])
        used.add(best["id"])
        assignment.append(
            {"slot": slot, "name": best["name"], "position": best["position"], "points": best["points"]}
        )
    return assignment


def reorder_by_canonical_slots(assignment: list[dict[str, Any]], canonical_slots: list[str]) -> list[dict[str, Any]]:
    """Optimal lineup assignments are built by filling the most scarce slot
    first, which can put slots in a different order for two different teams
    (their eligible pools differ). Re-sort both into the league's actual slot
    order so a side-by-side comparison lines up QB-with-QB, RB-with-RB, etc.
    """
    pool = list(assignment)
    ordered = []
    for slot in canonical_slots:
        idx = next((i for i, a in enumerate(pool) if a["slot"] == slot), None)
        if idx is not None:
            ordered.append(pool.pop(idx))
    ordered.extend(pool)
    return ordered


def compute_start_sit_accuracy(
    bundle: dict[str, Any], league_id: str, my_roster: dict[str, Any], through_week: int
) -> tuple[float, int] | None:
    """Actual starter points vs. the best possible lineup from your full roster,
    averaged across every completed week this season."""
    actual_total, optimal_total, weeks_counted = 0.0, 0.0, 0
    for wk in range(1, max(through_week, 0) + 1):
        matchups = load_matchups(league_id, wk)
        entry = next((m for m in matchups if int(m.get("roster_id", -1)) == int(my_roster["roster_id"])), None)
        if not entry or entry.get("points") is None:
            continue
        optimal = compute_optimal_lineup_points(bundle, my_roster, entry.get("players_points") or {})
        if not optimal or optimal <= 0:
            continue
        actual_total += float(entry["points"])
        optimal_total += optimal
        weeks_counted += 1
    if weeks_counted == 0 or optimal_total <= 0:
        return None
    return round(actual_total / optimal_total * 100, 1), weeks_counted


def simulate_playoff_odds(bundle: dict[str, Any], teams_scores: pd.DataFrame, team: str, current_week: int, trials: int = 300) -> float | None:
    """A simple Monte Carlo playoff-odds estimate: real remaining schedule, scores drawn
    from each team's own season-average and variance so far. This is our own simulation,
    not a licensed odds product — treat it as directional."""
    settings = bundle["league"].get("settings") or {}
    playoff_week_start = int(settings.get("playoff_week_start") or 15)
    playoff_teams_n = int(settings.get("playoff_teams") or 6)
    league_id = str(bundle["league"].get("league_id") or LEAGUE_ID)
    proj_season = int(bundle["league"].get("season") or 2026)

    users = {str(u.get("user_id")): team_name(u) for u in bundle["users"]}
    roster_to_team = {int(r["roster_id"]): users.get(str(r.get("owner_id")), f"Roster {r['roster_id']}") for r in bundle["rosters"]}
    all_teams = list(roster_to_team.values())
    if team not in all_teams:
        return None

    base_wins = {
        roster_to_team.get(int(r["roster_id"])): int((r.get("settings") or {}).get("wins") or 0)
        for r in bundle["rosters"]
    }
    stats = teams_scores.groupby("Team")["Points"].agg(["mean", "std"]) if not teams_scores.empty else pd.DataFrame()

    remaining_weeks = list(range(max(current_week, 1), playoff_week_start))
    weekly_proj = build_weekly_team_projections(bundle, remaining_weeks, proj_season, roster_to_team)

    remaining_schedule: list[tuple[int, list[tuple[str, str]]]] = []
    for wk in remaining_weeks:
        matchups = load_matchups(league_id, wk)
        if not matchups:
            continue
        pairs: dict[Any, list[str]] = {}
        for m in matchups:
            mid, rid = m.get("matchup_id"), m.get("roster_id")
            if mid is None or rid is None:
                continue
            pairs.setdefault(mid, []).append(roster_to_team.get(int(rid), f"Roster {rid}"))
        week_pairs = [tuple(v) for v in pairs.values() if len(v) == 2]
        remaining_schedule.append((wk, week_pairs))

    if not remaining_schedule:
        ranked = sorted(all_teams, key=lambda t: -base_wins.get(t, 0))
        return 100.0 if team in ranked[:playoff_teams_n] else 0.0

    def team_score_for_week(t: str, wk: int) -> float:
        wk_proj = weekly_proj.get(wk, {}).get(t)
        if wk_proj is not None:
            mean = wk_proj
        elif t in stats.index and pd.notna(stats.loc[t, "mean"]):
            mean = float(stats.loc[t, "mean"])
        else:
            mean = 100.0
        std = max(float(stats.loc[t, "std"]) if t in stats.index and pd.notna(stats.loc[t, "std"]) else 30.0, 8.0)
        return random.gauss(mean, std)

    makes_playoffs = 0
    for _ in range(trials):
        wins = dict(base_wins)
        for wk, week_pairs in remaining_schedule:
            for a, b in week_pairs:
                if team_score_for_week(a, wk) >= team_score_for_week(b, wk):
                    wins[a] = wins.get(a, 0) + 1
                else:
                    wins[b] = wins.get(b, 0) + 1
        ranked = sorted(all_teams, key=lambda t: -wins.get(t, 0))
        if team in ranked[:playoff_teams_n]:
            makes_playoffs += 1
    return round(makes_playoffs / trials * 100, 1)


def simulate_bracket_once(
    seeds: list[str], team_mean: Any, team_std: Any
) -> str:
    """One trial of a standard fantasy playoff bracket, static seeding (no
    reseeding between rounds). Handles the common 2/4/6/8-team formats
    explicitly; anything unusual falls back to a single simulated high score."""
    n = len(seeds)
    if n <= 1:
        return seeds[0] if seeds else ""

    def draw(t: str) -> float:
        return random.gauss(team_mean(t), team_std(t))

    def head_to_head(a: str, b: str) -> str:
        sa, sb = draw(a), draw(b)
        return a if sa >= sb else b

    if n == 2:
        return head_to_head(seeds[0], seeds[1])
    if n == 4:
        w1 = head_to_head(seeds[0], seeds[3])
        w2 = head_to_head(seeds[1], seeds[2])
        return head_to_head(w1, w2)
    if n == 6:
        # Top 2 seeds get a bye into the semifinals.
        w36 = head_to_head(seeds[2], seeds[5])
        w45 = head_to_head(seeds[3], seeds[4])
        sf1 = head_to_head(seeds[0], w45)
        sf2 = head_to_head(seeds[1], w36)
        return head_to_head(sf1, sf2)
    if n == 8:
        w18 = head_to_head(seeds[0], seeds[7])
        w45 = head_to_head(seeds[3], seeds[4])
        w27 = head_to_head(seeds[1], seeds[6])
        w36 = head_to_head(seeds[2], seeds[5])
        sf1 = head_to_head(w18, w45)
        sf2 = head_to_head(w27, w36)
        return head_to_head(sf1, sf2)
    # Unusual bracket size — no defined structure, so just take the best
    # single simulated score among the seeds as a rough stand-in.
    return max(seeds, key=draw)


def build_weekly_team_projections(
    bundle: dict[str, Any], weeks: list[int], season: int, roster_to_team: dict[int, str]
) -> dict[int, dict[str, float]]:
    """Real per-week optimal-lineup projected totals for every team, across a
    range of weeks — using Sleeper's actual weekly projections, which vary
    week to week (byes, injury designations, matchup-specific news), rather
    than a single static number reused for the whole rest of the season.
    """
    scoring_settings = bundle["league"].get("scoring_settings")
    result: dict[int, dict[str, float]] = {}
    for wk in weeks:
        sleeper_proj = load_sleeper_projections(season, wk, scoring_settings)
        week_totals: dict[str, float] = {}
        if sleeper_proj:
            for r in bundle["rosters"]:
                team = roster_to_team.get(int(r["roster_id"]))
                if not team:
                    continue
                proj = optimal_projected_lineup(bundle, r, sleeper_proj)
                if proj is not None:
                    week_totals[team] = proj
        result[wk] = week_totals
    return result


def simulate_full_league(
    bundle: dict[str, Any],
    teams_scores: pd.DataFrame,
    current_week: int,
    trials: int = 500,
    variance_mult: float = 1.0,
    mean_adjustments: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Full-league Monte Carlo season + playoff simulation: real remaining
    schedule from Sleeper, each team's score drawn from its own season mean/
    variance (optionally nudged), tracking average final wins, playoff odds,
    and championship odds for every team at once. This is our own simulation
    — a modeling exercise, not a licensed odds product.

    The playoff bracket assumes standard static seeding (no reseeding between
    rounds) for 2/4/6/8-team playoff fields — the most common fantasy
    formats. If your league uses a different bracket structure, treat the
    championship odds as directional rather than exact.
    """
    settings = bundle["league"].get("settings") or {}
    playoff_week_start = int(settings.get("playoff_week_start") or 15)
    playoff_teams_n = int(settings.get("playoff_teams") or 6)
    league_id = str(bundle["league"].get("league_id") or LEAGUE_ID)
    proj_season = int(bundle["league"].get("season") or 2026)
    mean_adjustments = mean_adjustments or {}

    users = {str(u.get("user_id")): team_name(u) for u in bundle["users"]}
    roster_to_team = {
        int(r["roster_id"]): users.get(str(r.get("owner_id")), f"Roster {r['roster_id']}")
        for r in bundle["rosters"]
    }
    all_teams = list(roster_to_team.values())
    if not all_teams:
        return pd.DataFrame()

    base_wins = {
        roster_to_team.get(int(r["roster_id"])): int((r.get("settings") or {}).get("wins") or 0)
        for r in bundle["rosters"]
    }
    base_pf = {
        roster_to_team.get(int(r["roster_id"])): float((r.get("settings") or {}).get("fpts") or 0)
        for r in bundle["rosters"]
    }
    stats = teams_scores.groupby("Team")["Points"].agg(["mean", "std"]) if not teams_scores.empty else pd.DataFrame()

    # Real schedule + a REAL projection for every remaining week — each
    # week's simulated matchup draws from that specific week's actual
    # projected total per team (byes, injury designations, and week-specific
    # news all naturally reflected), not one static number reused all season.
    remaining_weeks = list(range(max(current_week, 1), playoff_week_start))
    weekly_proj = build_weekly_team_projections(bundle, remaining_weeks, proj_season, roster_to_team)

    remaining_schedule: list[tuple[int, list[tuple[str, str]]]] = []
    for wk in remaining_weeks:
        matchups = load_matchups(league_id, wk)
        if not matchups:
            continue
        pairs: dict[Any, list[str]] = {}
        for m in matchups:
            mid, rid = m.get("matchup_id"), m.get("roster_id")
            if mid is None or rid is None:
                continue
            pairs.setdefault(mid, []).append(roster_to_team.get(int(rid), f"Roster {rid}"))
        week_pairs = [tuple(v) for v in pairs.values() if len(v) == 2]
        remaining_schedule.append((wk, week_pairs))

    def team_std(t: str) -> float:
        if t in stats.index and pd.notna(stats.loc[t, "std"]):
            base = float(stats.loc[t, "std"])
        else:
            # No real variance data yet — a generic full-lineup weekly std,
            # calibrated earlier against real dynasty-tool win% displays.
            base = 30.0
        return max(base, 8.0) * variance_mult

    def team_mean_for_week(t: str, wk: int) -> float:
        wk_proj = weekly_proj.get(wk, {}).get(t)
        if wk_proj is not None:
            base = wk_proj
        elif t in stats.index and pd.notna(stats.loc[t, "mean"]):
            base = float(stats.loc[t, "mean"])
        else:
            base = 100.0
        return base * (1 + mean_adjustments.get(t, 0.0) / 100.0)

    def team_overall_mean(t: str) -> float:
        # Used only for the playoff bracket, which sits further out than
        # Sleeper's real per-week projection horizon usually reaches —
        # averages whatever real per-week projections we do have for this
        # team across the regular season, falling back the same way as above.
        vals = [weekly_proj[wk][t] for wk in remaining_weeks if t in weekly_proj.get(wk, {})]
        if vals:
            base = sum(vals) / len(vals)
        elif t in stats.index and pd.notna(stats.loc[t, "mean"]):
            base = float(stats.loc[t, "mean"])
        else:
            base = 100.0
        return base * (1 + mean_adjustments.get(t, 0.0) / 100.0)

    playoff_count = {t: 0 for t in all_teams}
    champ_count = {t: 0 for t in all_teams}
    win_totals = {t: 0 for t in all_teams}
    seed_totals = {t: 0 for t in all_teams}

    for _ in range(trials):
        wins = dict(base_wins)
        pf = dict(base_pf)
        for wk, week_pairs in remaining_schedule:
            for a, b in week_pairs:
                sa = random.gauss(team_mean_for_week(a, wk), team_std(a))
                sb = random.gauss(team_mean_for_week(b, wk), team_std(b))
                pf[a] = pf.get(a, 0) + sa
                pf[b] = pf.get(b, 0) + sb
                if sa >= sb:
                    wins[a] = wins.get(a, 0) + 1
                else:
                    wins[b] = wins.get(b, 0) + 1

        ranked = sorted(all_teams, key=lambda t: (-wins.get(t, 0), -pf.get(t, 0)))
        for i, t in enumerate(ranked):
            win_totals[t] += wins.get(t, 0)
            seed_totals[t] += i + 1

        seeds = ranked[: min(playoff_teams_n, len(ranked))]
        for t in seeds:
            playoff_count[t] += 1
        champion = simulate_bracket_once(seeds, team_overall_mean, team_std)
        if champion:
            champ_count[champion] += 1

    rows = [
        {
            "Team": t,
            "Avg Final Wins": round(win_totals[t] / trials, 1),
            "Avg Seed": round(seed_totals[t] / trials, 1),
            "Playoff Odds": round(playoff_count[t] / trials * 100, 1),
            "Champion Odds": round(champ_count[t] / trials * 100, 1),
        }
        for t in all_teams
    ]
    return pd.DataFrame(rows).sort_values("Champion Odds", ascending=False).reset_index(drop=True)


def build_player_avg_lookup(league_id: str, through_week: int) -> dict[str, float]:
    """League-wide season-average points per player, built from every team's
    completed-week matchup data — used to fill in projections for players
    Sleeper's own projections endpoint doesn't cover."""
    per_player: dict[str, list[float]] = {}
    for wk in range(1, through_week + 1):
        for m in load_matchups(league_id, wk):
            for pid, pts in (m.get("players_points") or {}).items():
                per_player.setdefault(pid, []).append(float(pts))
    return {pid: sum(v) / len(v) for pid, v in per_player.items() if v}


def optimal_projected_lineup(
    bundle: dict[str, Any], roster: dict[str, Any], player_projections: dict[str, float]
) -> float | None:
    """The BEST possible lineup a team could set from its full roster, given a
    projection for each player — not whatever they've actually got starting
    right now. Reuses the same slot-eligibility logic as Start/Sit Accuracy,
    just fed projected points instead of actual results.
    """
    return compute_optimal_lineup_points(bundle, roster, player_projections)


def matchup_win_probability(mean_a: float, mean_b: float, std_a: float = 35.0, std_b: float = 35.0) -> float:
    """P(team A outscores team B), assuming each team's score is roughly
    normally distributed around its projection. A fixed default std is used
    when there's no real season data yet to estimate one (e.g. Week 1)."""
    combined_std = math.sqrt(std_a**2 + std_b**2)
    if combined_std <= 0:
        return 1.0 if mean_a > mean_b else (0.0 if mean_a < mean_b else 0.5)
    z = (mean_a - mean_b) / combined_std
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def build_full_week_board(
    bundle: dict[str, Any], week: int, roster_to_team: dict[int, str],
    season: int, completed_weeks: int,
) -> pd.DataFrame:
    """Every real matchup pairing for a given week, with each team's BEST
    POSSIBLE lineup total (optimal-lineup projection, not their currently-set
    real starters), plus a win probability for each side.
    """
    league_id = str(bundle["league"].get("league_id") or LEAGUE_ID)
    matchups = load_matchups(league_id, week)
    if not matchups:
        return pd.DataFrame()

    sleeper_proj = load_sleeper_projections(season, week, bundle["league"].get("scoring_settings"))
    season_avg = build_player_avg_lookup(league_id, completed_weeks) if completed_weeks > 0 else {}
    combined_proj = {**season_avg, **sleeper_proj}  # Sleeper's real numbers win where both exist

    stats = build_weekly_scores(league_id, roster_to_team, completed_weeks)
    team_stats = stats.groupby("Team")["Points"].agg(["mean", "std"]) if not stats.empty else pd.DataFrame()

    def std_for(team: str) -> float:
        if team in team_stats.index and pd.notna(team_stats.loc[team, "std"]):
            return max(float(team_stats.loc[team, "std"]), 8.0)
        return 35.0  # realistic full-lineup weekly std dev when there's no real variance data yet

    roster_by_id = {int(r["roster_id"]): r for r in bundle["rosters"]}
    by_matchup: dict[Any, list[dict[str, Any]]] = {}
    for m in matchups:
        mid = m.get("matchup_id")
        if mid is None:
            continue
        by_matchup.setdefault(mid, []).append(m)

    rows = []
    for mid, entries in by_matchup.items():
        if len(entries) != 2:
            continue
        proj_by_side = []
        for m in entries:
            rid = m.get("roster_id")
            roster = roster_by_id.get(int(rid)) if rid is not None else None
            team = roster_to_team.get(int(rid), f"Roster {rid}") if rid is not None else "Unknown"
            proj = optimal_projected_lineup(bundle, roster, combined_proj) if roster else None
            proj_by_side.append((team, proj, rid))

        (team_a, proj_a, rid_a), (team_b, proj_b, rid_b) = proj_by_side
        pa = proj_a if proj_a is not None else 100.0
        pb = proj_b if proj_b is not None else 100.0
        win_a = matchup_win_probability(pa, pb, std_for(team_a), std_for(team_b))

        rows.append(
            {
                "Matchup ID": mid,
                "Team A": team_a, "Proj A": proj_a, "Win % A": round(win_a * 100, 1), "Roster ID A": rid_a,
                "Team B": team_b, "Proj B": proj_b, "Win % B": round((1 - win_a) * 100, 1), "Roster ID B": rid_b,
            }
        )
    return pd.DataFrame(rows)


    return pd.DataFrame(rows)


def build_waiver_targets(bundle: dict[str, Any], players: pd.DataFrame, limit: int = 8) -> pd.DataFrame:
    """League-wide trending Sleeper adds, filtered to players not already rostered here."""
    trending = load_trending_adds()
    if not trending:
        return pd.DataFrame()
    rostered_ids = set(players["Sleeper ID"].astype(str))
    rows = []
    for t in trending:
        pid = str(t.get("player_id"))
        if pid in rostered_ids:
            continue
        p = bundle["players"].get(pid, {}) or {}
        if (p.get("position") or "") not in {"QB", "RB", "WR", "TE"}:
            continue
        name = p.get("full_name") or " ".join(filter(None, [p.get("first_name"), p.get("last_name")])) or pid
        rows.append(
            {
                "Player": name, "Position": p.get("position"), "NFL Team": p.get("team") or "FA",
                "Adds": int(t.get("count") or 0), "Image": player_image_url({"player_id": pid}),
            }
        )
        if len(rows) >= limit:
            break
    return pd.DataFrame(rows)


def build_injury_report(bundle: dict[str, Any], players: pd.DataFrame, team: str) -> pd.DataFrame:
    """Real injury flags from Sleeper's own player metadata for this team's roster."""
    roster = players[players["Team"] == team]
    rows = []
    for _, r in roster.iterrows():
        meta = bundle["players"].get(r["Sleeper ID"], {}) or {}
        status = meta.get("injury_status")
        if not status:
            continue
        rows.append(
            {
                "Player": r["Player"], "Position": r["Position"], "Status": status,
                "Note": meta.get("injury_body_part") or "", "Image": r["Image"],
            }
        )
    return pd.DataFrame(rows)


def official_draft_order(
    drafts: list[dict[str, Any]],
    season: int,
    users: dict[str, str],
) -> list[str]:
    """The commissioner-set draft order from Sleeper, if one exists for this season.

    Sleeper stores this on the draft object as draft_order: a dict mapping
    user_id -> 1-indexed slot number. This reflects manual reordering (e.g. a
    league using a set order rather than reverse-standings) and should take
    priority over any computed order.
    """
    for d in drafts:
        if str(d.get("season")) != str(season):
            continue
        order_map = d.get("draft_order") or {}
        if not order_map:
            continue
        slots = sorted(order_map.items(), key=lambda kv: kv[1])
        return [users.get(str(uid), str(uid)) for uid, _ in slots]
    return []


def standings_order(rosters: list[dict[str, Any]], roster_to_team: dict[int, str]) -> pd.DataFrame:
    """Teams sorted worst-to-first by record, the standard rookie-draft slotting rule."""
    rows = []
    for r in rosters:
        settings = r.get("settings") or {}
        wins = int(settings.get("wins") or 0)
        losses = int(settings.get("losses") or 0)
        ties = int(settings.get("ties") or 0)
        fpts = float(settings.get("fpts") or 0) + float(settings.get("fpts_decimal") or 0) / 100
        games = max(wins + losses + ties, 1)
        roster_id = int(r.get("roster_id"))
        rows.append(
            {
                "Team": roster_to_team.get(roster_id, f"Roster {roster_id}"),
                "Wins": wins,
                "Losses": losses,
                "Ties": ties,
                "Points": round(fpts, 1),
                "Win %": round(wins / games, 3),
            }
        )
    return (
        pd.DataFrame(rows)
        .sort_values(["Win %", "Points"], ascending=[True, True])
        .reset_index(drop=True)
    )


def simulate_mock_draft(
    picks: pd.DataFrame,
    teams: pd.DataFrame,
    rookies: pd.DataFrame,
    order: list[str],
    season: int,
    rounds: int,
    need_weight: float,
) -> pd.DataFrame:
    """Assign the rookie pool to picks for one season, respecting real pick ownership.

    `order` lists original-slot teams worst-to-best record. For every round
    we look up who currently owns each original team's pick (so prior trades
    are reflected via the existing picks table), then select from the
    remaining rookie pool. need_weight of 0 is pure best-player-available;
    1 leans hard on filling each team's weakest positional room.
    """
    if rookies.empty or not order:
        return pd.DataFrame()

    board = picks[(picks["Season"] == season) & (picks["Round"] <= rounds)]
    if board.empty:
        return pd.DataFrame()

    pool = rookies.sort_values("Prospect Rank").to_dict("records")
    team_names = set(teams["Team"])
    results = []

    for rnd in sorted(board["Round"].unique()):
        for slot_idx, original_team in enumerate(order, start=1):
            row = board[(board["Round"] == rnd) & (board["Original Team"] == original_team)]
            if row.empty or not pool:
                continue
            current_owner = row.iloc[0]["Current Owner"]
            profile = positional_profile(teams, current_owner) if current_owner in team_names else {}

            def score(p: dict[str, Any], profile: dict[str, int] = profile) -> float:
                base = -p["Prospect Rank"]
                need_rank = profile.get(p["Position"], 6)
                return base + need_rank * need_weight * 3

            pool.sort(key=score, reverse=True)
            selection = pool.pop(0)

            reason = "Best player available"
            if profile:
                weakest = max(["QB", "RB", "WR", "TE"], key=lambda pos: profile.get(pos, 6))
                if selection["Position"] == weakest:
                    reason = f"Fills the {weakest} need (currently ranked #{profile[weakest]})"

            results.append(
                {
                    "Season": season,
                    "Round": int(rnd),
                    "Slot": slot_idx,
                    "Overall": (int(rnd) - 1) * len(order) + slot_idx,
                    "Team": current_owner,
                    "Original Slot Team": original_team,
                    "Player": selection["Player"],
                    "Position": selection["Position"],
                    "Prospect Rank": selection["Prospect Rank"],
                    "Value": selection["Value"],
                    "Image": selection["Image"],
                    "Reason": reason,
                }
            )

    return pd.DataFrame(results)


def render_mock_draft(
    bundle: dict[str, Any],
    fc_rows: list[dict[str, Any]],
    picks: pd.DataFrame,
    teams: pd.DataFrame,
) -> None:
    render_brand("Mock Draft", "Rookie-only simulated draft using pick ownership and team needs")

    render_html(
        '<div class="gm-card"><b>How this works:</b> draft slots are ordered worst-to-first by '
        "record (the standard rookie-draft rule), then matched to whoever currently owns that "
        "pick after trades. Rookies are pulled live from Sleeper and ranked by FantasyCalc dynasty "
        "value where the market has priced them. This is a simulation, not a prediction of the "
        "real draft.</div>"
    )

    league = bundle["league"]
    users = {str(u.get("user_id")): team_name(u) for u in bundle["users"]}
    roster_to_team = {
        int(r["roster_id"]): users.get(str(r.get("owner_id")), f"Roster {r['roster_id']}")
        for r in bundle["rosters"]
    }

    seasons = sorted(picks["Season"].unique())
    default_season = int(league.get("season") or seasons[0])

    c1, c2, c3 = st.columns([1, 1, 1.4])
    with c1:
        season = st.selectbox(
            "Draft season",
            seasons,
            index=seasons.index(default_season) if default_season in seasons else 0,
        )
    with c2:
        max_rounds = int(picks["Round"].max())
        rounds = st.number_input("Rounds", min_value=1, max_value=max_rounds, value=min(3, max_rounds))
    with c3:
        strategy = st.slider(
            "Draft strategy",
            0.0, 1.0, 0.35,
            help="0 = pure best-player-available, 1 = heavily need-based",
        )

    use_previous = st.checkbox(
        "Base draft order on last season's final standings (previous league history) "
        "instead of the current live record",
        value=True,
    )

    drafts = load_league_drafts(str(league.get("league_id") or LEAGUE_ID))
    order = official_draft_order(drafts, int(season), users)
    used_official_order = bool(order)

    if order:
        st.success(
            f"Using the official {int(season)} draft order set in Sleeper "
            "(commissioner-configured, not computed)."
        )
        order_df = pd.DataFrame({"Slot": range(1, len(order) + 1), "Team": order})
    else:
        order_df = pd.DataFrame()
        if use_previous:
            previous_rosters = load_previous_rosters(league.get("previous_league_id"))
            if previous_rosters:
                order_df = standings_order(previous_rosters, roster_to_team)
            else:
                st.info(
                    "No previous-season standings were found for this league; "
                    "using the current record instead."
                )
        if order_df.empty:
            order_df = standings_order(bundle["rosters"], roster_to_team)
        st.caption(
            "No official draft order is set for this season in Sleeper yet, "
            "so this order is estimated from standings."
        )
        order = order_df["Team"].tolist()

    with st.expander("Draft order basis"):
        st.dataframe(order_df, hide_index=True, use_container_width=True)

    rookies = build_rookies(bundle, fc_rows, int(season), default_season)
    devy_pool = build_devy_pool(load_devy_prospects(), int(season))

    using_devy_pool = False
    if int(season) > default_season and len(rookies) < 12 and not devy_pool.empty:
        rookies = devy_pool.drop(columns="Notes")
        using_devy_pool = True
        render_html(
            f'<div class="gm-card"><b>Using a devy consensus board for {int(season)}:</b> '
            "Sleeper doesn't have real NFL players for this class yet, since the actual draft "
            "hasn't happened. This pool is aggregated from public dynasty rookie mock-draft "
            "coverage (Dynasty Nerds, Dynasty League Football, DraftSharks, FootballGuys forums, "
            "Roto Street Journal, FlurrySports, NFL Mock Draft Database) as of when "
            f"<code>{clean(DEVY_PROSPECTS_PATH)}</code> was last updated. Treat it as directional "
            "— players will transfer, get injured, declare early, or return to school between now "
            "and the real draft. Refresh the CSV from current mock drafts periodically.</div>"
        )
    elif int(season) > default_season:
        st.warning(
            f"The {int(season)} rookie class won't be finalized until after the {int(season)} "
            "NFL Draft (roughly next April). Sleeper only lists real, drafted NFL players, so "
            "college underclassmen and other future-class prospects generally aren't in its "
            "database yet, and no devy fallback list was found for this season either. Add rows "
            f"for {int(season)} to {DEVY_PROSPECTS_PATH} to enable a mock draft this far out."
        )
    if rookies.empty:
        st.warning("No rookie-eligible players were found for this season.")
        return

    with st.expander(f"Rookie pool ({len(rookies)} players)"):
        if using_devy_pool:
            st.caption("Source: curated devy consensus board, not live Sleeper data.")
        st.dataframe(
            rookies[["Prospect Rank", "Player", "Position", "NFL Team", "Age", "Value"]],
            hide_index=True,
            use_container_width=True,
            height=420,
        )

    state_key = f"mock_draft_{season}_{rounds}_{strategy}_{'official' if used_official_order else use_previous}"
    if st.button("Generate mock draft", use_container_width=True) or state_key not in st.session_state:
        st.session_state[state_key] = simulate_mock_draft(
            picks, teams, rookies, order, int(season), int(rounds), strategy
        )

    board = st.session_state.get(state_key, pd.DataFrame())
    if board.empty:
        st.info("No picks were available to simulate for this season/round combination.")
        return

    for rnd in sorted(board["Round"].unique()):
        render_html(f'<div class="section-title"><h3>Round {int(rnd)}</h3></div>')
        round_rows = board[board["Round"] == rnd].sort_values("Slot")
        cards = "".join(
            f"""
            <div class="draft-pick-card">
              <div class="draft-pick-top">
                <span class="draft-pick-overall">#{int(r["Overall"])}</span>
                <span class="pos-pill {pos_class(r["Position"])}">{clean(r["Position"])}</span>
              </div>
              <div class="draft-pick-photo">
                <img src="{clean(r["Image"])}"
                     onerror="this.onerror=null;this.src='https://a.espncdn.com/i/teamlogos/leagues/500/nfl.png';">
              </div>
              <div class="draft-pick-body">
                <div class="draft-pick-name">{clean(r["Player"])}</div>
                <div class="draft-pick-team">{clean(r["Team"])}</div>
                <div class="draft-pick-reason">{clean(r["Reason"])}</div>
              </div>
            </div>
            """
            for _, r in round_rows.iterrows()
        )
        render_html(f'<div class="draft-round-grid">{cards}</div>')

    st.download_button(
        "Download mock draft as CSV",
        board[
            ["Overall", "Round", "Slot", "Team", "Player", "Position", "Prospect Rank", "Reason"]
        ].to_csv(index=False),
        file_name=f"mock_draft_{season}.csv",
        mime="text/csv",
        use_container_width=True,
    )


def main() -> None:
    st.sidebar.markdown("## 🏈 Front Office")
    page = st.sidebar.radio(
        "Navigation",
        ["My Team", "Team Blueprint", "League", "League Projections", "League Analyzer", "Rankings", "Team Needs", "Roster Lab", "Draft Capital", "Draft History", "Trade History", "Mock Draft"],
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
        render_team_review(bundle, teams, players, picks, bundle["league"].get("name", "Weekend Warriors"))
    elif page == "Team Blueprint":
        render_team_blueprint(bundle, teams, players, picks)
    elif page == "League":
        render_power_rankings(teams, players, picks)
    elif page == "League Projections":
        render_league_projections(bundle, teams, players)
    elif page == "League Analyzer":
        render_league_analyzer(bundle, teams, players)
    elif page == "Rankings":
        render_rankings(players)
    elif page == "Team Needs":
        render_team_needs(bundle, fc_rows, teams, players, picks)
    elif page == "Roster Lab":
        render_roster_lab(bundle, fc_rows, teams, players, picks)
    elif page == "Draft Capital":
        render_draft(picks, teams)
    elif page == "Draft History":
        render_draft_history(bundle)
    elif page == "Trade History":
        render_trade_history(bundle, teams)
    else:
        render_mock_draft(bundle, fc_rows, picks, teams)


if __name__ == "__main__":
    main()
