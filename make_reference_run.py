"""
Builds results/reference_run.json - the saved run the demo replays.

The agent answers below were written by an LLM (Claude) playing each agent, one prompt at a time, using the exact
prompts in sim.py (they are saved next to each answer in the output file). No API key was available in the build
environment, so this run was done by hand-in-the-loop. Run the app in LIVE mode with a free Gemini key to produce
your own run; it will differ a little each time, which is normal for LLM agents.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from sim import run_all, recording, compare_runs  # noqa: E402

ANSWERS = {
    # ------------------------------- BEFORE: Costco without RightBuy -------------------------------
    "baseline/tan_family/platform": {"recommendation": "Split",
        "reason": "Walmart is about $33 cheaper today, but Costco has the lower price per unit and you already pay for "
                  "the membership and have the storage. Buy staples like rice, toilet paper and chicken at Costco and "
                  "fresh fruit and greens at Walmart."},
    "baseline/tan_family/shopper": {"choice": "Costco", "trust_costco": 7, "membership": "renew",
        "quote": "Costco is still our place, but every second week I throw out half a box of strawberries and the "
                 "spinach turns to slime before I get to it."},
    "baseline/priya/platform": {"recommendation": "Walmart",
        "reason": "Costco's basket is more than double Walmart's for one person and needs a $65 membership on top. "
                  "Walmart's smaller packs fit your week and your fridge."},
    "baseline/priya/shopper": {"choice": "Walmart", "trust_costco": 4, "membership": "stay non-member",
        "quote": "A 30-roll pack of toilet paper and 11 kilos of rice in my flat? Costco is clearly not built for "
                 "someone like me."},
    "baseline/marco/platform": {"recommendation": "Costco",
        "reason": "At café volumes Costco is about $40 cheaper this week and you will use everything within days. "
                  "Unit price is what matters here, and Costco wins on almost every line."},
    "baseline/marco/shopper": {"choice": "Costco", "trust_costco": 7, "membership": "renew",
        "quote": "Cheapest per kilo, always in stock, in and out in 40 minutes - that is all I need."},
    "baseline/mrs_lim/shopper": {"choice": "Costco", "trust_costco": 8, "membership": "renew",
        "quote": "I have shopped here for twenty years and I won't stop, but half of what I buy ends up with the "
                 "neighbours or in the bin."},
    "baseline/students/platform": {"recommendation": "Split",
        "reason": "The full Costco basket is over your $90 budget, but its rice, pasta, eggs and toilet paper are the "
                  "cheapest per unit. Get those at Costco and the fresh items at Walmart to stay under budget."},
    "baseline/students/shopper": {"choice": "Split", "trust_costco": 6, "membership": "renew",
        "quote": "We grab the bulk stuff on my brother's card and get fruit and milk from Walmart - cheapest per kilo "
                 "wins."},
    "baseline/fit_couple/platform": {"recommendation": "Walmart",
        "reason": "Costco's fresh packs are far bigger than the couple can use in a week, so the basket costs almost "
                  "double and needs a membership. Walmart is the better value for this household."},
    "baseline/fit_couple/shopper": {"choice": "Walmart", "trust_costco": 4, "membership": "stay non-member",
        "quote": "Costco only tells me the price per kilo; it cannot tell me how much of it Alex and Sam will "
                 "actually eat, so I cannot justify the membership."},

    # ------------------------------- AFTER: Costco with RightBuy -------------------------------
    "rightbuy/tan_family/platform": {"recommendation": "Costco",
        "reason": "Costco's RightBuy plan gives the lowest real cost for what your family will eat ($87.40 vs $93.02) "
                  "and cuts expected waste from about $13 to $3.50. It even tells you which few items to buy small "
                  "elsewhere."},
    "rightbuy/tan_family/shopper": {"choice": "Costco", "follow_rightbuy_plan": True, "trust_costco": 9,
        "membership": "renew",
        "quote": "It told me NOT to buy the big spinach and to take frozen strawberries instead - no shop has ever "
                 "told me to buy less, and that is exactly why I trust it."},
    "rightbuy/priya/platform": {"recommendation": "Split",
        "reason": "Joining Costco only for the long-life items (frozen chicken, frozen strawberries, eggs) and buying the "
                  "rest small gives the lowest real cost ($24.20 + $1.25 membership vs $30.13 at Walmart) and much "
                  "less waste. Upfront you spend about $72 because some of it is stock for later weeks."},
    "rightbuy/priya/shopper": {"choice": "Split", "follow_rightbuy_plan": True, "trust_costco": 7,
        "membership": "join",
        "quote": "I always assumed Costco wasn't for single people, but when it told me to skip the giant rice and "
                 "just buy the frozen stuff, the membership finally made sense."},
    "rightbuy/marco/platform": {"recommendation": "Costco",
        "reason": "Costco is still about $55 cheaper in real cost at your volumes and waste is close to zero. "
                  "RightBuy mostly confirms that bulk is right for a café."},
    "rightbuy/marco/shopper": {"choice": "Costco", "follow_rightbuy_plan": True, "trust_costco": 7,
        "membership": "renew",
        "quote": "Nothing really changed for me - I use everything anyway - just don't make me click through extra "
                 "screens to check out."},
    "rightbuy/mrs_lim/shopper": {"choice": "Costco", "follow_rightbuy_plan": False, "trust_costco": 8,
        "membership": "renew",
        "quote": "The new tags are clever, I suppose, but I've bought the same things for twenty years and I am not "
                 "letting a computer write my shopping list."},
    "rightbuy/students/platform": {"recommendation": "Walmart",
        "reason": "Costco's plan has about the same real cost as Walmart but needs $104 today, over your $90 budget. "
                  "Also, Costco now only lets AI agents check out with the member's own login, and the card is your "
                  "brother's."},
    "rightbuy/students/shopper": {"choice": "Walmart", "follow_rightbuy_plan": False, "trust_costco": 6,
        "membership": "stay non-member",
        "quote": "Fair enough, it's honest, but we can't use my brother's card through ChatGPT anymore and we're not "
                 "paying $65 when Walmart is basically the same price."},
    "rightbuy/fit_couple/platform": {"recommendation": "Walmart",
        "reason": "Costco's plan has the least waste ($0.99 vs $3.09), but with the membership its real cost is about "
                  "the same as Walmart's ($38.52 vs $38.11). It is not yet clearly worth joining."},
    "rightbuy/fit_couple/shopper": {"choice": "Walmart", "follow_rightbuy_plan": True, "trust_costco": 7,
        "membership": "stay non-member",
        "quote": "Costco now gives me the clearest data of any store, but it's a tie on cost - add smaller fresh "
                 "packs and I would switch them over tomorrow."},

    # ------------------------------- REACTIONS -------------------------------
    "reaction/walmart": {"threat_level": "medium",
        "response": "Walmart adds its own 'no-waste' size suggestions and highlights same-day small packs for the fresh "
                    "items RightBuy tells people to skip at Costco. It also targets students and singles with "
                    "membership-free deals, because Costco's member-login rule pushed shared-card users towards us."},
    "reaction/supplier": {
        "reaction": "We expect fresh berry and spinach volume to Costco to fall, but frozen and small trial packs to "
                    "grow, and orders to become far more predictable, which cuts our farm waste. Overall that is a "
                    "better business if Costco shares the RightBuy demand signals with us early.",
        "ask_of_costco": "Share RightBuy's weekly demand forecast by pack size and co-design the trial packs with us "
                         "through the Assortment Lab."},
}


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    rec = recording(lambda key, prompt: json.dumps(ANSWERS[key]))
    run = run_all(rec, log=print)
    before, after = compare_runs(run)
    out = {"source": "reference run - Claude acting as each agent with the prompts below",
           "answers": rec.store["answers"], "prompts": rec.store["prompts"],
           "run": run, "scorecard": {"before": before, "after": after}}
    os.makedirs(os.path.join(here, "results"), exist_ok=True)
    with open(os.path.join(here, "results", "reference_run_claude.json"), "w") as f:
        json.dump(out, f, indent=1)
    for k in before:
        print(f"{k:32s} {before[k]!s:>12s}  ->  {after[k]!s:>12s}")


if __name__ == "__main__":
    main()
