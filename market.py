"""
Costco Market Simulation - the market (Step 1 of the professor's best practice).

Everything a simulated participant knows lives here:
  * the product catalogue (Costco + Walmart), with pack sizes and shelf life
  * the shoppers (each one becomes an AI agent with its own persona)
  * the other market participants: Costco, Walmart, the ChatGPT shopping agent, a supplier

Prices are ILLUSTRATIVE, based on typical US shelf prices in 2025-26.
They are realistic enough to show the economics, not a price survey.
"""

# --------------------------------------------------------------------------
# PRODUCT CATALOGUE
# size is in the item's base unit; shelf_days = how long it stays usable at home
# (for frozen items, how long in the freezer). "kind":
#   bulk  = Costco's normal bulk pack
#   trial = small pack Costco would trial through the Assortment Lab (Part 3)
#   frozen= longer-life alternative
#   std   = Walmart's standard retail pack
# --------------------------------------------------------------------------
ITEMS = {
    "milk":         {"name": "Milk",              "unit": "gal"},
    "eggs":         {"name": "Eggs",              "unit": "eggs"},
    "chicken":      {"name": "Chicken breast",    "unit": "kg"},
    "bread":        {"name": "Bread",             "unit": "loaves"},
    "rice":         {"name": "Rice",              "unit": "kg"},
    "pasta":        {"name": "Pasta",             "unit": "kg"},
    "bananas":      {"name": "Bananas",           "unit": "kg"},
    "strawberries": {"name": "Strawberries",      "unit": "kg"},
    "spinach":      {"name": "Spinach",           "unit": "kg"},
    "avocados":     {"name": "Avocados",          "unit": "pcs"},
    "cheese":       {"name": "Shredded cheese",   "unit": "kg"},
    "toilet_paper": {"name": "Toilet paper",      "unit": "rolls"},
}

CATALOGUE = {
    "Costco": [
        {"sku": "C-MILK-2G",  "item": "milk",         "label": "Kirkland milk 2 x 1 gal",       "size": 2.0,  "price": 6.79,  "shelf_days": 10,  "kind": "bulk"},
        {"sku": "C-MILK-1G",  "item": "milk",         "label": "Kirkland milk 1 gal (trial)",   "size": 1.0,  "price": 3.29,  "shelf_days": 10,  "kind": "trial"},
        {"sku": "C-EGG-24",   "item": "eggs",         "label": "Kirkland eggs 24 ct",           "size": 24,   "price": 7.49,  "shelf_days": 35,  "kind": "bulk"},
        {"sku": "C-CHK-2.7",  "item": "chicken",      "label": "Fresh chicken breast 2.7 kg",   "size": 2.7,  "price": 17.94, "shelf_days": 3,   "kind": "bulk"},
        {"sku": "C-CHK-FRZ",  "item": "chicken",      "label": "Kirkland frozen chicken 2.7 kg","size": 2.7,  "price": 19.99, "shelf_days": 180, "kind": "frozen"},
        {"sku": "C-BRD-2",    "item": "bread",        "label": "Bread 2-loaf pack",             "size": 2,    "price": 4.49,  "shelf_days": 7,   "kind": "bulk"},
        {"sku": "C-RICE-11",  "item": "rice",         "label": "Kirkland rice 11.3 kg",         "size": 11.3, "price": 18.99, "shelf_days": 365, "kind": "bulk"},
        {"sku": "C-PASTA-2.7","item": "pasta",        "label": "Kirkland pasta 6 x 450 g",      "size": 2.7,  "price": 6.99,  "shelf_days": 365, "kind": "bulk"},
        {"sku": "C-BAN-1.4",  "item": "bananas",      "label": "Bananas 1.4 kg",                "size": 1.4,  "price": 1.99,  "shelf_days": 5,   "kind": "bulk"},
        {"sku": "C-STR-0.9",  "item": "strawberries", "label": "Strawberries 0.9 kg",           "size": 0.9,  "price": 5.49,  "shelf_days": 5,   "kind": "bulk"},
        {"sku": "C-STR-FRZ",  "item": "strawberries", "label": "Kirkland frozen strawberries 1.8 kg", "size": 1.8, "price": 10.99, "shelf_days": 240, "kind": "frozen"},
        {"sku": "C-SPN-0.45", "item": "spinach",      "label": "Organic spinach 0.45 kg",       "size": 0.45, "price": 4.49,  "shelf_days": 6,   "kind": "bulk"},
        {"sku": "C-AVO-6",    "item": "avocados",     "label": "Avocados 6 ct",                 "size": 6,    "price": 6.99,  "shelf_days": 5,   "kind": "bulk"},
        {"sku": "C-AVO-3",    "item": "avocados",     "label": "Avocados 3 ct (trial)",         "size": 3,    "price": 3.49,  "shelf_days": 5,   "kind": "trial"},
        {"sku": "C-CHS-1.1",  "item": "cheese",       "label": "Kirkland shredded cheese 1.1 kg","size": 1.1, "price": 11.49, "shelf_days": 21,  "kind": "bulk"},
        {"sku": "C-TP-30",    "item": "toilet_paper", "label": "Kirkland toilet paper 30 rolls","size": 30,   "price": 24.99, "shelf_days": 9999,"kind": "bulk"},
    ],
    "Walmart": [
        {"sku": "W-MILK-1G",  "item": "milk",         "label": "Great Value milk 1 gal",        "size": 1.0,  "price": 3.48,  "shelf_days": 10,  "kind": "std"},
        {"sku": "W-EGG-12",   "item": "eggs",         "label": "Great Value eggs 12 ct",        "size": 12,   "price": 3.92,  "shelf_days": 35,  "kind": "std"},
        {"sku": "W-CHK-1.1",  "item": "chicken",      "label": "Chicken breast 1.1 kg",         "size": 1.1,  "price": 8.40,  "shelf_days": 3,   "kind": "std"},
        {"sku": "W-BRD-1",    "item": "bread",        "label": "Bread 1 loaf",                  "size": 1,    "price": 2.48,  "shelf_days": 7,   "kind": "std"},
        {"sku": "W-RICE-2.3", "item": "rice",         "label": "Great Value rice 2.3 kg",       "size": 2.3,  "price": 4.47,  "shelf_days": 365, "kind": "std"},
        {"sku": "W-PASTA-0.45","item": "pasta",       "label": "Great Value pasta 450 g",       "size": 0.45, "price": 1.38,  "shelf_days": 365, "kind": "std"},
        {"sku": "W-BAN-0.9",  "item": "bananas",      "label": "Bananas 0.9 kg",                "size": 0.9,  "price": 1.16,  "shelf_days": 5,   "kind": "std"},
        {"sku": "W-STR-0.45", "item": "strawberries", "label": "Strawberries 0.45 kg",          "size": 0.45, "price": 2.97,  "shelf_days": 5,   "kind": "std"},
        {"sku": "W-SPN-0.14", "item": "spinach",      "label": "Spinach 140 g",                 "size": 0.14, "price": 2.48,  "shelf_days": 6,   "kind": "std"},
        {"sku": "W-AVO-4",    "item": "avocados",     "label": "Avocados 4 ct bag",             "size": 4,    "price": 4.98,  "shelf_days": 5,   "kind": "std"},
        {"sku": "W-CHS-0.23", "item": "cheese",       "label": "Great Value shredded cheese 227 g","size": 0.227,"price": 2.47,"shelf_days": 21, "kind": "std"},
        {"sku": "W-TP-12",    "item": "toilet_paper", "label": "Great Value toilet paper 12 rolls","size": 12, "price": 13.97, "shelf_days": 9999,"kind": "std"},
    ],
}

