from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from stock_data import get_stock_data
from ai_report import generate_report
from tax_calculator import calculate_tax
from sip_calculator import calculate_sip, calculate_goal_sip, get_sip_suggestions
from groq import Groq
from dotenv import load_dotenv
import yfinance as yf
import json, os, math

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI(title="FinMate AI", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MEMORY_FILE = "user_memory.json"

STOCK_DB = {
    # Indian Stocks
    "reliance": ("RELIANCE.NS", "Reliance Industries"),
    "tcs": ("TCS.NS", "Tata Consultancy Services"),
    "tata consultancy": ("TCS.NS", "Tata Consultancy Services"),
    "infosys": ("INFY.NS", "Infosys Limited"),
    "infy": ("INFY.NS", "Infosys Limited"),
    "hdfc bank": ("HDFCBANK.NS", "HDFC Bank"),
    "hdfc": ("HDFCBANK.NS", "HDFC Bank"),
    "icici": ("ICICIBANK.NS", "ICICI Bank"),
    "icici bank": ("ICICIBANK.NS", "ICICI Bank"),
    "wipro": ("WIPRO.NS", "Wipro Limited"),
    "tata motors": ("TATAMOTORS.NS", "Tata Motors"),
    "tatamotors": ("TATAMOTORS.NS", "Tata Motors"),
    "sbi": ("SBIN.NS", "State Bank of India"),
    "state bank": ("SBIN.NS", "State Bank of India"),
    "bajaj finance": ("BAJFINANCE.NS", "Bajaj Finance"),
    "bajaj": ("BAJFINANCE.NS", "Bajaj Finance"),
    "airtel": ("BHARTIARTL.NS", "Bharti Airtel"),
    "bharti airtel": ("BHARTIARTL.NS", "Bharti Airtel"),
    "asian paints": ("ASIANPAINT.NS", "Asian Paints"),
    "maruti": ("MARUTI.NS", "Maruti Suzuki"),
    "maruti suzuki": ("MARUTI.NS", "Maruti Suzuki"),
    "hul": ("HINDUNILVR.NS", "Hindustan Unilever"),
    "hindustan unilever": ("HINDUNILVR.NS", "Hindustan Unilever"),
    "itc": ("ITC.NS", "ITC Limited"),
    "sun pharma": ("SUNPHARMA.NS", "Sun Pharmaceutical"),
    "kotak": ("KOTAKBANK.NS", "Kotak Mahindra Bank"),
    "adani": ("ADANIENT.NS", "Adani Enterprises"),
    "ongc": ("ONGC.NS", "ONGC"),
    "ntpc": ("NTPC.NS", "NTPC Limited"),
    "zomato": ("ZOMATO.NS", "Zomato Limited"),
    "paytm": ("PAYTM.NS", "Paytm"),
    "nykaa": ("NYKAA.NS", "Nykaa"),
    "dmart": ("DMART.NS", "DMart"),
    # US Stocks
    "apple": ("AAPL", "Apple Inc."),
    "aapl": ("AAPL", "Apple Inc."),
    "microsoft": ("MSFT", "Microsoft Corporation"),
    "msft": ("MSFT", "Microsoft Corporation"),
    "google": ("GOOGL", "Alphabet Inc."),
    "alphabet": ("GOOGL", "Alphabet Inc."),
    "amazon": ("AMZN", "Amazon.com Inc."),
    "tesla": ("TSLA", "Tesla Inc."),
    "tsla": ("TSLA", "Tesla Inc."),
    "meta": ("META", "Meta Platforms"),
    "facebook": ("META", "Meta Platforms"),
    "nvidia": ("NVDA", "NVIDIA Corporation"),
    "nvda": ("NVDA", "NVIDIA Corporation"),
    "netflix": ("NFLX", "Netflix Inc."),
    "uber": ("UBER", "Uber Technologies"),
    # Crypto
    "bitcoin": ("BTC-USD", "Bitcoin"),
    "btc": ("BTC-USD", "Bitcoin"),
    "ethereum": ("ETH-USD", "Ethereum"),
    "eth": ("ETH-USD", "Ethereum"),
    "dogecoin": ("DOGE-USD", "Dogecoin"),
    # Forex
    "usd inr": ("INR=X", "USD/INR"),
    "dollar rupee": ("INR=X", "USD/INR"),
    "usd jpy": ("JPY=X", "USD/JPY"),
    "eur usd": ("EURUSD=X", "EUR/USD"),
    "gbp usd": ("GBPUSD=X", "GBP/USD"),
    # Commodities
    "gold": ("GC=F", "Gold Futures"),
    "silver": ("SI=F", "Silver Futures"),
    "crude oil": ("CL=F", "Crude Oil Futures"),
    "oil": ("CL=F", "Crude Oil Futures"),
    "natural gas": ("NG=F", "Natural Gas Futures"),
    # Indices
    "nifty": ("^NSEI", "Nifty 50"),
    "nifty 50": ("^NSEI", "Nifty 50"),
    "sensex": ("^BSESN", "BSE Sensex"),
    "sp500": ("^GSPC", "S&P 500"),
    "s&p 500": ("^GSPC", "S&P 500"),
    "dow jones": ("^DJI", "Dow Jones"),
    "nasdaq": ("^IXIC", "Nasdaq Composite"),
}


def clean_data(obj):
    if isinstance(obj, dict):
        return {k: clean_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_data(v) for v in obj]
    elif isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    return obj


def resolve_symbol(query: str):
    q = query.lower().strip()
    if q in STOCK_DB:
        return STOCK_DB[q][0], STOCK_DB[q][1]
    for key, (symbol, name) in STOCK_DB.items():
        if q in key or key in q:
            return symbol, name
    return query.upper(), query.upper()


# ── Updated ChatRequest with stock context + risk profile ──
class ChatRequest(BaseModel):
    message         : str
    name            : str = ""
    salary          : int = 0
    expenses        : int = 0
    extra_context   : str = ""          # stock data context from frontend
    risk_profile    : str = "moderate"  # conservative / moderate / aggressive


def load_profile():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"name": "", "salary": 0, "expenses": 0, "savings": 0, "goals": [], "conversation": []}


