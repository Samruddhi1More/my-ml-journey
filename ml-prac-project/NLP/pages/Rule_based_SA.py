import streamlit as st
from textblob import TextBlob

def get_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    return "Positive Review" if polarity>=0 else "Negative Review"

st.title("🎬 Movie Review Sentiment Analyzer")

review = st.text_area("Enter your moview review")

if st.button("Analyze"):
    if review:
        sentiment = get_sentiment(review)
        st.success(sentiment)