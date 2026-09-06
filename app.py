import re
import streamlit as st
from pypdf import PdfReader
from docx import Document

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🤖", layout="wide")

st.title("🤖 AI Resume Analyzer")
st.caption("Analyze your resume against a job description and get an ATS-style score.")

def extract_text(uploaded_file):
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if name.endswith(".docx"):
        doc = Document(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs)

    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    return ""

def clean_words(text):
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}", text.lower()))

def analyze(resume, job):
    resume_words = clean_words(resume)
    job_words = clean_words(job)

    stopwords = {
        "the","and","for","with","from","that","this","are","you","your",
        "have","has","will","our","they","their","into","using","about",
        "years","work","working","role","job","skills","experience"
    }

    keywords = sorted(w for w in job_words if w not in stopwords and len(w) > 2)
    matched = [w for w in keywords if w in resume_words]
    missing = [w for w in keywords if w not in resume_words]

    score = round((len(matched) / len(keywords)) * 100) if keywords else 0

    sections = {
        "Education": bool(re.search(r"\b(b\.?tech|bachelor|degree|education|college|university)\b", resume, re.I)),
        "Experience": bool(re.search(r"\b(experience|internship|intern|employment|worked)\b", resume, re.I)),
        "Projects": bool(re.search(r"\b(projects?|project work)\b", resume, re.I)),
        "Skills": bool(re.search(r"\b(skills?|technologies|technical skills)\b", resume, re.I)),
    }

    suggestions = []
    if score < 60:
        suggestions.append("Add more keywords from the job description naturally to your resume.")
    if not sections["Projects"]:
        suggestions.append("Add a Projects section with 2–4 strong technical projects.")
    if not sections["Skills"]:
        suggestions.append("Add a clear Technical Skills section.")
    if not sections["Experience"]:
        suggestions.append("Add internship, freelance, college, or relevant practical experience.")
    if not suggestions:
        suggestions.append("Your resume has a good keyword match. Keep improving project impact and measurable results.")

    return score, matched, missing, sections, suggestions

left, right = st.columns(2)

with left:
    st.subheader("1️⃣ Upload Resume")
    resume_file = st.file_uploader("PDF, DOCX or TXT", type=["pdf", "docx", "txt"])

with right:
    st.subheader("2️⃣ Job Description")
    job_text = st.text_area("Paste the job description here", height=220,
                            placeholder="Example: Python, SQL, Machine Learning, Git, REST API...")

if resume_file and job_text.strip():
    resume_text = extract_text(resume_file)

    if not resume_text.strip():
        st.error("Could not extract text from this resume file.")
    else:
        if st.button("🚀 Analyze Resume", use_container_width=True):
            score, matched, missing, sections, suggestions = analyze(resume_text, job_text)

            st.divider()
            st.subheader("📊 ATS Analysis")

            c1, c2, c3 = st.columns(3)
            c1.metric("ATS Score", f"{score}%")
            c2.metric("Matched Keywords", len(matched))
            c3.metric("Missing Keywords", len(missing))

            st.progress(score / 100)

            a, b = st.columns(2)
            with a:
                st.markdown("### ✅ Matched Keywords")
                st.write(", ".join(matched[:60]) if matched else "No strong matches found.")

            with b:
                st.markdown("### ⚠️ Missing Keywords")
                st.write(", ".join(missing[:60]) if missing else "No major keyword gaps found.")

            st.markdown("### 📋 Resume Sections")
            for section, found in sections.items():
                st.write(("✅ " if found else "❌ ") + section)

            st.markdown("### 💡 Suggestions")
            for suggestion in suggestions:
                st.info(suggestion)

            st.success("Analysis complete! Use the suggestions to improve your resume.")
else:
    st.info("Upload a resume and paste a job description to start.")
