from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN

def calculate_dcf():
    ebit = 500_000_000         # INR 50 Cr
    tax_rate = 0.25
    dna = 50_000_000           # INR 5 Cr
    capex = 60_000_000         # INR 6 Cr
    nwc_change = 15_000_000    # INR 1.5 Cr

    # FCFF = EBIT * (1 - t) + D&A - CapEx - Delta NWC
    fcff_base = ebit * (1 - tax_rate) + dna - capex - nwc_change # 350,000,000 INR

    # WACC Calculation using PAYFIN Beta (1.35)
    beta = STOCK_UNIVERSE["PAYFIN"]["beta"]
    cost_of_equity = RISK_FREE_RATE + beta * (MARKET_RETURN - RISK_FREE_RATE) # 15.1%
    cost_of_debt_after_tax = 0.08 * (1 - tax_rate) # 6.0%
    weight_equity = 0.8
    weight_debt = 0.2
    
    base_wacc = weight_equity * cost_of_equity + weight_debt * cost_of_debt_after_tax # 13.28%
    base_growth = 0.04 # 4.0% terminal growth (Base WACC - growth = 9.28% >= 3pp constraint)

    growth_rates_5yr = [0.15, 0.12, 0.10, 0.08, 0.06]

    def compute_enterprise_value(wacc, g_term):
        cf = fcff_base
        pv_cfs = 0
        for i, g in enumerate(growth_rates_5yr, start=1):
            cf = cf * (1 + g)
            pv_cfs += cf / ((1 + wacc) ** i)
        
        terminal_value = (cf * (1 + g_term)) / (wacc - g_term)
        pv_terminal_value = terminal_value / ((1 + wacc) ** 5)
        
        return pv_cfs + pv_terminal_value

    base_ev = compute_enterprise_value(base_wacc, base_growth)

    wacc_range = [base_wacc - 0.01, base_wacc, base_wacc + 0.01]
    growth_range = [base_growth - 0.01, base_growth, base_growth + 0.01]

    sensitivity_matrix = {}
    for w in wacc_range:
        sensitivity_matrix[f"{w:.2%}"] = {}
        for g in growth_range:
            sensitivity_matrix[f"{w:.2%}"][f"{g:.2%}"] = compute_enterprise_value(w, g)

    # EV/EBITDA Cross-Check
    ebitda = ebit + dna # 550,000,000 INR
    ev_ebitda_multiple = 8.5
    multiple_ev = ebitda * ev_ebitda_multiple

    return {
        "fcff_base": fcff_base,
        "base_wacc": base_wacc,
        "base_growth": base_growth,
        "base_ev_inr": base_ev,
        "sensitivity_matrix": sensitivity_matrix,
        "ebitda": ebitda,
        "multiple_ev_inr": multiple_ev
    }

if __name__ == "__main__":
    res = calculate_dcf()
    print("\n--- PART D: DCF VALUATION CALCULATOR ---")
    print(f"Base FCFF: INR {res['fcff_base']:,}")
    print(f"Base WACC: {res['base_wacc']:.2%}")
    print(f"Base Terminal Growth: {res['base_growth']:.2%}")
    print(f"DCF Implied Enterprise Value: INR {res['base_ev_inr']:,.2f}")
    print(f"EV/EBITDA Cross-Check Valuation: INR {res['multiple_ev_inr']:,.2f}")
    print("\n3x3 Sensitivity Table (Enterprise Value in INR):")
    for wacc, row in res['sensitivity_matrix'].items():
        print(f"WACC {wacc}: " + " | ".join([f"g={g}: INR {val:,.0f}" for g, val in row.items()]))