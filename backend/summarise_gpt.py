from openai import OpenAI
from backend.configuration import global_config


class GPTSummarisation:
    """
    Class for performing text summarization using OpenAI's GPT model.

    This class provides methods to summarize text documents using the OpenAI GPT model.

    Attributes:
        api_key (str): The API key for accessing OpenAI services.
        model (str): The GPT model to use for summarization.
        client: The OpenAI client instance.
    """

    def __init__(
        self,
        api_key=global_config["OpenAI"]["API_KEY"],
        model=global_config["OpenAI"]["MODEL"],
    ):
        """
        Initialize the GPTSummarisation instance.

        Args:
            api_key (str): The API key for accessing OpenAI services.
            model (str): The GPT model to use for summarization.
        """
        self.client = client = OpenAI(api_key=global_config["OpenAI"]["API_KEY"])
        self.model = model

    def call_open_api(self, prompt: str, prompt_length: int) -> str:
        """
        Call the OpenAI API to generate a summary based on the provided prompt.

        Args:
            prompt (str): The prompt to be used for generating the summary.
            prompt_length (int): The length of the prompt.

        Returns:
            str: The generated summary.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=prompt_length,  # summary can not be longer than original
        )
        return response.choices[0].message.content.strip()

    @staticmethod
    def get_subset(text, i: int, j: int):
        """
        Get a subset of the text based on the specified indices.

        Args:
            text (str): The input text.
            i (int): The start index.
            j (int): The end index.

        Returns:
            str: The subset of the text.

        Note:
            - Returns empty string if start index is more than length of text
        """
        if i < len(text) - 1:
            return text[i:j]
        return ""

    @staticmethod
    def format_prompt(prompt: str):
        """
        Format the prompt for summarization.

        Args:
            prompt (str): The prompt to be formatted.

        Returns:
            str: The formatted prompt.
        """
        addition = "Can you please summarise the following texts as simply and concisely without losing any information as possible\n"
        return addition + prompt

    def summarise_doc(self, text: str, page_size: int = 1000):
        """
        Summarize a document using the OpenAI GPT model.

        Args:
            text (str): The document text to be summarized.
            page_size (int): The size of each page for summarization (default is 1000).

        Returns:
            str: The summarized document.
        """
        generated_summaries = []
        i = 0
        j = page_size
        while get_subset(text, i, j) != "":
            generated_summaries.append(
                self.call_open_api(
                    prompt=GPTSummarisation.format_prompt(text[i:j]),
                    prompt_length=j - i + 1,
                )
            )
            i += page_size
            j += page_size
        return "\n".join(generated_summaries)
