from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ─── Trading Style Prompts ────────────────────────────────────────
STYLE_CONTEXT = {
    "intraday": {
        "label"      : "Intraday ⚡",
        "timeframe"  : "15min / 1hr candles",
        "hold_period": "Same day — exit before market close",
        "focus"      : """
INTRADAY FOCUS:
- Entry: exact price level for today's trade
- Exit: same day target (don't hold overnight)
- Stop Loss: very tight — max 0.5% to 1% below entry
- Key levels: today's high/low, pre-market gaps, VWAP
- Volume: high volume confirmation is must
- Avoid: low liquidity stocks, news-heavy days without direction
- Position size: max 5-10% of capital per trade (leverage risk)
""",
        "verdict_label": "TRADE TODAY",
    },
    "swing": {
        "label"      : "Swing 🔄",
        "timeframe"  : "Daily / 4hr candles",
        "hold_period": "2 to 10 days",
        "focus"      : """
SWING TRADING FOCUS:
- Entry: near support level or breakout confirmation
- Hold: 2-10 days, can hold overnight
- Stop Loss: 2-4% below entry (below key support)
- Target: next resistance level (risk:reward min 1:2)
- RSI: look for 40-60 range with bullish divergence
- MACD crossover: strong signal for swing entries
- Bollinger Bands: entry near lower band, exit near upper
- Position size: 10-20% of capital per swing trade
""",
        "verdict_label": "SWING TRADE",
    },
    "positional": {
        "label"      : "Positional 📅",
        "timeframe"  : "Weekly / Daily candles",
        "hold_period": "Weeks to months (1-6 months)",
        "focus"      : """
POSITIONAL TRADING FOCUS:
- Entry: on pullbacks in strong uptrend (MA50 bounce)
- Hold: weeks to months — ride the larger trend
- Stop Loss: 5-8% below entry (below MA50 or key support)
- Target: based on trend continuation (risk:reward 1:3+)
- MA50/MA200: golden cross = strong buy signal
- Sector rotation: is the sector in favor?
- Fundamentals matter: revenue growth, margin expansion
- Position size: 15-25% of portfolio per position
""",
        "verdict_label": "POSITIONAL TRADE",
    },
    "longterm": {
        "label"      : "Long-term 🌱",
        "timeframe"  : "Monthly / Weekly candles",
        "hold_period": "1 year or more",
        "focus"      : """
LONG-TERM INVESTMENT FOCUS:
- Fundamentals are primary: P/E, ROE, Revenue growth, Debt
- Business moat: competitive advantage, market leadership
- Management quality: promoter holding, corporate governance
- Valuation: is stock trading below intrinsic value?
- Dividend history: consistent payer = stable business
- Technicals secondary: use dips to accumulate
- SIP approach: buy on every 10-15% correction
- Position size: up to 30-40% of portfolio for high conviction
- Ignore short-term volatility — focus on 3-5 year horizon
""",
        "verdict_label": "INVESTMENT",
    },
}


