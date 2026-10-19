import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

# 1. Import TavilySearch directly instead of the hidden Wrapper
from langchain_tavily import TavilySearch

load_dotenv()

def ask_oracle(user_query: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base_dir, "oracle_tax_db")
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    vector_db = Chroma(persist_directory=db_dir, embedding_function=embeddings)
    llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.0)

    print("🔍 Checking local PDF database...")
    local_docs = vector_db.similarity_search(user_query, k=3)
    pdf_context = "\n\n".join([doc.page_content for doc in local_docs])

    router_prompt = (
        "Analyze the User Query and the provided PDF Context.\n"
        "Can the query be completely and accurately answered using ONLY this PDF context?\n"
        "Reply with exactly one word: 'YES' or 'NO'.\n\n"
        f"PDF Context:\n{pdf_context}\n\n"
        f"User Query: {user_query}"
    )
    
    # 🛠️ FIXED ROUTING SECTION START (Replaced the single line causing list.strip() error)
    response_router = llm.invoke([("user", router_prompt)])

    # Safely extract text if Gemini returns a list of blocks instead of a raw string
    if isinstance(response_router.content, list):
        raw_text = "".join([block.get("text", "") if isinstance(block, dict) else str(block) for block in response_router.content])
    else:
        raw_text = str(response_router.content)

    routing_decision = raw_text.strip().upper()
    # 🛠️ FIXED ROUTING SECTION END

    web_context = ""
    if "NO" in routing_decision:
        print("🌐 PDF context is insufficient. Triggering Tavily Web Search...")
                
        tavily_tool = TavilySearch(
            tavily_api_key="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", # <-- Pass the key explicitly here
            max_results=3, 
            search_depth="advanced"
        )
       
        
        # Invoke the tool directly using standard LangChain tool protocol
        web_results = tavily_tool.invoke({"query": user_query})
        
        # Process the clean JSON response string
        web_context = f"\n[Live Web Insights]:\n{web_results}\n"
    else:
        print("✅ Found sufficient answer in local PDFs. Skipping Web Search.")

    system_prompt = (
        "You are a strict financial and tax compliance assistant. You answer questions "
        "using ONLY the verified contexts provided below.\n\n"
        "STRICT RULES:\n"
        "1. Ground every claim you make using the provided data.\n"
        "2. If the answer cannot be confidently answered from either context, explicitly reply with: "
        "'I am sorry, but I cannot find authentic or verifiable information on this topic.'\n"
        "3. Do NOT make assumptions or use pre-trained creative knowledge.\n\n"
        f"--- START LOCAL PDF CONTEXT ---\n{pdf_context}\n--- END LOCAL PDF CONTEXT ---\n\n"
    )
    
    if web_context:
        system_prompt += f"--- START WEB SEARCH CONTEXT ---\n{web_context}\n--- END WEB SEARCH CONTEXT ---\n"

    print("🤖 Processing final grounded response...")
    
    # We apply the same safety unwrap logic to the final answer just in case
    response_final = llm.invoke([
        ("system", system_prompt),
        ("human", user_query)
    ])
    
    if isinstance(response_final.content, list):
        final_answer = "".join([block.get("text", "") if isinstance(block, dict) else str(block) for block in response_final.content])
    else:
        final_answer = str(response_final.content)
        
   
# 🛠️ NEW: Determine the data origin based on your routing decision
    if "NO" in routing_decision:
        # Check if local PDFs provided any content to determine the precise badge labels
        data_source = "Live Web Search" if not local_docs else "Live Web Search"
    else:
        data_source = "Internal PDFs"
    # 🚀 RETURN BOTH AT THE SAME TIME
    return {
        "answer": final_answer,
        "source": data_source
    }    


if __name__ == "__main__":
    # Test sample query
    query = "What are the latest updates on tax rulings for Oracle contracts or software licenses?"
    answer = ask_oracle(query)
    print("\n📝 ANSWER:\n", answer)
