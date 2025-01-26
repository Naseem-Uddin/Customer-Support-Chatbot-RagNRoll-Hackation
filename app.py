# Created by Jibril Wague
# This file is the front end and handles everything on the users front. Deployed using Streamlit as per the requirement of the Hackathon. For more information about the hackation please refer to this link: https://snowflake-mistral-rag.devpost.com/

from dotenv import load_dotenv
import os
import streamlit as st
from main import (
    create_embeddings,
    setup_faiss_index,
    retrieve_and_generate,
    connection,
    texts,
    embeddings,
    faiss_index
)


load_dotenv()

st.set_page_config(page_icon="", layout="wide", page_title="NxtGenAI")

def icon(emoji: str):
    st.write(f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,)

icon("✅")
st.subheader("Customer Support Chatbot Working...", divider="red", anchor=False)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    avatar = '🤖' if message["role"] == "assistant" else '👨‍💻'
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Handle user input and generate response
if prompt := st.chat_input("Enter your prompt here..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar='👨‍💻'):
        st.markdown(prompt)

    try:
        # Generate response using RAG pipeline
        response = retrieve_and_generate(prompt, faiss_index, texts)
        
        # Display assistant response
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response)
            
        # Save assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}", icon="🚨")
