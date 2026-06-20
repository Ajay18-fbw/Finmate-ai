def calculate_old_regime(income, deductions):
    taxable = max(0, income - deductions)
    tax = 0

    slabs = [
        (250000, 0),
        (500000, 0.05),
        (1000000, 0.20),
        (float('inf'), 0.30)
    ]

    prev = 0
    for limit, rate in slabs:
        if taxable <= prev:
            break
        taxable_in_slab = min(taxable, limit) - prev
        tax += taxable_in_slab * rate
        prev = limit

    # Rebate 87A — income under 5L
    if income <= 500000:
        tax = max(0, tax - 12500)

    cess = tax * 0.04
    return round(tax + cess)

def calculate_new_regime(income):
    tax = 0

    slabs = [
        (300000, 0),
        (600000, 0.05),
        (900000, 0.10),
        (1200000, 0.15),
        (1500000, 0.20),
        (float('inf'), 0.30)
    ]

    prev = 0
    for limit, rate in slabs:
        if income <= prev:
            break
        taxable_in_slab = min(income, limit) - prev
        tax += taxable_in_slab * rate
        prev = limit

    # Rebate 87A — income under 7L
    if income <= 700000:
        tax = 0

    cess = tax * 0.04
    return round(tax + cess)

def get_tax_suggestions(income, investments_80c, insurance_80d):
    suggestions = []

    # 80C suggestion
    max_80c = 150000
    if investments_80c < max_80c:
        remaining = max_80c - investments_80c
        suggestions.append(f"80C mein abhi Rs.{remaining:,} aur invest kar sakte ho (PPF, ELSS, LIC)")

    # 80D suggestion
    max_80d = 25000
    if insurance_80d < max_80d:
        remaining = max_80d - insurance_80d
        suggestions.append(f"80D mein Rs.{remaining:,} aur bachao — health insurance lo")

    # NPS suggestion
    if income > 500000:
        suggestions.append("NPS mein Rs.50,000 invest karo — extra 80CCD(1B) benefit milega")

    # HRA suggestion
    suggestions.append("Agar rent pe rehte ho toh HRA exemption claim karo")

    return suggestions

def calculate_tax(annual_salary, investments_80c=0, insurance_80d=0, hra=0):
    # Standard deduction
    standard_deduction = 50000

    # Old regime deductions
    total_deductions = standard_deduction + min(investments_80c, 150000) + min(insurance_80d, 25000) + hra

    old_tax = calculate_old_regime(annual_salary, total_deductions)
    new_tax = calculate_new_regime(annual_salary)

    better = "New Regime" if new_tax < old_tax else "Old Regime"
    savings = abs(old_tax - new_tax)

    suggestions = get_tax_suggestions(annual_salary, investments_80c, insurance_80d)

    return {
        "annual_salary"   : annual_salary,
        "old_regime_tax"  : old_tax,
        "new_regime_tax"  : new_tax,
        "better_regime"   : better,
        "you_save"        : savings,
        "monthly_old"     : round(old_tax / 12),
        "monthly_new"     : round(new_tax / 12),
        "effective_rate"  : round((min(old_tax, new_tax) / annual_salary) * 100, 2),
        "deductions_used" : round(total_deductions),
        "suggestions"     : suggestions
    }

if __name__ == "__main__":
    result = calculate_tax(
        annual_salary    = 800000,
        investments_80c  = 100000,
        insurance_80d    = 15000
    )
    print("\n" + "="*45)
    print("   TAX CALCULATION RESULT")
    print("="*45)
    for k, v in result.items():
        if k != "suggestions":
            print(f"  {k:20} : {v}")
    print("\n  Suggestions:")
    for s in result["suggestions"]:
        print(f"  → {s}")