import streamlit as st
import pandas as pd
import tempfile
import re
import pdfplumber
import docx2txt
import spacy
from collections import Counter
import time

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Skill list
skills_list = ["Python", "Java", "C++", "Machine Learning", "Data Science", "AI", "TensorFlow", "Keras", "SQL", "Pandas"]

# Functions
def extract_text(file_path):
    if file_path.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    elif file_path.endswith(".docx"):
        return docx2txt.process(file_path)
    return ""

def parse_resume(text):
    clean_text = re.sub(r'Email:|Phone:|Contact:', '', text, flags=re.IGNORECASE)
    doc = nlp(clean_text)

    name = None
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = re.sub(r'\S+@\S+', '', ent.text.strip().replace("\n", " ")).strip()
            break

    email = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    phone = re.findall(r'\+?\d[\d\s-]{8,}\d', text)
    skills = [skill for skill in skills_list if skill.lower() in text.lower()]

    return {
        "Name": name if name else "",
        "Email": email[0] if email else "",
        "Phone": phone[0] if phone else "",
        "Skills": ", ".join(skills)
    }

# --- Streamlit UI ---
st.set_page_config(page_title="AI Resume Parser", page_icon="📄", layout="wide")

# Custom CSS
st.markdown("""
    <style>
        .main {background-color: #0E1117; color: white;}
        .css-18e3th9 {padding: 2rem 1rem 10rem;}
        .stButton button {
            background-color: #00C851;
            color: white;
            font-size: 16px;
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
        }
        .header {
            font-size: 38px;
            color: #00E676;
            text-align: center;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .footer {
            text-align: center;
            color: gray;
            font-size: 14px;
            margin-top: 40px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header'>📄 AI-Powered Resume Parser</div>", unsafe_allow_html=True)
st.write("Upload resumes in PDF/DOCX format and extract **Name, Email, Phone, and Skills** instantly!")

with st.sidebar:
    st.header("📌 Instructions")
    st.markdown("1. Upload resumes (PDF/DOCX)\n2. Wait for parsing\n3. Download CSV\n4. View skill insights")
    st.markdown("**Tech Stack:** Python | SpaCy | Streamlit")

uploaded_files = st.file_uploader("📂 Drag and drop your resumes here", type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    progress = st.progress(0)
    results = []
    
    for i, file in enumerate(uploaded_files):
        progress.progress(int((i+1)/len(uploaded_files)*100))
        time.sleep(0.5)

        with tempfile.NamedTemporaryFile(delete=False, suffix=file.name) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
        text = extract_text(tmp_path)
        parsed = parse_resume(text)
        parsed["File"] = file.name
        results.append(parsed)
    
    st.success("✅ Parsing Complete!")
    
    df = pd.DataFrame(results)

    # Metrics Section
    total_resumes = len(df)
    all_skills = []
    for s in df["Skills"]:
        if s:
            all_skills.extend(s.split(", "))
    top_skill = Counter(all_skills).most_common(1)[0][0] if all_skills else "N/A"

    col1, col2 = st.columns(2)
    with col1:
        st.metric("📂 Total Resumes Parsed", total_resumes)
    with col2:
        st.metric("🔥 Most Common Skill", top_skill)

    # Expandable Results Table
    with st.expander("🔍 View Parsed Data"):
        st.dataframe(df, use_container_width=True)

    # Skill Frequency Chart
    if all_skills:
        st.subheader("📊 Skill Frequency Analysis")
        skill_counts = pd.Series(all_skills).value_counts().reset_index()
        skill_counts.columns = ["Skill", "Count"]
        st.bar_chart(skill_counts.set_index("Skill"))

    # Download Button
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Download Parsed Data (CSV)", csv_data, "parsed_resumes.csv", "text/csv")

else:
    st.info("Upload resumes to start parsing...")


