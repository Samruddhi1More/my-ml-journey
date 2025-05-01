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
          """  You are an NLP expert. Given a piece of document content, perform the following:

1. Extract keywords or entities that are specific to one of the following domains:
   - Legal (e.g., clause, agreement, party, court, contract)
   - Accounts (e.g., ledger, balance, invoice, audit, fiscal year)
   - Technical (e.g., python, CUDA, model, firmware, API)

2. Based on the entities, classify the document into **one and only one** of the following categories: 
   - Legal
   - Accounts
   - Technical

3. Respond only in the following format:

Entity: [comma-separated list of extracted domain-specific terms]  
Categorical: [only one of: Legal, Accounts, Technical]
            Document Content:"""
            ),
            ("human", "{query}")
        ])

chain = prompt | llm

st.title("👾 Entity Extraction")

text = st.text_area("Enter your doc content")

if st.button("Extract"):
    if text:
        response = chain.invoke({"query": text})
        st.success(response.content)