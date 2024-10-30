import search.functions.generate_rq as llm_gen_rq
import search.functions.update_input as llm_update_input
from nlp.ai import AI


def generate_rq(ai: AI, request: dict) -> dict:
    return llm_gen_rq.run(ai, request).model_dump(exclude_none=True, by_alias=True)


def update_input(ai: AI, request: dict) -> dict:
    return llm_update_input.run(ai, request).model_dump(exclude_none=True, by_alias=True)
