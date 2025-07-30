from utils.llm import LLM_RES
#from utils.dataset_c import FeedbackData
import pandas as pd

# Calling the LLM


def categorize(n=50):
    data = pd.read_csv('prompting/forslag_1.csv')

    data_subset = data.drop(columns=['ID','Category'])

    # Prompt
    task = f"""
You are a reasoning-based classification expert working with employee feedback from an IT company.

Your task is to analyze the content of each feedback entry and assign it to one of the following categories based on meaning, tone, and implied topic:

- **Training**: Mentions learning, onboarding, skill development, or lack of knowledge/training.
- **Network**: Refers to connectivity issues, Wi-Fi, VPN, latency, bandwidth, outages, or anything related to network infrastructure or access.
- **IT-support**: Involves direct interaction with IT staff, helpdesk, ticket systems, problem resolution, or service experiences.
- **Other**: Use this only when the feedback does not clearly belong in the above categories, is off-topic, vague, or nonsensical (e.g., "I do not know", "Help", "Potato internet").

Do not rely on keywords alone. **Reflect on the intent, context, and sentiment** behind the words. Consider what the person is trying to express. Some feedback will be ambiguous or deceptive — stay thoughtful and deliberate in your categorization.

Here is a sample of feedback data (one row per person):

{data_subset}

Return your answer in CSV format with two columns:
`category`, `feedback`
Keep the feedback text unchanged, and add your inferred category next to each entry.
    """

    # Giving the task to LLM
    response = LLM_RES.llm_res.invoke(task).content

    # Return the response
    return response


print(categorize())
