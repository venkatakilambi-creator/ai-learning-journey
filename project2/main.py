import streamlit as st
import pypdf
import io
import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()   

st.set_page_config(page_title="PDF Summarizer", page_icon=":books:", layout="wide") 
st.title("PDF Summarizer :books:")
st.markdown("Upload your resume and get AI-Powered feedback.")  

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
uploaded_file = st.file_uploader("Upload your resume (PDF or txt)", type=["pdf","txt"])  
job_role = st.text_input("Enter the job role / PDF name (optional):")

analyze = st.button("Analyze PDF")

if analyze and uploaded_file:
    # Read PDF text
    pdf_reader = pypdf.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""

    if not text.strip():
        st.error("The PDF file is empty or could not be read.")
    else:
        st.write("Analyzing the PDF...")

        if not ANTHROPIC_API_KEY:
            st.error("ANTHROPIC_API_KEY is missing. Please add it to your .env file.")
        else:
            client = Anthropic(api_key=ANTHROPIC_API_KEY)
            prompt = (
                f"Summarize the following PDF content for a {job_role or 'general professional'} audience:\n\n{text[:20000]}"
            )
            
            try:
                # Using a valid Anthropic model slug (e.g., claude-3-5-sonnet-latest)
                response = client.messages.create(
                    model="claude-sonnet-5-5",
                    max_tokens=1000,
                    system="You are a helpful assistant.",
                    messages=[{"role": "user", "content": prompt}],
                )
                
                # Safely extract text block contents while ignoring ThinkingBlocks
                final_text = "".join([block.text for block in response.content if getattr(block, 'type', None) == 'text'])
                summary = final_text.strip()
                
                st.success("PDF analyzed successfully.")
                st.markdown("### Summary of the PDF:")
                st.markdown(summary)
                
            except Exception as e:
                st.error(f"An error occurred during API call: {e}")

elif analyze:
    st.warning("Please upload a PDF file first.")
