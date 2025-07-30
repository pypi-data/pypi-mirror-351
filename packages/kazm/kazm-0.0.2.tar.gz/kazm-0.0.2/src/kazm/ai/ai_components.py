import os
from openai import OpenAI
from kazm import settings


# TODO add a history stuff for session speaking and overall with npc and stuff
ai_model_name = settings.get("AI", "ai_model_name")

api_key = settings.get("AI", "API_KEY")
if settings.get("AI", "API_KEY_TYPE") == "env":
    api_key = os.environ.get(api_key)


custom_ai_op = settings.get("AI", "custom_ai")
if custom_ai_op == "false":
    client = OpenAI(api_key=api_key)
else:
    client = OpenAI(
    base_url=custom_ai_op,
    api_key=api_key)


def simple_ai_chat(msg: str, system_msg: str|None = None) -> str: 
    messages=[
    {
        "role": "user",
        "content": msg,
    }]

    if system_msg:
        messages.insert(0, {"role": "system", "content": system_msg})
    
    completion = client.chat.completions.create(
    model=ai_model_name, messages=messages)

    return completion.choices[0].message.content


if __name__ == '__main__':
    print(simple_ai_chat(system_msg="How are you too smart?", msg="piracy?"))
    