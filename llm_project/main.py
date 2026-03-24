import streamlit as st 

pages = [
    st.Page(
        page="pages/chatbot_api.py",
        title="Chatbot API",
        icon="😊",
        default=True
    )
]

nav = st.navigation(pages)
nav.run()