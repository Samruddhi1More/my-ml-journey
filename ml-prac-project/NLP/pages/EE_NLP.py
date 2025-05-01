import streamlit as st
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Defining category-specific keywords
cat_keyword = {
    "Legal": {"clause", "agreement", "party", "court", "contract", "act", "affidavit", "summon"},
    "Accounts": {"ledger", "balance", "invoice", "fy", "audit", "debit", "credit", "revenue"},
    "Technical": {"python", "cuda", "package", "api", "firmware", "neural", "deployment", "model",
                  "ml", "machine learning", "ai", "artificial intelligence"}
}

def content_to_cat(text):
    doc = nlp(text)

    
    entities = set(ent.text.lower() for ent in doc.ents)
    tokens = set(token.text.lower() for token in doc if token.is_alpha)

  
    all_words = entities.union(tokens)

    
    cat_score = {cat: len(all_words & set(k.lower() for k in keywords)) for cat, keywords in cat_keyword.items()}

    
    best_cat = max(cat_score, key=cat_score.get)

    
    extracted_ent = list(set(ent.text.upper() for ent in doc.ents))

    return extracted_ent, best_cat

# Streamlit UI
st.title("👾 Entity Extraction & Document Categorization")

text = st.text_area("Enter your document content below:")

if st.button("Extract"):
    if text.strip():
        ent, cat = content_to_cat(text)
        st.markdown("###  Extracted Entities:")
        st.success(", ".join(ent) if ent else "No entities found.")
        
        st.markdown("###  Likely Document Category:")
        st.success(cat)
    else:
        st.warning("Please enter some text before clicking Extract.")
