# Costco market simulation: what changed

**Set-up:** six shopper agents, Walmart, a ChatGPT shopping agent and a produce supplier. All shoppers get the same
task: their normal grocery shop on their normal budget. We ran the market twice:
- **Before:** Costco sells bulk packs at the lowest price per unit.
- **After:** Costco launches **RightBuy** ("the lowest cost of what you actually use"). AI agents can only check out
  through the member's own login.

**Main run:** live Gemini agents (gemini-3.5-flash, fast mode). A first test run (Claude playing the agents) is kept
as a cross-check (see the end).

## Scorecard: live Gemini run (per week)

| Metric | Before | After | Change |
|---|---|---|---|
| Shoppers using Costco | 3 of 6 | 4 of 6 | **+1 shopper** |
| Costco revenue | $534.78 | $613.47 | **+15%** |
| Food thrown away | $49.32 | $40.94 | **−17%** |
| Average trust in Costco (1-10) | 7.0 | 7.3 | +0.3 |
| Paying member households (own card) | 3 | 4 | **+1 new member** |

## Shopper by shopper (live run)

| Shopper | Before → After | Trust | What happened and why |
|---|---|---|---|
| 👨‍👩‍👧‍👦 Tan family | Costco → **Split** | 9 → 9 | Followed RightBuy. Bulk staples at Costco, fresh fruit small elsewhere. Waste per trip fell from **$12.71 to $3.47** while Costco spend stayed the same. *"Saves us money and keeps food out of the trash."* |
| 👩‍💻 Priya (single, small flat) | Walmart → Walmart | 4 → 4 | Her ChatGPT agent compared **today's bill** ($48.53 Walmart vs about $72 for the RightBuy plan, over her $70 budget), not real cost. *"I don't have the space or money to store giant bulk items."* |
| 🧑‍🍳 Marco's café | Costco → Costco | 9 → 8 | No change. Bulk was already right for a café. |
| 👵 Mrs Lim | Costco → Costco | 8 → 9 | Loyal, but **ignored the RightBuy tags**. Her waste did not fall ($32.77). *"…even if we end up giving extra food to the neighbours."* |
| 🎓 Students | Walmart → Walmart | 7 → 6 | Budget first. The Costco plan was over $90 today. |
| 🥗 Meal-prep couple's AI agent | Walmart → **Split, joins Costco** | 5 → 8 | The autonomous AI agent read RightBuy's real-cost data and **joined Costco**. Waste fell from $3.09 to $0.99. Costco gained **$65/week** of new spend. |

## Market reactions (live run)

- **Walmart (threat: HIGH):** will push "no membership, same-day delivery" through ChatGPT Instant Checkout to win back
  split-cart households. It will also add its own **price-per-use calculator** to copy RightBuy.
- **Supplier:** will expand flash-frozen and small-pack lines and rely less on bulk fresh packs. Asks Costco for
  **90-day rolling forecast commitments** and **co-investment in small-pack bagging machines**.

## Six findings for the deck

1. **AI agents respond to data; people respond to habit and today's budget.** The meal-prep couple's autonomous agent
   switched and joined. Mrs Lim and the students did not move. RightBuy's first customers are **AI agents**, which is
   exactly the "AI-first" shift from Part 1.
2. **Waste fell and revenue rose.** −17% waste and +15% revenue, from a new member, not bigger baskets. Costco makes
   much of its profit from membership fees, so this fits its model.
3. **"Today's bill" beats "real cost".** Priya's AI compared upfront spend, and the plan was over her weekly budget.
   RightBuy needs a **"fits your budget today" option**: smaller trial packs (Assortment Lab) or pay-per-week stock.
4. **Technology alone does not reach every member.** Mrs Lim ignored the tags in **both runs**. Non-AI members need
   staff and in-store help. That is organisation transformation, not technology.
5. **Competitors copy within months.** Walmart rated the threat HIGH and will build its own price-per-use tool
   (Kovács: if it is easy to build, it is easy to copy). The lasting moat is the member relationship, not the feature
   (Homework 5: whoever wins the customer first, wins).
6. **RightBuy reshapes the supply chain.** The supplier shifts to frozen and small packs but wants forecast commitments
   and shared investment. So Part 4 needs a supplier-partnership action, not just an app.

## Cross-check: two runs, same direction

| | Test run (Claude as agents) | Live run (Gemini) |
|---|---|---|
| Food waste | −42% | −17% |
| Trust | 6.0 → 7.3 | 7.0 → 7.3 |
| New paying member | +1 (Priya joined) | +1 (meal-prep couple joined) |
| Mrs Lim follows RightBuy? | No | No |
| Marco changes? | No | No |
| Walmart threat | Medium | High |

Both runs agree on the direction: less waste, a bit more trust, one new member, non-AI members unchanged, and Walmart
copies. **Who** converts differs from run to run, which is normal with LLM agents and worth saying in class.

*Prices are illustrative US shelf prices. Every prompt and answer is in live_run_gemini.json and in the app's
"Agent transcripts" tab.*
