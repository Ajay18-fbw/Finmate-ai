import yfinance as yf
import pandas as pd

def calculate_rsi(prices, period=14):
    delta  = prices.diff()
    gain   = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss   = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs     = gain / loss
    return round(100 - (100 / (1 + rs)).iloc[-1], 2)

def calculate_macd(prices):
    ema12  = prices.ewm(span=12).mean()
    ema26  = prices.ewm(span=26).mean()
    macd   = ema12 - ema26
    signal = macd.ewm(span=9).mean()
    return round(macd.iloc[-1], 2), round(signal.iloc[-1], 2)

def calculate_bollinger(prices, period=20):
    sma    = prices.rolling(window=period).mean()
    std    = prices.rolling(window=period).std()
    upper  = round((sma + 2 * std).iloc[-1], 2)
    lower  = round((sma - 2 * std).iloc[-1], 2)
    return upper, lower


def detect_asset_type(symbol):
    s = symbol.upper()
    if s.endswith("=X"):
        return "forex"
    if s.endswith("=F"):
        return "commodity"
    if s.endswith("-USD") or s.endswith("-INR"):
        return "crypto"
    if s.startswith("^"):
        return "index"
    return "stock"

def get_stock_data(symbol):
    print(f"\nFetching {symbol}...")
    asset_type = detect_asset_type(symbol)

    try:
        stock = yf.Ticker(symbol)
        fast  = stock.fast_info
        hist  = stock.history(period="1y")
        close = hist["Close"]

        if close.empty:
            return None

        ma50  = round(close.rolling(50).mean().iloc[-1], 2) if len(close) >= 50 else None
        ma200 = round(close.rolling(200).mean().iloc[-1], 2) if len(close) >= 200 else None
        rsi   = calculate_rsi(close)
        macd, signal = calculate_macd(close)
        bb_upper, bb_lower = calculate_bollinger(close)

        price_1d = round(((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2]) * 100, 2) if len(close) > 1 else 0
        price_1m = round(((close.iloc[-1] - close.iloc[-22]) / close.iloc[-22]) * 100, 2) if len(close) > 22 else 0
        price_1y = round(((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100, 2)

        support    = round(close.tail(30).min(), 2)
        resistance = round(close.tail(30).max(), 2)

        if rsi > 70:   rsi_signal = "Overbought ⚠️"
        elif rsi < 30: rsi_signal = "Oversold 🟢"
        else:          rsi_signal = "Neutral"

        macd_signal = "Bullish 🟢" if macd > signal else "Bearish 🔴"

        current = round(fast.last_price, 4 if asset_type == "forex" else 2)
        trend = "Sideways"
        if ma200:
            trend = "Uptrend 🟢" if current > ma200 else "Downtrend 🔴"

        data = {
            "symbol"         : symbol.upper(),
            "asset_type"     : asset_type,
            "current_price"  : current,
            "currency"       : fast.currency if hasattr(fast, "currency") else "USD",
            "price_change_1d": price_1d,
            "price_change_1m": price_1m,
            "price_change_1y": price_1y,
            "ma50"           : ma50,
            "ma200"          : ma200,
            "rsi"            : rsi,
            "rsi_signal"     : rsi_signal,
            "macd"           : macd,
            "macd_signal"    : macd_signal,
            "bb_upper"       : bb_upper,
            "bb_lower"       : bb_lower,
            "support"        : support,
            "resistance"     : resistance,
            "trend"          : trend,
            "52w_high"       : round(close.max(), 2),
            "52w_low"        : round(close.min(), 2),
            "volume"         : int(fast.last_volume) if hasattr(fast, "last_volume") else None,
        }

        if asset_type == "stock":
            info = stock.info
            data.update({
                "name"           : info.get("longName", symbol),
                "sector"         : info.get("sector", "N/A"),
                "industry"       : info.get("industry", "N/A"),
                "market_cap"     : fast.market_cap if hasattr(fast, "market_cap") else None,
                "pe_ratio"       : info.get("trailingPE", "N/A"),
                "eps"            : info.get("trailingEps", "N/A"),
                "revenue"        : info.get("totalRevenue", "N/A"),
                "profit_margin"  : info.get("profitMargins", "N/A"),
                "debt_to_equity" : info.get("debtToEquity", "N/A"),
                "roe"            : info.get("returnOnEquity", "N/A"),
                "dividend_yield" : info.get("dividendYield", "N/A"),
            })

        elif asset_type == "forex":
            pair = symbol.replace("=X", "")
            data.update({
                "name"      : f"{pair[:3]}/{pair[3:]} Exchange Rate",
                "sector"    : "Foreign Exchange",
                "industry"  : "Currency Pair",
                "market_cap": None,
            })

        elif asset_type == "commodity":
            names = {"GC=F": "Gold Futures", "SI=F": "Silver Futures", "CL=F": "Crude Oil Futures", "NG=F": "Natural Gas Futures"}
            data.update({
                "name"      : names.get(symbol.upper(), symbol),
                "sector"    : "Commodities",
                "industry"  : "Futures Contract",
                "market_cap": None,
            })

        elif asset_type == "crypto":
            data.update({
                "name"      : symbol.replace("-USD", "").replace("-INR", ""),
                "sector"    : "Cryptocurrency",
                "industry"  : "Digital Asset",
                "market_cap": fast.market_cap if hasattr(fast, "market_cap") else None,
            })

        elif asset_type == "index":
            data.update({
                "name"      : symbol.replace("^", ""),
                "sector"    : "Market Index",
                "industry"  : "Benchmark Index",
                "market_cap": None,
            })

        # Candlestick chart data — last 1 hour, 5-min OHLC candles
        try:
            intraday = stock.history(period="1d", interval="5m").tail(12)
            data["chart_1h"] = {
                "labels": [t.strftime("%H:%M") for t in intraday.index],
                "open"  : [round(p, 2) for p in intraday["Open"].tolist()],
                "high"  : [round(p, 2) for p in intraday["High"].tolist()],
                "low"   : [round(p, 2) for p in intraday["Low"].tolist()],
                "close" : [round(p, 2) for p in intraday["Close"].tolist()],
            }
        except:
            data["chart_1h"] = {"labels": [], "open": [], "high": [], "low": [], "close": []}

        print(f"✓ {data.get('name', symbol)} data fetched successfully!")
        return data

    except Exception as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    data = get_stock_data("RELIANCE.NS")
    if data:
        print("\n" + "="*45)
        for k, v in data.items():
            print(f"  {k:20} : {v}")
        print("="*45)