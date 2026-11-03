"""Page 2 - SmartShop: the member-facing chat, powered by the RightBuy engine."""
import json
import re

import streamlit as st

from market import ITEMS, COSTCO_MEMBERSHIP_FEE_YEAR
from sim import build_basket, totals, offers_for
from theme import RED, NAVY, D, esc, apply

apply()

# ------------------------------------------------------------------ household model
# What one adult typically uses per week (base units from market.ITEMS). Used when the member doesn't say.
PER_PERSON = {"milk": 0.4, "eggs": 5, "chicken": 0.45, "bread": 0.4, "rice": 0.4, "pasta": 0.25, "bananas": 0.4,
              "strawberries": 0.15, "spinach": 0.08, "avocados": 1, "cheese": 0.08, "toilet_paper": 1.5}
KEYWORDS = {"milk": ["milk"], "eggs": ["egg"], "chicken": ["chicken", "protein", "meat"], "bread": ["bread", "toast"],
            "rice": ["rice"], "pasta": ["pasta", "spaghetti", "noodle"], "bananas": ["banana"],
            "strawberries": ["strawberr", "berries", "berry"], "spinach": ["spinach", "greens", "salad", "veg"],
            "avocados": ["avocado", "guac"], "cheese": ["cheese"], "toilet_paper": ["toilet", "loo roll", "tissue"]}
EXAMPLES = [("🥗", "Meal-prep couple · $120", "Meal-prep for 2 of us, $120 a week, lots of chicken, spinach and berries"),
            ("👩‍💻", "Just me, small flat · $70", "Just me in a small flat, $70 for the week, not a member yet"),
            ("👨‍👩‍👧‍👦", "Family of 4, 2 weeks · $230", "Family of 4 with a big freezer, shopping for 2 weeks, $230")]


def parse_rules(text):
    """Turn a plain-English request into a household profile, without any AI (always works in class)."""
    t = text.lower()
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "just me": 1, "myself": 1, "couple": 2}
    people = 2
    m = m_people = re.search(r"(?:family of|for|we are|we're|household of)\s+(\d+|one|two|three|four|five|six)", t)
    if m:
        people = int(m.group(1)) if m.group(1).isdigit() else words[m.group(1)]
    elif any(k in t for k in ("just me", "myself", "single", "alone", "only me")):
        people = 1
    elif "couple" in t or "2 of us" in t or "two of us" in t:
        people = 2
    m = re.search(r"\$\s?(\d+)", t) or re.search(r"(\d+)\s?(?:dollars|usd|budget)", t)
    budget = int(m.group(1)) if m else 60 * people
    weeks = 2 if any(k in t for k in ("2 weeks", "two weeks", "fortnight", "2 week")) else 1
    storage = "medium"
    if any(k in t for k in ("small flat", "small fridge", "studio", "tiny", "small apartment", "no space", "small")):
        storage = "small"
    if any(k in t for k in ("big freezer", "chest freezer", "large", "big fridge", "freezer", "garage")):
        storage = "large"
    if any(k in t for k in ("cafe", "café", "restaurant", "business")):
        storage = "commercial"
        if not m_people:
            people = 30   # a small café cooks for roughly 30 people a day
    member = not any(k in t for k in ("not a member", "no membership", "non-member", "not member"))
    mentioned = [i for i, kws in KEYWORDS.items() if any(k in t for k in kws)]
    items = mentioned if len(mentioned) >= 3 else list(PER_PERSON)
    use = {}
    for i in items:
        q = PER_PERSON[i] * people
        if re.search(rf"(lots of|a lot of|loads of|plenty of|love|loves|eat a lot)[^.]*?({'|'.join(KEYWORDS[i])})", t):
            q *= 1.8
        use[i] = round(q, 2)
    return {"people": people, "budget": budget, "weeks": weeks, "storage": storage, "member": member, "weekly_use": use}


def parse_gemini(text, key, model):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=key)
    prompt = ("Turn this grocery request into JSON. Keys: people (int), budget (number, for the whole trip), weeks (1 or 2), "
              "storage (small|medium|large|commercial), member (true/false: is the person a Costco member? default true), "
              f"weekly_use (object: item -> quantity the household eats PER WEEK, only items from {json.dumps(list(ITEMS))}, "
              f"units: {json.dumps({k: v['unit'] for k, v in ITEMS.items()})}). Use realistic quantities. Request: {text}")
    r = client.models.generate_content(model=model, contents=prompt,
                                       config=types.GenerateContentConfig(response_mime_type="application/json",
                                                                          temperature=0.2))
    p = json.loads(re.search(r"\{.*\}", r.text, re.S).group(0))
    p["weekly_use"] = {k: float(v) for k, v in p.get("weekly_use", {}).items() if k in ITEMS and float(v) > 0}
    if not p["weekly_use"]:
        raise ValueError("empty basket")
    p["weeks"] = 2 if int(p.get("weeks", 1)) >= 2 else 1
    p["storage"] = p.get("storage", "medium") if p.get("storage") in ("small", "medium", "large", "commercial") else "medium"
    return p


