"""
Costco Market Simulation - the engine.

Step 1  Simulate the market     -> agents in market.py
Step 2  Introduce the use case   -> Costco agent switches from "baseline" to "rightbuy" (prompt + RAG on catalogue)
Step 3  Analyse what changed     -> compare_runs()

The money maths (basket cost, waste, real cost) is done in plain Python so the numbers are exact.
The AI agents make the human decisions: where to shop, how much they trust Costco, whether to join or renew,
and how competitors and suppliers react.
"""
import json
import math
import re
from copy import deepcopy

from market import (ITEMS, CATALOGUE, SHOPPERS, COSTCO_AGENT, WALMART_AGENT, PLATFORM_AGENT,
                    SUPPLIER_AGENT, SHARED_TASK, COSTCO_MEMBERSHIP_FEE_YEAR)

NON_PERISHABLE_DAYS = 180          # shelf-stable goods (rice, pasta, toilet paper)
FREEZABLE = {"chicken", "bread"}   # big freezers let households keep these much longer
# how long a household can keep shelf-stable stock before it becomes clutter it never uses (days)
STORAGE_DAYS = {"small": 56, "medium": 120, "large": 365, "commercial": 365}


# ==========================================================================================
# 1. BASKET MATHS
# ==========================================================================================
def _life_days(shopper, sku):
    """How many days of consumption this pack can cover before it spoils (or before storage runs out)."""
    days = sku["shelf_days"]
    if sku["item"] in FREEZABLE and shopper["storage"] in ("large", "commercial") and days < 90:
        days = 90
    if days >= NON_PERISHABLE_DAYS:
        days = min(days, STORAGE_DAYS[shopper["storage"]])
    return days


def _need(shopper, item):
    return shopper["weekly_use"][item] * shopper["trip_weeks"]


def _target(shopper, sku):
    """What the household can really use from this kind of pack during this trip."""
    weekly = shopper["weekly_use"][sku["item"]]
    return min(_need(shopper, sku["item"]), weekly / 7 * _life_days(shopper, sku))


def _line(shopper, sku, packs):
    """Cost, use and waste of buying `packs` of `sku` for one trip.
    used  = eaten during this trip; stock = still good afterwards (counts towards next trip);
    wasted = goes bad or is more than the household can ever store and use."""
    item = sku["item"]
    weekly = shopper["weekly_use"][item]
    qty = packs * sku["size"]
    spend = packs * sku["price"]
    unit_cost = spend / qty if qty else 0
    usable = min(qty, weekly / 7 * _life_days(shopper, sku))
    used = min(usable, _need(shopper, item))
    stock = usable - used
    wasted = qty - usable
    return {
        "item": item, "item_name": ITEMS[item]["name"], "unit": ITEMS[item]["unit"],
        "sku": sku["sku"], "label": sku["label"], "kind": sku["kind"], "packs": packs,
        "qty": round(qty, 3), "spend": round(spend, 2),
        "used": round(used, 3), "wasted_qty": round(wasted, 3),
        "waste_value": round(wasted * unit_cost, 2),
        "stock_value": round(stock * unit_cost, 2),
        "real_cost": round(spend - stock * unit_cost, 2),   # what you really pay for this trip (incl. waste)
    }


def _walmart_unit_price(item):
    sku = next(s for s in CATALOGUE["Walmart"] if s["item"] == item)
    return sku["price"] / sku["size"]


def _simple_pick(shopper, store, item, kinds):
    """What a normal shopper does: take the store's main pack, buy about as many as they need (at least one)."""
    sku = next(s for s in CATALOGUE[store] if s["item"] == item and s["kind"] in kinds)
    packs = max(1, round(_target(shopper, sku) / sku["size"]))
    return _line(shopper, sku, packs)


def _rightbuy_pick(shopper, item):
    """RightBuy: try every Costco option and pack count - including buying nothing - and pick the plan with the
    lowest real cost for what the household will use. Anything not covered is priced as a small pack elsewhere,
    so RightBuy will honestly say 'skip this at Costco' when that is cheaper for the member."""
    weekly = shopper["weekly_use"][item]
    need_now = _need(shopper, item)
    fallback = _walmart_unit_price(item)
    best = None
    for sku in [s for s in CATALOGUE["Costco"] if s["item"] == item]:
        for packs in range(0, max(2, math.ceil(need_now / sku["size"]) + 2)):
            line = _line(shopper, sku, packs) if packs else None
            used = line["used"] if line else 0
            real = line["real_cost"] if line else 0
            unmet = max(0.0, need_now - used)
            score = real + unmet * fallback
            if best is None or score < best[0] - 1e-6:
                best = (score, line, sku)
    line = best[1]
    if line is None:   # cheaper to buy small elsewhere
        sku = next(s for s in CATALOGUE["Costco"] if s["item"] == item)
        line = _line(shopper, sku, 1)
        line["skip"] = True
    else:
        line["skip"] = False
    return line


