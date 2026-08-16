Paytm Fintech AI Platform
Project Overview
This project combines three core themes: portfolio advisory, structured risk extraction, and fintech/crypto risk assessment. It demonstrates an agentic workflow for investment recommendations, extracts risk signals from disclosure text, evaluates a pricing model for credit risk, and performs a DCF-based valuation and market-risk analysis for a digital finance use case.

Part A — Portfolio Advisory Agent
This module follows a think-act-observe pattern to recommend portfolios based on investor risk tolerance. The allocation logic is deterministic and follows the required mapping:

Conservative: PAYBOND, PAYGOLD, PAYRETAIL
Moderate: PAYRETAIL, PAYINFRA, PAYGOLD
Aggressive: PAYTECH, PAYFIN, PAYINFRA
Each allocation is equal-weighted (1/3 each), and the portfolio expected return is computed using CAPM with beta-based risk:

Expected return = Risk-free rate + beta × (Market return − Risk-free rate)
Portfolio volatility is computed using variance and pairwise covariance with rho = 0.3
Investor Results
Investor	Risk Profile	Expected Return	Volatility	Status
INV01	Conservative	7.90%	8.44%	FINALIZED
INV02	Moderate	10.90%	12.57%	FINALIZED
INV03	Aggressive	14.80%	20.58%	ESCALATED_TO_HUMAN_ADVISOR
INV04	Moderate	10.90%	12.57%	FINALIZED
INV05	Aggressive	14.80%	20.58%	ESCALATED_TO_HUMAN_ADVISOR
This confirms the expected escalation behavior: low- and medium-risk portfolios remain within safe volatility limits, while aggressive portfolios cross the 20% threshold and require human review.

The narrative recommendation is generated in MOCK_LLM mode using a deterministic template.

Part B — Structured Disclosure Extraction
This module reads disclosure snippets and extracts structured risk signals with no external API dependency. It flags legal, regulatory, and customer-concentration issues, identifies hedging language, and classifies the sentiment as confident, cautious, or neutral.

Extracted Signals
Document	Risk Flags	Hedging	Sentiment
doc_01	None	Yes	Cautious
doc_02	Litigation	No	Neutral
doc_03	Customer concentration	No	Neutral
doc_04	None	Yes	Cautious
doc_05	None	No	Confident
doc_06	Regulatory	No	Neutral
This demonstrates how structured disclosures can be converted into interpretable risk metadata for downstream investment monitoring.

Part C — Multi-Agent Debate Demo
A three-agent debate is implemented for a chosen stock in the universe, using a bull case, bear case, and synthesizer summary. The chosen stock is PAYTECH, which has:

Beta: 1.55
Standard deviation: 34%
CAPM expected return: approximately 16.3%
The bull agent highlights upside and risk-adjusted attractiveness, the bear agent focuses on volatility and downside risk, and the synthesizer combines both arguments into a balanced conclusion. This approach mirrors a structured investment debate and helps surface both sides of the thesis.

Part D — DCF Valuation Calculator
The DCF model estimates enterprise value using unlevered free cash flow to the firm:

FCFF = EBIT × (1 − tax rate) + D&A − CapEx − ΔNWC
The base scenario assumes:

EBIT = INR 500M
Tax rate = 25%
D&A = INR 50M
CapEx = INR 60M
ΔNWC = INR 15M
Base FCFF = INR 350M
The model computes WACC using CAPM-based cost of equity and an illustrative debt blend:

Cost of equity ≈ 15.1%
After-tax debt cost ≈ 6.0%
WACC ≈ 13.28%
A 5-year growth ramp is projected and discounted to present value, followed by a terminal value calculation. A 3×3 sensitivity table varies WACC and terminal growth by ±1 percentage point, and the model checks that WACC remains above terminal growth in all scenarios. The DCF valuation is also cross-checked against an EV/EBITDA multiple to confirm the order of magnitude of value.

Part E — Blockchain & Crypto Risk Appendix
The blockchain appendix evaluates how a retail-facing crypto watchlist should be designed responsibly. It emphasizes the need for strong safeguards around stablecoin peg quality and governance risk in DeFi protocols before exposing any digital assets to consumers.

Key recommendations
Fiat-backed stablecoins with 1:1 reserves are far safer than algorithmic stablecoins, which are more exposed to de-pegging or death-spiral dynamics.
DeFi governance risk should be reviewed using token concentration, admin-key control, smart contract audit status, and protocol-level vulnerabilities.
For a retail advisory product, crypto should not be treated as a core asset class because it lacks intrinsic cash flows, dividend yield, and stable valuation fundamentals.
Recommended stance: zero allocation as a baseline, with a strict limit of 1–2% only for highly aggressive, speculative investors.
T.A.N.G. Fraud Framework
Two social-engineering vectors are highlighted as most relevant to a UPI/wallet + lending + wealth platform:

Greed vector: fake investment or yield promises
Authority vector: fake regulatory or tax notices
For each, the note proposes a bank-side real-time defense:

Greed vector: velocity controls, risk scoring, biometric verification, and friction on high-risk beneficiary additions
Authority vector: NLP-based narration monitoring and account-linking anomaly detection
Final Recommendation
This project demonstrates a practical fintech AI workflow spanning investor advisory, risk extraction, and financial-risk analytics. The strongest overall implementation is the agentic advisory pipeline combined with structured risk filtering and anomaly detection, while the DCF and blockchain notes provide the strategic and governance context needed for a modern digital finance platform.

Recorded run transcripts for this project use the MOCK_LLM=1 baseline mode with deterministic outputs and no external LLM dependency.

