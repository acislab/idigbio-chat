from chat.agent import Agent
import search.functions.generate_rq as rq


def generate_rq(agent: Agent, data: dict):
    return rq.run(agent, data)


__all__ = ["generate_rq"]
