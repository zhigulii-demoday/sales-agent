import streamlit as st

import requests
# with st.sidebar:
#     openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "curr_company" not in st.session_state:
    st.session_state["curr_company"] = ''

if "companies" not in st.session_state:
    r = requests.get('http://84.252.143.166:8097/companies')
    if r:
        st.session_state["companies"] = [x['name'] for x in r.json()['data']]
    else:
        st.session_state["companies"] = []








tab1, tab2 = st.tabs(["Чат", 'Tab2'])

with tab1:



    st.markdown(f"<h3 style='text-align: center;'>Чатик с промптом </h3>", unsafe_allow_html=True)


    def button_gitlab():
        st.session_state["messages"].append({
            "role": "assistant", "content" : "Generated first message to client"
        })




    tab11, tab12, tab13 = st.columns(3)
    with tab11:
        if not st.session_state.messages:
            st.button("Generate first message", type="primary", on_click=button_gitlab, disabled = False)
        else:
            st.button("Generate first message", type="primary", on_click=button_gitlab, disabled = True)
    with tab12:
        st.session_state.curr_company = st.selectbox('Выберите компанию', st.session_state.companies, label_visibility='collapsed') 

    if not st.session_state.messages:
        prompt = st.chat_input("Say something", disabled=True)
    else:
        prompt = st.chat_input("Say something")

    if prompt:
        st.session_state.messages.append({
                    "role": "user", "content" : prompt
                })
    

    for msg in st.session_state["messages"]:
        st.chat_message(msg['role']).write(msg['content'])