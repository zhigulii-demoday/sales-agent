import asyncio
import streamlit as st

import requests
# with st.sidebar:
#     openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

from llm_scripts.sales_handler import SalesBotHandler

import time

d_model = SalesBotHandler()
from messages.telegram_scripts import send_message
from messages.emai_scripts import send_email

with st.spinner('Loading Language Model...'):
    d_model = SalesBotHandler()


st.title("💬 Chatbot")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "curr_company" not in st.session_state:
    st.session_state["curr_company"] = ''

if "companies" not in st.session_state:
    r = requests.get('http://89.169.163.130:8097/companies')
    if r:
        st.session_state["companies"] = [x['name'] for x in r.json()['data']]
    else:
        st.session_state["companies"] = []








tab1, tab2 = st.tabs(["Чат", 'Tab2'])

with tab1:



    st.markdown(f"<h3 style='text-align: center;'>Чатик с промптом </h3>", unsafe_allow_html=True)


    def button_first_message():
        
        start_time = time.time()
        with st.spinner("Generating First Message...%s"):
            msg = d_model.generate_first_message()
        print("--- %s seconds ---" % (time.time() - start_time))
        st.session_state["messages"].append({
            "role": "assistant", "content" : msg
        })




    tab11, tab12, tab13 = st.columns(3)
    with tab11:
        if not st.session_state.messages:
            st.button("Generate first message", type="primary", on_click=button_first_message, disabled = False)
        else:
            st.button("Generate first message", type="primary", on_click=button_first_message, disabled = True)
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

        
        start_time = time.time()
        msg = d_model.generate_answer(prompt)
        print("--- %s seconds ---" % (time.time() - start_time))
        st.session_state.messages.append({
                    "role": "assistant", "content" : msg
                })

    for msg in st.session_state["messages"]:
        st.chat_message(msg['role']).write(msg['content'])
        
with st.sidebar:
    st.markdown("### Отправить сообщение")

    recipient = st.text_input("Введите адрес получателя")

    platform = st.selectbox("Выберите платформу", ["Telegram", "Email"])

    if st.button("Отправить"):
        if platform == "Email":
            asyncio.run(send_email(to_email=recipient, body=d_model.generate_first_message(), subject="Napoleon IT Отзывы"))
        elif platform == "Telegram":
            asyncio.run(send_message(user=recipient, message=d_model.generate_first_message()))