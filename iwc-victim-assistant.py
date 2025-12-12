import streamlit as st
import requests

st.title("Integrity Wins Consulting Fraud Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help with fraud concerns?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {st.secrets['API_KEY']}"},
            json={
                "model": "grok-3-mini",
                "messages": [
                    {"role": "system", "content": "You are a fraud prevention assistant for Integrity Wins Consulting. Help K-1 visa fraud victims. Guide to contact form. Analyze texts for evidence."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
        )
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        else:
            st.error("API error—check key or credits.")