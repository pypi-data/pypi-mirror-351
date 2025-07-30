from utils.llm import LLM_RES
import pandas as pd

def categorize(n=50):
    data = pd.read_csv('./prompting/output_df_filtered.csv')
    sample_data = data.sample(n=min(len(data), 10)).to_csv(index=False)

    task = f"""
You're a dataset generator. Use the style and structure of this sample data (from a real IT company employee feedback dataset) to create a new dataset with {n} rows.

- Each row should represent feedback from one individual.
- 25 rows should clearly fit under these categories: 'Training', 'Network', or 'IT-support'.
  - Assign 10 feedbacks to one category, 7 to another, and 8 to the last.
- 25 rows should clearly fit under these categories: 'Security', 'Business needs', or 'Quality of tools'.
  - Assign 10 feedbacks to one category, 7 to another, and 8 to the last.
- Maintain a realistic tone and variation, simulating genuine employee feedback.

Sample data:
{sample_data}

Return the final dataset in CSV format (with header).
"""
  
    response = LLM_RES.llm_res.invoke(task).content

    with open("./prompting/forslag_1.csv", "w") as ofile:
        ofile.write(response)

    return response 

print(categorize())