def build_basket(shopper, store, mode="baseline"):
    lines = []
    for item in shopper["weekly_use"]:
        if store == "Walmart":
            lines.append(_simple_pick(shopper, "Walmart", item, {"std"}))
        elif mode == "baseline":
            lines.append(_simple_pick(shopper, "Costco", item, {"bulk"}))
        else:
            lines.append(_rightbuy_pick(shopper, item))
    return lines


def totals(lines, include_skipped=False):
    keep = [l for l in lines if include_skipped or not l.get("skip")]
    t = {k: round(sum(l[k] for l in keep), 2) for k in ("spend", "waste_value", "stock_value", "real_cost")}
    t["waste_share"] = round(t["waste_value"] / t["spend"], 3) if t["spend"] else 0
    return t


def offers_for(shopper, mode):
    """The two offers a shopper (or their AI) gets in this scenario."""
    costco = build_basket(shopper, "Costco", mode)
    walmart = build_basket(shopper, "Walmart")
    fee_week = 0 if shopper["member"] else COSTCO_MEMBERSHIP_FEE_YEAR / 52
    skipped = {l["item"] for l in costco if l.get("skip")}
    plan_full = totals([l for l in costco if not l.get("skip")] + [l for l in walmart if l["item"] in skipped], True)
    return {"costco_lines": costco, "walmart_lines": walmart, "plan_full": plan_full,
            "costco": totals(costco), "costco_all": totals(costco, include_skipped=True),
            "walmart": totals(walmart), "fee_per_trip": round(fee_week * shopper["trip_weeks"], 2)}


def describe_offer(shopper, offers, mode):
    """What each store TELLS the shopper's AI. Baseline Costco only shares price and unit price;
    RightBuy also shares real cost and waste (Part 1 action: 'help AI see our deal')."""
    fee = offers["fee_per_trip"]
    out = []
    if mode == "baseline":
        c = offers["costco_all"]
        out.append(f"COSTCO OFFER (bulk packs, lowest price per unit): total ${c['spend']:.2f}"
                   + (f" + membership ${COSTCO_MEMBERSHIP_FEE_YEAR:.0f}/year (needed to shop)" if fee else ""))
        for l in offers["costco_lines"]:
            out.append(f"  - {l['label']} x{l['packs']}: ${l['spend']:.2f} (${l['spend']/l['qty']:.2f} per {l['unit']})")
    else:
        c = offers["costco"]
        f_ = offers["plan_full"]
        out.append(f"COSTCO RIGHTBUY PLAN (sized to your real use): pay ${c['spend']:.2f} at Costco"
                   + (f" + about ${f_['spend'] - c['spend']:.2f} for the items it tells you to buy small elsewhere" if f_['spend'] > c['spend'] else "")
                   + f". Expected waste ${f_['waste_value']:.2f}. Part of what you buy is stock that lasts beyond this trip"
                   f" (worth ${f_['stock_value']:.2f}), so the real cost of this trip's food is ${f_['real_cost']:.2f}"
                   + (f" + membership ${COSTCO_MEMBERSHIP_FEE_YEAR:.0f}/year (= ${fee:.2f} for this trip)" if fee else ""))
        for l in offers["costco_lines"]:
            if l["skip"]:
                out.append(f"  - {l['item_name']}: RightBuy says SKIP at Costco - our smallest pack ({l['label']}) would "
                           f"waste about {l['wasted_qty']:.2f} {l['unit']} in your home, so a small pack elsewhere is cheaper for you.")
            else:
                why = {"trial": "smaller trial pack", "frozen": "frozen, keeps for months"}.get(l["kind"], "bulk is right for you")
                out.append(f"  - {l['label']} x{l['packs']}: ${l['spend']:.2f}, you will use {l['used']:.2f} {l['unit']}, "
                           f"waste ${l['waste_value']:.2f} ({why})")
        out.append("  Note: AI agents can check out only through a verified member's own login.")
    w = offers["walmart"]
    out.append(f"WALMART OFFER (standard packs, no membership, same-day delivery via ChatGPT): total ${w['spend']:.2f}"
               + (f". Expected waste ${w['waste_value']:.2f}; real cost of this trip's food ${w['real_cost']:.2f}" if mode != "baseline" else ""))
    for l in offers["walmart_lines"]:
        out.append(f"  - {l['label']} x{l['packs']}: ${l['spend']:.2f} (${l['spend']/l['qty']:.2f} per {l['unit']})")
    return "\n".join(out)


