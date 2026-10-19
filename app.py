import os
import streamlit as st
from dotenv import load_dotenv
from query_engine import ask_oracle 

# Load API keys from .env
load_dotenv()

# Set up the Streamlit page configuration
st.set_page_config(page_title="Oracle Tax Assistant", page_icon="💼", layout="centered")
st.title("💼 Oracle Tax Assistant")
st.write("Ask questions based on your ingested tax documents and the live web.")

# 1. MANAGE CHAT HISTORY: Keep track of messages across Streamlit reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages from history safely
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Using unsafe_allow_html=True guarantees that saved badges render correctly during historical reruns
        st.markdown(message["content"], unsafe_allow_html=True)

# 2. CHAT INPUT: Accept user questions
if user_query := st.chat_input("Ask a tax question..."):
    # Display the user's message immediately
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Generate the AI response using our smart query_engine
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        with st.spinner("Analyzing local PDFs and routing queries..."):
            try:
                # Execute the dual routing logic
                result_dict = ask_oracle(user_query)
                
                # Safely parse the returning dictionary attributes
                answer = result_dict.get("answer", "")
                source = result_dict.get("source", "Unknown")
                
                # Format a clean, visual HTML badge based on the query origin
                if source == "Internal PDFs":
                    badge_html = f'<div style="margin-top:12px;"><span style="background-color:#d4edda; color:#155724; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; display:inline-block;">📂 Source: {source}</span></div>'
                elif source == "Live Web Search":
                    badge_html = f'<div style="margin-top:12px;"><span style="background-color:#cce5ff; color:#004085; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; display:inline-block;">🌐 Source: {source}</span></div>'
                else:
                    badge_html = f'<div style="margin-top:12px;"><span style="background-color:#fff3cd; color:#856404; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold; display:inline-block;">⚡ Source: {source}</span></div>'

                # Combine markdown answer body text with the visual footer badge
                full_display_content = f"{answer}\n\n{badge_html}"
                
                # Push content cleanly to the placeholder element
                response_placeholder.markdown(full_display_content, unsafe_allow_html=True)
                
                # Append the full string component state to history
                st.session_state.messages.append({"role": "assistant", "content": full_display_content})
                
            except Exception as api_err:
                response_placeholder.error(f"An error occurred while generating the answer: {api_err}")
