import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# -------------------------------
# Initialize VADER (once)
# -------------------------------
nltk.download('vader_lexicon', quiet=True)
vader = SentimentIntensityAnalyzer()

# -------------------------------
# Simple financial lexicon
# -------------------------------
POSITIVE_WORDS = {
    "gain", "gains", "growth", "profit", "profits",
    "strong", "bullish", "positive", "surge", "rise"
}

NEGATIVE_WORDS = {
    "loss", "losses", "decline", "declining", "weak",
    "bearish", "negative", "risk", "fall", "falls"
}


# -------------------------------
# Lexicon-based sentiment
# -------------------------------
def lexicon_sentiment(text: str) -> float:
    """
    Rule-based sentiment using a financial lexicon.
    Output normalized to range [-1, 1].
    """
    words = text.lower().split()
    score = 0

    for w in words:
        if w in POSITIVE_WORDS:
            score += 1
        elif w in NEGATIVE_WORDS:
            score -= 1

    # Normalize score
    if score == 0:
        return 0.0

    return max(min(score / 5, 1.0), -1.0)


# -------------------------------
# Multi-source sentiment ensemble
# -------------------------------
def multi_source_sentiment(headlines):
    """
    Combines multiple sentiment sources (VADER + Lexicon)
    and measures agreement to produce confidence.

    Returns:
    {
        score: float (-1 to +1),
        confidence: float (0 to 1),
        label: Positive / Neutral / Negative,
        sources: { vader, lexicon }
    }
    """
    if not headlines:
        return {
            "score": 0.0,
            "confidence": 0.0,
            "label": "Neutral",
            "sources": {
                "vader": 0.0,
                "lexicon": 0.0
            }
        }

    vader_scores = []
    lexicon_scores = []

    for text in headlines:
        vader_scores.append(vader.polarity_scores(text)["compound"])
        lexicon_scores.append(lexicon_sentiment(text))

    avg_vader = sum(vader_scores) / len(vader_scores)
    avg_lexicon = sum(lexicon_scores) / len(lexicon_scores)

    # Ensemble score (direction)
    final_score = (avg_vader + avg_lexicon) / 2

    # Agreement-based confidence
    agreement = 1 - abs(avg_vader - avg_lexicon)
    confidence = round(max(min(agreement, 1.0), 0.0), 2)

    # Label assignment
    if final_score > 0.05:
        label = "Positive"
    elif final_score < -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "score": round(final_score, 3),
        "confidence": confidence,
        "label": label,
        "sources": {
            "vader": round(avg_vader, 3),
            "lexicon": round(avg_lexicon, 3)
        }
    }
