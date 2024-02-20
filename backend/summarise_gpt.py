from openai import OpenAI
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
# Set up your API key
client = OpenAI(
  api_key=config["OpenAI"]["API_KEY"] 
)

def call_open_api(prompt: str, prompt_length: int):
    response = client.completions.create(
        model="gpt-3.5-turbo-1106",
        prompt=prompt,
        max_tokens=prompt_length,  # summary can not be longer than original
    )
    return response.choices[0].text.strip()


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
            call_open_api(format_prompt(text[i:j]), prompt_length=i + j - 1)
        )
        i += page_size
        j += page_size
    return "\n".join(generated_summaries)
