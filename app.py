"""
Costco Market Simulator - Streamlit demo for BMS5213 Group Project Part 4.
Run:  streamlit run app.py
"""
import json
import os

import pandas as pd
import streamlit as st

from market import SHOPPERS, CATALOGUE, COSTCO_AGENT, WALMART_AGENT, PLATFORM_AGENT, SUPPLIER_AGENT, SHARED_TASK
from sim import (offers_for, run_all, compare_runs, gemini_llm, replay_llm, recording)

HERE = os.path.dirname(os.path.abspath(__file__))
SAVED_RUNS = {"Live Gemini run (gemini-3.5-flash)": os.path.join(HERE, "results", "live_run_gemini.json"),
              "First test run (Claude as the agents)": os.path.join(HERE, "results", "reference_run_claude.json")}
NAVY, BLUE, RED = "#0b3d7a", "#005daa", "#d0142c"

st.set_page_config(page_title="Costco Market Simulator", page_icon="🛒", layout="wide")
st.markdown(f"""
<style>
  .stApp {{ background: #f4f6f9; }}
  .stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div {{ color: #1b2430; }}
  .hero {{ background: {BLUE}; border-radius: 18px; padding: 28px 32px; margin-bottom: 18px; }}
  .hero h1, .hero h1 * {{ color: #fff !important; margin: 0; font-size: 2.1rem; }}
  .hero p {{ color: #dbe7f5 !important; margin: 6px 0 0; font-size: 1.05rem; }}
  .hero .tag {{ background: {RED}; color: #fff !important; border-radius: 999px; padding: 3px 12px; font-size: .8rem;
               font-weight: 700; letter-spacing: 1px; display: inline-block; margin-bottom: 10px; }}
  .card {{ background: #fff; border: 1px solid #d6dee8; border-radius: 14px; padding: 16px 18px; height: 100%; }}
  .card h4 {{ margin: 0 0 6px; color: {NAVY} !important; }}
  .muted {{ color: #5a6b80 !important; font-size: .92rem; }}
  .quote {{ border-left: 0; background: #eef3fa; border-radius: 10px; padding: 10px 14px; font-style: italic; }}
  .stButton button p, .stDownloadButton button p {{ color: #fff !important; font-weight: 700; }}
  .stDownloadButton button {{ background: {NAVY} !important; border-color: {NAVY} !important; }}
  .metric {{ background: #fff; border: 1px solid #d6dee8; border-radius: 14px; padding: 14px 16px; }}
  .metric .lbl {{ color: #5a6b80 !important; font-size: .85rem; }}
  .metric .val {{ color: {NAVY} !important; font-size: 1.6rem; font-weight: 800; }}
  .metric .delta-up {{ color: #0a7a3d !important; font-weight: 700; }}
  .metric .delta-down {{ color: {RED} !important; font-weight: 700; }}
</style>""", unsafe_allow_html=True)

st.markdown("""<div class="hero"><span class="tag">BMS5213 · GROUP PROJECT PART 4</span>
<h1>Costco Market Simulator</h1>
<p>Six shoppers, Walmart, a ChatGPT shopping agent and a supplier - all AI agents. We run the market before and after
Costco launches <b>RightBuy</b>, and watch what changes.</p></div>""", unsafe_allow_html=True)

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.header("Run settings")
    mode = st.radio("Agents", ["Replay saved run (no key needed)", "Run live with Gemini"], index=0)
    saved_name = list(SAVED_RUNS)[0]
    if mode.startswith("Replay"):
        saved_name = st.selectbox("Saved run", list(SAVED_RUNS))
    REFERENCE = SAVED_RUNS[saved_name]
    api_key, model, fast = None, "gemini-3.8-flash", False
    if mode.startswith("Run live"):
        api_key = st.text_input("Gemini API key", type="password",
                                help="Free key from aistudio.google.com → Get API key")
        model = st.text_input("Model", value="gemini-3.8-flash",
                              help="If Google says a model is no longer available, type the name it suggests")
        fast = st.toggle("Fast mode: 3 requests instead of 24", value=True,
                         help="Each scenario's agents answer in one request. Use this on the free tier.")
    st.caption("Prices are illustrative US shelf prices. The money maths is exact Python; the agents make the "
               "human decisions (where to shop, trust, membership) and the competitor/supplier reactions.")

want = f"Saved run · {saved_name}"
if "run" not in st.session_state or (mode.startswith("Replay") and st.session_state.source != want):
    with open(REFERENCE) as f:
        ref = json.load(f)
    st.session_state.run, st.session_state.prompts = ref["run"], ref["prompts"]
    st.session_state.answers, st.session_state.source = ref["answers"], want

tab1, tab2, tab3, tab4, tab5 = st.tabs(["① The market", "② The use case: RightBuy", "③ Run the market",
                                        "④ What changed", "Agent transcripts"])

