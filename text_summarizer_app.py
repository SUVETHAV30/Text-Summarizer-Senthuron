import streamlit as st
from transformers import pipeline
from deep_translator import GoogleTranslator
import docx
import fitz  # PyMuPDF for PDF support

# Load the summarizer model
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Helper function to translate text
def translate_text(text, target_lang):
    return GoogleTranslator(source='auto', target=target_lang).translate(text)

# Helper function to read uploaded documents
def read_file(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8")
    elif file.type == "application/pdf":
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return ""

# Streamlit UI
st.set_page_config(page_title="Text Summarizer", layout="centered")
st.title("📝TinyTalk- Your Text summarizer and Translator")

input_mode = st.radio("Choose input type:", ["Manual Text", "Upload Document"])

text = ""
if input_mode == "Manual Text":
    text = st.text_area("Enter text to summarize:")
else:
    file = st.file_uploader("Upload a file (.txt, .pdf, .docx)", type=["txt", "pdf", "docx"])
    if file:
        text = read_file(file)
        st.success("Document loaded successfully!")

# Controls
min_len = st.slider("Minimum summary length", 10, 100, 30)
max_len = st.slider("Maximum summary length", 30, 300, 60)
target_lang = st.selectbox("Translate summary to:", ["en", "ta", "hi", "fr", "es"])

# Summarization action
if st.button("Summarize"):
    if not text.strip():
        st.warning("Please enter or upload some text first.")
    else:
        with st.spinner("Summarizing..."):
            translated_input = translate_text(text, "en")
            summary = summarizer(translated_input, max_length=max_len, min_length=min_len, do_sample=False)
            result = summary[0]['summary_text']
            translated_summary = translate_text(result, target_lang)

            st.subheader("📝 Summary:")
            st.write(translated_summary)