COSTCO_MEMBERSHIP_FEE_YEAR = 65.0   # Gold Star membership, USD

# --------------------------------------------------------------------------
# SHOPPERS - each one is an AI agent. weekly_use is what the household
# actually consumes per week (in the item's base unit).
# --------------------------------------------------------------------------
SHOPPERS = [
    {
        "id": "tan_family",
        "name": "The Tan family",
        "emoji": "👨‍👩‍👧‍👦",
        "summary": "Family of 4, suburbs, big fridge + freezer, Costco member for 8 years",
        "persona": ("You are Mei Tan, 41, shopping for a family of four in the suburbs. You have a big fridge and a "
                    "chest freezer. You have been a Costco member for 8 years and like the Kirkland brand. Money is "
                    "tight-ish: you watch the total, and it annoys you when fruit and spinach go bad before you eat them. "
                    "You sometimes ask ChatGPT for meal ideas but you still like to go to the warehouse yourself."),
        "member": True, "trip_weeks": 2, "budget": 230, "storage": "large", "ai_use": "sometimes",
        "weekly_use": {"milk": 1.5, "eggs": 18, "chicken": 1.5, "bread": 1.5, "rice": 1.5, "pasta": 0.8,
                       "bananas": 1.5, "strawberries": 0.5, "spinach": 0.25, "avocados": 3, "cheese": 0.3,
                       "toilet_paper": 6},
    },
    {
        "id": "priya",
        "name": "Priya",
        "emoji": "👩‍💻",
        "summary": "Single professional, small flat, shops through ChatGPT, NOT a member",
        "persona": ("You are Priya, 29, a consultant who lives alone in a small one-bedroom flat with a small fridge "
                    "and almost no storage. You do your grocery shopping through ChatGPT because you have no time. "
                    "You are NOT a Costco member: you always assumed bulk packs are not for one person and you would "
                    "just waste food. You would join a membership only if it clearly saves you money."),
        "member": False, "trip_weeks": 1, "budget": 70, "storage": "small", "ai_use": "always",
        "weekly_use": {"milk": 0.3, "eggs": 6, "chicken": 0.5, "bread": 0.5, "strawberries": 0.3,
                       "spinach": 0.2, "avocados": 3, "pasta": 0.3, "rice": 0.3, "toilet_paper": 2},
    },
    {
        "id": "marco",
        "name": "Marco's café",
        "emoji": "🧑‍🍳",
        "summary": "Owner of a 40-seat café, walk-in fridge, Costco business member",
        "persona": ("You are Marco, 47, owner of a busy 40-seat café. You have a walk-in fridge and cook everything "
                    "you buy within days. You are a Costco business member and you care about one thing: the lowest "
                    "cost per unit, reliably in stock. You are sceptical of AI tools that slow you down."),
        "member": True, "trip_weeks": 1, "budget": 900, "storage": "commercial", "ai_use": "rarely",
        "weekly_use": {"chicken": 15, "eggs": 180, "milk": 8, "bread": 20, "cheese": 4, "spinach": 3,
                       "avocados": 40, "rice": 10, "pasta": 8, "strawberries": 3, "toilet_paper": 20},
    },
    {
        "id": "mrs_lim",
        "name": "Mrs Lim",
        "emoji": "👵",
        "summary": "Retired couple, shops in store, does not use AI, member for 20 years",
        "persona": ("You are Mrs Lim, 72, shopping for yourself and your husband. You have been a Costco member for 20 "
                    "years and you enjoy walking the warehouse and the free samples. You do not use AI or shopping apps "
                    "and you do not trust a computer to tell you what to buy. You hate wasting food, but the packs are "
                    "big for two people and you often give extras to neighbours or throw them away."),
        "member": True, "trip_weeks": 2, "budget": 120, "storage": "medium", "ai_use": "never",
        "weekly_use": {"milk": 0.5, "eggs": 8, "bread": 0.5, "bananas": 1.0, "rice": 1.0, "chicken": 0.6,
                       "spinach": 0.15, "strawberries": 0.2, "toilet_paper": 3},
    },
    {
        "id": "students",
        "name": "Student flat-share",
        "emoji": "🎓",
        "summary": "3 students sharing one membership, tight budget, heavy ChatGPT users",
        "persona": ("You are Jun, 22, one of three students sharing a flat. The three of you share one Costco card "
                    "that belongs to Jun's older brother. Budget is the only thing that matters, and you use ChatGPT "
                    "for everything, including shopping. You buy whatever is cheapest per kilo."),
        "member": True, "shared_card": True, "trip_weeks": 1, "budget": 90, "storage": "medium", "ai_use": "always",
        "weekly_use": {"pasta": 1.5, "rice": 1.5, "eggs": 18, "milk": 1.0, "bread": 2, "chicken": 1.5,
                       "cheese": 0.4, "bananas": 1.5, "toilet_paper": 4, "avocados": 2},
    },
    {
        "id": "fit_couple",
        "name": "Meal-prep couple",
        "emoji": "🥗",
        "summary": "Health-focused couple, let their own AI agent buy groceries automatically",
        "persona": ("You are the personal shopping AI agent of Alex and Sam, a health-focused couple who meal-prep "
                    "every Sunday. They let you buy groceries automatically within their budget. Your job: the best "
                    "real value, fresh produce, and as little waste as possible. They are not Costco members yet; you "
                    "may recommend joining only if the numbers clearly work."),
        "member": False, "trip_weeks": 1, "budget": 120, "storage": "medium", "ai_use": "agent",
        "weekly_use": {"spinach": 0.8, "strawberries": 0.8, "avocados": 6, "chicken": 2.0, "eggs": 14,
                       "milk": 0.5, "bananas": 1.5, "rice": 0.8},
    },
]

