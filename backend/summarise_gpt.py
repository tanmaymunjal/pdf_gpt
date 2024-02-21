from openai import OpenAI
from configuration import global_config

client = OpenAI(api_key=global_config["OpenAI"]["API_KEY"])


def call_open_api(prompt: str, model: str, prompt_length: int):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=prompt_length,  # summary can not be longer than original
    )
    return response.choices[0].message.content.strip()


def format_prompt(prompt: str):
    addition = "Can you please summarise the following texts as simply and concisely without losing any information as possible\n"
    return addition + prompt


def get_subset(text, i: int, j: int):
    if i < len(text) - 1:
        return text[i:j]
    return ""


def summarise_doc(text: str, page_size: int = 1000):
    generated_summaries = []
    i = 0
    j = page_size
    while get_subset(text, i, j) != "":
        generated_summaries.append(
            call_open_api(
                format_prompt(text[i:j]),
                model=global_config["OpenAI"]["MODEL"],
                prompt_length=j - i + 1,
            )
        )
        i += page_size
        j += page_size
    return "\n".join(generated_summaries)
