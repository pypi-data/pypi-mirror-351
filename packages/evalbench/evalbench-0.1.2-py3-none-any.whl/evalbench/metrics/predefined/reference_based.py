from typing import List, Dict
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
from nltk.translate.meteor_score import meteor_score as meteor
from nltk.tokenize import word_tokenize
import bert_score as bert
from sentence_transformers import util
from evalbench.utils.helper import get_config, handle_output, register_metric
import evalbench.error_handling.validation_helpers as validation

@register_metric('bleu', required_args=['reference', 'generated'], module='reference_based')
@handle_output()
def bleu_score(reference: List[str], generated: List[str]) -> List[float]:
    validation.validate_batch_inputs(('reference', reference), ('generated', generated))

    return [
        sentence_bleu([word_tokenize(ref)], word_tokenize(gen))
        for ref, gen in zip(reference, generated)
    ]

@register_metric('rouge', required_args=['reference', 'generated'], module='reference_based')
@handle_output()
def rouge_score(reference: List[str], generated: List[str]) -> List[Dict[str, float]]:
    validation.validate_batch_inputs(('reference', reference), ('generated', generated))

    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    return [
        {k: v.fmeasure for k, v in scorer.score(ref, gen).items()}
        for ref, gen in zip(reference, generated)
    ]

@register_metric('meteor', required_args=['reference', 'generated'], module='reference_based')
@handle_output()
def meteor_score(reference: List[str], generated: List[str]) -> List[float]:
    validation.validate_batch_inputs(('reference', reference), ('generated', generated))

    return [
        meteor([word_tokenize(ref)], word_tokenize(gen))
        for ref, gen in zip(reference, generated)
    ]

@register_metric('semantic_similarity', required_args=['reference', 'generated'], module='reference_based')
@handle_output()
def semantic_similarity_score(reference: List[str], generated: List[str]) -> List[float]:
    validation.validate_batch_inputs(('reference', reference), ('generated', generated))

    cfg = get_config()

    return [
        util.pytorch_cos_sim(
            cfg.sentence_model.encode(ref, convert_to_tensor=True),
            cfg.sentence_model.encode(gen, convert_to_tensor=True)
        ).item()
        for ref, gen in zip(reference, generated)
    ]

@register_metric('bert', required_args=['reference', 'generated'], module='reference_based')
@handle_output()
def bert_score(reference: List[str], generated: List[str]) -> List[Dict[str, float]]:
    validation.validate_batch_inputs(('reference', reference), ('generated', generated))

    precision, recall, f1 = bert.score(generated, reference, lang='en', verbose=False)
    return [
        {
            'precision': precision[i].item(),
            'recall': recall[i].item(),
            'f1': f1[i].item()
        }
        for i in range(len(reference))
    ]