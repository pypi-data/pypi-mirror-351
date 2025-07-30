from langchain_openai import AzureChatOpenAI
from dotenv import find_dotenv, load_dotenv
import os


# Get environment variables
load_dotenv(find_dotenv(), override=True)


class LLM:
    """
    Class containing the language model.
    """

    llm = AzureChatOpenAI(
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_GPT_4O_MINI"],
        model=os.environ.get("OPENAI_MODEL_GPT_4O-MINI", default="gpt-4o-mini"),
        temperature=0,
        # reasoning_effort: str,
        # Constrains effort on reasoning for reasoning models.
        # Reasoning models only, like OpenAI o1 and o3-mini.
        # Currently supported values are low, medium, and high.
        # Reducing reasoning effort can result in faster responses and fewer tokens used on reasoning in a response.
    )

class LLM_RES:
    """
    Class containing the reasoning model.
    """

    llm_res = AzureChatOpenAI(
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_GPT_3O_MINI"],
        model=os.environ.get("OPENAI_MODEL_GPT_3O-MINI", default="o3-mini"),
        reasoning_effort="high",
        # temperature=0,
        # reasoning_effort: str,
        # Constrains effort on reasoning for reasoning models.
        # Reasoning models only, like OpenAI o1 and o3-mini.
        # Currently supported values are low, medium, and high.
        # Reducing reasoning effort can result in faster responses and fewer tokens used on reasoning in a response.
    )


# LLM = Llm()

# print(Llm.llm.invoke("whats up?").content)
