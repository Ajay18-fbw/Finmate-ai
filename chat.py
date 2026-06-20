from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MEMORY_FILE = "user_memory.json"

def load_profile():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "name"         : "",
        "salary"       : 0,
        "expenses"     : 0,
        "savings"      : 0,
        "goals"        : [],
        "investments"  : [],
        "conversation" : []
    }

def save_profile(profile):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)

def get_advice(user_input, profile):
    system_prompt = f"""You are FinMate AI — India's #1 personal finance advisor.
You are a certified financial expert with deep knowledge of Indian finance.

USER PROFILE:
Name       : {profile['name'] or 'User'}
Salary     : Rs.{profile['salary']}/month
Expenses   : Rs.{profile['expenses']}/month
Savings    : Rs.{profile['savings']}/month
Goals      : {profile['goals']}
Investments: {profile['investments']}

YOUR EXPERTISE:

1. MUTUAL FUNDS & SIP:
   - Large Cap, Mid Cap, Small Cap, Flexi Cap funds
   - Index Funds (Nifty 50, Sensex)
   - ELSS (tax saving funds)
   - SIP calculation: P x [(1+r)^n - 1] / r
   - Best funds: Mirae Asset, Axis, HDFC, SBI, Parag Parikh

2. STOCK MARKET:
   - NSE, BSE, Nifty 50, Sensex
   - Technical analysis basics (RSI, MACD, MA)
   - Fundamental analysis (P/E, EPS, ROE)
   - F&O, IPO, Bonus shares

3. TAX PLANNING:
   - Section 80C (Rs.1.5L limit): ELSS, PPF, NPS, LIC, FD
   - Section 80D: Health insurance (Rs.25,000 to Rs.1L)
   - HRA exemption calculation
   - New vs Old tax regime comparison
   - Capital Gains tax (STCG 15%, LTCG 10% above Rs.1L)

4. FIXED INCOME:
   - PPF: 7.1% p.a., 15 year lock-in, tax free
   - NPS: Market-linked, 80C + 80CCD benefits
   - FD rates: SBI 6.5%, HDFC 7%, Post Office 7.5%
   - RD, NSC, Senior Citizen Savings Scheme
   - Sovereign Gold Bonds (2.5% + gold appreciation)

5. INSURANCE:
   - Term Insurance: 10-15x annual income
   - Health Insurance: Min Rs.5L cover
   - ULIP vs Pure Term difference
   - LIC vs Private insurers

6. BUDGETING:
   - 50/30/20 rule: 50% needs, 30% wants, 20% savings
   - Emergency fund: 6 months expenses
   - Zero-based budgeting
   - Expense tracking methods

7. GOAL-BASED PLANNING:
   - Short term (0-3 years): FD, RD, Liquid funds
   - Medium term (3-7 years): Balanced funds, NPS
   - Long term (7+ years): Equity, ELSS, PPF
   - Retirement planning: 25x annual expense rule
   - Child education planning

8. ADVANCED TOPICS:
   - Asset allocation based on age (100 minus age = equity %)
   - Rebalancing portfolio
   - Rupee Cost Averaging
   - Power of compounding
   - Inflation impact on savings

RESPONSE STYLE:
- Always use Rs. amounts with specific numbers
- Give step by step action plan
- Compare options with pros and cons
- Use simple Hindi/Hinglish mix
- Max 200 words per response
- Always end with "Next Step:" action

PERSONALIZATION RULES:
- Savings Rs.0-5000: Focus on emergency fund + basic SIP
- Savings Rs.5000-15000: SIP + tax saving + insurance
- Savings Rs.15000+: Diversified portfolio + advanced planning

IMPORTANT:
- Always calculate based on user's ACTUAL salary and savings
- Never give vague advice, always specific amounts
- For complex decisions say: "Ek baar SEBI registered advisor se milna"
"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(profile["conversation"][-10:])
    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=400,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

def setup_profile(profile):
    print("\n" + "="*45)
    print("   Pehle thoda tumhare baare mein jaante hain!")
    print("="*45)

    if not profile["name"]:
        profile["name"] = input("\nTumhara naam kya hai? -> ").strip()

    if not profile["salary"]:
        try:
            profile["salary"] = int(input(f"Monthly salary kitni hai {profile['name']}? Rs. -> "))
        except:
            profile["salary"] = 0

    if not profile["expenses"]:
        try:
            profile["expenses"] = int(input("Monthly expenses kitne hain? Rs. -> "))
        except:
            profile["expenses"] = 0

    profile["savings"] = max(0, profile["salary"] - profile["expenses"])
    print(f"\n   Monthly savings: Rs.{profile['savings']}")
    print(f"   Savings rate: {(profile['savings']/profile['salary']*100):.1f}%" if profile['salary'] > 0 else "")

    save_profile(profile)
    return profile

def main():
    print("=" * 45)
    print("   FinMate AI — Your Personal Finance Dost!")
    print("=" * 45)

    profile = load_profile()

    if profile["name"]:
        print(f"\n   Wapas aa gaye {profile['name']}!")
        print(f"   Salary  : Rs.{profile['salary']}")
        print(f"   Savings : Rs.{profile['savings']}")
        print(f"   Goals   : {profile['goals'] or 'None set yet'}")
    else:
        profile = setup_profile(profile)

    print("\n   Commands:")
    print("   'exit'    = quit & save")
    print("   'reset'   = clear profile")
    print("   'profile' = update salary/expenses")
    print("   'goals'   = add a new goal")
    print("-" * 45 + "\n")

    while True:
        user_input = input(f"{profile['name']}: ").strip()

        if not user_input:
            continue

        if user_input.lower() == "exit":
            save_profile(profile)
            print("\nFinMate: Alvida! Apna paisa sambhalo!")
            break

        if user_input.lower() == "reset":
            profile = {
                "name": "", "salary": 0, "expenses": 0,
                "savings": 0, "goals": [], "investments": [],
                "conversation": []
            }
            save_profile(profile)
            print("Profile reset!\n")
            profile = setup_profile(profile)
            continue

        if user_input.lower() == "profile":
            try:
                profile["salary"]   = int(input("New salary? Rs. -> "))
                profile["expenses"] = int(input("New expenses? Rs. -> "))
                profile["savings"]  = max(0, profile["salary"] - profile["expenses"])
                save_profile(profile)
                print(f"Updated! New savings: Rs.{profile['savings']}\n")
            except:
                print("Invalid input!\n")
            continue

        if user_input.lower() == "goals":
            goal = input("Kya goal add karna hai? (e.g. Car 2026, House 2030) -> ").strip()
            if goal:
                profile["goals"].append(goal)
                save_profile(profile)
                print(f"Goal added: {goal}\n")
            continue

        reply = get_advice(user_input, profile)

        profile["conversation"].append({"role": "user",      "content": user_input})
        profile["conversation"].append({"role": "assistant", "content": reply})
        save_profile(profile)

        print(f"\nFinMate: {reply}\n")

if __name__ == "__main__":
    main()