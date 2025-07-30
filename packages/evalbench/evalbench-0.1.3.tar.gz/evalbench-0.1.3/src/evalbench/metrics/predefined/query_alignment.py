from typing import List
from evalbench.utils.helper import get_config, handle_output, register_metric
import evalbench.error_handling.validation_helpers as validation
from evalbench.utils.enum import Relevance

@register_metric('context_relevance', required_args=['query', 'context'], module='query_alignment')
@handle_output()
def context_relevance_score(query: List[str], context: List[str]) -> List[str]:
    validation.validate_batch_inputs(('context', context), ('query', query))

    cfg = get_config()
    results = []

    for q, ctx in zip(query, context):
        prompt = f'''
        You are a search relevance evaluator. Your task is to score how well a retrieved context matches the user query.

        Scoring Guidelines:
        1 = Completely irrelevant  
        2 = Weakly related, mostly off-topic  
        3 = Partially relevant, some connection  
        4 = Mostly relevant, minor issues  
        5 = Highly relevant 

        Instructions:
        - ONLY output the number 1–5. No extra text.
        - Use the full range when appropriate.

        Examples:
        Query: 'What are the symptoms of heat stroke?'  
        Context: 'The Eiffel Tower is located in Paris.'  
        Score: 1

        Query: 'What are the symptoms of heat stroke?'  
        Context: 'Heat-related illnesses include dehydration, fatigue, and muscle cramps.'  
        Score: 3

        Query: 'What are the symptoms of heat stroke?'  
        Context: 'Common symptoms of heat stroke include high body temperature, confusion, rapid pulse, and nausea.'  
        Score: 5

        Now rate the following:
        Query: {q}  
        Retrieved Context: {ctx}  

        Relevance Score:
        '''.strip()

        try:
            response = cfg.groq_client.chat.completions.create(
                model=cfg.llm,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.0,
            )
            score = response.choices[0].message.content.strip()
            label = Relevance.from_score(float(score))
            if label:
                results.append(f"{float(score)} - {label.description}")
        except ValueError as e:
            results.append("Invalid score")

    return results