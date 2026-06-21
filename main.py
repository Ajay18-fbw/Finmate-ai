from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
from stock_data import get_stock_data
from ai_report import generate_report
from tax_calculator import calculate_tax
from sip_calculator import calculate_sip, calculate_goal_sip, get_sip_suggestions
from auth import (
    init_db, get_db, hash_password, verify_password,
    create_token, get_current_user, get_current_user_optional,
    load_user_profile, save_user_profile
)
from groq import Groq
from dotenv import load_dotenv
import yfinance as yf
import json, os, math, sqlite3

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI(title="FinMate AI", version="3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Init DB on startup ────────────────────────────────────────────
@app.on_event("startup")
def startup():
    init_db()

# ── STOCK_DB ──────────────────────────────────────────────────────
STOCK_DB = {
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
    "bitcoin": ("BTC-USD", "Bitcoin"),
    "btc": ("BTC-USD", "Bitcoin"),
    "ethereum": ("ETH-USD", "Ethereum"),
    "eth": ("ETH-USD", "Ethereum"),
    "dogecoin": ("DOGE-USD", "Dogecoin"),
    "usd inr": ("INR=X", "USD/INR"),
    "dollar rupee": ("INR=X", "USD/INR"),
    "usd jpy": ("JPY=X", "USD/JPY"),
    "eur usd": ("EURUSD=X", "EUR/USD"),
    "gbp usd": ("GBPUSD=X", "GBP/USD"),
    "gold": ("GC=F", "Gold Futures"),
    "silver": ("SI=F", "Silver Futures"),
    "crude oil": ("CL=F", "Crude Oil Futures"),
    "oil": ("CL=F", "Crude Oil Futures"),
    "natural gas": ("NG=F", "Natural Gas Futures"),
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
    # Direct match
    if q in STOCK_DB:
        return STOCK_DB[q][0], STOCK_DB[q][1]
    # Partial match
    for key, (symbol, name) in STOCK_DB.items():
        if q in key or key in q:
            return symbol, name
    # Already a valid symbol (e.g. MARUTI.NS passed directly)
    upper = query.upper()
    return upper, upper

# ─── Pydantic Models ──────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name    : str
    email   : str
    password: str

class LoginRequest(BaseModel):
    email   : str
    password: str

class ChatRequest(BaseModel):
    message      : str
    salary       : int = 0
    expenses     : int = 0
    extra_context: str = ""
    risk_profile : str = "moderate"

class ProfileUpdate(BaseModel):
    salary      : int = 0
    expenses    : int = 0
    risk_profile: str = "moderate"

# ─── AUTH ENDPOINTS ───────────────────────────────────────────────
@app.post("/auth/register")
def register(req: RegisterRequest):
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    if len(req.name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters")

    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?", (req.email.lower().strip(),)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed = hash_password(req.password)
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (req.name.strip(), req.email.lower().strip(), hashed)
        )
        user_id = cursor.lastrowid
        conn.commit()

        # Create default profile
        save_user_profile(user_id, {
            "salary": 0, "expenses": 0, "goals": [],
            "risk_profile": "moderate", "conversation": [], "watchlist": []
        })

        token = create_token(user_id, req.email.lower().strip(), req.name.strip())
        return {
            "success": True,
            "token"  : token,
            "user"   : {"id": user_id, "name": req.name.strip(), "email": req.email.lower().strip()}
        }
    except HTTPException:
        raise
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/auth/login")
def login(req: LoginRequest):
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (req.email.lower().strip(),)
        ).fetchone()

        if not user or not verify_password(req.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Update last login
        conn.execute(
            "UPDATE users SET last_login = datetime('now') WHERE id = ?", (user["id"],)
        )
        conn.commit()

        token = create_token(user["id"], user["email"], user["name"])
        return {
            "success": True,
            "token"  : token,
            "user"   : {"id": user["id"], "name": user["name"], "email": user["email"]}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    profile = load_user_profile(current_user["user_id"])
    return {
        "success": True,
        "user"   : current_user,
        "profile": profile
    }

@app.post("/auth/update-profile")
def update_profile(req: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    profile = load_user_profile(current_user["user_id"])
    profile["salary"]       = req.salary
    profile["expenses"]     = req.expenses
    profile["risk_profile"] = req.risk_profile
    save_user_profile(current_user["user_id"], profile)
    return {"success": True, "profile": profile}

# ─── CORE ENDPOINTS (now per-user) ───────────────────────────────
@app.get("/")
def home():
    return {"message": "FinMate AI v3.0 — with Auth 🔐"}

@app.get("/search/{query}")
def search_stocks(query: str):
    q = query.lower().strip()
    results, seen = [], set()
    for key, (symbol, name) in STOCK_DB.items():
        if (q in key or q in name.lower()) and symbol not in seen:
            results.append({
                "symbol"  : symbol,
                "name"    : name,
                "exchange": "NSE" if ".NS" in symbol else "BSE" if ".BO" in symbol
                            else "CRYPTO" if "-USD" in symbol else "US"
            })
            seen.add(symbol)
    if len(results) < 3:
        try:
            search = yf.Search(query, max_results=8)
            for item in search.quotes:
                symbol = item.get("symbol", "")
                name   = item.get("shortname") or item.get("longname") or symbol
                if symbol and symbol not in seen:
                    results.append({"symbol": symbol, "name": name, "exchange": item.get("exchange", "US")})
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

@app.post("/chat")
def chat(req: ChatRequest, current_user: dict = Depends(get_current_user)):
    try:
        profile = load_user_profile(current_user["user_id"])
        if req.salary:   profile["salary"]   = req.salary
        if req.expenses: profile["expenses"] = req.expenses
        profile["savings"]      = max(0, profile["salary"] - profile["expenses"])
        risk_profile            = req.risk_profile or profile.get("risk_profile", "moderate")
        profile["risk_profile"] = risk_profile

        risk_emoji = {"conservative": "🛡️", "moderate": "⚖️", "aggressive": "🚀"}.get(risk_profile, "⚖️")

        stock_block = ""
        if req.extra_context and req.extra_context.strip():
            stock_block = f"\n════════════════════════════════════\nLIVE STOCK DATA:\n{req.extra_context.strip()}\n════════════════════════════════════"

        system_prompt = f"""You are FinMate AI — a dual-expert financial advisor:

🏦 CA EXPERTISE: Tax planning (80C/80D/HRA/NPS), ITR, old vs new regime, salary structuring
📈 BROKER EXPERTISE: Stock entry/exit/stop-loss/target, portfolio allocation, MF selection, SIP strategy

USER:
• Name        : {current_user['name']}
• Salary      : ₹{profile['salary']:,}/month
• Expenses    : ₹{profile['expenses']:,}/month
• Savings     : ₹{max(0, profile['salary'] - profile['expenses']):,}/month
• Goals       : {profile.get('goals') or 'Not set'}
• Risk Profile: {risk_emoji} {risk_profile.upper()}
{stock_block}

RULES:
1. Specific ₹ amounts + % always — never vague
2. Stocks: entry price, stop loss, target (1M/3M/6M), position size %
3. Tax: exact savings + IT section (80C etc.)
4. MF: real fund names + expected CAGR
5. Risk matching: Conservative=FD/PPF/debt | Moderate=60:40 equity:debt | Aggressive=stocks/small-cap
6. Hinglish — conversational, like trusted CA friend
7. End with "📌 Next Step:" always
8. >₹5L decisions: add "⚠️ SEBI registered advisor se confirm karo"
9. If stock data above → use EXACT numbers
10. Max 300 words — direct, no fluff
"""
        msgs = [{"role": "system", "content": system_prompt}]
        msgs.extend(profile["conversation"][-12:])
        msgs.append({"role": "user", "content": req.message})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=msgs, max_tokens=520, temperature=0.65
        )
        reply = response.choices[0].message.content.strip()

        profile["conversation"].append({"role": "user",      "content": req.message})
        profile["conversation"].append({"role": "assistant", "content": reply})
        save_user_profile(current_user["user_id"], profile)

        return {"success": True, "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/goals")
def add_goal(goal: dict, current_user: dict = Depends(get_current_user)):
    profile = load_user_profile(current_user["user_id"])
    profile["goals"].append(goal.get("goal", ""))
    save_user_profile(current_user["user_id"], profile)
    return {"success": True, "goals": profile["goals"]}

@app.post("/watchlist/save")
def save_watchlist(data: dict, current_user: dict = Depends(get_current_user)):
    profile = load_user_profile(current_user["user_id"])
    profile["watchlist"] = data.get("watchlist", [])
    save_user_profile(current_user["user_id"], profile)
    return {"success": True}

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
        suggestions = get_sip_suggestions(data.get("monthly_investment", 0), data.get("years", 10))
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
                prompt = f"""News: "{art['title']}"
Reply EXACTLY:
SENTIMENT: Positive
SUMMARY: 1 line Hinglish investor ke liye (max 15 words)"""
                resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=80, temperature=0.4
                )
                text = resp.choices[0].message.content.strip()
                sentiment, ai_sum = "Neutral", art["title"]
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
        prompt = f"""Compare as senior broker:
{d1.get('name')} ({sym1}): Price={d1.get('current_price')}, RSI={d1.get('rsi')}, MACD={d1.get('macd_signal')}, Trend={d1.get('trend')}, P/E={d1.get('pe_ratio')}, 1Y={d1.get('price_change_1y')}%
{d2.get('name')} ({sym2}): Price={d2.get('current_price')}, RSI={d2.get('rsi')}, MACD={d2.get('macd_signal')}, Trend={d2.get('trend')}, P/E={d2.get('pe_ratio')}, 1Y={d2.get('price_change_1y')}%
Hinglish max 120 words. End with: WINNER: [company name]"""
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=260, temperature=0.6
        )
        verdict = resp.choices[0].message.content.strip()
        winner  = None
        vl      = verdict.lower()
        if "winner:" in vl:
            winner = verdict[vl.index("winner:") + 7:].strip().split("\n")[0].strip()
        return {"success": True, "sym1": results[sym1], "sym2": results[sym2], "verdict": verdict, "winner": winner}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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