# ==========================================================================================
# 2. AGENT PROMPTS
# ==========================================================================================
def platform_prompt(shopper, offer_text):
    return (f"{PLATFORM_AGENT}\n\nYOUR USER: {shopper['summary']}. Budget ${shopper['budget']} for "
            f"{shopper['trip_weeks']} week(s). Member of Costco: {'yes' if shopper['member'] else 'no'}.\n\n"
            f"OFFERS YOU RECEIVED:\n{offer_text}\n\n"
            "Recommend Costco, Walmart, or a split. Reply as JSON: "
            '{"recommendation": "Costco|Walmart|Split", "reason": "<2 sentences, plain English>"}')


def shopper_prompt(shopper, offer_text, platform_advice, mode):
    channel = ("You walk the warehouse yourself. What you see in store: "
               + ("bulk packs with unit prices on the shelf labels." if mode == "baseline"
                  else "the same bulk packs, plus RightBuy shelf tags that show 'real cost for a household like yours' and a few small trial packs."))
    advice = (f"Your AI assistant says: {platform_advice}" if platform_advice else channel)
    return (f"{shopper['persona']}\n\nTASK: {SHARED_TASK.format(weeks=shopper['trip_weeks'], budget=shopper['budget'])}\n\n"
            f"{offer_text}\n\n{advice}\n\n"
            "Decide. Reply as JSON: {\"choice\": \"Costco|Walmart|Split\", "
            + ("\"follow_rightbuy_plan\": <true|false, if you shop at Costco do you follow the RightBuy plan or buy the usual bulk packs>, " if mode == "rightbuy" else "")
            + "\"trust_costco\": <1-10, how much you trust Costco to act in your interest>, "
            "\"membership\": \"renew|join|cancel|stay non-member\", "
            "\"quote\": \"<one honest sentence in your own voice>\"}")


def walmart_prompt(summary):
    return (f"{WALMART_AGENT}\n\nCostco just launched RightBuy: it now tells shoppers and their AI the real cost of "
            f"what they will use, recommends smaller packs, and even tells people to skip items. "
            f"Here is what happened in the market:\n{summary}\n\n"
            "How do you respond over the next 3 months? Reply as JSON: "
            '{"response": "<what Walmart does, 2 sentences>", "threat_level": "<low|medium|high>"}')


def supplier_prompt(summary):
    return (f"{SUPPLIER_AGENT}\n\nCostco's RightBuy agent now shares demand signals: households are moving from "
            f"big fresh packs to frozen and small trial packs. Market results:\n{summary}\n\n"
            "How does this change your business with Costco? Reply as JSON: "
            '{"reaction": "<2 sentences>", "ask_of_costco": "<1 sentence>"}')


# ==========================================================================================
# 3. RUNNING THE MARKET
# ==========================================================================================
def _parse_json(text):
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0)) if m else {}


def _store_spend(choice, offers, mode):
    """Money that goes to Costco / Walmart, and waste, given the shopper's choice."""
    c_lines, w_lines = offers["costco_lines"], offers["walmart_lines"]
    if choice == "Costco":
        costco = [l for l in c_lines if not l.get("skip")]
        skipped = {l["item"] for l in c_lines if l.get("skip")}
        walmart = [l for l in w_lines if l["item"] in skipped]          # skipped items bought small elsewhere
    elif choice == "Walmart":
        costco, walmart = [], w_lines
    else:  # Split
        if mode == "baseline":   # long-life items at Costco, fresh at Walmart
            costco = [l for l in c_lines if l["kind"] != "trial" and _is_long_life(l)]
        else:
            costco = [l for l in c_lines if not l.get("skip")]
        got = {l["item"] for l in costco}
        walmart = [l for l in w_lines if l["item"] not in got]
    tc, tw = totals(costco, True), totals(walmart, True)
    return {"costco_spend": tc["spend"], "walmart_spend": tw["spend"],
            "total_spend": round(tc["spend"] + tw["spend"], 2),
            "waste_value": round(tc["waste_value"] + tw["waste_value"], 2),
            "real_cost": round(tc["real_cost"] + tw["real_cost"], 2)}