# ------------------------------------------------------------------ 1. market
with tab1:
    st.subheader("Step 1 · Simulate the market with AI agents")
    st.write(f"Every shopper gets the same task: *{SHARED_TASK.format(weeks='N', budget='B')}*")
    cols = st.columns(3)
    for i, s in enumerate(SHOPPERS):
        with cols[i % 3]:
            st.markdown(f"""<div class="card"><h4>{s['emoji']} {s['name']}</h4>
            <div class="muted">{s['summary']}</div><br>
            <b>Budget:</b> ${s['budget']} per {s['trip_weeks']} week(s) · <b>Uses AI:</b> {s['ai_use']} ·
            <b>Storage:</b> {s['storage']}</div>""", unsafe_allow_html=True)
            st.write("")
    st.markdown("#### The other market participants")
    c = st.columns(4)
    for col, (title, text) in zip(c, [("🏬 Costco (before)", COSTCO_AGENT["baseline"]),
                                       ("🟦 Walmart", WALMART_AGENT),
                                       ("🤖 ChatGPT shopping agent", PLATFORM_AGENT),
                                       ("🍓 Kirkland produce supplier", SUPPLIER_AGENT)]):
        col.markdown(f'<div class="card"><h4>{title}</h4><div class="muted">{text}</div></div>', unsafe_allow_html=True)
    with st.expander("Product catalogue the agents shop from"):
        rows = [{"Store": store, "Product": p["label"], "Pack": p["size"], "Price ($)": p["price"],
                 "Keeps (days)": str(p["shelf_days"]) if p["shelf_days"] < 9999 else "years", "Type": p["kind"]}
                for store, items in CATALOGUE.items() for p in items]
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

# ------------------------------------------------------------------ 2. use case
with tab2:
    st.subheader("Step 2 · Introduce the use case into the Costco agent")
    a, b = st.columns(2)
    a.markdown(f'<div class="card"><h4>Before: Costco sales agent</h4><div class="muted">{COSTCO_AGENT["baseline"]}'
               '</div></div>', unsafe_allow_html=True)
    b.markdown(f'<div class="card"><h4>After: Costco RightBuy agent (new prompt + catalogue via RAG)</h4>'
               f'<div class="muted">{COSTCO_AGENT["rightbuy"]}</div></div>', unsafe_allow_html=True)
    st.write("")
    who = st.selectbox("See what each Costco agent offers to…", [f"{s['emoji']} {s['name']}" for s in SHOPPERS])
    s = SHOPPERS[[f"{x['emoji']} {x['name']}" for x in SHOPPERS].index(who)]
    base, rb = offers_for(s, "baseline"), offers_for(s, "rightbuy")

    def lines_df(lines):
        return pd.DataFrame([{"Product": (f"{l['item_name']}: SKIP at Costco → buy small elsewhere" if l.get("skip") else l["label"]),
                              "Packs": "" if l.get("skip") else str(l["packs"]),
                              "Pay ($)": 0.0 if l.get("skip") else l["spend"],
                              "Thrown away ($)": 0.0 if l.get("skip") else l["waste_value"]} for l in lines])
    a, b = st.columns(2)
    with a:
        st.markdown("**Before - bulk packs, lowest price per unit**")
        st.dataframe(lines_df(base["costco_lines"]), hide_index=True, width="stretch", height=38 + 35 * len(base["costco_lines"]))
        st.markdown(f"Pay **\\${base['costco_all']['spend']:.2f}** · thrown away **\\${base['costco_all']['waste_value']:.2f}**")
    with b:
        st.markdown("**After - RightBuy, lowest cost of what you actually use**")
        st.dataframe(lines_df(rb["costco_lines"]), hide_index=True, width="stretch", height=38 + 35 * len(rb["costco_lines"]))
        st.markdown(f"Pay **\\${rb['costco']['spend']:.2f}** at Costco · thrown away **\\${rb['plan_full']['waste_value']:.2f}**"
                    f" (incl. small packs elsewhere)")

