from evalbench.runtime_setup.config import EvalConfig
from evalbench.metrics.evaluate_module import evaluate_module
from evalbench.utils.helper import expose_metrics, expose_additional_helpers, register_metric, handle_output
from evalbench.metrics.custom.custom_metrics import load_custom_metrics
from evalbench.runtime_setup.runtime import set_config

metric_registry = {}
__all__ = []

# metric modules and individual metrics
module_names = {
    "response_quality": "metrics.predefined.response_quality",
    "reference_based": "metrics.predefined.reference_based",
    "contextual_generation": "metrics.predefined.contextual_generation",
    "retrieval": "metrics.predefined.retrieval",
    "query_alignment": "metrics.predefined.query_alignment",
    "response_alignment": "metrics.predefined.response_alignment",
}

# evaluate module
module_evaluation = ['evaluate_module']

# decorators for custom metrics
decorators = ['register_metric', 'handle_output']

# custom metrics
custom = ['load_custom_metrics']

# configs
configs = ["EvalConfig", "set_config"]

expose_metrics(module_names)

expose_additional_helpers(module_evaluation)
expose_additional_helpers(custom)
expose_additional_helpers(decorators)
expose_additional_helpers(configs)
