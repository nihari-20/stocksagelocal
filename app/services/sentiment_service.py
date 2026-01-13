from textblob import TextBlob


def analyze_sentiment(news_articles):
    # If no news, return neutral
    if not news_articles:
        return {
            "sentiment": "Neutral",
            "score": 0.0
        }

    scores = []

    for article in news_articles:
        title = article.get("title", "")
        if title:
            polarity = TextBlob(title).sentiment.polarity

            # 🔥 amplify negative sentiment (finance-aware tweak)
            if polarity < 0:
                polarity *= 1.5

            scores.append(polarity)

    # If no valid scores
    if not scores:
        return {
            "sentiment": "Neutral",
            "score": 0.0
        }

    avg = sum(scores) / len(scores)

    # More sensitive thresholds (finance-friendly)
    if avg >= 0.05:
        sentiment = "Positive"
    elif avg <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return {
        "sentiment": sentiment,
        "score": round(avg, 3)
    }