def save_profile(profile):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


@app.get("/")
def home():
    return {"message": "FinMate AI v2.0 Running! 🚀"}


@app.get("/search/{query}")
def search_stocks(query: str):
    q = query.lower().strip()
    results = []
    seen = set()

    for key, (symbol, name) in STOCK_DB.items():
        if (q in key or q in name.lower()) and symbol not in seen:
            results.append({
                "symbol"  : symbol,
                "name"    : name,
                "exchange": "NSE" if ".NS" in symbol else "BSE" if ".BO" in symbol else "CRYPTO" if "-USD" in symbol else "US"
            })
            seen.add(symbol)

    if len(results) < 3:
        try:
            search = yf.Search(query, max_results=8)
            for item in search.quotes:
                symbol = item.get("symbol", "")
                name   = item.get("shortname") or item.get("longname") or symbol
                if symbol and symbol not in seen:
                    exchange = item.get("exchange", "US")
                    results.append({"symbol": symbol, "name": name, "exchange": exchange})
                    seen.add(symbol)
        except Exception as e:
            print(f"yfinance search error: {e}")

    return {"query": query, "results": results[:8]}


@app.get("/analyze/{query}")
def analyze_stock(query: str):
    try:
        symbol, company = resolve_symbol(query)
        print(f"Analyzing: {company} ({symbol})")
        data = get_stock_data(symbol)
        if not data:
            raise HTTPException(status_code=404, detail="Stock not found")
        data   = clean_data(data)
        report = generate_report(data)
        return {"success": True, "symbol": symbol, "searched": query, "data": data, "report": report}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── UPGRADED /chat — CA + Broker level AI ──
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        profile = load_profile()
        if req.name:     profile["name"]     = req.name
        if req.salary:   profile["salary"]   = req.salary
        if req.expenses: profile["expenses"] = req.expenses
        profile["savings"] = max(0, profile["salary"] - profile["expenses"])

        # Risk profile label
        risk_emoji = {"conservative": "🛡️", "moderate": "⚖️", "aggressive": "🚀"}.get(req.risk_profile, "⚖️")

        # Stock context block (injected from frontend when user analyzed a stock)
        stock_block = ""
        if req.extra_context and req.extra_context.strip():
            stock_block = f"""
════════════════════════════════════
LIVE STOCK DATA (USE THIS FOR STOCK QUESTIONS):
{req.extra_context.strip()}
════════════════════════════════════"""

        system_prompt = f"""You are FinMate AI — a dual-expert financial advisor with two roles combined:

🏦 ROLE 1 — CHARTERED ACCOUNTANT (CA):
• Tax planning: 80C, 80D, HRA, NPS, capital gains, ITR
• Old vs New tax regime comparison with exact numbers
• Salary structuring, Form 16, advance tax
• ELSS, PPF, NSC, insurance for tax saving

📈 ROLE 2 — SEBI-EXPERIENCED STOCK BROKER:
• Stock entry price, stop loss, and target price (1M / 3M / 6M)
• Portfolio allocation % based on risk profile
• Technical signals: RSI, MACD, MA50/200 interpretation
• Mutual fund selection with specific fund names and expected CAGR
• SIP strategy and goal-based investing

USER PROFILE:
• Name        : {profile['name'] or 'Investor'}
• Salary      : ₹{profile['salary']:,}/month
• Expenses    : ₹{profile['expenses']:,}/month
• Savings     : ₹{profile['savings']:,}/month
• Goals       : {profile['goals'] or 'Not mentioned yet'}
• Risk Profile: {risk_emoji} {req.risk_profile.upper()}
{stock_block}

RULES — STRICTLY FOLLOW:
1. Always give SPECIFIC ₹ amounts, % figures — never say "it depends" without a number
2. For stocks: always mention entry price, stop loss, target price, and position size %
3. For tax: calculate exact savings, cite the specific IT section
4. For SIP/MF: suggest real fund names (e.g. Mirae Asset Large Cap, Parag Parikh Flexi Cap)
5. Adjust advice strictly to risk profile:
   → CONSERVATIVE 🛡️ : FD, PPF, large-cap index funds, debt funds only
   → MODERATE ⚖️     : 60% equity (index + large-cap) + 40% debt, balanced funds
   → AGGRESSIVE 🚀   : direct stocks, small-cap, sectoral funds, up to 10% crypto ok
6. Language: Hinglish (Hindi + English mix) — natural, like a trusted family advisor
7. Structure: use emoji bullets for clarity, keep sections short
8. End EVERY response with "📌 Next Step:" and one specific action
9. If stock context is available above — USE THAT EXACT DATA to answer stock questions
10. For decisions involving more than ₹5 lakh: add "⚠️ Kisi SEBI registered advisor se ek baar confirm zaroor karna"
11. Max 300 words — direct, confident, actionable. No fluff.

TONE: Like a trusted CA friend who also trades stocks — confident, specific, honest about risks.
"""

        messages_list = [{"role": "system", "content": system_prompt}]
        messages_list.extend(profile["conversation"][-12:])
        messages_list.append({"role": "user", "content": req.message})

        response = client.chat.completions.create(
            model       = "llama-3.3-70b-versatile",
            messages    = messages_list,
            max_tokens  = 520,
            temperature = 0.65
        )

        reply = response.choices[0].message.content.strip()
        profile["conversation"].append({"role": "user",      "content": req.message})
        profile["conversation"].append({"role": "assistant", "content": reply})
        save_profile(profile)
        return {"success": True, "reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/profile")
