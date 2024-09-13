
from llm_scripts.prompts import (CONTEXT_NAPOLEON_IT,
                        SALES_SCRIPT, 
                        SYS_PROMPT_INIT_DIALOGUE,
                        USER_INIT_PROMPT,
                        SYS_PROMPT_CONTINUE_DIALOGUE,
                        SYS_PROMPT_FOR_INTENTION,
                        SYS_PROMPT_TEXT_2_PANDAS
                        )



import os
import re
import pandas as pd
from typing import Callable

import psycopg2 as pg

import openai

import sqlparse


import openai

from langchain_experimental.utilities.python import PythonREPL

# MAX_TOKENS = 131072
MAX_TOKENS = 300000

def formating_chat_template(system: Callable,
                            context: list[str],
                            user: list[str],
                            user_question: str,
                            assistant: list[str]) -> list[dict]:
    messages = [
            {'role': 'system', 'content': system(*context)},
            {'role': 'user', 'content': user_question}
    ]

    for assistant_replica, user_replica in zip(assistant, user):
        
        messages.append(assistant_replica)
        messages.append(user_replica)

    return messages


class DialogueModel:

    def init_pandas(self):
        self.PATH_TO_DATASET = 'cleaned_coffee.csv'

        delimeter = '\n\n' + ('='* 100) + '\n\n'
        self.dataset = pd.read_csv(self.PATH_TO_DATASET)

    def init_model(self):

        self.init_pandas()

        self.model = openai.Client(
                    base_url="http://47.186.63.233:53213/v1", api_key="EMPTY")

        self.REPL = PythonREPL()

        
        self.messages_init = [
                {'role': 'system', 'content': SYS_PROMPT_INIT_DIALOGUE(CONTEXT_NAPOLEON_IT, SALES_SCRIPT)},
                {'role': 'user', 'content': USER_INIT_PROMPT}
            ]

        self.USER = []
        self.ASSISTANT = []

        self.engine = pg.connect("dbname='sales' user='zhigul' host='89.169.163.130' port='5432' password='asd'")

        self.cleaning_t2pandas = lambda answer: re.sub('python', '', answer.split('```')[0]).strip()

        return 'Model Initizalization Done'
    
    def rag_answer_processor(self, customer_question: str, rag_answer: pd.DataFrame):
        system_prompt = f"""Ты профессиональный агент-продавец, опыт которого в продажах больше 10 лет.
            Ты ведешь диалог с клиентом, которому предлагаешь сотрудничество по продукту "Napoleon IT Отзывы".
            Ты должен обрабатывать любые вопросы потенциального клиента, предоставляя только релевантную и достовернную информацию, используя контекст.
            Не груби и будь дружелюбным собесебником.
            Отвечай только на Русском.

            Обработай запрос клиента и выдай точную информацию:
            Вот чистый ответ на следующий вопрос клиента: {rag_answer}. Дай его в развернутой форме.
            """
        user_prompt = f"Клиент спросил: '{customer_question}'"

        message = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    
        rag_agent = self.model.chat.completions.create(
                    model="default",
                    messages= message,
                    temperature=0,
                    max_tokens=MAX_TOKENS,
                    )
        if rag_agent:
            rag_agent = rag_agent.choices[0].message.content
        
        return rag_agent

        
