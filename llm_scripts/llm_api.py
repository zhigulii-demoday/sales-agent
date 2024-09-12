from openai import Client, OpenAI
from Flask import Flask

client = Client(
    base_url="http://127.0.0.1:30001/v1/completions", 
    api_key="EMPTY"
)

# Chat completion
response = client.chat.completions.create(
    model="default",
    messages=[
        {"role": "system", "content": "Ты дружелюбный AI-ассистент. Отвечай на вопросы пользователя. Используй только русский язык."},
        {"role": "user", "content": "Выведи стихотворение о грибах."},
    ],
    temperature=0.,
    max_tokens=4096,
)

print(response)
