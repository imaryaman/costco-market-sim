"""Shared brand styling for the Costco Market Simulator and SmartShop pages."""
import html

import streamlit as st

RED, NAVY, INK, MUTED, LINE, PAPER = "#b3121e", "#12386f", "#16202e", "#5b6878", "#dfe4ec", "#ffffff"
D = "&#36;"  # dollar sign that never triggers Streamlit's LaTeX


def esc(x):
    return html.escape(str(x)).replace("$", D)



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
[data-testid="stBaseButton-primary"], .stButton button[kind="primary"] { background: var(--red) !important; border: 0 !important; border-radius: 999px !important;
          padding: 12px 30px !important; box-shadow: 0 10px 24px rgba(179,18,30,.25); }
[data-testid="stBaseButton-secondary"], .stButton button[kind="secondary"] { background:#fff !important; border:1px solid var(--line) !important; border-radius: 14px !important; text-align:left; }
[data-testid="stBaseButton-secondary"]:hover { border-color: var(--red) !important; }
[data-testid="stBaseButton-secondary"] p, [data-testid="stBaseButton-secondary"] div { color: var(--navy) !important; font-weight: 600 !important; font-size: .9rem !important; }
[data-testid="stBaseButton-primary"] p, .stButton button[kind="primary"] p, .stDownloadButton button p { color:#fff !important; font-weight: 800 !important; font-family: var(--display) !important;
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



def section(title, sub=""):
    st.markdown(f'<div class="sec"><span class="motif"><i></i><b></b></span><h2>{title}</h2>'
                f'{f"<p>{sub}</p>" if sub else ""}</div>', unsafe_allow_html=True)


def avatar(emoji):
    return f'<div class="avatar">{emoji}</div>'



def apply():
    st.markdown(CSS, unsafe_allow_html=True)
