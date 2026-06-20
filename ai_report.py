from groq import Groq
from dotenv import load_dotenv
from stock_data import get_stock_data
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_report(stock_data):
    print("\nGenerating AI Report...")

    asset_type = stock_data.get("asset_type", "stock")

    # ── STOCK — original detailed format (unchanged) ──
    if asset_type == "stock":
        prompt = f"""
You are a senior professional stock market analyst at a top investment firm.
Generate a detailed, structured, and professional stock analysis report.

═══════════════════════════════════════
STOCK DATA
═══════════════════════════════════════
Company        : {stock_data.get('name')}
Symbol         : {stock_data.get('symbol')}
Sector         : {stock_data.get('sector')}
Industry       : {stock_data.get('industry')}

PRICE DATA:
Current Price  : {stock_data.get('current_price')} {stock_data.get('currency')}
Market Cap     : {stock_data.get('market_cap')}
52W High       : {stock_data.get('52w_high')}
52W Low        : {stock_data.get('52w_low')}
Volume         : {stock_data.get('volume')}
Change (1D)    : {stock_data.get('price_change_1d')}%
Change (1M)    : {stock_data.get('price_change_1m')}%
Change (1Y)    : {stock_data.get('price_change_1y')}%

TECHNICAL INDICATORS:
Trend          : {stock_data.get('trend')}
MA50           : {stock_data.get('ma50')}
MA200          : {stock_data.get('ma200')}
RSI            : {stock_data.get('rsi')} ({stock_data.get('rsi_signal')})
MACD           : {stock_data.get('macd')} ({stock_data.get('macd_signal')})
Bollinger Up   : {stock_data.get('bb_upper')}
Bollinger Low  : {stock_data.get('bb_lower')}
Support        : {stock_data.get('support')}
Resistance     : {stock_data.get('resistance')}

FUNDAMENTAL DATA:
P/E Ratio      : {stock_data.get('pe_ratio')}
EPS            : {stock_data.get('eps')}
Revenue        : {stock_data.get('revenue')}
Profit Margin  : {stock_data.get('profit_margin')}
Debt/Equity    : {stock_data.get('debt_to_equity')}
ROE            : {stock_data.get('roe')}
Dividend Yield : {stock_data.get('dividend_yield')}

═══════════════════════════════════════
Generate a professional report with EXACTLY these sections:

1. EXECUTIVE SUMMARY
   Brief 2-3 line overview

2. PRICE PERFORMANCE
   Analyze 1D, 1M, 1Y performance and trend

3. TECHNICAL ANALYSIS
   Analyze RSI, MACD, MA50/200, Bollinger Bands
   Support/Resistance levels
   Short-term outlook

4. FUNDAMENTAL ANALYSIS
   P/E vs industry, EPS, Revenue growth
   Profitability and debt analysis

5. RISK ASSESSMENT
   Key risks (minimum 3 points)
   Risk Score: X/10

6. INVESTMENT VERDICT
   ▶ BUY / HOLD / SELL
   ▶ Confidence: X%
   ▶ Target Price (6 months): X
   ▶ Stop Loss: X
   ▶ Time Horizon: Short/Medium/Long term

Use professional tone. Be specific with numbers.
Max 500 words.
"""

    # ── FOREX — currency pair format ──
    elif asset_type == "forex":
        prompt = f"""
You are a senior forex market analyst at a top investment firm.
Generate a detailed, structured, professional currency pair analysis report.

═══════════════════════════════════════
FOREX DATA
═══════════════════════════════════════
Currency Pair  : {stock_data.get('name')}
Symbol         : {stock_data.get('symbol')}

PRICE DATA:
Current Rate   : {stock_data.get('current_price')}
52W High       : {stock_data.get('52w_high')}
52W Low        : {stock_data.get('52w_low')}
Change (1D)    : {stock_data.get('price_change_1d')}%
Change (1M)    : {stock_data.get('price_change_1m')}%
Change (1Y)    : {stock_data.get('price_change_1y')}%

TECHNICAL INDICATORS:
Trend          : {stock_data.get('trend')}
MA50           : {stock_data.get('ma50')}
MA200          : {stock_data.get('ma200')}
RSI            : {stock_data.get('rsi')} ({stock_data.get('rsi_signal')})
MACD           : {stock_data.get('macd')} ({stock_data.get('macd_signal')})
Bollinger Up   : {stock_data.get('bb_upper')}
Bollinger Low  : {stock_data.get('bb_lower')}
Support        : {stock_data.get('support')}
Resistance     : {stock_data.get('resistance')}

═══════════════════════════════════════
Generate a report with EXACTLY these sections:

1. EXECUTIVE SUMMARY
   Brief 2-3 line overview of this currency pair

2. PRICE PERFORMANCE
   Analyze 1D, 1M, 1Y performance and trend

3. TECHNICAL ANALYSIS
   Analyze RSI, MACD, MA50/200, Bollinger Bands
   Support/Resistance levels
   Short-term outlook

4. MACRO FACTORS
   Interest rate differentials, central bank policy,
   inflation, and geopolitical factors affecting this pair

5. RISK ASSESSMENT
   Key risks (minimum 3 points)
   Risk Score: X/10

6. TRADING VERDICT
   ▶ BUY / HOLD / SELL
   ▶ Confidence: X%
   ▶ Target Rate (1 month): X
   ▶ Stop Loss: X
   ▶ Time Horizon: Short/Medium/Long term

DO NOT mention P/E, EPS, Revenue or any company fundamentals.
Use professional tone. Be specific with numbers. Max 400 words.
"""

    # ── COMMODITY — futures contract format ──
    elif asset_type == "commodity":
        prompt = f"""
You are a senior commodities market analyst at a top investment firm.
Generate a detailed, structured, professional commodity analysis report.

═══════════════════════════════════════
COMMODITY DATA
═══════════════════════════════════════
Commodity      : {stock_data.get('name')}
Symbol         : {stock_data.get('symbol')}

PRICE DATA:
Current Price  : {stock_data.get('current_price')} {stock_data.get('currency')}
52W High       : {stock_data.get('52w_high')}
52W Low        : {stock_data.get('52w_low')}
Change (1D)    : {stock_data.get('price_change_1d')}%
Change (1M)    : {stock_data.get('price_change_1m')}%
Change (1Y)    : {stock_data.get('price_change_1y')}%

TECHNICAL INDICATORS:
Trend          : {stock_data.get('trend')}
MA50           : {stock_data.get('ma50')}
MA200          : {stock_data.get('ma200')}
RSI            : {stock_data.get('rsi')} ({stock_data.get('rsi_signal')})
MACD           : {stock_data.get('macd')} ({stock_data.get('macd_signal')})
Support        : {stock_data.get('support')}
Resistance     : {stock_data.get('resistance')}

═══════════════════════════════════════
Generate a report with EXACTLY these sections:

1. EXECUTIVE SUMMARY
   Brief 2-3 line overview of this commodity's current state

2. PRICE PERFORMANCE
   Analyze 1D, 1M, 1Y performance and trend

3. TECHNICAL ANALYSIS
   Analyze RSI, MACD, MA50/200, Support/Resistance
   Short-term outlook

4. SUPPLY & DEMAND FACTORS
   Key factors: geopolitical events, production levels,
   seasonal demand, inventory data

5. RISK ASSESSMENT
   Key risks (minimum 3 points)
   Risk Score: X/10

6. TRADING VERDICT
   ▶ BUY / HOLD / SELL
   ▶ Confidence: X%
   ▶ Target Price (1 month): X
   ▶ Stop Loss: X
   ▶ Time Horizon: Short/Medium/Long term

DO NOT mention P/E, EPS, Revenue or any company fundamentals.
Use professional tone. Be specific with numbers. Max 400 words.
"""

    # ── CRYPTO — digital asset format ──
    elif asset_type == "crypto":
        prompt = f"""
You are a senior crypto market analyst at a top investment firm.
Generate a detailed, structured, professional cryptocurrency analysis report.

═══════════════════════════════════════
CRYPTO DATA
═══════════════════════════════════════
Asset          : {stock_data.get('name')}
Symbol         : {stock_data.get('symbol')}

PRICE DATA:
Current Price  : {stock_data.get('current_price')} {stock_data.get('currency')}
Market Cap     : {stock_data.get('market_cap')}
52W High       : {stock_data.get('52w_high')}
52W Low        : {stock_data.get('52w_low')}
Volume         : {stock_data.get('volume')}
Change (1D)    : {stock_data.get('price_change_1d')}%
Change (1M)    : {stock_data.get('price_change_1m')}%
Change (1Y)    : {stock_data.get('price_change_1y')}%

TECHNICAL INDICATORS:
Trend          : {stock_data.get('trend')}
MA50           : {stock_data.get('ma50')}
MA200          : {stock_data.get('ma200')}
RSI            : {stock_data.get('rsi')} ({stock_data.get('rsi_signal')})
MACD           : {stock_data.get('macd')} ({stock_data.get('macd_signal')})
Bollinger Up   : {stock_data.get('bb_upper')}
Bollinger Low  : {stock_data.get('bb_lower')}
Support        : {stock_data.get('support')}
Resistance     : {stock_data.get('resistance')}

═══════════════════════════════════════
Generate a report with EXACTLY these sections:

1. EXECUTIVE SUMMARY
   Brief 2-3 line overview of this crypto asset

2. PRICE PERFORMANCE
   Analyze 1D, 1M, 1Y performance and trend

3. TECHNICAL ANALYSIS
   Analyze RSI, MACD, MA50/200, Bollinger Bands
   Support/Resistance levels
   Short-term outlook

4. MARKET SENTIMENT & ADOPTION
   Network activity, adoption trends, regulatory environment,
   correlation with broader crypto market

5. RISK ASSESSMENT
   Key risks (minimum 3 points — include volatility, regulation)
   Risk Score: X/10

6. TRADING VERDICT
   ▶ BUY / HOLD / SELL
   ▶ Confidence: X%
   ▶ Target Price (1 month): X
   ▶ Stop Loss: X
   ▶ Time Horizon: Short/Medium/Long term

DO NOT mention P/E, EPS, Revenue or any company fundamentals.
Use professional tone. Be specific with numbers. Max 400 words.
"""

    # ── INDEX — benchmark format ──
    elif asset_type == "index":
        prompt = f"""
You are a senior market strategist at a top investment firm.
Generate a detailed, structured, professional market index analysis report.

═══════════════════════════════════════
INDEX DATA
═══════════════════════════════════════
Index          : {stock_data.get('name')}
Symbol         : {stock_data.get('symbol')}

PRICE DATA:
Current Level  : {stock_data.get('current_price')}
52W High       : {stock_data.get('52w_high')}
52W Low        : {stock_data.get('52w_low')}
Change (1D)    : {stock_data.get('price_change_1d')}%
Change (1M)    : {stock_data.get('price_change_1m')}%
Change (1Y)    : {stock_data.get('price_change_1y')}%

TECHNICAL INDICATORS:
Trend          : {stock_data.get('trend')}
MA50           : {stock_data.get('ma50')}
MA200          : {stock_data.get('ma200')}
RSI            : {stock_data.get('rsi')} ({stock_data.get('rsi_signal')})
MACD           : {stock_data.get('macd')} ({stock_data.get('macd_signal')})
Support        : {stock_data.get('support')}
Resistance     : {stock_data.get('resistance')}

═══════════════════════════════════════
Generate a report with EXACTLY these sections:

1. EXECUTIVE SUMMARY
   Brief 2-3 line overview of this market index's current state

2. PRICE PERFORMANCE
   Analyze 1D, 1M, 1Y performance and trend

3. TECHNICAL ANALYSIS
   Analyze RSI, MACD, MA50/200, Support/Resistance
   Short-term outlook

4. MARKET BREADTH & MACRO FACTORS
   Overall economic sentiment, key sector contributions,
   global market correlation

5. RISK ASSESSMENT
   Key risks (minimum 3 points)
   Risk Score: X/10

6. MARKET OUTLOOK
   ▶ BULLISH / NEUTRAL / BEARISH
   ▶ Confidence: X%
   ▶ Target Level (1 month): X
   ▶ Time Horizon: Short/Medium/Long term

DO NOT mention P/E, EPS, Revenue or any company fundamentals.
Use professional tone. Be specific with numbers. Max 400 words.
"""

    else:
        prompt = f"Analyze this financial asset data and give a short BUY/HOLD/SELL recommendation: {stock_data}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.7
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    symbol = input("Enter symbol (e.g. RELIANCE.NS / AAPL / GC=F / USDINR=X): ").strip()
    data   = get_stock_data(symbol)

    if data:
        report = generate_report(data)
        print("\n")
        print("═" * 55)
        print(f"   📊 ANALYSIS REPORT — {data.get('name')} ({data.get('asset_type', 'stock').upper()})")
        print("═" * 55)
        print(report)
        print("═" * 55)
        print(f"\n  Price    : {data.get('currency')} {data.get('current_price')}")
        print(f"  RSI      : {data.get('rsi')} — {data.get('rsi_signal')}")
        print(f"  MACD     : {data.get('macd_signal')}")
        print(f"  Trend    : {data.get('trend')}")
        print("═" * 55)
    else:
        print("Could not fetch data. Check the symbol and try again.")