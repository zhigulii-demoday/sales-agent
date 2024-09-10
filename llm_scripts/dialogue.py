
from llm_scripts.prompts import (CONTEXT_NAPOLEON_IT,
                        SALES_SCRIPT, 
                        SYS_PROMPT_INIT_DIALOGUE,
                        USER_INIT_PROMPT,
                        SYS_PROMPT_CONTINUE_DIALOGUE,
                        SYS_PROMPT_FOR_INTENTION,
                        SYS_PROMPT_TEXT_2_PANDAS
                        )

from llm_scripts.model_llm import SalesAgent

import os
import re
import pandas as pd
from typing import Callable

import torch
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from langchain_experimental.utilities.python import PythonREPL


class DialogueModel:

    def init_pandas(self):
        self.PATH_TO_DATASET = 'cleaned_coffee.csv'

        delimeter = '\n\n' + ('='* 100) + '\n\n'
        self.dataset = pd.read_csv(self.PATH_TO_DATASET)


    def init_model(self):

        self.init_pandas()

        model_id = 'meta-llama/Meta-Llama-3.1-8B-Instruct'
        repo_gguf_id = 'QuantFactory/Meta-Llama-3.1-8B-GGUF'
        filename_gguf = 'Meta-Llama-3.1-8B.Q4_0.gguf'


        LOAD_GGUF_CONFIG = {
            'n_gpu_layers': 0, # not GPUs
            'n_threads': 32, # for CPUs
            'n_ctx': 4096  # length context ...
        }

        self.model = SalesAgent(model_id,
                        repo_gguf_id,
                        filename_gguf,
                        LOAD_GGUF_CONFIG)

        self.REPL = PythonREPL()

        
        self.messages_init = [
                {'role': 'system', 'content': SYS_PROMPT_INIT_DIALOGUE(CONTEXT_NAPOLEON_IT, SALES_SCRIPT)},
                {'role': 'user', 'content': USER_INIT_PROMPT}
            ]

        self.USER = []
        self.ASSISTANT = []

        self.cleaning_t2pandas = lambda answer: re.sub('python', '', answer.split('```')[0]).strip()

        return 'Model Initizalization Done'

        


### Инициализация диалога

    def generate_first_message(self) -> str:
        started_message_to_customer = self.model.inference_agent(self.messages_init)
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
        label_intention = self.model.inference_agent(messages_intent)

        print(f'ВЫЯВЛЯЕМ НАМЕРЕНИЕ:\n\nНАМЕРЕНИЕ: {label_intention}', end=';')

        # без RAG'a

        if 'да' in label_intention:
            print('КОНТЕКСТ:\n{CONTEXT_NAPOLEON_IT}', end=';')

            messages = self.model.formating_chat_template(system=SYS_PROMPT_CONTINUE_DIALOGUE,
                                                    context=CONTEXT_NAPOLEON_IT,
                                                    user=self.USER,
                                                    assistant=self.ASSISTANT)
            agent = self.model.inference_agent(messages)
        elif 'нет' in label_intention:
            path_to_data, columns, example = self.PATH_TO_DATASET, self.dataset.columns.to_list(), self.dataset.sample(1)

            messages = self.model.formating_chat_template(system=SYS_PROMPT_TEXT_2_PANDAS,
                                                    context=[path_to_data, columns, example],
                                                    user=self.USER,
                                                    assistant=self.ASSISTANT)
            rag_agent = self.model.inference_agent(messages)

            print(f'TEXT_2_PANDAS ЗАПРОС МОДЕЛИ:\n{rag_agent}', end=';')

            CONTEXT_RAG = self.REPL.run(rag_agent)
            CONTEXT_RAG = self.cleaning_t2pandas(CONTEXT_RAG)

            print(f'ПОЛУЧЕННЫЙ КОНТЕКСТ С RAGA:\n{CONTEXT_RAG}', end=';')
            
            messages = self.model.formating_chat_template(system=SYS_PROMPT_CONTINUE_DIALOGUE,
                                                    context=[CONTEXT_RAG],
                                                    user=customer,
                                                    assistant=self.ASSISTANT)
            agent = self.model.inference_agent(messages)

            print(f'ОТВЕТ МОДЕЛИ ПО RAGy:\n{agent}', end=';')



        self.ASSISTANT.append(agent) # запоминаем диалог со стороны ассистента
        return agent