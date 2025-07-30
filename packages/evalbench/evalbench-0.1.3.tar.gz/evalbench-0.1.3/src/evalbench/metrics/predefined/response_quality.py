from typing import List
from evalbench.utils.helper import get_config, handle_output, register_metric
import evalbench.error_handling.validation_helpers as validation
from evalbench.utils.enum import Coherence, Conciseness

@register_metric('conciseness', required_args=['response'], module='response_quality')
@handle_output()
def conciseness_score(response: List[str]) -> List[str]:
    validation.validate_type_list_non_empty(('response', response))

    cfg = get_config()
    results = []
    for resp in response:
        prompt = f'''
        You are a helpful and fair evaluator. Your task is to assess the following response based on conciseness using a numeric rating between 1 and 3. Respond with only the number.

        Scoring Guidelines:
        1 = Too verbose: Repetitive or long  
        2 = Somewhat concise: Communicates key ideas but could be shorter  
        3 = Very concise: Clear and avoids unnecessary detail

        Instructions:
        - Use the full scale (1 to 3) when evaluating.
        - Return only the number—no extra explanation.
        - Assume you're evaluating as a human would: fair, consistent, and strict.

        Examples:
        Query: "What is the capital of France?"  
        Response: "The capital city of France, which is a country in Europe, is the well-known and widely celebrated city of Paris."  
        Rating: 1

        Query: "What is the capital of France?"  
        Response: "The capital of France is Paris."  
        Rating: 3

        Now evaluate:
        Response:
        \'\'\'{resp}\'\'\'

        Rating:
        '''.strip()

        try:
            completion = cfg.groq_client.chat.completions.create(
                model=cfg.llm,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.0
            )
            score = completion.choices[0].message.content
            label = Conciseness.from_score(float(score))
            if label:
                results.append(f"{float(score)} - {label.description}")
        except ValueError as e:
            results.append("Invalid score")

    return results

@register_metric('coherence', required_args=['response'], module='response_quality')
@handle_output()
def coherence_score(response: List[str]) -> List[str]:
    validation.validate_type_list_non_empty(('response', response))
    
    cfg = get_config()
    results = []

    for resp in response:
        prompt = f'''
        You are a helpful and fair evaluator. Your task is to assess the following response based on coherence using a numeric rating between 1 and 3. Respond with only the number.

        Scoring Guidelines:
        1 = Incoherent: Hard to follow or disjointed  
        2 = Somewhat coherent: Mostly makes sense but has minor gaps  
        3 = Very coherent: Logical, easy to follow, and well-connected

        Instructions:
        - Use the full scale (1 to 3) when evaluating.
        - Return only the number—no extra explanation.
        - Assume you're evaluating as a human would: fair, consistent, and strict.

        Examples:
        Query: "How does a bill become a law?"  
        Response: "First, lawmakers. Then the president. Law!"  
        Rating: 1

        Query: "How does a bill become a law?"  
        Response: "A bill is proposed, goes through committees and votes, and if approved, the president signs it into law."  
        Rating: 3

        Now evaluate:
        Response:
        \'\'\'{resp}\'\'\'

        Rating:
        '''.strip()

        try:
            completion = cfg.groq_client.chat.completions.create(
                model=cfg.llm,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.0
            )
            score = completion.choices[0].message.content
            label = Coherence.from_score(float(score))
            if label:
                results.append(f"{float(score)} - {label.description}")
        except ValueError as e:
            results.append("Invalid score")

    return results

@register_metric('factuality', required_args=['response'], module='response_quality')
@handle_output()
def factuality_score(response: List[str]) -> List[float]:
    validation.validate_type_list_non_empty(('response', response))

    cfg = get_config()
    candidate_labels = ['factually correct', 'factually incorrect']
    results = []

    for resp in response:
        hypothesis = f"Is the following response factually correct. Response: ""{resp}"""
        result = cfg.fact_check_model(resp, candidate_labels, hypothesis=hypothesis)
        labels = result["labels"]
        scores = result["scores"]
        results.append(scores[labels.index("factually correct")])

    return results
