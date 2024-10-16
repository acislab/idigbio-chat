import search.functions.generate_rq as llm_gen_rq
import search.functions.update_input as llm_update_input
from nlp.agent import Agent


def generate_rq(agent: Agent, request: dict) -> dict:
    return llm_gen_rq.run(agent, request).model_dump(exclude_none=True, by_alias=True)


def update_input(agent: Agent, request: dict) -> dict:
    return llm_update_input.run(agent, request).model_dump(exclude_none=True, by_alias=True)
