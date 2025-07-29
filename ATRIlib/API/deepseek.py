from ATRIlib.Config.config import deepseek_key,translate_prompt
from openai import OpenAI

try:
    client = OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com")
except:
    pass

def translate(mycontent):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful translator. Translate the user's markdown text into Chinese. Keep markdown style."},
            {"role": "user", "content": translate_prompt+mycontent},
        ],
        stream=False
    )

    return response.choices[0].message.content
