import streamlit as st
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import os
llm = ChatOllama(
                model="llama3",
                temperature=0,
            )

prompt = ChatPromptTemplate.from_messages([
            (
                "system",
          """  Sentiment Analysis Task: Movie Review Classification\

             You will be provided with a movie review text. Your task is to determine whether the sentiment of the review is POSITIVE or NEGATIVE.\

                Guidelines:
                1. Read the entire review carefully.\
                2. Analyze the language, tone, and specific expressions used by the reviewer.\
                3. Look for sentiment indicators such as praise, criticism, emotional reactions, and evaluative statements.\
                4. Consider the overall impression the reviewer conveys about the film.\
                5. Respond with ONLY ONE of these two classifications:
                - "POSITIVE" - if the review generally expresses approval, enjoyment, or recommendation of the film\
                - "NEGATIVE" - if the review generally expresses disapproval, disappointment, or advises against watching the film\

            Provide your classification as a single word response: either "POSITIVE" or "NEGATIVE".\

            Review text:"""
            ),
            ("human", "{query}")
        ])

chain = prompt | llm

st.title("🎬 Movie Review Sentiment Analyzer")

review = st.text_area("Enter your moview review")

if st.button("Analyze"):
    if review:
        response = chain.invoke({"query": review})
        st.success(response.content)