# ------------------------------------------------------------------ 3. run
with tab3:
    st.subheader("Run both scenarios")
    st.write("**Before:** Costco without RightBuy.  **After:** Costco with RightBuy and member-login-only checkout "
             "for AI agents. Then Walmart and the supplier react.")
    if mode.startswith("Run live"):
        done = len(st.session_state.get("live_cache", {}).get(f"{model}|{fast}", {}))
        if done:
            st.info(f"{done} of {3 if fast else 24} requests already saved from your last attempt - "
                    "pressing Run continues from there.")
    if st.button("▶ Run the market", type="primary"):
        box = st.empty()
        log = []

        def show(msg):
            log.append(msg)
            box.code("\n".join(log[-30:]))
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
            with st.spinner("Agents are shopping… (on a busy day this can take 10-20 minutes - don't touch the page)"):
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
                         "Either type a lighter model in the Model box (for example gemini-3.8-flash-lite) and run again, "
                         "or wait until the quota resets (midnight US Pacific time = 3-4pm Singapore).")
            else:
                st.error(f"Google's servers stopped answering ({str(e)[:120]}…). {saved} of {total} requests are saved. "
                         "Wait a few minutes and press ▶ Run the market again - it continues where it stopped.")
            st.stop()
        st.session_state.run, st.session_state.source = run, source
        st.session_state.prompts, st.session_state.answers = rec.store["prompts"], rec.store["answers"]
        st.session_state.download = json.dumps({"answers": rec.store["answers"], "prompts": rec.store["prompts"],
                                                "run": run, "source": source}, indent=1)
        st.success("Done - open ④ What changed.")
    if st.session_state.get("download"):
        st.download_button("Download this run (JSON)", st.session_state.download, "costco_run.json")
    st.caption(f"Currently showing: {st.session_state.source}")

# ------------------------------------------------------------------ 4. results
with tab4:
    run = st.session_state.run
    before, after = compare_runs(run)
    st.subheader("Step 3 · How the market changed")
    st.caption(st.session_state.source)
    cols = st.columns(len(before))
    good_if_up = {"Avg trust in Costco (1-10)": True, "Food wasted per week ($)": False,
                  "Costco revenue per week ($)": True, "Paying member households (own card)": True,
                  "Spend on someone else's card ($/week)": False, "Shoppers using Costco": True}
    for col, k in zip(cols, before):
        b, a = before[k], after[k]
        delta = ""
        if isinstance(b, (int, float)) and b != a:
            diff = a - b
            pct = f" ({diff / b * 100:+.0f}%)" if b else ""
            good = (diff > 0) == good_if_up.get(k, True)
            delta = f'<span class="{"delta-up" if good else "delta-down"}">{diff:+,.1f}{pct}</span>'
        fmt = (lambda v: f"${v:,.2f}") if "$" in k else (lambda v: f"{v}")
        col.markdown(f'<div class="metric"><div class="lbl">{k.replace(" ($)", "").replace(" ($/week)", " per week")}</div>'
                     f'<div class="val">{fmt(a)}</div>'
                     f'<div class="lbl">before: {fmt(b)} {delta}</div></div>', unsafe_allow_html=True)

    st.markdown("#### Shopper by shopper")
    rows = []
    for b, a in zip(run["before"], run["after"]):
        rows.append({"Shopper": f"{a['emoji']} {a['name']}",
                     "Before": b["choice"], "After": a["choice"],
                     "Trust before": b["decision"].get("trust_costco"), "Trust after": a["decision"].get("trust_costco"),
                     "Membership after": a["decision"].get("membership"),
                     "Costco $ before": b["costco_spend"], "Costco $ after": a["costco_spend"],
                     "Waste $ before": b["waste_value"], "Waste $ after": a["waste_value"]})
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Food thrown away per trip ($)**")
        st.bar_chart(pd.DataFrame({"Before": [r["waste_value"] for r in run["before"]],
                                   "After": [r["waste_value"] for r in run["after"]]},
                                  index=[r["name"] for r in run["before"]]), color=["#9fb3cc", BLUE], stack=False)
    with c2:
        st.markdown("**Money spent at Costco per trip ($)**")
        st.bar_chart(pd.DataFrame({"Before": [r["costco_spend"] for r in run["before"]],
                                   "After": [r["costco_spend"] for r in run["after"]]},
                                  index=[r["name"] for r in run["before"]]), color=["#9fb3cc", RED], stack=False)

    st.markdown("#### In their own words (after RightBuy)")
    q = st.columns(3)
    for i, a in enumerate(run["after"]):
        q[i % 3].markdown(f'<div class="quote">{a["emoji"]} <b>{a["name"]}:</b> "{a["decision"].get("quote", "")}"</div>',
                          unsafe_allow_html=True)
        q[i % 3].write("")

    st.markdown("#### How the rest of the market reacts")
    w, s_ = st.columns(2)
    w.markdown(f'<div class="card"><h4>🟦 Walmart · threat: {run["walmart"].get("threat_level", "")}</h4>'
               f'{run["walmart"].get("response", "")}</div>', unsafe_allow_html=True)
    s_.markdown(f'<div class="card"><h4>🍓 Supplier</h4>{run["supplier"].get("reaction", "")}<br><br>'
                f'<b>Ask of Costco:</b> {run["supplier"].get("ask_of_costco", "")}</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------ 5. transcripts
with tab5:
    st.subheader("Every prompt and every agent answer")
    for key in st.session_state.prompts:
        with st.expander(key):
            st.markdown("**Prompt**")
            st.code(st.session_state.prompts[key], language=None)
            st.markdown("**Answer**")
            st.json(st.session_state.answers.get(key, {}))
