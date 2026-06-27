import datetime
import pytz

def get_market_status(asset_type: str, symbol: str) -> dict:
    """
    Returns market status and last trading session info.
    Markets:
    - NSE/BSE: Mon-Fri 9:15 AM - 3:30 PM IST
    - NYSE/NASDAQ: Mon-Fri 9:30 AM - 4:00 PM ET
    - Crypto: 24/7
    - Commodities/Forex: Near 24/7 (MCX, COMEX)
    """
    now_utc = datetime.datetime.now(pytz.utc)
    now_ist = now_utc.astimezone(pytz.timezone("Asia/Kolkata"))
    now_et  = now_utc.astimezone(pytz.timezone("America/New_York"))

    weekday = now_ist.weekday()  # 0=Mon, 6=Sun
    
    # Crypto / Forex — always open
    if asset_type in ["crypto", "forex"]:
        return {
            "is_open"     : True,
            "market"      : "Global",
            "note"        : "24/7 market",
            "data_note"   : "Live data",
        }

    # Indian market (NSE/BSE)
    if symbol.endswith(".NS") or symbol.endswith(".BO") or symbol in ["^NSEI", "^BSESN"]:
        market_open  = now_ist.replace(hour=9,  minute=15, second=0)
        market_close = now_ist.replace(hour=15, minute=30, second=0)
        is_weekday   = weekday < 5
        is_open      = is_weekday and market_open <= now_ist <= market_close

        if not is_weekday:
            day_name = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][weekday]
            note = f"NSE/BSE closed — {day_name}. Showing last trading session data."
        elif now_ist < market_open:
            note = f"NSE/BSE opens at 9:15 AM IST. Showing previous close data."
        elif now_ist > market_close:
            note = f"NSE/BSE closed at 3:30 PM IST. Showing today's closing data."
        else:
            note = "NSE/BSE is open (9:15 AM - 3:30 PM IST)"

        return {
            "is_open"   : is_open,
            "market"    : "NSE/BSE",
            "note"      : note,
            "data_note" : "Live" if is_open else "Last session",
        }

    # US Market (NYSE/NASDAQ)
    if not (symbol.endswith(".NS") or symbol.endswith(".BO") or "-USD" in symbol or "=F" in symbol or "=X" in symbol):
        market_open  = now_et.replace(hour=9,  minute=30, second=0)
        market_close = now_et.replace(hour=16, minute=0,  second=0)
        is_weekday   = now_et.weekday() < 5
        is_open      = is_weekday and market_open <= now_et <= market_close

        if not is_weekday:
            day_name = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][now_et.weekday()]
            note = f"NYSE/NASDAQ closed — {day_name}. Showing last trading session data."
        elif now_et < market_open:
            note = "NYSE/NASDAQ opens at 9:30 AM ET. Showing previous close data."
        elif now_et > market_close:
            note = "NYSE/NASDAQ closed at 4:00 PM ET. Showing today's closing data."
        else:
            note = "NYSE/NASDAQ is open (9:30 AM - 4:00 PM ET)"

        return {
            "is_open"   : is_open,
            "market"    : "NYSE/NASDAQ",
            "note"      : note,
            "data_note" : "Live" if is_open else "Last session",
        }

    # Commodities
    return {
        "is_open"   : True,
        "market"    : "Commodities",
        "note"      : "Commodities trade near 24/7",
        "data_note" : "Latest available data",
    }