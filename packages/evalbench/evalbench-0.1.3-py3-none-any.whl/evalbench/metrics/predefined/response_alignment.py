from typing import List
from evalbench.utils.helper import get_config, handle_output, register_metric
import evalbench.error_handling.validation_helpers as validation
from evalbench.utils.enum import Relevance, AnswerHelpfulness

@register_metric('answer_relevance', required_args=['query', 'response'], module='response_alignment')
@handle_output()
def answer_relevance_score(query: List[str], response: List[str]) -> List[str]:
    validation.validate_batch_inputs(('response', response), ('query', query))

    cfg = get_config()
    results = []

    for q, r in zip(query, response):
        prompt = f'''
        You are an expert evaluator. Rate how relevant a given response is to a specific question, on a scale from 1 to 5.

        Scoring Guidelines:
        1 = Completely irrelevant  
        2 = Weakly related, mostly off-topic  
        3 = Partially relevant, some connection  
        4 = Mostly relevant, minor issues  
        5 = Highly relevant

         Instructions:
        - Use the full 1–5 scale.
        - ONLY return the number. Do not include explanations or comments.

        Examples:

        Question: 'What is the capital of France?'  
        Response: 'Bananas are a good source of potassium.'  
        Rating: 1

        Question: 'What is the capital of France?'  
        Response: 'France is a country in Europe.'  
        Rating: 3

        Question: 'What is the capital of France?'  
        Response: 'The capital of France is Paris.'  
        Rating:** 5

        Now evaluate this:
        Question: {q}  
        Response: {r}  

        Relevance Score:
        '''.strip()

        try:
            completion = cfg.groq_client.chat.completions.create(
                model=cfg.llm,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.0,
            )
            score = completion.choices[0].message.content.strip()
            label = Relevance.from_score(float(score))
            if label:
                results.append(f"{float(score)} - {label.description}")
        except ValueError as e:
            results.append("Invalid score")

    return results

@register_metric('answer_helpfulness', required_args=['query', 'response'], module='response_alignment')
@handle_output()
def helpfulness_score(query: List[str], response: List[str]) -> List[str]:
    validation.validate_batch_inputs(('response', response), ('query', query))

    cfg = get_config()
    results = []

    for q, r in zip(query, response):
        prompt = f'''
            You are a helpful and fair evaluator. Your task is to assess the following response based on answer helpfulness using a numeric rating between 1 and 5. Respond with only the number.

            Scoring Guidelines:
            1 = Unhelpful or irrelevant
            2 = Slightly helpful, mostly vague
            3 = Somewhat helpful, partially answers
            4 = Mostly helpful, minor issues
            5 = Very helpful, clear and complete
            
             Instructions:
            - Use the full scale (1 to 5) when evaluating.
            - Do not include any explanation—just return a single number.
            - Assume you're evaluating as a human would: fair, consistent, and strict.

            Examples:
            Query: 'How can I improve my public speaking skills?'
            Response: 'Maybe just try not to be nervous or something.'
            Rating: 2

            Query: 'How can I improve my public speaking skills?'
            Response: 'Practice regularly, record yourself to evaluate progress, and consider joining a local speaking group like Toastmasters.'
            Rating: 5

            Now rate this:
            Query:
            \'\'\"{q}\"\"\"

            Response:
            \"\"\"{r}\"\"\"

            Rating:
            '''.strip()

        try:
            completion = cfg.groq_client.chat.completions.create(
                model=cfg.llm,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.0,
            )
            score = completion.choices[0].message.content.strip()
            label = AnswerHelpfulness.from_score(float(score))
            if label:
                results.append(f"{float(score)} - {label.description}")
        except ValueError as e:
            results.append("Invalid score")

    return results