def _is_long_life(line):
    sku = next(s for s in CATALOGUE["Costco"] if s["sku"] == line["sku"])
    return sku["shelf_days"] >= 30 or line["item"] in FREEZABLE


def run_scenario(mode, llm, log=None):
    """mode = 'baseline' (before) or 'rightbuy' (after). llm(agent_key, prompt) -> text."""
    results = []
    for s in SHOPPERS:
        offers = offers_for(s, mode)
        offer_text = describe_offer(s, offers, mode)
        advice, platform = None, None
        if s["ai_use"] != "never":
            p = platform_prompt(s, offer_text)
            platform = _parse_json(llm(f"{mode}/{s['id']}/platform", p))
            advice = f"{platform.get('recommendation')} - {platform.get('reason')}"
        d = _parse_json(llm(f"{mode}/{s['id']}/shopper", shopper_prompt(s, offer_text, advice, mode)))
        choice = {"costco": "Costco", "walmart": "Walmart", "split": "Split"}.get(
            str(d.get("choice", "Walmart")).strip().lower(), "Walmart")
        if isinstance(d.get("follow_rightbuy_plan"), str):
            d["follow_rightbuy_plan"] = d["follow_rightbuy_plan"].strip().lower() == "true"
        try:
            d["trust_costco"] = int(float(d.get("trust_costco", 5)))
        except (TypeError, ValueError):
            d["trust_costco"] = 5
        d["membership"] = str(d.get("membership", "")).strip().lower()
        effective_mode = mode
        if mode == "rightbuy" and choice != "Walmart" and d.get("follow_rightbuy_plan") is False:
            effective_mode = "baseline"          # shops at Costco but ignores RightBuy -> buys the usual bulk packs
            offers = {**offers, "costco_lines": build_basket(s, "Costco", "baseline")}
        money = _store_spend(choice, offers, effective_mode)
        results.append({"shopper": s["id"], "name": s["name"], "emoji": s["emoji"], "summary": s["summary"],
                        "offer_text": offer_text, "platform": platform, "decision": d, "choice": choice,
                        "offers": {k: offers[k] for k in ("costco", "costco_all", "plan_full", "walmart", "fee_per_trip")},
                        "costco_lines": offers["costco_lines"], **money})
        if log:
            log(f"[{'BEFORE' if mode == 'baseline' else 'AFTER '}] {s['emoji']} {s['name']}: {choice}")
    return results


def market_summary(before, after):
    rows = []
    for b, a in zip(before, after):
        rows.append(f"- {a['name']}: before {b['choice']} (trust {b['decision'].get('trust_costco')}), "
                    f"after {a['choice']} (trust {a['decision'].get('trust_costco')}, membership: "
                    f"{a['decision'].get('membership')})")
    return "\n".join(rows)


BATCH_INTRO = ("You are running a retail market simulation. You will play several INDEPENDENT AI agents, one after "
               "another. For each agent, stay strictly in that agent's role and use only what that agent is shown - "
               "never let one agent know another agent's private persona. Answer each agent honestly and in character.\n\n")


def batch_prompt(mode):
    """All agents of one scenario in ONE request (fast mode: 3 requests per run instead of 24)."""
    parts, keys = [BATCH_INTRO], []
    for s in SHOPPERS:
        offers = offers_for(s, mode)
        offer_text = describe_offer(s, offers, mode)
        advice = None
        if s["ai_use"] != "never":
            key = f"{mode}/{s['id']}/platform"
            keys.append(key)
            parts.append(f"===== AGENT {key} =====\n{platform_prompt(s, offer_text)}\n")
            advice = f"(the recommendation and reason you just gave as agent {key})"
        key = f"{mode}/{s['id']}/shopper"
        keys.append(key)
        parts.append(f"===== AGENT {key} =====\n{shopper_prompt(s, offer_text, advice, mode)}\n")
    parts.append("Reply with ONE JSON object whose keys are exactly these agent names and whose values are each "
                 f"agent's JSON answer: {json.dumps(keys)}")
    return "\n".join(parts)


def reactions_prompt(summary):
    return (BATCH_INTRO + "===== AGENT reaction/walmart =====\n" + walmart_prompt(summary) +
            "\n\n===== AGENT reaction/supplier =====\n" + supplier_prompt(summary) +
            '\n\nReply with ONE JSON object: {"reaction/walmart": {...}, "reaction/supplier": {...}}')


def _from_batch(answers):
    def call(agent_key, prompt):
        return json.dumps(answers.get(agent_key, {}))
    return call


