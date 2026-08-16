import os
from stock_universe import STOCK_UNIVERSE, RISK_FREE_RATE, MARKET_RETURN

def run_debate(ticker: str = "PAYTECH") -> dict:
    stock = STOCK_UNIVERSE[ticker]
    beta = stock["beta"]
    capm_return = RISK_FREE_RATE + beta * (MARKET_RETURN - RISK_FREE_RATE)
    std_dev = stock["std_dev"]

    mock_llm = os.getenv("MOCK_LLM", "1")

    if mock_llm == "1" or not mock_llm:
        bull_arg = f"PAYTECH offers strong growth potential with a CAPM expected return of {capm_return:.1%} against a beta of {beta:.2f}, presenting attractive risk-adjusted upside."
        bear_arg = f"PAYTECH carries high risk given its high volatility of {std_dev:.1%} and elevated beta of {beta:.2f}, making it vulnerable to market pullbacks."
        synthesizer = f"While PAYTECH delivers an impressive expected return of {capm_return:.1%}, its elevated standard deviation of {std_dev:.1%} requires careful risk management. An allocation is suitable primarily for high-risk portfolios."

    return {
        "ticker": ticker,
        "bull_agent": bull_arg,
        "bear_agent": bear_arg,
        "synthesizer_agent": synthesizer
    }

if __name__ == "__main__":
    print("\n--- PART C: MULTI-AGENT DEBATE DEMO ---")
    res = run_debate("PAYTECH")
    print(f"Ticker: {res['ticker']}")
    print(f"Bull Agent: {res['bull_agent']}")
    print(f"Bear Agent: {res['bear_agent']}")
    print(f"Synthesizer: {res['synthesizer_agent']}")