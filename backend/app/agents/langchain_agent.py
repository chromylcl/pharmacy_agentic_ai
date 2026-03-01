from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from app.agents.tools import TOOLS
import os

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

agent = initialize_agent(
    tools=TOOLS,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)


def run_agent(user_query: str):
    """
    Main agent execution
    """
    response = agent.run(user_query)
    return response