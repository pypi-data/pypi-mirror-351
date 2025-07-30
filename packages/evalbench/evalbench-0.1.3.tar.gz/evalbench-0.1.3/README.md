# EvalBench 🧪📊  
**Lightweight, extensible, open-source evaluation framework for LLM applications covering approximately 18 metrics and allows adding of user-defined custom metrics**

---

## 🔍 About EvalBench

`EvalBench` is a plug-and-play Python package for evaluating outputs of large language models (LLMs) across a variety of metrics.

#### Supports:
- Predefined metrics (faithfulness, coherence, BLEU, hallucination, etc.)
- Easy registration of custom user-defined metrics
- Evaluation across different modalities/ use-cases
- Flexible input/output options (print/ save) with support for list-based batching

#### Modules and Metric Categories:

| Module               | Metrics                                          | Required Arguments                         | Argument Types                          |
|----------------------|-------------------------------------------------|-------------------------------------------|----------------------------------------|
| response_quality     | conciseness_score, coherence_score, factuality_score   | response                                  | `List[str]`                            |
| reference_based      | bleu_score, rouge_score, meteor_score, semantic_similarity_score, bert_score  | reference, generated      | `List[str]`, `List[str]`        |
| contextual_generation | faithfulness_score, hallucination_score, groundedness_score       | context, generated                        | `List[List[str]]`, `List[str]` |
| retrieval          | recall_at_k, precision_at_k, ndcg_at_k, mrr_score             | relevant_docs, retrieved_docs, k         | `List[List[str]]`, `List[List[str]]`, `int`       |
| query_alignment       | context_relevance_score                                | query, context                           | `List[str]`, `List[str]`                    |
| response_alignment    | answer_relevance_score, helpfulness_score            | query, response                          | `List[str]`, `List[str]`                    |
| user defined module               | User-registered custom metrics                   | Varies (user-defined)                    | Varies (user-defined)                  |

#### EvalBench is especially useful when you're:
- Building small-scale LLM pipelines
- Comparing different prompts or model outputs
- Rapidly iterating on metrics

---

## 🚀 Usage

### Installation

```bash
pip install evalbench
```
### Initialize Configuration

```python
import evalbench as eb

# Create and apply evaluation configuration
config = eb.EvalConfig(groq_api_key="", output_mode="print")
eb.set_config(config)
```

### Usage Examples
#### 1. Evaluate a single predefined metric

```python
response = ["A binary search algorithm reduces the time complexity to O(log n)."]
context = [["Binary search works on sorted arrays and is faster than linear search."]]

eb.faithfulness_score(context=context, generated=response)

# metrics can also be printed as a list
result = eb.faithfulness_score(context=context, generated=response)
print(result) # [0.44]
```

#### 2. Evaluate all metrics in a predefined module

```python
eb.evaluate_module(
    module=["contextual_generation"],
    context=context,
    generated=response,
)
```

#### 3. Register custom metrics
Create a custom metric in a file (eg. custom.py):

```python
from evalbench import register_metric, handle_output

@register_metric(name="len_metric", module="custom", required_args=["response", "reference"])
@handle_output()
def my_custom_metric(response, reference):
    return [len(response) / len(reference)]
```

#### 4. Load custom metric file and evaluate

```python
eb.load_custom_metrics("custom.py")

response = ["A binary search algorithm reduces the time complexity to O(log n).", "The Eiffel Tower is located in Berlin and was built in the 1800s."]
reference = ["Binary search works on sorted arrays and is faster than linear search.", "In Python, a generator yields items one at a time using the 'yield' keyword."]

# Evaluate custom metric directly
eb.my_custom_metric(response, reference)

# Evaluate all metrics in the 'custom' module
eb.evaluate_module(
    module=["custom"],
    response=response,
    reference=reference,
)
```

---

## 💡 Use Cases
EvalBench is built for fast feedback loops while developing:
- LLM Applications: Chatbots, assistants, summarization tools
- Prompt Engineering: Compare prompt variations using faithfulness, conciseness, or BLEU
- Model Evaluation: Benchmark outputs from different model runs
- Custom Evaluation Design: Rapidly prototype domain-specific metrics

---

## 🚧 Coming Soon
- Basic visualizations: Histograms and score distributions to quickly interpret results
- Batch mode via JSONL/Pandas: Evaluate and export results from structured files