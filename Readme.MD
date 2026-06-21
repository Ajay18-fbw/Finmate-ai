# 💰 FinMate AI

**India's AI-powered personal finance advisor — CA + Broker intelligence in one app.**

FinMate AI combines the knowledge of a Chartered Accountant and a Stock Broker into a single conversational AI. Ask anything in Hindi or English — get specific numbers, real fund names, entry/exit levels, and tax-saving strategies.

---

## 🚀 Live Demo

> Coming soon — deployment in progress

---

## ✨ Features

### 🤖 AI Financial Advisor (CA + Broker Mode)
- Conversational AI powered by **LLaMA 3.3 70B** via Groq
- Responds in **Hinglish** (Hindi + English mix)
- Gives specific ₹ amounts, fund names, and actionable next steps
- **Risk profile aware** — Conservative 🛡️ / Moderate ⚖️ / Aggressive 🚀
- Remembers conversation history per user session

### 📊 Stock Analysis
- Search any **Indian stock, US stock, Crypto, Forex, Commodity, or Index**
- Live data via Yahoo Finance
- Full **Technical Analysis** — RSI, MACD, MA50/200, Bollinger Bands, Support/Resistance
- Full **Fundamental Analysis** — P/E, EPS, Revenue, ROE, Debt/Equity
- Interactive **Candlestick Chart** with hover OHLC tooltip
- AI-generated **Buy / Hold / Sell** report for each asset

### ⭐ Watchlist
- Star any analyzed stock to add to watchlist
- Live price + % change updates every 60 seconds
- Persists across sessions (saved per user in database)
- Visible on Home page for quick access

### 📰 News Feed
- Latest financial news for any stock or index
- AI-generated **1-line Hinglish summary** per article
- **Sentiment badge** — Positive 📈 / Negative 📉 / Neutral ➖
- Trending topics quick-select

### ⚖️ Stock Comparison
- Compare any two assets side by side
- Metrics table with **winner highlighted** in green
- AI Hinglish comparison verdict
- Quick presets — TCS vs Infosys, BTC vs ETH, Apple vs Microsoft

### 🧾 Tax Calculator (2024-25)
- Old Regime vs New Regime comparison
- Inputs — Salary, 80C investments, 80D insurance, HRA
- Exact tax savings calculation
- AI-generated tax saving tips

### 📈 SIP Calculator
- **Calculate Returns mode** — monthly SIP → future value with donut chart
- **Goal Planning mode** — target amount → required monthly SIP
- Interactive range sliders with real-time updates
- Fund recommendations

### 🔐 Authentication System
- Secure **JWT-based login** with 7-day session
- **bcrypt + SHA-256** password hashing
- Per-user data isolation — each user has their own profile, watchlist, and chat history
- SQLite database (no external DB server needed)

### 🌙 Dark Mode
- Full dark/light theme toggle
- Saved to localStorage — persists across sessions
- Smooth transitions on all components

### 📱 Responsive Design
- Mobile-first layout
- Bottom navigation bar on mobile
- Collapsible hamburger menu
- All grids adapt to screen size

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Axios |
| Backend | FastAPI (Python) |
| AI Model | LLaMA 3.3 70B via Groq API |
| Market Data | Yahoo Finance (yfinance) |
| Database | SQLite (via Python sqlite3) |
| Auth | JWT (python-jose) + bcrypt |
| News | RSS feeds + AI summarization |
| Fonts | Inter + JetBrains Mono |

---

## 📁 Project Structure

```
finmate-ai/
├── main.py              # FastAPI backend — all API endpoints
├── auth.py              # JWT authentication + SQLite helpers
├── stock_data.py        # Yahoo Finance data fetching + technical indicators
├── ai_report.py         # AI report generation (stock/forex/crypto/commodity)
├── tax_calculator.py    # Old vs New regime tax calculation logic
├── sip_calculator.py    # SIP returns + goal planning calculations
├── .env                 # API keys (never commit this)
├── finmate.db           # SQLite database (never commit this)
├── requirements.txt     # Python dependencies
└── frontend/
    └── src/
        └── App.jsx      # Full React frontend (single file)
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/finmate-ai.git
cd finmate-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo GROQ_API_KEY=your_key_here > .env

# Start backend
python -m uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App will be live at `http://localhost:5173`

---

## 📦 Requirements

Create a `requirements.txt` in your project root:

```
fastapi
uvicorn
groq
yfinance
python-jose[cryptography]
bcrypt
python-multipart
feedparser
python-dotenv
pandas
numpy
pydantic
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Register new user | ❌ |
| POST | `/auth/login` | Login + get JWT token | ❌ |
| GET | `/auth/me` | Get current user profile | ✅ |
| GET | `/ticker` | Live market ticker data | ❌ |
| GET | `/search/{query}` | Stock search autocomplete | ❌ |
| GET | `/analyze/{symbol}` | Full stock analysis + AI report | ❌ |
| POST | `/chat` | AI financial advisor chat | ✅ |
| POST | `/tax` | Tax calculation | ❌ |
| POST | `/sip` | SIP calculation | ❌ |
| GET | `/news/{symbol}` | News + AI summaries | ❌ |
| GET | `/compare/{sym1}/{sym2}` | Side-by-side comparison | ❌ |
| POST | `/watchlist/prices` | Live watchlist prices | ❌ |
| POST | `/watchlist/save` | Save watchlist to DB | ✅ |

---

## 📊 Supported Assets

| Category | Examples |
|---|---|
| Indian Stocks | Reliance, TCS, HDFC Bank, Infosys, Wipro, Zomato, Paytm (+20 more) |
| US Stocks | Apple, Microsoft, Google, Tesla, NVIDIA, Meta, Amazon |
| Crypto | Bitcoin, Ethereum, Dogecoin |
| Forex | USD/INR, EUR/USD, GBP/USD, USD/JPY |
| Commodities | Gold, Silver, Crude Oil, Natural Gas |
| Indices | Nifty 50, Sensex, S&P 500, Nasdaq, Dow Jones |

> Any other symbol can be searched via Yahoo Finance search integration.

---

## 🔮 Future Scope

- **Portfolio Tracker** — Add holdings, track real-time P&L, allocation pie chart
- **Deploy to Cloud** — Vercel (frontend) + Render (backend) + Supabase (PostgreSQL)
- **Google OAuth** — One-click login with Google account
- **Price Alerts** — Notify when stock hits target or stop loss
- **PDF Reports** — Download stock analysis as PDF to share with advisor
- **Paper Trading** — Simulate trades without real money
- **Mutual Fund Screener** — Filter funds by category, returns, risk rating
- **Budget Tracker** — Monthly income/expense tracking with charts
- **Goal Tracker** — Visual progress bar for financial goals (house, car, retirement)
- **WhatsApp Bot** — Send financial queries via WhatsApp

---

## ⚠️ Disclaimer

FinMate AI is a **personal project built for educational purposes**. It is not a SEBI-registered investment advisor. All stock analysis, AI reports, and financial advice generated by this app should not be treated as professional financial advice. Always consult a SEBI-registered advisor before making investment decisions.

---

## 👨‍💻 Built By

**Ajay Singh** — Student, SAU (South Asian University)

---

## 📄 License

MIT License — free to use, modify, and distribute.