def plan_for(p):
    shopper = {"id": "member", "name": "You", "emoji": "🧑", "summary": "", "persona": "", "member": p["member"],
               "trip_weeks": p["weeks"], "budget": p["budget"], "storage": p["storage"], "ai_use": "always",
               "weekly_use": p["weekly_use"]}
    rb = offers_for(shopper, "rightbuy")
    bulk = build_basket(shopper, "Costco", "baseline")
    lines = [dict(l) for l in rb["costco_lines"]]
    # "Fits your budget today": if the plan costs more upfront than the budget, push long-life stock to next trip
    plan_full = rb["plan_full"]
    over = plan_full["spend"] - p["budget"]
    moved = []
    if over > 0:
        for l in sorted([l for l in lines if not l["skip"] and l["stock_value"] > 0], key=lambda x: -x["stock_value"]):
            if over <= 0:
                break
            l["next_trip"] = True
            moved.append(l)
            over -= l["spend"]
    fee = 0 if p["member"] else COSTCO_MEMBERSHIP_FEE_YEAR
    return {"profile": p, "lines": lines, "bulk": totals(bulk, True), "plan": plan_full, "walmart": rb["walmart"],
            "moved": moved, "fee": fee,
            "today": round(sum(l["spend"] for l in lines if not l["skip"] and not l.get("next_trip"))
                           + plan_full["spend"] - rb["costco"]["spend"], 2),
            "costco_today": round(sum(l["spend"] for l in lines if not l["skip"] and not l.get("next_trip")), 2),
            "elsewhere": round(plan_full["spend"] - rb["costco"]["spend"], 2)}


def reply_text(r):
    p = r["profile"]
    skipped = [l["item_name"].lower() for l in r["lines"] if l["skip"]]
    saved = r["bulk"]["waste_value"] - r["plan"]["waste_value"]
    who = "just you" if p["people"] == 1 else f"{p['people']} people"
    msg = (f"Here's your RightBuy plan for **{who}**, **{p['weeks']} week{'s' if p['weeks'] > 1 else ''}**, "
           f"budget **{D}{p['budget']}**. ")
    if saved > 0.5:
        msg += f"Compared with the usual bulk packs, you'll throw away about **{D}{saved:.2f} less food**. "
    if len(skipped) > 4:
        msg += (f"Honest advice: **{len(skipped)} of your items** ({', '.join(skipped[:3])} and more) are cheaper "
                "for you in small packs elsewhere, because our packs are bigger than you can use. ")
    elif skipped:
        msg += f"I'd honestly **skip {', '.join(skipped)}** at Costco: our packs are bigger than you can use. "
    if r["moved"]:
        msg += ("To fit today's budget, I've moved the long-life stock "
                f"({', '.join(l['item_name'].lower() for l in r['moved'])}) to your next trip. ")
    if not p["member"]:
        msg += f"You're not a member yet: membership is {D}{COSTCO_MEMBERSHIP_FEE_YEAR:.0f}/year, so compare that with your savings. "
    return msg + "You decide, nothing is bought until you confirm."


