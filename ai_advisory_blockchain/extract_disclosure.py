import os
from disclosure_snippets import DISCLOSURE_SNIPPETS

def extract_signals(snippet: str) -> dict:
    mock_llm = os.getenv("MOCK_LLM", "1")
    
    if mock_llm == "1" or not mock_llm:
        text_lower = snippet.lower()
        risk_flags = []
        
        # Risk Flags Rule
        if "litigation" in text_lower:
            risk_flags.append("litigation exposure")
        if "regulatory" in text_lower or "compliance" in text_lower:
            risk_flags.append("regulatory compliance notice")
        if "customer" in text_lower or "42 percent" in text_lower:
            risk_flags.append("customer concentration risk")

        # Hedging Rule
        hedging_keywords = ["assuming", "cautiously", "visibility"]
        hedging_detected = any(kw in text_lower for kw in hedging_keywords)

        # Sentiment Rule
        if "confident" in text_lower or "approved" in text_lower:
            sentiment = "confident"
        elif hedging_detected:
            sentiment = "cautious"
        else:
            sentiment = "neutral"

        return {
            "risk_flags": risk_flags,
            "hedging_detected": hedging_detected,
            "sentiment": sentiment
        }

if __name__ == "__main__":
    print("\n--- PART B: DISCLOSURE EXTRACTION RESULTS ---")
    for snippet in DISCLOSURE_SNIPPETS:
        doc_id = snippet.split(":")[0]
        signals = extract_signals(snippet)
        print(f"{doc_id}: Sentiment={signals['sentiment']}, Hedging={signals['hedging_detected']}, Risks={signals['risk_flags']}")