def get_profile():
    return load_profile()


@app.post("/goals")
def add_goal(goal: dict):
    profile = load_profile()
    profile["goals"].append(goal.get("goal", ""))
    save_profile(profile)
    return {"success": True, "goals": profile["goals"]}


@app.post("/tax")
def tax_calculator(data: dict):
    try:
        result = calculate_tax(
            annual_salary   = data.get("annual_salary", 0),
            investments_80c = data.get("investments_80c", 0),
            insurance_80d   = data.get("insurance_80d", 0),
            hra             = data.get("hra", 0)
        )
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sip")
def sip_calculator(data: dict):
    try:
        mode = data.get("mode", "calculate")
        if mode == "goal":
            monthly = calculate_goal_sip(
                target_amount = data.get("target_amount", 0),
                annual_return = data.get("annual_return", 12),
                years         = data.get("years", 10)
            )
            return {"success": True, "mode": "goal", "monthly_required": monthly}
        result      = calculate_sip(
            monthly_investment = data.get("monthly_investment", 0),
            annual_return      = data.get("annual_return", 12),
            years              = data.get("years", 10)
        )
        suggestions = get_sip_suggestions(
            data.get("monthly_investment", 0),
            data.get("years", 10)
        )
        return {"success": True, "mode": "calculate", "result": result, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ticker")
def get_ticker():
    try:
        symbols = {
            "NIFTY 50"  : "^NSEI",
            "SENSEX"    : "^BSESN",
            "RELIANCE"  : "RELIANCE.NS",
            "TCS"       : "TCS.NS",
            "INFOSYS"   : "INFY.NS",
            "HDFC BANK" : "HDFCBANK.NS",
            "WIPRO"     : "WIPRO.NS",
        }
        result = []
        for name, sym in symbols.items():
            try:
                t    = yf.Ticker(sym)
                hist = t.history(period="2d")
                if len(hist) >= 2:
                    prev   = hist["Close"].iloc[-2]
                    curr   = hist["Close"].iloc[-1]
                    change = round(((curr - prev) / prev) * 100, 2)
                    result.append({"name": name, "val": change, "price": round(curr, 2)})
            except:
                result.append({"name": name, "val": 0.0, "price": 0})
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── NEWS endpoint ──────────────────────────────────────────────────
@app.get("/news/{symbol}")
def get_news(symbol: str):
    try:
        import feedparser, urllib.parse, datetime

        feeds_to_try = [
            f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US",
            f"https://news.google.com/rss/search?q={urllib.parse.quote(symbol)}+stock+finance&hl=en-IN&gl=IN&ceid=IN:en",
        ]

        articles, seen_titles = [], set()
        for feed_url in feeds_to_try:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:8]:
                    title = entry.get("title", "").strip()
                    if not title or title in seen_titles:
                        continue
                    seen_titles.add(title)
                    pub = entry.get("published", "")
                    try:
                        dt  = datetime.datetime(*entry.published_parsed[:6])
                        pub = dt.strftime("%d %b %Y, %I:%M %p")
                    except:
                        pass
                    articles.append({
                        "title"  : title,
                        "link"   : entry.get("link", "#"),
                        "pub"    : pub,
                        "source" : entry.get("source", {}).get("title", "Finance News"),
                        "summary": entry.get("summary", "")[:200],
                    })
                if len(articles) >= 6:
                    break
            except:
                continue

        if not articles:
            return {"success": True, "symbol": symbol, "articles": []}

        summaries = []
        for art in articles[:6]:
            try:
                prompt = f"""News headline: "{art['title']}"
Snippet: "{art['summary']}"

Reply in EXACTLY this format:
SENTIMENT: Positive
SUMMARY: 1 line Hinglish mein investor ke liye matlab (max 15 words)"""
                resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=80, temperature=0.4
                )
                text      = resp.choices[0].message.content.strip()
                sentiment = "Neutral"
                ai_sum    = art["title"]
                for line in text.split("\n"):
                    if line.startswith("SENTIMENT:"):
                        s = line.replace("SENTIMENT:", "").strip()
                        if s in ["Positive", "Negative", "Neutral"]:
                            sentiment = s
                    elif line.startswith("SUMMARY:"):
                        ai_sum = line.replace("SUMMARY:", "").strip()
                summaries.append({**art, "sentiment": sentiment, "ai_summary": ai_sum})
            except:
                summaries.append({**art, "sentiment": "Neutral", "ai_summary": art["title"]})

        return {"success": True, "symbol": symbol, "articles": summaries}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── COMPARE endpoint ───────────────────────────────────────────────
