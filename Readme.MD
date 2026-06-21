<div align="center">

# 💰 FinMate AI
### India's AI-Powered Personal Finance Advisor

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org)
[![Groq](https://img.shields.io/badge/AI-LLaMA%203.3%2070B-orange.svg)](https://groq.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen.svg)]()

[Why FinMate?](#-why-finmate-not-chatgpt-or-gemini) • [Features](#-features) • [Tech Stack](#-tech-stack) • [Installation](#-installation) • [Usage](#-usage) • [Roadmap](#-roadmap)

</div>

---

## 🧠 About

**FinMate AI** is a full-stack AI-powered personal finance web application built to explore the intersection of **LLM APIs**, **real-time financial data**, and **multilingual user experience** for Indian users.

The core idea: most online financial tools assume the user speaks English and already understands finance. FinMate AI flips this — it communicates in **Hindi/Hinglish**, accepts plain questions like *"Bhai meri salary 35,000 hai, kya karun?"* and responds with a clear, personalized, step-by-step financial plan.

---

## 🤔 Why FinMate? Not ChatGPT or Gemini?

This is the most important question. Here's the honest answer:

### 1. 🎯 Domain-Specific vs General Purpose

ChatGPT and Gemini are **general-purpose** assistants. FinMate is built **exclusively for Indian personal finance**.

```
ChatGPT: "You should consider diversifying your portfolio 
          with index funds and bonds..."

FinMate: "Teri salary Rs.35,000 aur expenses Rs.22,000 ke 
          hisaab se abhi Rs.13,000 bachte hain. 
          
          Step 1: Rs.5,000 emergency fund mein daal
                  (target: Rs.1,32,000 — 6 months cover)
          Step 2: Rs.5,000 Nifty 50 SIP shuru karo
                  (5 saal baad: Rs.3.8 Lakh+)
          Step 3: Rs.2,000 PPF — Rs.600 tax bachega
          Step 4: Rs.1,000 health insurance lo"
```

The difference: **FinMate uses your actual numbers. ChatGPT gives general theory.**

---

### 2. 💾 Persistent Financial Memory

ChatGPT/Gemini forget everything when you close the tab. FinMate remembers your complete financial profile.

```
Session 1 (Monday):
You: "Meri salary 45,000 hai"
FinMate: Saves your profile permanently

Session 2 (Friday):
You: "Aaj bonus mila Rs.10,000 — kya karun?"
FinMate: "Tera emergency fund Rs.8,000 tha last time.
          Rs.7,000 wahan daalo, Rs.3,000 SIP top-up karo"
          → Already knows your situation!

ChatGPT: "What is your salary and financial situation?"
          → Starts from zero every time
```

---

### 3. 📊 Live Market Data Integration

ChatGPT and Gemini have **knowledge cutoffs** — they don't know today's stock prices.

```
You: "Reliance mein invest karun?"

ChatGPT: "Reliance is a good company with strong fundamentals..."
          → No current price, no live data

FinMate: "RELIANCE.NS — Current: Rs.1,321 | RSI: 31 (Oversold)
          52W High: Rs.1,611 | Today: -2.1%
          Technical: Bearish MACD, near support Rs.1,290
          Fundamental: P/E 22x, Revenue Rs.10.5T
          
          Verdict: HOLD — Wait for RSI above 40
          Target: Rs.1,450 (6 months)"
          → Real data, real analysis, right now
```

---

### 4. 🇮🇳 India-Specific Financial Knowledge

General AI gives global advice. FinMate knows Indian finance deeply.

```
Topics ChatGPT handles generically that FinMate handles specifically:

✅ Section 80C, 80D, 80CCD tax deductions
✅ PPF, NPS, ELSS — Indian instruments only
✅ NSE, BSE, Nifty 50, Sensex
✅ New vs Old Tax Regime comparison
✅ SEBI regulations
✅ Indian mutual fund houses (Mirae, Parag Parikh, Axis)
✅ CIBIL score guidance
✅ HRA calculation for Indian salaried employees
```

---

### 5. 💬 Natural Hinglish — Not Just Hindi Translation

ChatGPT translates English financial concepts into Hindi. FinMate thinks in Hinglish natively.

```
ChatGPT Hindi mode:
"आपको विविध पोर्टफोलियो बनाना चाहिए जिसमें..."
→ Direct translation, sounds unnatural

FinMate:
"Yaar, abhi tera sara paisa FD mein hai — yeh thoda 
risky hai inflation ke against. Chal SIP shuru karte 
hain, Rs.1,000 se bhi ho jaata hai. Nifty 50 mein 
lagao — market ke saath grow karta hai..."
→ Sounds like a real dost talking
```

---

### 6. 💰 Built for Indian Income Levels

Global AI tools are optimized for Western financial contexts ($, €, global markets). FinMate is calibrated for **Indian salaries, Indian prices, Indian goals**.

```
FinMate understands:
→ Rs.15,000/month salary (entry level)
→ Rs.25,000 rent in Mumbai
→ Getting married in 2 years
→ Sending money to parents every month
→ Planning for a home loan in India
→ Gold as investment (very Indian concept)

ChatGPT would suggest: "Consider a Roth IRA..." 
→ Completely irrelevant for India
```

---

### Summary Table

| Feature | ChatGPT / Gemini | FinMate AI |
|---|---|---|
| Financial Memory | ❌ Resets every session | ✅ Permanent profile |
| Live Stock Data | ❌ Knowledge cutoff | ✅ Real-time via yfinance |
| Indian Tax Laws | Generic | ✅ 80C, 80D, HRA specific |
| Indian Markets | Generic | ✅ NSE, BSE, Nifty, Sensex |
| Language | Translated Hindi | ✅ Native Hinglish |
| Personalization | Based on chat only | ✅ Full financial profile |
| Stock Analysis | Text only | ✅ RSI, MACD, Live data |
| Indian Salary Context | ❌ Western-biased | ✅ Rs. calibrated |

> **In short: ChatGPT is a smart generalist. FinMate is a specialist who knows your finances.**

---

## ✨ Features

| Module | Description | Status |
|---|---|---|
| 🤖 AI Financial Chat | Hindi/Hinglish advice based on your salary & goals | ✅ Live |
| 📊 Stock Analysis | Any stock → AI Buy/Hold/Sell report with live data | ✅ Live |
| 💰 Finance Dashboard | Income, expenses, net worth, goal tracker | 🔨 Building |
| 🧾 Tax Planning | 80C, 80D calculator — legal tax reduction | 🔨 Building |
| 📈 MF Guide | Fund recommendations + SIP calculator | 🔨 Building |
| 🎓 FinMate Learn | 5-min lessons — SIP, stocks, tax basics | 📋 Planned |

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.11+ | Core language |
| FastAPI | REST API — fast, async, auto-documented |
| Groq API (LLaMA 3.3 70B) | AI financial advice + stock reports |
| yfinance | Real-time stock market data |
| Pandas | Technical indicator calculations (RSI, MACD, MA) |
| PostgreSQL | Database |
| Redis | Caching for stock data |

### Frontend
| Technology | Purpose |
|---|---|
| React 18 + Vite | UI framework + fast dev server |
| TailwindCSS | Utility-first styling |
| Axios | API communication |
| Recharts | Stock price charts |

---

## 📁 Project Structure

```
finmate-ai/
│
├── backend/
│   ├── chat.py                  # AI Financial Advisor (Terminal)
│   ├── main.py                  # FastAPI entry point
│   ├── stock_data.py            # Live data + technical analysis
│   ├── ai_report.py             # AI stock report generation
│   ├── routers/
│   │   ├── chat.py              # Chat API endpoints
│   │   ├── stocks.py            # Stock analysis endpoints
│   │   ├── tax.py               # Tax planning endpoints
│   │   └── mf.py                # Mutual fund endpoints
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # Main dashboard
│   │   ├── components/
│   │   │   ├── Chat/            # AI chat interface
│   │   │   ├── StockSearch/     # Stock analysis UI
│   │   │   ├── Dashboard/       # Finance dashboard
│   │   │   └── TaxPlanner/      # Tax planning UI
│   │   └── pages/
│   ├── vite.config.js
│   └── package.json
│
├── .env.example
└── README.md
```

---

## ⚡ Installation

### Prerequisites
- Python 3.11+
- Node.js 16+
- Git

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/finmate-ai.git
cd finmate-ai

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

Create `.env` file in backend folder:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your **free** Groq API key at: https://console.groq.com

---

## 💻 Usage

### AI Financial Chat

```bash
python chat.py
```

```
=============================================
   FinMate AI — Your Personal Finance Dost!
=============================================

Tumhara naam kya hai? -> Ajay
Monthly salary kitni hai? Rs. -> 45000
Monthly expenses kitne hain? Rs. -> 30000
Monthly savings: Rs.15000 (33.3%)

Ajay: SIP mein kitna invest karun?

FinMate: Teri savings Rs.15,000/month ke hisaab se:

  Step 1 — Emergency Fund (Rs.5,000/month)
           Target: Rs.1,80,000 (6 months cover)

  Step 2 — SIP (Rs.7,000/month)
           Rs.3,000 → Nifty 50 Index Fund
           Rs.2,000 → Mirae Asset Large Cap
           Rs.2,000 → Parag Parikh Flexi Cap

  Step 3 — Tax Saving (Rs.3,000/month)
           Rs.1,500 → PPF (7.1% guaranteed)
           Rs.1,500 → ELSS (80C benefit)

  5 saal baad: Rs.6.2 Lakh+ expected

  Next Step: Aaj Groww pe account kholo,
             Rs.500 SIP se start karo!
```

### Stock Analysis

```bash
# Start API server
uvicorn main:app --reload

# Analyze stocks
curl http://localhost:8000/analyze/RELIANCE.NS
curl http://localhost:8000/analyze/AAPL
curl http://localhost:8000/analyze/TCS.NS
```

---

## 🗺 Roadmap

- [x] AI Financial Chat with Hindi/Hinglish support
- [x] Persistent user financial profile (memory)
- [x] Stock Analysis with live data (yfinance)
- [x] Technical indicators (RSI, MACD, Bollinger Bands)
- [x] AI-generated Buy/Hold/Sell reports
- [x] FastAPI backend
- [x] React frontend dashboard
- [ ] Tax Planning calculator (80C, 80D)
- [ ] Mutual Fund recommendation engine
- [ ] User authentication (JWT)
- [ ] Finance Dashboard with charts
- [ ] Mobile App (React Native)
- [ ] Fine-tune LLaMA on Indian financial data

---

## 🧩 Key Learnings

**AI & Prompt Engineering**
- Writing domain-specific system prompts for finance AI
- Injecting user context (salary, goals) into LLM prompts
- Balancing response quality vs speed with different models

**Backend**
- Building async REST APIs with FastAPI
- Fetching and processing real-time financial data
- Custom technical indicator calculations with Pandas

**Frontend**
- React + Vite workflow
- Connecting React frontend to Python backend
- Displaying financial data in readable UI

**Finance Domain**
- SIP and mutual fund return calculations
- Tax deductions under Section 80C/80D
- Reading stock fundamentals and technical charts

---

## ⚠️ Disclaimer

FinMate AI provides general financial information for educational purposes only. It is **NOT** a SEBI registered investment advisor. For major financial decisions, please consult a certified financial planner.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built by **Ajay Singh** | B.Tech CSE | South Asian University, New Delhi

*"Learning AI and finance — one commit at a time."*

⭐ If you found this useful, please star the repo!

</div>
