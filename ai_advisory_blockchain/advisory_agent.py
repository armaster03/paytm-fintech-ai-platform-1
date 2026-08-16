import os
import math
from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN
from investor_profiles import INVESTOR_PROFILES

def get_stock_data(ticker: str) -> dict:
    return STOCK_UNIVERSE[ticker]

def run_advisory_agent(investor_profile: dict) -> dict:
    inv_id = investor_profile["investor_id"]
    risk_tol = investor_profile["risk_tolerance"]

    # 1. THINK: Select prescribed tickers based on risk tolerance
    if risk_tol == "Conservative":
        tickers = ["PAYBOND", "PAYGOLD", "PAYRETAIL"]
    elif risk_tol == "Moderate":
        tickers = ["PAYRETAIL", "PAYINFRA", "PAYGOLD"]
    elif risk_tol == "Aggressive":
        tickers = ["PAYTECH", "PAYFIN", "PAYINFRA"]
    else:
        raise ValueError(f"Unknown risk tolerance: {risk_tol}")

    weights = [1/3, 1/3, 1/3]

    # 2. ACT: Call tool to fetch stock metrics
    stock_data = [get_stock_data(t) for t in tickers]

    # 3. OBSERVE & DECIDE: Compute CAPM Expected Return and Portfolio Volatility
    # CAPM E(R) = R_f + beta * (R_m - R_f)
    capm_returns = [RISK_FREE_RATE + data["beta"] * (MARKET_RETURN - RISK_FREE_RATE) for data in stock_data]
    portfolio_return = sum(w * r for w, r in zip(weights, capm_returns))

    std_devs = [data["std_dev"] for data in stock_data]
    rho = 0.3

    # Var(R_p) = sum(w_i^2 * sigma_i^2) + 2 * sum_{i<j}(w_i * w_j * rho * sigma_i * sigma_j)
    variance = 0.0
    for i in range(3):
        variance += (weights[i] ** 2) * (std_devs[i] ** 2)
    
    for i in range(3):
        for j in range(i + 1, 3):
            variance += 2 * weights[i] * weights[j] * rho * std_devs[i] * std_devs[j]

    portfolio_std_dev = math.sqrt(variance)

    # Human-in-the-Loop Escalation
    is_escalated = portfolio_std_dev > 0.20
    status = "ESCALATED_TO_HUMAN_ADVISOR" if is_escalated else "FINALIZED"

    # Narrative generation (Gated by MOCK_LLM)
    mock_llm = os.getenv("MOCK_LLM", "1")
    if mock_llm == "1" or not mock_llm:
        narrative = f"For {risk_tol} investor {inv_id}, we recommend an allocation across {', '.join(tickers)} with an expected portfolio return of {portfolio_return:.1%} and volatility of {portfolio_std_dev:.1%}."
    else:
        narrative = f"For {risk_tol} investor {inv_id}, we recommend an allocation across {', '.join(tickers)} with an expected portfolio return of {portfolio_return:.1%} and volatility of {portfolio_std_dev:.1%}."

    return {
        "investor_id": inv_id,
        "risk_tolerance": risk_tol,
        "allocated_tickers": tickers,
        "portfolio_expected_return": portfolio_return,
        "portfolio_std_dev": portfolio_std_dev,
        "status": status,
        "recommendation_narrative": narrative
    }

if __name__ == "__main__":
    print("--- PART A: PORTFOLIO ADVISORY AGENT RESULTS ---")
    for profile in INVESTOR_PROFILES:
        res = run_advisory_agent(profile)
        print(f"ID: {res['investor_id']} | Risk: {res['risk_tolerance']:12} | Exp. Return: {res['portfolio_expected_return']:.2%} | Volatility: {res['portfolio_std_dev']:.2%} | Status: {res['status']}")