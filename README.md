# Costco Market Simulator (BMS5213 · Group Project Part 4)

The professor's best practice, built as a working app:

| Step | What the professor asked | Where it is |
|---|---|---|
| 1 | Simulate your market with AI agents, including one for your organisation | `market.py` - 6 shopper agents, Costco, Walmart, a ChatGPT shopping agent, a produce supplier |
| 2 | Introduce your AI use case into the simulated organisation (modify prompt or RAG) | `COSTCO_AGENT["rightbuy"]` prompt + the catalogue/shelf-life data fed in (RAG) |
| 3 | Analyse how the market changed - have customer reactions changed? | `compare_runs()` and tab ④ in the app |

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

- **Replay saved run** (default): no key needed, always works in class.
- **Run live with Gemini**: paste a free key from aistudio.google.com. Every agent answers live; results vary a bit
  each run, which is normal (worth saying in class).

To put it online like SmartShop: push this folder to GitHub → share.streamlit.io → New app → `app.py`.

## How it works

- **Python does the money maths** (pack sizes, shelf life, waste, real cost) so the numbers are exact and auditable.
- **The AI agents make the human decisions**: where to shop, trust (1-10), join/renew/cancel, whether to follow the
  RightBuy plan, and how Walmart and the supplier react.
- **RightBuy logic**: for each item it tries every Costco option (bulk, frozen, small trial pack) and every pack count,
  *including buying nothing*, and picks the lowest real cost for what the household will actually use. If a small
  pack elsewhere is cheaper, it honestly says "skip this at Costco".
- **Member-login rule** (Part 1 action): AI agents can check out only through the member's own login, so shared cards
  stop working through AI.

## Files

- `market.py` - catalogue, personas, agent prompts, shared task
- `sim.py` - basket maths, RightBuy engine, prompts, run + scorecard, Gemini/replay backends
- `app.py` - the Streamlit demo
- `results/live_run_gemini.json` - the live run with real Gemini agents (gemini-3.5-flash, fast mode) - shown by default
- `results/reference_run_claude.json` - first test run, with Claude playing the agents (built by `make_reference_run.py`)

Prices are illustrative US shelf prices, not a price survey.
