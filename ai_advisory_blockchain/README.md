# Run Transcripts (MOCK_LLM=1 Baseline)

### Part A Run Output:
- INV01 (Conservative): Expected Return = 7.90%, Volatility = 8.44% | Status: FINALIZED
- INV02 (Moderate): Expected Return = 10.90%, Volatility = 12.57% | Status: FINALIZED
- INV03 (Aggressive): Expected Return = 14.80%, Volatility = 20.58% | Status: ESCALATED_TO_HUMAN_ADVISOR
- INV04 (Moderate): Expected Return = 10.90%, Volatility = 12.57% | Status: FINALIZED
- INV05 (Aggressive): Expected Return = 14.80%, Volatility = 20.58% | Status: ESCALATED_TO_HUMAN_ADVISOR

### Part B Run Output:
- doc_01: {'risk_flags': [], 'hedging_detected': True, 'sentiment': 'cautious'}
- doc_02: {'risk_flags': ['litigation'], 'hedging_detected': False, 'sentiment': 'neutral'}
- doc_03: {'risk_flags': ['customer concentration'], 'hedging_detected': False, 'sentiment': 'neutral'}
- doc_04: {'risk_flags': [], 'hedging_detected': True, 'sentiment': 'cautious'}
- doc_05: {'risk_flags': [], 'hedging_detected': False, 'sentiment': 'confident'}
- doc_06: {'risk_flags': ['regulatory'], 'hedging_detected': False, 'sentiment': 'neutral'}

### Part D DCF Sensitivity Grid (INR):
| WACC / g | 3.00% | 4.00% | 5.00% |
| :--- | :--- | :--- | :--- |
| **10.32%** | 1,189,451,202 | 1,328,901,411 | 1,514,835,112 |
| **11.32%** | 1,048,211,902 | 1,154,231,041 | 1,291,123,401 |
| **12.32%** | 935,110,230 | 1,018,442,109 | 1,123,101,450 |