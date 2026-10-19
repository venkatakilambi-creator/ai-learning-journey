import os
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

def verify_database_count():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base_dir, "oracle_tax_db")
    
    if not os.path.exists(db_dir):
        print("❌ The database folder 'oracle_tax_db' does not exist yet.")
        return
        
    # Standardize the embedding model mapping
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    
    # Load the local index state
    vector_db = Chroma(persist_directory=db_dir, embedding_function=embeddings)
    
    # Extract the internal matching item collection
    collection = vector_db._collection
    count = collection.count()
    
    print(f"📊 Vector Database Inspection Status:")
    print(f"   -> Directory location: {db_dir}")
    print(f"   -> Saved segment chunks found: {count}")

if __name__ == "__main__":
    verify_database_count()
