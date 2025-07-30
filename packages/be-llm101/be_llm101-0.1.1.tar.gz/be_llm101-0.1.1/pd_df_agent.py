from utils.llm import LLM
from utils.dataset_c import News_dataset

# from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent


df_agent = create_pandas_dataframe_agent(
    LLM.llm,
    News_dataset.df,
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,  # The agent’s behavior type
    # agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # The agent’s behavior type (denne klarte ikke oppgaven)
    allow_dangerous_code=True,  # Set this to False in production for security
)

"""
response = df_agent.invoke('How many rows are there?')
print(response)
"""

r = df_agent.invoke(
    "What are the 4 main topics of the news articles? Do a thourough analysis of at least the first 50 descriptions."
)
print(r)


# print(News_dataset.df.shape)