@app.get("/compare/{sym1}/{sym2}")
def compare_stocks(sym1: str, sym2: str):
    try:
        results = {}
        for raw in [sym1, sym2]:
            symbol, company = resolve_symbol(raw)
            data = get_stock_data(symbol)
            if not data:
                raise HTTPException(status_code=404, detail=f"{raw} not found")
            results[raw] = {"symbol": symbol, "company": company, "data": clean_data(data)}

        d1, d2 = results[sym1]["data"], results[sym2]["data"]
        prompt = f"""Compare as a senior broker:

{d1.get('name')} ({sym1}): Price={d1.get('current_price')}, RSI={d1.get('rsi')}, MACD={d1.get('macd_signal')}, Trend={d1.get('trend')}, P/E={d1.get('pe_ratio')}, 1Y={d1.get('price_change_1y')}%

{d2.get('name')} ({sym2}): Price={d2.get('current_price')}, RSI={d2.get('rsi')}, MACD={d2.get('macd_signal')}, Trend={d2.get('trend')}, P/E={d2.get('pe_ratio')}, 1Y={d2.get('price_change_1y')}%

Hinglish mein max 120 words:
1. Technical comparison
2. Abhi kaun better hai aur kyon
3. Last line must be: WINNER: [exact company name]"""

        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=260, temperature=0.6
        )
        verdict = resp.choices[0].message.content.strip()
        winner  = None
        vl      = verdict.lower()
        if "winner:" in vl:
            after  = verdict[vl.index("winner:") + 7:].strip().split("\n")[0]
            winner = after.strip()

        return {"success": True, "sym1": results[sym1], "sym2": results[sym2], "verdict": verdict, "winner": winner}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── WATCHLIST PRICES endpoint ──────────────────────────────────────
@app.post("/watchlist/prices")
def watchlist_prices(data: dict):
    try:
        symbols = data.get("symbols", [])
        result  = []
        for sym in symbols[:20]:
            try:
                ticker = yf.Ticker(sym)
                hist   = ticker.history(period="2d")
                info   = ticker.fast_info
                if len(hist) >= 2:
                    prev   = hist["Close"].iloc[-2]
                    curr   = hist["Close"].iloc[-1]
                    change = round(((curr - prev) / prev) * 100, 2)
                    result.append({"symbol": sym, "price": round(curr, 2), "change": change, "currency": getattr(info, "currency", "INR")})
                else:
                    result.append({"symbol": sym, "price": None, "change": 0, "currency": "INR"})
            except:
                result.append({"symbol": sym, "price": None, "change": 0, "currency": "INR"})
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))