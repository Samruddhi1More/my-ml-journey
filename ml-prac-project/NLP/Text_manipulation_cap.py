import streamlit as st

st.set_page_config(page_title="Text Tools", layout="wide")
st.title("📑 Text Manipulation Capabilities")

st.divider()

# HTML template for bordered tile
def render_tile(title):
    st.markdown(
        f"""
        <div style='
            border: 2px solid #d1d1d1;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            font-weight: 600;
            font-size: 16px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        '>
            {title}
        </div>
        """,
        unsafe_allow_html=True
    )

#  Sentiment Analysis Section
st.subheader("👩‍💻 Sentiment Analysis")

sentiment_methods = [
    "Rule-based",
    "Traditional Machine Learning",
    "Using LLM"
]

cols = st.columns(len(sentiment_methods))
for col, method in zip(cols, sentiment_methods):
    with col:
        render_tile(method)

st.divider()

# Entity Extraction Section
st.subheader("👾 Entity Extraction")

entity_methods = [
    "Using NLP",
    "Using LLM"
]

cols = st.columns(len(entity_methods))
for col, method in zip(cols, entity_methods):
    with col:
        render_tile(method)
