from typing import List
from evalbench.utils.helper import  get_config, handle_output, register_metric
import evalbench.error_handling.validation_helpers as validation
from evalbench.utils.enum import Groundedness

@register_metric('faithfulness', required_args=['context', 'generated'], module='contextual_generation')
@handle_output()
def faithfulness_score(context: List[List[str]], generated: List[str]) -> List[float]:
    validation.validate_batch_inputs(('context', context), ('generated', generated))

    cfg = get_config()
    candidate_labels = ['faithful to context', 'unfaithful to context']
    results = []

    for ctx, gen in zip(context, generated):
        result = cfg.fact_check_model(
            sequences=" ".join(ctx),
            candidate_labels=candidate_labels,
            hypothesis=gen
        )
        labels = result["labels"]
        scores = result["scores"]
        results.append(scores[labels.index("faithful to context")])

    return results

@register_metric('hallucination', required_args=['context', 'generated'], module='contextual_generation')
@handle_output()
def hallucination_score(context: List[List[str]], generated: List[str]) -> List[float]:
    validation.validate_batch_inputs(('context', context), ('generated', generated))

    cfg = get_config()
    candidate_labels = ["entailment", "neutral", "contradiction"]
    results = []

    for ctx, gen in zip(context, generated):
        result = cfg.fact_check_model(
            sequences=" ".join(ctx),
            candidate_labels=candidate_labels,
            hypothesis=gen
        )
        labels = result["labels"]
        scores = result["scores"]
        # Lower entailment score = higher hallucination likelihood
        results.append(1 - scores[labels.index("entailment")])

    return results

@register_metric('groundedness', required_args=['context', 'generated'], module='contextual_generation')
@handle_output()
def groundedness_score(context: List[List[str]], generated: List[str]) -> List[str]:
    validation.validate_batch_inputs(('context', context), ('generated', generated))

    cfg = get_config()
    results = []

    for ctx, gen in zip(context, generated):
        prompt = f'''
        You are a helpful evaluator. Given a retrieved context and a generated response, your task is to rate how well the response is grounded in the context. Use the following 1–3 scale:

        Scoring Guidelines:
        1 = Not grounded: unrelated or contradicts context  
        2 = Partially grounded: uses some context, but incomplete
        3 = Fully grounded: completely supported by context

        Instructions:
        - Base your rating only on how well the response aligns with the provided context.
        - Do not include explanations — respond with a single number (1, 2, or 3).
        - Use the full scale when appropriate.

        Examples:
        Context: "Apple is headquartered in Cupertino, California. Its CEO is Tim Cook."  
        Response: "Apple was founded in 1976 and is based in California."  
        Rating: 2

        Context: "Apple is headquartered in Cupertino, California. Its CEO is Tim Cook."  
        Response: "Apple's CEO is Tim Cook and its headquarters are in Cupertino."  
        Rating: 3

        Context: "Apple is headquartered in Cupertino, California. Its CEO is Tim Cook."  
        Response: "Microsoft is based in Redmond and led by Satya Nadella."  
        Rating: 1

        Now evaluate:
        Context:
        \'\'\'{ctx}\'\'\'

        Response:
        \'\'\'{gen}\'\'\'

        Rating:
        '''.strip()

        try:
            completion = cfg.groq_client.chat.completions.create(
                model=cfg.llm,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.0
            )
            score = completion.choices[0].message.content
            label = Groundedness.from_score(float(score))
            if label:
                results.append(f"{float(score)} - {label.description}")
        except ValueError as e:
            results.append("Invalid score")

    return results

