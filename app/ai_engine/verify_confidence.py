import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai_engine.red_engine import red_engine
import pandas as pd

def verify_variance():
    print("Checking Confidence Variance for HOLD signals...")
    
    # Simulate various tech scores near 0 (HOLD territory)
    scores = [-0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3]
    
    # Simulate typical sentiment confidence (e.g., 0.6 for existing news)
    sentiment = {"score": 0.0, "confidence": 0.6} 
    regime = "Range-Bound" # Typical regime for confusion

    results = []

    for s in scores:
        # We need to construct inputs such that they result in 's' as final score
        # In Range-Bound: score = tech * 0.5 + sent * 0.5
        # Let sent_score = 0.0 --> score = tech * 0.5
        # So tech_input = s / 0.5 = s * 2
        
        tech_input = s * 2
        
        res = red_engine(tech_input, sentiment, regime)
        if res['signal'] == 'HOLD':
            results.append(res['confidence'])
            print(f"Tech Score: {s:.2f} -> Conf: {res['confidence']}")

    # Check if they are all the same
    unique_results = set(results)
    print(f"Unique Confidence Values: {len(unique_results)}")
    
    if len(unique_results) > 1:
        print("PASS: Variance detected.")
    else:
        print("FAIL: Confidence is stuck.")
        raise Exception("Confidence stuck")

if __name__ == "__main__":
    verify_variance()
