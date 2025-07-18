import pdfplumber
import docx2txt
import spacy
import re
import pandas as pd
import os

nlp = spacy.load("en_core_web_sm")

skills_list = ["Python", "Java", "C++", "Machine Learning", "Data Science", "AI", "TensorFlow", "SQL", "Pandas"]

def extract_text(file_path):
    if file_path.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    elif file_path.endswith(".docx"):
        return docx2txt.process(file_path)
    else:
        return ""

def parse_resume(text):
    # Clean text: remove Email/Phone labels
    clean_text = re.sub(r'Email:|Phone:|Contact:', '', text, flags=re.IGNORECASE)

    doc = nlp(clean_text)

    # Extract Name
    name = None
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.strip().replace("\n", " ")
            # Remove any email-like strings accidentally included
            name = re.sub(r'\S+@\S+', '', name).strip()
            break

    # Extract Email
    email = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)

    # Extract Phone
    phone = re.findall(r'\+?\d[\d\s-]{8,}\d', text)

    # Extract Skills
    skills = [skill for skill in skills_list if skill.lower() in text.lower()]

    return {
        "Name": name if name else "",
        "Email": email[0] if email else "",
        "Phone": phone[0] if phone else "",
        "Skills": ", ".join(skills)
    }




def process_resumes(folder_path):
    data = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        text = extract_text(file_path)
        parsed_data = parse_resume(text)
        parsed_data["File"] = file
        data.append(parsed_data)

    df = pd.DataFrame(data)
    df.to_csv("parsed_resumes.csv", index=False)
    print("✅ Results saved to parsed_resumes.csv")

if __name__ == "__main__":
    folder = input("Enter folder path of resumes: ")
    process_resumes(folder)
