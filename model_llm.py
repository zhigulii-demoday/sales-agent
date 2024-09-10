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


    def load_gguf_model(self) -> Llama:

        model_path = hf_hub_download(repo_id=self.repo_gguf_id, filename=self.filename_gguf)
        print('Llama init...')
        model = Llama(
            model_path,
            **self.load_gguf_config
        )
        return model
    

    def inference_agent(self, messages: list[dict]) -> str:
        response = self.model.create_chat_completion(messages)

        return response['choices'][0]['content']
    

    def formating_chat_template(self, 
                                system: Callable,
                                context: list[str],
                                user: list[str],
                                assistan: list[str]) -> list[dict]:
        messages = [
                {'role': 'system', 'content': system(*context)}
        ]

        for assistant_replica, user_replica in zip(assistan, user):
            
            messages.append(assistant_replica)
            messages.append(user_replica)

        return messages
    


if __name__ == "__main__":
    model_id = 'microsoft/Phi-3.5-mini-instruct'
    repo_gguf_id = 'QuantFactory/Phi-3.5-mini-instruct-GGUF'
    filename_gguf = 'Phi-3.5-mini-instruct.Q8_0.gguf'

    LOAD_GGUF_CONFIG = {
        'n_gpu_layers': 0, # not GPUs
        'n_threads': 32, # for CPUs
        'n_ctx': 4096  # length context ...
    }

    model = SalesAgent(model_id,
                    repo_gguf_id,
                    filename_gguf,
                    LOAD_GGUF_CONFIG)