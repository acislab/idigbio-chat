from chat.agent import Agent
import search.functions.generate_rq as llm_gen_rq
import search.functions.update_input as llm_update_input


def generate_rq(agent: Agent, data: dict):
    return llm_gen_rq.run(agent, data)


def update_input(agent: Agent, data: dict):
    return llm_update_input.run(agent, data)
