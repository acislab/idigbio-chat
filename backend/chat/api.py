from chat.plan_response import ask_llm_to_call_a_function
from nlp.agent import Agent


def chat(agent: Agent, conversation: []) -> dict:
    res = ask_llm_to_call_a_function(agent, conversation)
    
    return res.model_dump(exclude_none=True)
