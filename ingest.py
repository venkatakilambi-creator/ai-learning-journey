import os
import glob
import time
import re
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from google.api_core import retry

load_dotenv()

def build_vector_database():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    db_dir = os.path.join(base_dir, "oracle_tax_db")
    log_file = os.path.join(base_dir, "processed_files.txt")
    
    # Track which files we have already ingested in the past
    processed_files = set()
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            processed_files = set(line.strip() for line in f.readlines())

    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    pdf_files = [f for f in pdf_files if ":Zone.Identifier" not in f]
    # Filter out files that were already processed
    new_pdf_files = [f for f in pdf_files if os.path.basename(f) not in processed_files]
    
    if not pdf_files:
        print("❌ No PDFs found in the 'data' folder. Add files first!")
        return
        
    if not new_pdf_files:
        print("💡 All PDFs in the data folder are already fully ingested. Nothing new to add!")
        return
        
    print(f"📂 Found {len(new_pdf_files)} NEW PDFs out of {len(pdf_files)} total files. Extracting text blocks...")
    all_chunks = []
    successfully_processed = []
    
    for pdf in new_pdf_files:
        filename = os.path.basename(pdf)
        print(f"📄 Segmenting: {filename}")
        try:
            loader = PyMuPDFLoader(pdf)
            docs = loader.load()
            
            # Subdivide text blocks cleanly
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            chunks = text_splitter.split_documents(docs)
            all_chunks.extend(chunks)
            successfully_processed.append(filename)
        except Exception as e:
            print(f"⚠️ Error reading {pdf}: {e}")

    if not all_chunks:
        print("⚠️ No new text blocks could be generated. Aborting.")
        return

    print(f"🤖 Total NEW generated segments: {len(all_chunks)}")
    print("🤖 Initializing free tier Google indexer...")
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-2",
        client_options={"requests_retry_config": retry.Retry(predicate=lambda e: False)}
    )
    
    print(f"💾 Appending to local database directory at '{db_dir}'...")
    vector_db = Chroma(persist_directory=db_dir, embedding_function=embeddings)
    
    batch_size = 5
    print(f"🚀 Processing and uploading in safe micro-batches of {batch_size}...")
    
    i = 0
    while i < len(all_chunks):
        batch = all_chunks[i:i + batch_size]
        print(f"📦 Uploading chunks {i} to {i + len(batch)} of {len(all_chunks)}...")
        
        try:
            vector_db.add_documents(batch)
            i += batch_size  
            time.sleep(3)    
            
        except Exception as api_err:
            err_msg = str(api_err)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "Quota exceeded" in err_msg:
                match = re.search(r"retry in (\d+\.\d+)s|RetryInfo.*retryDelay':\s*'(\d+)s'", err_msg)
                wait_time = 60 
                if match:
                    seconds = match.group(1) or match.group(2)
                    wait_time = int(float(seconds)) + 2
                
                print(f"⏳ Rate limit hit. Intentionally sleeping for {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"❌ Unhandled structural error: {api_err}")
                raise api_err
                
    # Save the successfully completed files to the log so we never duplicate them
    with open(log_file, "a") as f:
        for file in successfully_processed:
            f.write(f"{file}\n")
            
    print("✅ Success! Your new knowledge has been merged into the database.")

if __name__ == "__main__":
    build_vector_database()
