# src/app.py

import streamlit as st

def add_two_numbers(a, b):
    """A simple function to demonstrate a testable component."""
    return a + b

def main():
    """
    Main function to run the Streamlit application.
    This will serve as the main entry point for your Thudbot.
    """
    st.set_page_config(page_title="Project Title", page_icon="🤖")

    st.title("🤖 Project Title")
    st.markdown("A brief description of your project and its purpose.")

    # --- CHAT INTERFACE PLACEHOLDER ---
    # This is where you would build your Streamlit chat UI.
    # For a RAG application, you'll want to add code here to:
    # 1. Initialize a chat history session state.
    # 2. Display previous chat messages.
    # 3. Handle a user's input.
    # 4. Invoke your RAG pipeline.
    # 5. Display the agent's response.
    
    st.info("Start building your application here!")


if __name__ == "__main__":
    main()