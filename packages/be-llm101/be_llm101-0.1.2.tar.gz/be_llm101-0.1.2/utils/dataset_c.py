import pandas as pd


class FeedbackData:
    """
    Class containing partitions of the ag-news-classification-dataset.

    This file consists of 7600 testing samples of news articles that contain 3 columns.
    The first column is Class Id, the second column is Title and the third column is Description.
    The class ids are numbered 1-4 where 1 represents World, 2 represents Sports,
    3 represents Business and 4 represents Sci/Tech.
    """

    # Load a DataFrame with a specific version of a CSV
    file_path = "./utils/shuffled_df_LLM101_filtered.csv"
    df = pd.read_csv(file_path)


# print(FeedbackData.df["Feedback"][0])
