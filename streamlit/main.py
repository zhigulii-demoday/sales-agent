import streamlit as st

# with st.sidebar:
#     openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = []







tab1, tab2, tab3, tab4 = st.tabs(["Чат", "Проект", "GitLab", "Обновление данных"])

with tab1:



    st.markdown(f"<h3 style='text-align: center;'>Чатик с промптом </h3>", unsafe_allow_html=True)


    def button_gitlab():
        st.session_state["messages"].append({
            "role": "assistant", "content" : "Generated first message to client"
        })

    if not st.session_state["messages"]:
        st.button("Generate first message", type="primary", on_click=button_gitlab, disabled = False)
    else:
        st.button("Generate first message", type="primary", on_click=button_gitlab, disabled = True)

    prompt = st.chat_input("Say something")
    if prompt:
        st.session_state["messages"].append({
                    "role": "user", "content" : prompt
                })
        
    for msg in st.session_state["messages"]:
        st.chat_message(msg['role']).write(msg['content'])