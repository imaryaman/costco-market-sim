"""
Costco Market Simulator - Streamlit demo for BMS5213 Group Project Part 4.
Run:  streamlit run app.py
"""
import html
import json
import os

import altair as alt
import pandas as pd
import streamlit as st

from market import SHOPPERS, CATALOGUE, COSTCO_AGENT, WALMART_AGENT, PLATFORM_AGENT, SUPPLIER_AGENT, SHARED_TASK
from sim import (offers_for, run_all, compare_runs, gemini_llm, replay_llm, recording)

HERE = os.path.dirname(os.path.abspath(__file__))
SAVED_RUNS = {"Live Gemini run (gemini-3.5-flash)": os.path.join(HERE, "results", "live_run_gemini.json"),
              "First test run (Claude as the agents)": os.path.join(HERE, "results", "reference_run_claude.json")}
RED, NAVY, INK, MUTED, LINE, PAPER = "#b3121e", "#12386f", "#16202e", "#5b6878", "#dfe4ec", "#ffffff"
D = "&#36;"  # dollar sign that never triggers Streamlit's LaTeX


def esc(x):
    return html.escape(str(x)).replace("$", D)


st.set_page_config(page_title="Costco Market Simulator", page_icon="🛒", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;800;900&family=Inter:wght@400;500;600;700&display=swap');
:root { --display: 'Archivo', 'Arial Black', 'Helvetica Neue', Arial, sans-serif; --body: 'Inter', 'Helvetica Neue', Arial, sans-serif; --red: RED; --navy: NAVY; --ink: INK; --muted: MUTED; --line: LINE; }
.stApp { background: #f6f7fa; }
.stApp, .stApp p, .stApp li, .stApp label, .stApp div, .stApp td, .stApp th { font-family: var(--body); color: var(--ink); }
[data-testid="stIconMaterial"], .material-symbols-rounded, [data-testid="stExpanderToggleIcon"] { font-family: 'Material Symbols Rounded' !important; }
.block-container { padding-top: 3.6rem; max-width: 1280px; }
h1, h2, h3, h4 { font-family: var(--display) !important; }

/* top strip like the slide header */
.topstrip { display:flex; justify-content:space-between; font-size:.82rem; font-weight:600; color: var(--ink);
            letter-spacing:.2px; padding: 0 2px 14px; border-bottom: 1px solid var(--line); margin-bottom: 26px; }
.topstrip span { color: var(--muted) !important; }

/* hero */
.hero { display:grid; grid-template-columns: 1.35fr 1fr; gap: 34px; align-items: center; margin-bottom: 30px; }
.eyebrow { display:inline-flex; align-items:center; gap:10px; font: 700 .78rem var(--body); letter-spacing: 2px;
           color: var(--red) !important; text-transform: uppercase; margin-bottom: 14px; }
.headline { font-family: var(--display); font-weight: 900; font-size: clamp(2.8rem, 5.6vw, 5rem); line-height: .92;
            letter-spacing: -2.5px; text-transform: uppercase; margin: 0; }
.headline .n { color: var(--navy) !important; } .headline .r { color: var(--red) !important; }
.lede { font-size: 1.08rem; line-height: 1.6; color: #344152 !important; margin: 20px 0 18px; max-width: 620px; }
.promise { display:inline-block; background:#fff; border:1px solid var(--line); border-radius: 999px; padding: 9px 18px;
           font-weight: 600; font-size: .95rem; }
.promise b { color: var(--red) !important; }
.scoreboard { background: var(--navy); border-radius: 22px; padding: 26px 28px; box-shadow: 0 18px 40px rgba(18,56,111,.22); }
.scoreboard .lbl { color: #b9c8e0 !important; font: 700 .74rem var(--body); letter-spacing: 1.6px; text-transform: uppercase; }
.scoreboard .row { display:grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 16px; }
.scoreboard .big { font-family: var(--display); font-weight:900; font-size: 2.6rem; color:#fff !important; line-height:1; letter-spacing:-1px; }
.scoreboard .cap { color:#d6e0ef !important; font-size:.84rem; margin-top:6px; line-height:1.3; }
.scoreboard .foot { color:#9fb2cf !important; font-size:.78rem; margin-top:18px; border-top:1px solid rgba(255,255,255,.15); padding-top: 12px; }

/* pill motif from the slides: red ring + navy bar */
.motif { display:inline-flex; align-items:center; vertical-align: middle; }
.motif i { width:13px; height:13px; border:3px solid var(--red); border-radius:50%; background:#fff; display:inline-block; z-index:1; }
.motif b { width:34px; height:10px; background: var(--navy); border-radius: 0 6px 6px 0; margin-left:-3px; display:inline-block; }

/* section headings like the slide titles */
.sec { margin: 8px 0 18px; }
.sec h2 { font-family: var(--display); font-weight:900; text-transform:uppercase; letter-spacing:-1px; color: var(--navy) !important;
          font-size: 2.05rem; margin: 6px 0 2px; padding: 0; }
.sec p { color: var(--red) !important; font-weight: 600; margin: 0; font-size: .98rem; }

/* tabs */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] { font-family: var(--display) !important; font-weight: 800; text-transform: uppercase; letter-spacing: .3px;
          padding: 10px 16px; border-radius: 10px 10px 0 0; }
.stTabs [data-baseweb="tab"] p { font-family: var(--display) !important; font-weight: 800 !important; font-size: .92rem !important; }
.stTabs [aria-selected="true"] { background: #fff; }
.stTabs [aria-selected="true"] p, [data-testid="stTab"][aria-selected="true"] p { color: var(--red) !important; }
[data-testid="stTab"] p, .stTabs [role="tab"] p { font-family: var(--display) !important; font-weight: 800 !important; text-transform: uppercase; font-size: .9rem !important; letter-spacing: .3px; }
.stTabs [data-baseweb="tab-highlight"], [data-testid="stTab"] .react-aria-SelectionIndicator { background: var(--red) !important; }

/* cards */
.card { background:#fff; border:1px solid var(--line); border-radius: 18px; padding: 20px 22px; height: 100%;
        box-shadow: 0 1px 2px rgba(22,32,46,.04); }
.card h4 { margin: 0 0 4px; color: var(--navy) !important; font-size: 1.22rem; font-weight: 800; }
.muted { color: var(--muted) !important; font-size: .93rem; line-height: 1.5; }
.avatar { width:54px; height:54px; border-radius: 50%; display:flex; align-items:center; justify-content:center;
          font-size: 1.7rem; background:#eef2f8; margin-bottom: 12px; }
.chips { display:flex; flex-wrap:wrap; gap:6px; margin-top: 14px; }
.chip { font-size: .78rem; font-weight: 600; padding: 4px 10px; border-radius: 999px; background:#eef2f8; color: var(--navy) !important; }
.chip.red { background:#fbe7e9; color: var(--red) !important; } .chip.grey { background:#eef0f3; color: var(--muted) !important; }
.chip.green { background:#e3f4ea; color:#17773f !important; }
.task { background: var(--navy); border-radius: 18px; padding: 18px 24px; margin: 4px 0 22px; display:flex; gap:18px; align-items:center; }
.task .k { color:#ffd3d7 !important; font: 800 .76rem var(--body); letter-spacing: 1.6px; white-space: nowrap; }
.task .v { color:#fff !important; font-size: 1.05rem; font-weight: 500; }
.agentcard { background:#fff; border:1px solid var(--line); border-radius:18px; padding: 18px 20px; height:100%; }
.agentcard .ic { font-size: 1.5rem; } .agentcard h5 { font-family: var(--display); font-weight:800; color:var(--navy)!important; margin:8px 0 6px; font-size:1.02rem; }

/* RightBuy */
.bigquote { font-family: var(--display); font-weight: 800; font-size: 1.7rem; line-height: 1.2; color: var(--navy) !important; margin: 4px 0 20px; letter-spacing:-.5px; }
.bigquote s { color: var(--muted) !important; } .bigquote em { color: var(--red) !important; font-style: normal; }
.steps { display:grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 22px; }
.step { background:#fff; border:1px solid var(--line); border-radius: 16px; padding: 16px; }
.step .num { width:30px; height:30px; border-radius:50%; background: var(--navy); color:#fff !important; display:flex; align-items:center;
             justify-content:center; font-weight:800; font-size:.9rem; margin-bottom: 10px; }
.step b { display:block; font-size: 1rem; } .step span { color: var(--muted) !important; font-size: .86rem; }
.prompt-before { background:#eef0f4; border-radius: 18px; padding: 20px 22px; height:100%; }
.prompt-after { background: var(--navy); border-radius: 18px; padding: 20px 22px; height:100%; }
.prompt-before .t, .prompt-after .t { font: 800 .76rem var(--body); letter-spacing: 1.6px; text-transform: uppercase; }
.prompt-before .t { color: var(--muted) !important; } .prompt-after .t { color:#ffd3d7 !important; }
.prompt-after p, .prompt-after div { color:#e6edf7 !important; }
.basket { background:#fff; border:1px solid var(--line); border-radius: 18px; padding: 20px 22px; }
.basket.after { border: 2px solid var(--red); }
.basket .hd { font: 800 .76rem var(--body); letter-spacing: 1.6px; text-transform: uppercase; color: var(--muted) !important; }
.basket .nums { display:flex; gap: 28px; margin: 10px 0 14px; }
.basket .nums div div:first-child { font-family: var(--display); font-weight:900; font-size: 2.1rem; letter-spacing:-1px; line-height:1; }
.basket .nums .pay { color: var(--navy) !important; } .basket .nums .waste { color: var(--red) !important; }
.basket .nums .c { font-size:.8rem; color: var(--muted) !important; }
.li { display:flex; justify-content:space-between; gap: 10px; padding: 8px 0; border-top: 1px solid #eef1f5; font-size: .9rem; }
.li .r { white-space: nowrap; color: var(--muted) !important; }

/* run */
.scen { border-radius: 18px; padding: 20px 22px; height: 100%; }
.scen.b { background:#fff; border:1px solid var(--line); } .scen.a { background:#fff; border:2px solid var(--red); }
.scen .t { font: 800 .76rem var(--body); letter-spacing:1.6px; color: var(--red) !important; }
.scen h4 { font-family: var(--display); font-weight:900; color: var(--navy) !important; font-size: 1.5rem; margin: 6px 0 6px; text-transform: uppercase; letter-spacing:-.5px; }
.stButton button[kind="primary"] { background: var(--red) !important; border: 0 !important; border-radius: 999px !important;
          padding: 12px 30px !important; box-shadow: 0 10px 24px rgba(179,18,30,.25); }
.stButton button p, .stDownloadButton button p { color:#fff !important; font-weight: 800 !important; font-family: var(--display) !important;
          letter-spacing: .4px; font-size: 1rem !important; }
.stDownloadButton button { background: var(--navy) !important; border: 0 !important; border-radius: 999px !important; }
.stCode, .stCode pre { border-radius: 14px !important; }

/* results */
.kpi { background:#fff; border:1px solid var(--line); border-radius: 18px; padding: 18px 18px 16px; height:100%; }
.kpi .l { color: var(--muted) !important; font-size: .82rem; font-weight: 600; min-height: 2.3em; }
.kpi .v { font-family: var(--display); font-weight: 900; font-size: clamp(1.4rem, 2.1vw, 2.2rem); white-space: nowrap; letter-spacing:-1px; color: var(--navy) !important; line-height: 1.05; margin-top: 6px; }
.kpi .b { color: var(--muted) !important; font-size: .82rem; margin-top: 6px; }
.delta { display:inline-block; padding: 2px 9px; border-radius: 999px; font-weight: 700; font-size: .78rem; margin-left: 4px; }
.delta.up { background:#e3f4ea; color:#17773f !important; } .delta.down { background:#fbe7e9; color: var(--red) !important; }
.journey { background:#fff; border:1px solid var(--line); border-radius: 18px; padding: 16px 20px; margin-bottom: 10px;
           display:grid; grid-template-columns: 1.25fr 1.15fr .55fr 2fr; gap: 18px; align-items:center; }
.journey .who { display:flex; gap: 12px; align-items:center; font-weight: 700; }
.journey .who .avatar { flex-shrink: 0; margin: 0; width: 44px; height: 44px; font-size: 1.35rem; }
.journey .who small { display:block; color: var(--muted) !important; font-weight: 500; font-size: .78rem; }
.store { font-weight: 800; font-size: .8rem; padding: 4px 10px; border-radius: 999px; display:inline-block; }
.store.Costco { background: #fbe7e9; color: var(--red) !important; } .store.Walmart { background:#e5edf8; color: var(--navy) !important; }
.store.Split { background:#f3ecfa; color:#6b3fa0 !important; }
.arrow { color: var(--muted) !important; margin: 0 6px; }
.journey .path { white-space: nowrap; }
.trust { font-size: .82rem; color: var(--muted) !important; }
.trust b { font-family: var(--display); font-size: 1.15rem; color: var(--navy) !important; }
.say { font-style: italic; color: #2b3747 !important; font-size: .93rem; line-height: 1.45; }
.react { border-radius: 18px; padding: 22px 24px; height: 100%; }
.react.w { background: var(--navy); } .react.w p, .react.w div, .react.w span { color:#e6edf7 !important; }
.react.w h4 { color:#fff !important; } .react.s { background:#eaf5ee; border: 1px solid #cfe7d8; }
.react h4 { font-family: var(--display); font-weight:900; text-transform:uppercase; margin: 0 0 8px; letter-spacing:-.3px; font-size: 1.3rem; }
.meter { display:inline-flex; gap:4px; margin-left: 8px; vertical-align: middle; }
.meter i { width: 26px; height: 8px; border-radius: 4px; background: rgba(255,255,255,.25); display:inline-block; }
.meter i.on { background: #ff5a66; }
.oneline { background: var(--red); border-radius: 18px; padding: 18px 24px; margin: 6px 0 24px; }
.oneline, .oneline * { color: #fff !important; } .oneline b { font-family: var(--display); font-weight: 900; }
.foot { margin-top: 48px; padding-top: 18px; border-top: 1px solid var(--line); display:flex; justify-content:space-between;
        gap: 20px; flex-wrap: wrap; font-size: .8rem; }
.foot, .foot * { color: var(--muted) !important; } .foot b { color: var(--ink) !important; }

/* sidebar */
section[data-testid="stSidebar"] { background: #fff; border-right: 1px solid var(--line); }
.sidebrand { font-family: var(--display); font-weight:900; font-size: 1.5rem; letter-spacing:-1px; line-height: .95; text-transform: uppercase; margin-bottom: 4px; }
.sidebrand .r { color: var(--red) !important; } .sidebrand .n { color: var(--navy) !important; }
@media (max-width: 900px) { .hero, .journey, .steps { grid-template-columns: 1fr; } }
</style>
"""
for k, v in {"RED": RED, "NAVY": NAVY, "INK": INK, "MUTED": MUTED, "LINE": LINE}.items():
    CSS = CSS.replace(f": {k};", f": {v};")
st.markdown(CSS, unsafe_allow_html=True)


def section(title, sub=""):
    st.markdown(f'<div class="sec"><span class="motif"><i></i><b></b></span><h2>{title}</h2>'
                f'{f"<p>{sub}</p>" if sub else ""}</div>', unsafe_allow_html=True)


def avatar(emoji):
    return f'<div class="avatar">{emoji}</div>'


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown('<div class="sidebrand"><span class="r">Control</span><br><span class="n">Room</span></div>',
                unsafe_allow_html=True)
    st.caption("Choose which market run to show.")
    mode = st.radio("Agents", ["Replay saved run (no key needed)", "Run live with Gemini"], index=0)
    saved_name = list(SAVED_RUNS)[0]
    if mode.startswith("Replay"):
        saved_name = st.selectbox("Saved run", list(SAVED_RUNS))
    REFERENCE = SAVED_RUNS[saved_name]
    api_key, model, fast = None, "gemini-3.5-flash", False
    if mode.startswith("Run live"):
        api_key = st.text_input("Gemini API key", type="password",
                                help="Free key from aistudio.google.com → Get API key")
        model = st.text_input("Model", value="gemini-3.5-flash",
                              help="If Google says a model is no longer available, type the name it suggests")
        fast = st.toggle("Fast mode: 3 requests instead of 24", value=True,
                         help="Each scenario's agents answer in one request. Use this on the free tier.")
    st.divider()
    st.caption("Prices are illustrative US shelf prices. The money maths is exact Python; the AI agents make the "
               "human decisions (where to shop, trust, membership) and the competitor and supplier reactions.")

want = f"Saved run · {saved_name}"
if "run" not in st.session_state or (mode.startswith("Replay") and st.session_state.source != want):
    with open(REFERENCE) as f:
        ref = json.load(f)
    st.session_state.run, st.session_state.prompts = ref["run"], ref["prompts"]
    st.session_state.answers, st.session_state.source = ref["answers"], want

RUN = st.session_state.run
BEFORE, AFTER = compare_runs(RUN)


def pct(a, b):
    return (a - b) / b * 100 if b else 0


waste_d = pct(AFTER["Food wasted per week ($)"], BEFORE["Food wasted per week ($)"])
rev_d = pct(AFTER["Costco revenue per week ($)"], BEFORE["Costco revenue per week ($)"])
mem_d = AFTER["Paying member households (own card)"] - BEFORE["Paying member households (own card)"]
src_label = st.session_state.source.replace("Saved run · ", "")

# ------------------------------------------------------------------ header + hero
st.markdown('<div class="topstrip">Costco Wholesale · Market Simulator<span>BMS5213 Applied AI Use Case Factory · '
            'Group Project Part 4</span></div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="hero">
  <div>
    <div class="eyebrow"><span class="motif"><i></i><b></b></span> Welcome to the aisle of tomorrow</div>
    <h1 class="headline"><span class="n">Your members</span><br><span class="n">won't shop.</span><br>
        <span class="r">Their AI will.</span></h1>
    <p class="lede">Six households hand their grocery list to an AI. Walmart, a ChatGPT shopping agent and a Kirkland
      supplier fight for the basket. We open the doors twice: once as Costco is today, once with
      <b>RightBuy</b>. Then we count who wins.</p>
    <span class="promise">Not the lowest price per kg. <b>The lowest cost of what you actually use.</b></span>
  </div>
  <div class="scoreboard">
    <div class="lbl">What RightBuy changed · per week</div>
    <div class="row">
      <div><div class="big">{waste_d:+.0f}%</div><div class="cap">food thrown away</div></div>
      <div><div class="big">{rev_d:+.0f}%</div><div class="cap">Costco revenue</div></div>
      <div><div class="big">{mem_d:+d}</div><div class="cap">new paying member{'s' if abs(mem_d) != 1 else ''}</div></div>
    </div>
    <div class="foot">Shoppers using Costco: {BEFORE['Shoppers using Costco']} → {AFTER['Shoppers using Costco']}
      · Trust {BEFORE['Avg trust in Costco (1-10)']} → {AFTER['Avg trust in Costco (1-10)']}<br>Source: {esc(src_label)}</div>
  </div>
</div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["01 · The market", "02 · RightBuy", "03 · Open the doors",
                                        "04 · What changed", "Transcripts"])

# ------------------------------------------------------------------ 1. market
with tab1:
    section("Meet the market", "Every participant below is an AI agent with its own persona, budget and goals")
    st.markdown(f'<div class="task"><span class="k">ONE TASK FOR ALL</span><span class="v">'
                f'{esc(SHARED_TASK.format(weeks="N", budget="B"))}</span></div>', unsafe_allow_html=True)
    cols = st.columns(3, gap="medium")
    for i, s in enumerate(SHOPPERS):
        member = ('<span class="chip red">Costco member</span>' if s["member"] and not s.get("shared_card")
                  else '<span class="chip red">Shared card</span>' if s.get("shared_card")
                  else '<span class="chip grey">Not a member</span>')
        with cols[i % 3]:
            st.markdown(f"""<div class="card">{avatar(s['emoji'])}<h4>{esc(s['name'])}</h4>
              <div class="muted">{esc(s['summary'])}</div>
              <div class="chips"><span class="chip">{D}{s['budget']} / {s['trip_weeks']} wk</span>
              <span class="chip">AI use: {s['ai_use']}</span><span class="chip">Storage: {s['storage']}</span>{member}</div>
              </div>""", unsafe_allow_html=True)
            st.write("")
    st.markdown('<div class="sec" style="margin-top:14px"><h2 style="font-size:1.5rem">Around them</h2></div>',
                unsafe_allow_html=True)
    c = st.columns(4, gap="medium")
    for col, (ic, title, text) in zip(c, [("🏬", "Costco · today", COSTCO_AGENT["baseline"]),
                                          ("🛒", "Walmart", WALMART_AGENT),
                                          ("🤖", "ChatGPT shopping agent", PLATFORM_AGENT),
                                          ("🍓", "Kirkland produce supplier", SUPPLIER_AGENT)]):
        col.markdown(f'<div class="agentcard"><div class="ic">{ic}</div><h5>{title}</h5>'
                     f'<div class="muted">{esc(text)}</div></div>', unsafe_allow_html=True)
    st.write("")
    with st.expander("Product catalogue the agents shop from"):
        rows = [{"Store": store, "Product": p["label"], "Pack": p["size"], "Price ($)": p["price"],
                 "Keeps (days)": str(p["shelf_days"]) if p["shelf_days"] < 9999 else "years", "Type": p["kind"]}
                for store, items in CATALOGUE.items() for p in items]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

# ------------------------------------------------------------------ 2. RightBuy
with tab2:
    section("RightBuy", "The use case we plug into the Costco agent: new prompt + catalogue and shelf-life data (RAG)")
    st.markdown('<div class="bigquote"><s>The lowest unit price.</s> <em>The lowest cost of what members actually use.</em></div>',
                unsafe_allow_html=True)
    st.markdown("""<div class="steps">
      <div class="step"><div class="num">1</div><b>Input needs</b><span>What the household really eats per week</span></div>
      <div class="step"><div class="num">2</div><b>Predict use</b><span>Consumption, shelf life, storage space</span></div>
      <div class="step"><div class="num">3</div><b>Compare packs</b><span>Bulk, frozen, trial pack, or skip it</span></div>
      <div class="step"><div class="num">4</div><b>Member decides</b><span>Clear plan, real cost, always optional</span></div>
    </div>""", unsafe_allow_html=True)
    a, b = st.columns(2, gap="medium")
    a.markdown(f'<div class="prompt-before"><div class="t">Before · the Costco agent today</div>'
               f'<p class="muted" style="margin-top:8px">{esc(COSTCO_AGENT["baseline"])}</p></div>', unsafe_allow_html=True)
    b.markdown(f'<div class="prompt-after"><div class="t">After · the RightBuy agent</div>'
               f'<p style="margin-top:8px; font-size:.93rem; line-height:1.5">{esc(COSTCO_AGENT["rightbuy"])}</p></div>',
               unsafe_allow_html=True)
    st.write("")
    st.markdown("**Pick a shopper and watch the basket change**")
    labels = [f"{s['emoji']} {s['name']}" for s in SHOPPERS]
    who = st.segmented_control("Shopper", labels, default=labels[0], label_visibility="collapsed") or labels[0]
    s = SHOPPERS[labels.index(who)]
    base, rb = offers_for(s, "baseline"), offers_for(s, "rightbuy")

    def lines_html(lines):
        out = []
        for l in lines:
            if l.get("skip"):
                out.append(f'<div class="li"><span>{esc(l["item_name"])} <span class="chip red">Skip · buy small elsewhere</span>'
                           f'</span><span class="r">{D}0.00</span></div>')
                continue
            tag = {"frozen": '<span class="chip">Frozen</span>', "trial": '<span class="chip green">Trial pack</span>'}.get(l["kind"], "")
            waste = f' · waste {D}{l["waste_value"]:.2f}' if l["waste_value"] > 0 else ""
            out.append(f'<div class="li"><span>{esc(l["label"])} ×{l["packs"]} {tag}</span>'
                       f'<span class="r">{D}{l["spend"]:.2f}{waste}</span></div>')
        return "".join(out)
    a, b = st.columns(2, gap="medium")
    a.markdown(f"""<div class="basket"><div class="hd">Bulk packs · lowest price per unit</div>
      <div class="nums"><div><div class="pay">{D}{base['costco_all']['spend']:.0f}</div><div class="c">paid at Costco</div></div>
      <div><div class="waste">{D}{base['costco_all']['waste_value']:.2f}</div><div class="c">thrown away</div></div></div>
      {lines_html(base['costco_lines'])}</div>""", unsafe_allow_html=True)
    b.markdown(f"""<div class="basket after"><div class="hd" style="color:{RED} !important">RightBuy · sized to real use</div>
      <div class="nums"><div><div class="pay">{D}{rb['costco']['spend']:.0f}</div><div class="c">paid at Costco</div></div>
      <div><div class="waste">{D}{rb['plan_full']['waste_value']:.2f}</div><div class="c">thrown away (incl. small packs elsewhere)</div></div></div>
      {lines_html(rb['costco_lines'])}</div>""", unsafe_allow_html=True)

# ------------------------------------------------------------------ 3. run
with tab3:
    section("Open the doors", "Same shoppers, same task, two versions of Costco")
    a, b = st.columns(2, gap="medium")
    a.markdown('<div class="scen b"><div class="t">SCENARIO A · BEFORE</div><h4>Costco as it is today</h4>'
               '<div class="muted">Bulk packs at the lowest price per unit. AI shopping agents compare sticker prices.'
               '</div></div>', unsafe_allow_html=True)
    b.markdown('<div class="scen a"><div class="t">SCENARIO B · AFTER</div><h4>Costco with RightBuy</h4>'
               '<div class="muted">Real-cost plans, honest "skip it" advice, and AI agents may only check out through '
               'a member\'s own login. Then Walmart and the supplier react.</div></div>', unsafe_allow_html=True)
    st.write("")
    if mode.startswith("Run live"):
        done = len(st.session_state.get("live_cache", {}).get(f"{model}|{fast}", {}))
        if done:
            st.info(f"{done} of {3 if fast else 24} requests already saved from your last attempt - "
                    "pressing the button continues from there.")
    if st.button("▶  OPEN THE DOORS", type="primary"):
        box = st.empty()
        log = []

        def show(msg):
            log.append(msg)
            box.code("\n".join(log[-30:]), language=None)
        if mode.startswith("Run live"):
            if not api_key:
                st.error("Add a Gemini API key in the sidebar, or use the saved run.")
                st.stop()
            cache = st.session_state.setdefault("live_cache", {}).setdefault(f"{model}|{fast}", {})
            rec = recording(gemini_llm(api_key, model, on_wait=show), cache)
            source = f"Live run · {model}" + (" · fast mode" if fast else "")
        else:
            rec = recording(replay_llm(REFERENCE))
            source = f"Saved run · {saved_name}"
        try:
            with st.spinner("Agents are shopping… (on a busy day this can take a while - don't touch the page)"):
                if mode.startswith("Run live"):
                    batched = fast
                else:
                    with open(REFERENCE) as f:
                        batched = "batch/before" in json.load(f)["answers"]
                run = run_all(rec, log=show, batched=batched)
        except Exception as e:  # noqa: BLE001
            total = 3 if fast else 24
            saved = len(st.session_state.get("live_cache", {}).get(f"{model}|{fast}", {}))
            if "quota" in str(e).lower():
                st.error(f"Your free daily quota for {model} is used up ({saved} of {total} requests saved). "
                         "Type another model in the Model box and run again, or wait until the quota resets "
                         "(midnight US Pacific time = 3-4pm Singapore).")
            else:
                st.error(f"Google's servers stopped answering ({str(e)[:120]}…). {saved} of {total} requests are saved. "
                         "Wait a few minutes and press the button again - it continues where it stopped.")
            st.stop()
        st.session_state.run, st.session_state.source = run, source
        st.session_state.prompts, st.session_state.answers = rec.store["prompts"], rec.store["answers"]
        st.session_state.download = json.dumps({"answers": rec.store["answers"], "prompts": rec.store["prompts"],
                                                "run": run, "source": source}, indent=1)
        st.success("Done - open 04 · What changed.")
    if st.session_state.get("download"):
        st.download_button("Download this run (JSON)", st.session_state.download, "costco_run.json")
    st.caption(f"Currently showing: {st.session_state.source}")

# ------------------------------------------------------------------ 4. results
with tab4:
    section("What changed", f"Before vs after RightBuy · {src_label}")
    st.markdown(f'<div class="oneline">In one line: <b>{waste_d:+.0f}% food waste</b> · <b>{rev_d:+.0f}% Costco revenue</b> · '
                f'<b>{mem_d:+d} paying member{"s" if abs(mem_d) != 1 else ""}</b> · trust '
                f'<b>{BEFORE["Avg trust in Costco (1-10)"]} → {AFTER["Avg trust in Costco (1-10)"]}</b></div>',
                unsafe_allow_html=True)
    good_if_up = {"Food wasted per week ($)": False, "Spend on someone else's card ($/week)": False}
    cols = st.columns(len(BEFORE), gap="small")
    for col, k in zip(cols, BEFORE):
        b, a = BEFORE[k], AFTER[k]
        delta = ""
        if isinstance(b, (int, float)) and b != a:
            diff = a - b
            p = f" ({diff / b * 100:+.0f}%)" if b else ""
            good = (diff > 0) == good_if_up.get(k, True)
            delta = f'<span class="delta {"up" if good else "down"}">{diff:+,.1f}{p}</span>'
        fmt = (lambda v: f"{D}{v:,.2f}") if "$" in k else (lambda v: f"{v}")
        label = k.replace(" ($)", "").replace(" ($/week)", " per week")
        col.markdown(f'<div class="kpi"><div class="l">{esc(label)}</div><div class="v">{fmt(a)}</div>'
                     f'<div class="b">before {fmt(b)} {delta}</div></div>', unsafe_allow_html=True)

    st.write("")
    section("Shopper journeys", "Where each household shopped, how much it trusts Costco, and what it said")
    for b, a in zip(RUN["before"], RUN["after"]):
        tb, ta = b["decision"].get("trust_costco"), a["decision"].get("trust_costco")
        mem = a["decision"].get("membership", "")
        memchip = {"join": '<span class="chip green">Joins Costco</span>', "renew": '<span class="chip">Renews</span>',
                   "cancel": '<span class="chip red">Cancels</span>'}.get(mem, '<span class="chip grey">Non-member</span>')
        st.markdown(f"""<div class="journey">
          <div class="who">{avatar(a['emoji'])}<div>{esc(a['name'])}<small>{esc(a['summary'])}</small></div></div>
          <div><div class="path"><span class="store {b['choice']}">{b['choice']}</span><span class="arrow">→</span>
               <span class="store {a['choice']}">{a['choice']}</span></div><div style="margin-top:8px">{memchip}</div></div>
          <div class="trust">Trust<br><b>{tb} → {ta}</b></div>
          <div class="say">“{esc(a['decision'].get('quote', ''))}”</div></div>""", unsafe_allow_html=True)

    st.write("")
    section("The money", "Per shopping trip, before vs after")

    def bars(field, color, title):
        df = pd.DataFrame([{"Shopper": r["name"], "Phase": "Before", "Value": r0[field]} for r, r0 in
                           zip(RUN["before"], RUN["before"])] +
                          [{"Shopper": r["name"], "Phase": "After", "Value": r[field]} for r in RUN["after"]])
        base_ = alt.Chart(df).encode(
            y=alt.Y("Shopper:N", sort=[r["name"] for r in RUN["before"]], title=None,
                    axis=alt.Axis(labelFont="Inter, Arial", labelFontSize=12, labelColor=INK, labelLimit=220, domain=False, ticks=False)),
            yOffset=alt.YOffset("Phase:N", sort=["Before", "After"]),
            x=alt.X("Value:Q", title=None, axis=alt.Axis(format="$,.0f", grid=True, gridColor="#eef1f5",
                                                         labelColor=MUTED, domain=False, ticks=False)),
            color=alt.Color("Phase:N", scale=alt.Scale(domain=["Before", "After"], range=["#c9d2df", color]),
                            legend=alt.Legend(orient="top", title=None, labelFont="Inter")))
        chart = (base_.mark_bar(cornerRadiusEnd=5, height=13) +
                 base_.mark_text(align="left", dx=4, font="Inter, Arial", fontSize=11, color=MUTED)
                 .encode(text=alt.Text("Value:Q", format="$,.0f")))
        return chart.properties(height=360, title=alt.TitleParams(title, font="Archivo, Arial Black, Arial", fontSize=17, color=NAVY,
                                                                  anchor="start")).configure_view(stroke=None)
    c1, c2 = st.columns(2, gap="large")
    c1.altair_chart(bars("waste_value", RED, "Food thrown away"), use_container_width=True)
    c2.altair_chart(bars("costco_spend", NAVY, "Money spent at Costco"), use_container_width=True)

    section("The market fights back", "How the other AI agents respond to RightBuy")
    lvl = str(RUN["walmart"].get("threat_level", "")).lower()
    on = {"low": 1, "medium": 2, "high": 3}.get(lvl, 0)
    meter = "".join(f'<i class="{"on" if i < on else ""}"></i>' for i in range(3))
    w, s_ = st.columns(2, gap="medium")
    w.markdown(f'<div class="react w"><h4>🛒 Walmart</h4><div style="margin-bottom:10px">Threat level: '
               f'<b style="color:#fff">{esc(lvl.upper())}</b><span class="meter">{meter}</span></div>'
               f'<p>{esc(RUN["walmart"].get("response", ""))}</p></div>', unsafe_allow_html=True)
    s_.markdown(f'<div class="react s"><h4 style="color:#17773f">🍓 Kirkland supplier</h4>'
                f'<p>{esc(RUN["supplier"].get("reaction", ""))}</p>'
                f'<p><b>Asks Costco:</b> {esc(RUN["supplier"].get("ask_of_costco", ""))}</p></div>', unsafe_allow_html=True)
    st.write("")
    with st.expander("All the numbers in a table"):
        rows = []
        for b, a in zip(RUN["before"], RUN["after"]):
            rows.append({"Shopper": f"{a['emoji']} {a['name']}", "Before": b["choice"], "After": a["choice"],
                         "Trust before": b["decision"].get("trust_costco"), "Trust after": a["decision"].get("trust_costco"),
                         "Membership after": a["decision"].get("membership"),
                         "Costco $ before": b["costco_spend"], "Costco $ after": a["costco_spend"],
                         "Waste $ before": b["waste_value"], "Waste $ after": a["waste_value"]})
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

# ------------------------------------------------------------------ 5. transcripts
with tab5:
    section("Agent transcripts", "Every prompt we sent and every answer the agents gave - nothing hidden")
    for key in st.session_state.prompts:
        with st.expander(key):
            st.markdown("**Prompt**")
            st.code(st.session_state.prompts[key], language=None)
            st.markdown("**Answer**")
            st.json(st.session_state.answers.get(key, {}))

st.markdown('<div class="foot"><div><b>Retail Group</b> · Gan Jiaxin · Aryaman Agrawal · Somya Jain · Su Jianuo · '
            'Xia Yiwuyou</div><div>BMS5213 Applied AI Use Case Factory · NUS · 6 November 2026 · '
            'Prices are illustrative</div></div>', unsafe_allow_html=True)
