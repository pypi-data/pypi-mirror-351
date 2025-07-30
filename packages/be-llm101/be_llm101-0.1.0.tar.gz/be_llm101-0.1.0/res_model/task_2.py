from utils.llm import LLM_RES
#from utils.dataset_c import FeedbackData
import pandas as pd

# Calling the LLM

def summarize():
    feedback_data = pd.read_csv('res_model/feedback.csv')

    # Prompt
    task = f"""
You are a domain expert in internal IT operations and organizational analysis. You will be provided with a dataset containing qualitative feedback from employees in an IT company. 
Each row in the dataset represents a feedback entry and is associated with a specific category.

For each category, carefully:
1. Read and interpret the feedback entries assigned to that category.
2. Identify core themes, recurring patterns, and contrasting opinions within that category.
3. Evaluate the feedback logically: What are the likely underlying causes of recurring issues or praises? Are there signs of systemic problems, isolated incidents, or misaligned expectations?
4. Summarize each category in 3 to 6 bullet points, highlighting key sentiments (positive and negative), representative concerns or compliments, and any significant outliers

Present your findings in a clean, professional way with one section per category. 

This is the employee feedback data: {feedback_data}
    """

    # Giving the task to LLM
    response = LLM_RES.llm_res.invoke(task).content

    # Write to output file
    with open("./res_model/result_task_2.md", "w") as ofile:
        ofile.write(response)

    # Return the response
    return response

print(summarize())