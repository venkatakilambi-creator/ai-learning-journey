# 💼 Oracle Tax Assistant (Web + PDF RAG)

An advanced, hallucination-free retrieval-augmented generation (RAG) system built with **Streamlit**, **LangChain**, and **Gemini 3.8-flash**. The assistant intelligently routes queries: checking your local ingested PDFs first, and dynamically fallback-searching the live web using **Tavily AI** if local knowledge is insufficient.

## 🚀 Features
* **Smart Conditional Routing:** Evaluates local PDF context before calling external APIs to optimize speed and API costs.
* **Anti-Hallucination Guardrails:** Enforces a deterministic temperature (`0.0`) and strict systemic boundaries to eliminate creative assumptions.
* **Visual Source Verification:** Displays color-coded badges in the UI (**Internal PDFs**, **Live Web Search**, or **Combined**) indicating precisely where the answer was derived from.

---

## 🛠️ Installation & Setup

This project utilizes `uv` for lightning-fast Python packaging and dependency management.

### 1. Clone the Repository
```bash
git clone https://github.com
cd YOUR_REPO_NAME
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory and add your API keys:
```env
GOOGLE_API_KEY="your_gemini_api_key_here"
TAVILY_API_KEY="your_tavily_api_key_here"
```

### 3. Add Your Local PDFs
Create a `data` directory and drop your target PDFs inside:
```bash
mkdir data
# Place your tax documentation PDFs into the data/ folder
```

### 4. Ingest Documents
Run the ingestion script to parse your PDFs and build the local vector database:
```bash
uv run python ingest.py
```

### 5. Launch the Streamlit App
Start the local interactive chat interface:
```bash
uv run python -m streamlit run app.py
```
