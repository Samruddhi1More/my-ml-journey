import streamlit as st
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
#Loading the vectorizer model
vectorizer = joblib.load(r"C:\Users\samru\OneDrive\Desktop\Provakil\pages\vectorizer.pkl")

#Loading the LR model
model = joblib.load(r"C:\Users\samru\OneDrive\Desktop\Provakil\pages\sentiment-analysis.pkl")

st.title("🎬 Movie Review Sentiment Analyzer")

review = st.text_area("Enter your moview review")

if st.button("Analyze"):
    if review:
        vector = vectorizer.transform([review])
        pred = model.predict(vector)
        st.success(pred)