def plan_html(r):
    rows = []
    for l in r["lines"]:
        if l["skip"]:
            rows.append(f'<div class="li"><span>{esc(l["item_name"])} <span class="chip red">Skip · buy small elsewhere</span>'
                        f'</span><span class="r">-</span></div>')
            continue
        tag = {"frozen": '<span class="chip">Frozen</span>', "trial": '<span class="chip green">Trial pack</span>'}.get(l["kind"], "")
        if l.get("next_trip"):
            tag += ' <span class="chip grey">Next trip</span>'
        extra = f' · lasts beyond this trip' if l["stock_value"] > 0.5 else ""
        rows.append(f'<div class="li"><span>{esc(l["label"])} ×{l["packs"]} {tag}</span>'
                    f'<span class="r">{D}{l["spend"]:.2f}{extra}</span></div>')
    left = r["profile"]["budget"] - r["today"]
    budget_chip = (f'<span class="chip green">{D}{left:.2f} left in budget</span>' if left >= 0
                   else f'<span class="chip red">{D}{-left:.2f} over budget</span>')
    return f"""<div class="basket after" style="margin-top:6px">
      <div class="hd" style="color:{RED} !important">RightBuy plan · sized to what you actually use</div>
      <div class="nums">
        <div><div class="pay">{D}{r['costco_today']:.0f}</div><div class="c">pay at Costco today</div></div>
        <div><div class="pay" style="color:{NAVY} !important">{D}{r['elsewhere']:.0f}</div><div class="c">small packs elsewhere</div></div>
        <div><div class="waste">{D}{r['plan']['waste_value']:.2f}</div><div class="c">thrown away<br>(bulk packs: {D}{r['bulk']['waste_value']:.2f})</div></div>
      </div>
      <div class="chips" style="margin:0 0 10px">{budget_chip}<span class="chip">{esc(r['profile']['storage'])} storage</span>
        <span class="chip">{r['profile']['people']} {'person' if r['profile']['people'] == 1 else 'people'}</span></div>
      {''.join(rows)}</div>"""


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown('<div class="sidebrand"><span class="r">Smart</span><br><span class="n">Shop</span></div>',
                unsafe_allow_html=True)
    st.caption("Works without a key (built-in understanding). Add a Gemini key to let the AI read any request.")
    key = st.text_input("Gemini API key (optional)", type="password")
    model = st.text_input("Model", value="gemini-3.5-flash")
    if st.button("Clear chat"):
        st.session_state.pop("chat", None)
    st.divider()
    st.caption("Prices are illustrative US shelf prices. Demo only: nothing is ordered.")

# ------------------------------------------------------------------ hero
st.markdown("""<div class="topstrip">Costco SmartShop · powered by RightBuy<span>BMS5213 Applied AI Use Case Factory ·
  Group Project Part 4</span></div>""", unsafe_allow_html=True)
st.markdown(f"""<div class="hero" style="grid-template-columns: 1.4fr 1fr">
  <div>
    <div class="eyebrow"><span class="motif"><i></i><b></b></span> Costco SmartShop</div>
    <h1 class="headline"><span class="n">Your list.</span><br><span class="n">Your budget.</span><br>
      <span class="r">Zero waste.</span></h1>
    <p class="lede">Tell SmartShop who you're shopping for, in your own words. RightBuy works out the cheapest way to buy
      what you will <b>actually use</b>: bulk where it pays, frozen or a trial pack where it doesn't, and an honest
      "skip it" when our pack is simply too big for you.</p>
    <span class="promise">You, or your own AI agent, shop through <b>your member login</b>. You always confirm.</span>
  </div>
  <div class="scoreboard">
    <div class="lbl">How SmartShop thinks</div>
    <div style="margin-top:14px; display:grid; gap:12px">
      <div class="cap"><b style="color:#fff">1 · Understand</b><br>who, how long, budget, fridge space</div>
      <div class="cap"><b style="color:#fff">2 · Predict use</b><br>what you'll eat before it spoils</div>
      <div class="cap"><b style="color:#fff">3 · Compare packs</b><br>bulk, frozen, trial pack, or skip</div>
      <div class="cap"><b style="color:#fff">4 · Fit today's budget</b><br>long-life stock moves to next trip</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ------------------------------------------------------------------ chat
chat = st.session_state.setdefault("chat", [])
st.markdown("**Try one:**")
cols = st.columns(3, gap="small")
clicked = None
for col, (ic, label, ex) in zip(cols, EXAMPLES):
    if col.button(f"{ic}  {label}", use_container_width=True, key=f"ex_{ic}"):
        clicked = ex

for m in chat:
    with st.chat_message(m["role"], avatar="🧑" if m["role"] == "user" else "🛒"):
        st.markdown(m["text"])
        if m.get("plan"):
            st.markdown(plan_html(m["plan"]), unsafe_allow_html=True)

prompt = st.chat_input("e.g. Weekly shop for 2, small fridge, $80, we love avocados") or clicked
if prompt:
    chat.append({"role": "user", "text": prompt.replace("$", "\\$")})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt.replace("$", "\\$"))
    with st.chat_message("assistant", avatar="🛒"):
        note = ""
        try:
            profile = parse_gemini(prompt, key, model) if key else parse_rules(prompt)
            if key:
                profile.setdefault("people", parse_rules(prompt)["people"])
                profile.setdefault("budget", parse_rules(prompt)["budget"])
                profile.setdefault("member", True)
        except Exception as e:  # noqa: BLE001  (busy server, quota, bad JSON -> fall back, never break the demo)
            profile = parse_rules(prompt)
            note = f"\n\n*(Gemini was unavailable, so I used SmartShop's built-in understanding: {str(e)[:60]}…)*"
        result = plan_for(profile)
        text = reply_text(result) + note
        st.markdown(text)
        st.markdown(plan_html(result), unsafe_allow_html=True)
        chat.append({"role": "assistant", "text": text, "plan": result})
