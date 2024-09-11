import os
import re
import pandas as pd
from typing import Callable

import torch
from llama_cpp import Llama
from huggingface_hub import hf_hub_download
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from langchain_experimental.utilities.python import PythonREPL

os.environ['HF_HUB_OFFLINE'] = '0'
os.environ['HUGGINGFACE_HUB_CACHE'] = './hugging_face_hub'



class SalesAgent:

    def __init__(self, 
                 model_id, 
                 repo_gguf_id, 
                 filename_gguf, 
                 load_gguf_config: dict) -> None:

        self.model_id = model_id
        self.repo_gguf_id = repo_gguf_id
        self.filename_gguf = filename_gguf
        self.load_gguf_config = load_gguf_config

        self.model = self.load_gguf_model()


    """
    Функция загрузки модели gguf-формата.

    Args:
        model_id (str): checkpoint основной модели (используется для загрузки токенизатора)
        repo_id_gguf (str): HF-репозиторий gguf-модели.
        filename_gguf (str): конкретный gguf-файл из "repo_id_gguf" для загрузки модели.

    Return:
        model: AutoModelForCausalLM
    """
    def load_gguf_model(self) -> Llama:
        model_path = hf_hub_download(repo_id=self.repo_gguf_id, filename=self.filename_gguf)

        model = Llama(
            model_path,
            **self.load_gguf_config
        )
        return model


    def inference_agent(self, messages: list[dict]) -> str:
        response = self.model.create_chat_completion(messages)
        return response['choices'][0]['message']['content']
    

    def formating_chat_template(self, 
                                system: Callable,
                                context: list[str],
                                user: list[str],
                                assistant: list[str]) -> list[dict]:
        messages = [
                {'role': 'system', 'content': system(*context)}
        ]

        for assistant_replica, user_replica in zip(assistant, user):
            
            messages.append(assistant_replica)
            messages.append(user_replica)

        return messages
    


# if __name__ == "__main__":
#     model_id = 'meta-llama/Meta-Llama-3.1-8B-Instruct'
#     #repo_gguf_id = 'QuantFactory/Meta-Llama-3.1-8B-GGUF'
#     repo_gguf_id = 'SanctumAI/Meta-Llama-3.1-8B-Instruct-GGUF'
#     #filename_gguf = 'Meta-Llama-3.1-8B.Q4_0.gguf'
#     filename_gguf = 'meta-llama-3.1-8b-instruct.Q4_0.gguf'

#     LOAD_GGUF_CONFIG = {
#         'n_gpu_layers': 0, # not GPUs
#         'n_threads': 32, # for CPUs
#         'n_ctx': 4096  # length context ...
#     }

#     model = SalesAgent(model_id,
#                     repo_gguf_id,
#                     filename_gguf,
#                     LOAD_GGUF_CONFIG)