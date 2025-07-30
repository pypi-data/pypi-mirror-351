from utils.llm import LLM_RES
#from utils.dataset_c import FeedbackData
import pandas as pd

# Calling the LLM

def summarize():
    feedback_data = pd.read_csv('res_model/feedback.csv')

    # Prompt
    task = f"""
You are an expert HR and technical operations analyst. I will provide you with a dataset of employee feedback collected from an IT company.

Your task is to deeply analyze this feedback and generate a concise executive-level summary report in markdown format that includes:

1. Key Takeaways
Provide a short summary of the overall feedback in 3-5 bullet points. Focus only on the main issues or areas of satisfaction.
Include both positive and negative themes, but prioritize the most important and impactful points.
Limit each point to 1-2 sentences.
Before finalizing each point, take a moment to reflect on why each issue might be present (e.g., systemic problems, temporary issues, resource constraints, etc.)

2. Suggested Improvements
Based on the overall feedback, propose 2-3 high-level, actionable measures that the company could take to address the most pressing issues and enhance overall performance or satisfaction.
Each suggestion should be brief, directly tied to the feedback, and strategic in nature.
Think about short-term vs long-term solutions and consider the feasibility of each suggestion.

3. Output Format
Present your findings as a well-structured markdown file with:
Clear section headings
Bullet points for easy scanning
A concise, direct, and professional tone suitable for leadership review

This is the employee feedback data: {feedback_data}
    """

    # Giving the task to LLM
    response = LLM_RES.llm_res.invoke(task).content

    # Write to output file
    with open("./res_model/result.md", "w") as ofile:
        ofile.write(response)

    # Return the response
    return response

print(summarize())