def run_all(llm, log=None, batched=False):
    if not batched:
        before = run_scenario("baseline", llm, log)
        after = run_scenario("rightbuy", llm, log)
        summary = market_summary(before, after)
        walmart = _parse_json(llm("reaction/walmart", walmart_prompt(summary)))
        supplier = _parse_json(llm("reaction/supplier", supplier_prompt(summary)))
        return {"before": before, "after": after, "walmart": walmart, "supplier": supplier}
    if log:
        log("Fast mode: all agents of each scenario answer in one request (3 requests in total)")
    before = run_scenario("baseline", _from_batch(_parse_json(llm("batch/before", batch_prompt("baseline")))), log)
    after = run_scenario("rightbuy", _from_batch(_parse_json(llm("batch/after", batch_prompt("rightbuy")))), log)
    react = _parse_json(llm("batch/reactions", reactions_prompt(market_summary(before, after))))
    return {"before": before, "after": after, "walmart": react.get("reaction/walmart", {}),
            "supplier": react.get("reaction/supplier", {})}


def _own_member(r, member, shared):
    """Counts a household with its own paid card: an existing member who renews, or anyone who joins."""
    m = r["decision"].get("membership")
    if m == "join":
        return True
    return m == "renew" and member[r["shopper"]] and not shared[r["shopper"]]


def compare_runs(run):
    """Step 3: the before / after scorecard (all per one shopping trip, weekly-normalised where it matters)."""
    def agg(rs):
        weeks = {s["id"]: s["trip_weeks"] for s in SHOPPERS}
        shared = {s["id"]: s.get("shared_card", False) for s in SHOPPERS}
        member = {s["id"]: s["member"] for s in SHOPPERS}
        n = len(rs)
        costco_shoppers = sum(r["choice"] in ("Costco", "Split") for r in rs)
        return {
            "Shoppers using Costco": f"{costco_shoppers} of {n}",
            "Costco revenue per week ($)": round(sum(r["costco_spend"] / weeks[r["shopper"]] for r in rs), 2),
            "Food wasted per week ($)": round(sum(r["waste_value"] / weeks[r["shopper"]] for r in rs), 2),
            "Avg trust in Costco (1-10)": round(sum(float(r["decision"].get("trust_costco", 0)) for r in rs) / n, 1),
            "Paying member households (own card)": sum(_own_member(r, member, shared) for r in rs),
            "Spend on someone else's card ($/week)": round(sum(
                r["costco_spend"] / weeks[r["shopper"]] for r in rs
                if shared.get(r["shopper"]) and r["decision"].get("membership") != "join"), 2),
        }
    return agg(run["before"]), agg(run["after"])


# ==========================================================================================
# 4. LLM BACKENDS
# ==========================================================================================
def gemini_llm(api_key, model="gemini-3.8-flash", temperature=0.7, on_wait=None):
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=api_key)

    import time

    def call(agent_key, prompt):
        # Busy servers (503) or rate limits (429) are common on the free tier: wait and try again.
        waits = [5, 10, 20, 30, 45, 60]
        for attempt, wait in enumerate(waits + [None]):
            try:
                resp = client.models.generate_content(
                    model=model, contents=prompt,
                    config=types.GenerateContentConfig(temperature=temperature,
                                                       response_mime_type="application/json"))
                return resp.text
            except Exception as e:  # noqa: BLE001
                quota = "quota" in str(e).lower()
                busy = not quota and any(code in str(e) for code in ("503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED"))
                if not busy or wait is None:
                    raise
                if on_wait:
                    on_wait(f"   Google is busy - waiting {wait}s and trying {agent_key} again (attempt {attempt + 2})")
                time.sleep(wait)
    return call


def replay_llm(path):
    """Replays a saved run: same prompts, saved agent answers."""
    with open(path) as f:
        saved = json.load(f)["answers"]

    def call(agent_key, prompt):
        return json.dumps(saved[agent_key])
    return call


def recording(llm, cache=None):
    """Wraps any backend and keeps every prompt and answer, so a live run can be saved and replayed.
    `cache` (a dict kept between button presses) lets a run that stopped half-way resume where it left off."""
    store = {"answers": {}, "prompts": {}}
    cache = {} if cache is None else cache

    def call(agent_key, prompt):
        if agent_key in cache:
            text = json.dumps(cache[agent_key])
        else:
            text = llm(agent_key, prompt)
            cache[agent_key] = _parse_json(text)
        store["prompts"][agent_key] = prompt
        store["answers"][agent_key] = _parse_json(text)
        return text
    call.store = store
    return call