def generate_report(stock_data: dict, trading_style: str = "swing") -> str:
    print(f"\nGenerating AI Report — Style: {trading_style}...")

    asset_type = stock_data.get("asset_type", "stock")
    style      = STYLE_CONTEXT.get(trading_style, STYLE_CONTEXT["swing"])

    # ── Common data block ──────────────────────────────────────────
    price_block = f"""
PRICE DATA:
Current Price  : {stock_data.get('current_price')} {stock_data.get('currency')}
Change (1D)    : {stock_data.get('price_change_1d')}%
Change (1M)    : {stock_data.get('price_change_1m')}%
Change (1Y)    : {stock_data.get('price_change_1y')}%
52W High       : {stock_data.get('52w_high')}
52W Low        : {stock_data.get('52w_low')}
Volume         : {stock_data.get('volume')}
Market Cap     : {stock_data.get('market_cap')}

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
"""

    fund_block = f"""
FUNDAMENTAL DATA:
P/E Ratio      : {stock_data.get('pe_ratio')}
EPS            : {stock_data.get('eps')}
Revenue        : {stock_data.get('revenue')}
Profit Margin  : {stock_data.get('profit_margin')}
Debt/Equity    : {stock_data.get('debt_to_equity')}
ROE            : {stock_data.get('roe')}
Dividend Yield : {stock_data.get('dividend_yield')}
"""

    style_block = f"""
TRADING STYLE SELECTED: {style['label']}
Recommended Timeframe : {style['timeframe']}
Hold Period           : {style['hold_period']}
{style['focus']}
"""

    # ── Asset-specific prompts ─────────────────────────────────────
    if asset_type == "stock":
        prompt = f"""You are a senior professional analyst. Generate a {style['label']} optimized stock analysis report.

ASSET: {stock_data.get('name')} ({stock_data.get('symbol')})
Sector: {stock_data.get('sector')} | Industry: {stock_data.get('industry')}
{price_block}
{fund_block if trading_style in ['positional', 'longterm'] else ''}
{style_block}

Generate report with EXACTLY these sections:

1. EXECUTIVE SUMMARY
   2-3 lines — is this a good {style['label']} opportunity right now?

2. TECHNICAL SETUP
   Analyze RSI, MACD, MA50/200, Support/Resistance for {style['label']} context
   {"Focus on today's key levels, VWAP, intraday momentum" if trading_style == 'intraday' else ''}
   {"Focus on swing entry zone, bollinger bands, RSI divergence" if trading_style == 'swing' else ''}
   {"Focus on MA50/200 crossover, weekly trend, sector strength" if trading_style == 'positional' else ''}
   {"Focus on business quality, long-term trend, value vs price" if trading_style == 'longterm' else ''}

3. {"FUNDAMENTALS" if trading_style in ['positional', 'longterm'] else "PRICE ACTION"}
   {"Analyze P/E, ROE, Revenue growth, Debt — is business quality strong?" if trading_style in ['positional', 'longterm'] else "Analyze recent price action, volume, momentum patterns"}

4. RISK ASSESSMENT
   Key risks for {style['label']} trader (minimum 3 points)
   Risk Score: X/10

5. {style['verdict_label']} VERDICT
   ▶ BUY / HOLD / SELL / AVOID
   ▶ Confidence: X%
   ▶ Entry Price: ₹X (specific level)
   ▶ Stop Loss: ₹X ({style['hold_period']})
   ▶ Target 1: ₹X | Target 2: ₹X
   ▶ Position Size: X% of capital
   ▶ Hold Period: {style['hold_period']}

Be specific with numbers. Max 450 words. Professional tone.
"""

    elif asset_type == "crypto":
        prompt = f"""You are a senior crypto analyst. Generate a {style['label']} optimized crypto report.

ASSET: {stock_data.get('name')} ({stock_data.get('symbol')})
{price_block}
{style_block}

Generate report with EXACTLY these sections:

1. EXECUTIVE SUMMARY
   Is this a good {style['label']} crypto opportunity?

2. TECHNICAL SETUP
   RSI, MACD, MA50/200, Support/Resistance — for {style['label']} context
   {"Intraday: focus on 15min momentum, volume spikes, key hourly levels" if trading_style == 'intraday' else ''}
   {"Swing: daily chart setup, bollinger bands, RSI divergence" if trading_style == 'swing' else ''}
   {"Positional/Long-term: weekly trend, market cycle position (bull/bear)" if trading_style in ['positional', 'longterm'] else ''}

3. MARKET SENTIMENT
   Crypto market sentiment, Bitcoin correlation, regulatory environment

4. RISK ASSESSMENT
   Crypto-specific risks — volatility, regulation, liquidity (min 3 points)
   Risk Score: X/10

5. {style['verdict_label']} VERDICT
   ▶ BUY / HOLD / SELL / AVOID
   ▶ Confidence: X%
   ▶ Entry: $X | Stop Loss: $X | Target 1: $X | Target 2: $X
   ▶ Position Size: X% of crypto allocation
   ▶ Hold: {style['hold_period']}

Max 400 words. No company fundamentals (P/E etc.).
"""

    elif asset_type == "forex":
        prompt = f"""You are a senior forex analyst. Generate a {style['label']} currency pair report.

PAIR: {stock_data.get('name')} ({stock_data.get('symbol')})
{price_block}
{style_block}

Sections:
1. EXECUTIVE SUMMARY
2. TECHNICAL SETUP — for {style['label']} ({"intraday key levels, pip targets" if trading_style=='intraday' else "swing levels, weekly pivots"})
3. MACRO FACTORS — interest rates, inflation, central bank policy
4. RISK ASSESSMENT (3 points) — Risk Score: X/10
5. {style['verdict_label']} VERDICT
   ▶ BUY/SELL | Entry: X | SL: X | TP1: X | TP2: X | Hold: {style['hold_period']}

Max 350 words.
"""

    elif asset_type == "commodity":
        prompt = f"""You are a senior commodities analyst. Generate a {style['label']} commodity report.

COMMODITY: {stock_data.get('name')} ({stock_data.get('symbol')})
{price_block}
{style_block}

Sections:
1. EXECUTIVE SUMMARY
2. TECHNICAL SETUP — {style['label']} levels, key support/resistance
3. SUPPLY & DEMAND — geopolitical factors, inventory, seasonal demand
4. RISK ASSESSMENT (3 points) — Risk Score: X/10
5. {style['verdict_label']} VERDICT
   ▶ BUY/SELL/HOLD | Entry: X | SL: X | Target: X | Hold: {style['hold_period']}

Max 350 words.
"""

    elif asset_type == "index":
        prompt = f"""You are a senior market strategist. Generate a {style['label']} index analysis.

INDEX: {stock_data.get('name')} ({stock_data.get('symbol')})
{price_block}
{style_block}

Sections:
1. EXECUTIVE SUMMARY
2. TECHNICAL SETUP — {style['label']} context, key levels
3. MARKET BREADTH & MACRO — economic sentiment, global correlation
4. RISK ASSESSMENT (3 points) — Risk Score: X/10
5. MARKET OUTLOOK
   ▶ BULLISH/NEUTRAL/BEARISH | Confidence: X%
   ▶ {"Today's range: X-X" if trading_style=='intraday' else f"Target (for {style['hold_period']}): X"} | SL: X

Max 350 words.
"""

    else:
        prompt = f"Analyze this {trading_style} trading opportunity and give BUY/HOLD/SELL with entry, stop loss, target: {stock_data}"

    response = client.chat.completions.create(
        model      = "llama-3.3-70b-versatile",
        messages   = [{"role": "user", "content": prompt}],
        max_tokens = 1200,
        temperature= 0.65,
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    from stock_data import get_stock_data
    symbol = input("Symbol: ").strip()
    style  = input("Trading style (intraday/swing/positional/longterm): ").strip() or "swing"
    data   = get_stock_data(symbol)
    if data:
        report = generate_report(data, trading_style=style)
        print("\n" + "═"*55)
        print(f"  📊 {style.upper()} REPORT — {data.get('name')}")
        print("═"*55)
        print(report)
        print("═"*55)
    else:
        print("Could not fetch data.")