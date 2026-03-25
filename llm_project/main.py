import streamlit as st 

pages = [
    st.Page(
        page="pages/chatbot_api.py",
        title="Chatbot API",
        icon="😊",
        default=True
    ),
    st.Page(
        page="pages/stt_chatbot.py",
        title="STT test",
        icon="😊"
    )
]

nav = st.navigation(pages)
nav.run()