### Инициализация диалога

    def generate_first_message(self) -> str:
        #started_message_to_customer = self.model.inference_agent(self.messages_init)
        started_message_to_customer = self.model.chat.completions.create(
                        model="default",
                        messages= self.messages_init,
                        temperature=0.5,
                        max_tokens=MAX_TOKENS
                    )
        if started_message_to_customer:
            started_message_to_customer = started_message_to_customer.choices[0].message.content

        self.ASSISTANT.append(started_message_to_customer) # запоминаем диалог со стороны ассистента
        return started_message_to_customer
        print(f'STEP #1:\n\nСООБЩЕНИЕ МОДЕЛИ ДЛЯ ИНИЦИАЛИЗАЦИИ: {started_message_to_customer}', end=';')


    def generate_answer(self, input: str) -> str | None:
        customer = input
        self.USER.append(customer) # запоминаем диалог со стороны клиента

        print(f'STEP #2:\n\nОТВЕТ КЛИЕНТА: {customer}', end=';')

        # проверяем intent
        messages_intent = [
            {'role': 'system', 'content': SYS_PROMPT_FOR_INTENTION},
            {'role': 'user', 'content': customer}
        ]
        #label_intention = self.model.inference_agent(messages_intent)
        label_intention = self.model.chat.completions.create(
                        model="default",
                        messages= messages_intent,
                        temperature=0,
                        max_tokens=MAX_TOKENS,
                    )
        if label_intention:
            label_intention = label_intention.choices[0].message.content

        print(f'ВЫЯВЛЯЕМ НАМЕРЕНИЕ:\n\nНАМЕРЕНИЕ: {label_intention}', end=';')

        # без RAG'a

        if 'нет' in label_intention.lower():
            print('КОНТЕКСТ:\n{CONTEXT_NAPOLEON_IT}', end=';')

            messages = formating_chat_template(system=SYS_PROMPT_CONTINUE_DIALOGUE,
                                                    context=[CONTEXT_NAPOLEON_IT],
                                                    user=self.USER,
                                                    user_question=customer,
                                                    assistant=self.ASSISTANT)
            agent = self.model.chat.completions.create(
                        model="default",
                        messages= messages,
                        temperature=0,
                        max_tokens=MAX_TOKENS,
                    )
            if agent:
                agent = agent.choices[0].message.content
            
            # agent = self.rag_answer_processor(customer, agent)

        elif 'да' in label_intention.lower():


            path_to_data, columns, example = self.PATH_TO_DATASET, self.dataset.columns.to_list(), self.dataset.sample(1)
            is_it_sql = self.classify_rag_or_text2sql(customer)
            if 'да' in is_it_sql.lower():
                try:
                    sql_res = self.generate_text2sql_response(customer)
                    agent = self.query(sql_res, self.engine)
                except:
                    agent = self.generate_rag_response(customer, self.dataset)
            else:
                agent = self.generate_rag_response(customer, self.dataset)

            agent = self.rag_answer_processor(customer, agent)
        self.ASSISTANT.append(agent) # запоминаем диалог со стороны ассистента
        return agent

    def query(self, sql, engine):
        print(f'"SQL QUERY:\n {sql}"')
        return pd.read_sql(sql, con=engine)
    
    def classify_rag_or_text2sql(self, client_query):
        system_prompt = f"""Ты должен будешь определить, можно-ли перевести отправленое тебе предложение в SQL. 
                            Ты должен отвечать на вопросы только 'Да' и 'Нет'.
                        """
        user_prompt = client_query

        message = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]

        result = self.model.chat.completions.create(
                        model="default",
                        messages= message,
                        temperature=0,
                        max_tokens=MAX_TOKENS,
                    )



        return result.choices[0].message.content

    def generate_text2sql_response(self, client_query):
        schema = """CREATE TABLE reviews (
        id INTEGER DEFAULT nextval('reviews_id_seq'::regclass) NOT NULL, 
        company_id INTEGER NOT NULL, 
        product_cat VARCHAR, 
        product_name VARCHAR, 
        review_dt TIMESTAMP, 
        review_text VARCHAR, 
        topic VARCHAR, 
        sentiment  ENUM ('Positive', 'Negative'), 
        marketplace VARCHAR, 
        embedding VECTOR(20), 
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
        deleted_at TIMESTAMP, 
        CONSTRAINT reviews_pkey PRIMARY KEY (id), 
        CONSTRAINT reviews_company_id_fkey FOREIGN KEY(company_id) REFERENCES companies (id)
            )      
        """
        sql_example = "SELECT * FROM reviews WHERE topic == 'Вкус"
        user_prompt = client_query
        system_prompt = f"""
                Generate a Postgresql SQL query to answer the following question:
                `{user_prompt}
                Please wrap your code answer using ```sql:
                ### Database Schema
                This query will run on a database whose schema is represented in this string:
                Don't use joins for this schema and if all columns are required give the (*) notation.
                `{schema}`
                An example of the SQL would be `{sql_example}`
                ### SQL
                Given the database schema, here is the SQL query that answers `{user_prompt}`:
                ```sql
                """

        message = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        
        #result = self.sql_llm.create_chat_completion(messages=message)
        result = self.model.chat.completions.create(
                model="default",
                messages= message,
                temperature=0,
                max_tokens=MAX_TOKENS,
            )
        if result:
            result = result.choices[0].message.content

        #print(f"Ответ модели: {sqlparse.format(result.split('```')[-2], reindent=True).replace('#','').replace('sql ','').replace('sql\n', '')}")
        return sqlparse.format(result.split('```')[-2], reindent=True).replace('#','').replace('sql ','').replace("sql\n", "")

    def generate_rag_response(self, client_query, relevant_reviews):
        review_texts = '\n'.join(relevant_reviews['Review Text'].tolist())
        system_prompt = f"""Ты профессиональный агент-продавец, опыт которого в продажах больше 10 лет.
            Ты ведешь диалог с клиентом, которому предлагаешь сотрудничество по продукту "Napoleon IT Отзывы".
            Ты должен обрабатывать любые вопросы потенциального клиента, предоставляя только релевантную и достовернную информацию, используя контекст.
            Не груби и будь дружелюбным собесебником.
            Отвечай только на Русском.

            Обработай запрос клиента и выдай точную информацию:
            Вот отзывы о товарах клиента: {review_texts}. Ответь на вопрос клиента на опираясь на них.
            """
        user_prompt = f"Клиент спросил: '{client_query}'"

        message = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    
        rag_agent = self.model.chat.completions.create(
                    model="default",
                    messages= message,
                    temperature=0,
                    max_tokens=MAX_TOKENS,
                    )
        if rag_agent:
            rag_agent = rag_agent.choices[0].message.content
        
        return rag_agent