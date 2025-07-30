from utils.llm import LLM
from utils.categorize_1 import Categorize_bound, Categorize_think
from utils.dataset_c import FeedbackData

"""
def open_categories() -> None:
    structured_llm = LLM.llm.with_structured_output(Categorize)
    for i in range(0, 10):
        response = structured_llm.invoke(
            f"Categorize this news article: '{News_dataset.descriptions[i]}'"
        )

        print(response, News_dataset.descriptions[i])


def bound_categories() -> None:
    structured_llm = LLM.llm.with_structured_output(Categorize_bound)
    task = "Categorize the folowing news article into the best fitting category. Allowed categories:\n
            1 - World\n
            2 - Sports\n
            3 - Business\n
                4 - Sci/Tech\n\n
                "
    for i in range(0, 10):
        response = structured_llm.invoke(
            task + f"Article:\n'{News_dataset.descriptions[i]}'"
        )
        print(response, f"label = {News_dataset.labels[i]}")


def loop_structured(task: str, structure_type, num_reps: int) -> None:
    structured_llm = LLM.llm.with_structured_output(structure_type)

    for i in range(num_reps):
        response = structured_llm.invoke(task + f"\n'{News_dataset.descriptions[i]}'")
        print(response)


loop_structured(
    task="Categorise this news article: ", structure_type=Categorize, num_reps=10
)
"""


def loop_structured(task: str, structure_type, num_reps: int) -> None:
    structured_llm = LLM.llm_res.with_structured_output(structure_type)

    for i in range(num_reps):
        response = structured_llm.invoke(task + f"\n'{FeedbackData.df['Feedback'][i]}'")
        print(response)


t = "Categorize the following feedback from an IT-questionnaire:"
loop_structured(t, Categorize_think, 10)
