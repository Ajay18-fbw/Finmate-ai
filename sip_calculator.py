def calculate_sip(monthly_investment, annual_return, years):
    r = annual_return / 12 / 100
    n = years * 12
    
    future_value = monthly_investment * (((1 + r) ** n - 1) / r) * (1 + r)
    total_invested = monthly_investment * n
    total_returns = future_value - total_invested
    
    return {
        "monthly_investment" : monthly_investment,
        "annual_return"      : annual_return,
        "years"              : years,
        "total_invested"     : round(total_invested),
        "future_value"       : round(future_value),
        "total_returns"      : round(total_returns),
        "wealth_gained"      : round((total_returns / total_invested) * 100, 2),
        "monthly_at_maturity": round(future_value / (years * 12))
    }

def calculate_goal_sip(target_amount, annual_return, years):
    r = annual_return / 12 / 100
    n = years * 12
    monthly = target_amount / ((((1 + r) ** n - 1) / r) * (1 + r))
    return round(monthly)

def get_sip_suggestions(monthly_investment, years):
    suggestions = []
    
    nifty    = calculate_sip(monthly_investment, 12, years)
    fd       = calculate_sip(monthly_investment, 7, years)
    flexi    = calculate_sip(monthly_investment, 14, years)

    suggestions.append(f"Nifty 50 Index Fund (12% avg): Rs.{nifty['future_value']:,} in {years} years")
    suggestions.append(f"Flexi Cap Fund (14% avg): Rs.{flexi['future_value']:,} in {years} years")
    suggestions.append(f"FD comparison (7%): Rs.{fd['future_value']:,} in {years} years")
    suggestions.append(f"SIP vs FD extra gain: Rs.{nifty['future_value'] - fd['future_value']:,}")

    return suggestions

if __name__ == "__main__":
    result = calculate_sip(5000, 12, 10)
    print("\n" + "="*45)
    print("   SIP CALCULATION RESULT")
    print("="*45)
    for k, v in result.items():
        print(f"  {k:25} : {v}")
    
    print("\n  Suggestions:")
    for s in get_sip_suggestions(5000, 10):
        print(f"  → {s}")
    
    print(f"\n  Goal Planning:")
    goal = calculate_goal_sip(1000000, 12, 10)
    print(f"  Rs.10L in 10 years → Rs.{goal}/month SIP needed")
    