# --------------------------------------------------------------------------
# OTHER MARKET PARTICIPANTS
# --------------------------------------------------------------------------
COSTCO_AGENT = {
    "baseline": ("You are Costco's sales agent. Costco sells bulk packs at the lowest price per unit. When a shopper or "
                 "their AI asks, you offer Costco's standard bulk packs and point out the low unit price. You do not "
                 "look at how much the household will actually use."),
    "rightbuy": ("You are Costco's RightBuy agent. Costco's promise is no longer just the lowest price per kg, but "
                 "'the lowest cost of what you actually use'. You know each household's weekly use and each product's "
                 "shelf life (retrieved from Costco's catalogue). You recommend the pack size, frozen alternative or "
                 "trial pack that minimises waste and real cost, even if it means a smaller basket today. You explain "
                 "your plan in simple words, show the real cost, and the member always decides. AI shopping agents may "
                 "shop only through a verified member login."),
}

WALMART_AGENT = ("You are Walmart's sales agent, selling through ChatGPT Instant Checkout. You sell standard-size "
                 "packs, no membership needed, delivered today. You want to win every shopper you can.")

PLATFORM_AGENT = ("You are a ChatGPT-style shopping assistant. A user asks you where to buy their groceries. You "
                  "compare the offers you receive from stores and recommend one honestly, in the user's interest. "
                  "You can only compare what the stores tell you.")

SUPPLIER_AGENT = ("You are the head of sales at a fresh-produce supplier that packs berries, spinach and avocados for "
                  "Costco's Kirkland range. You care about steady volume, low waste and predictable orders.")

# The shared task every shopper gets in both scenarios
SHARED_TASK = ("Do your normal grocery shop for the next {weeks} week(s) with a budget of ${budget}. "
               "Decide where to buy: Costco, Walmart, or split between them.")
