import os
import evalbench
from evalbench.error_handling.custom_error import MetricError, MetricErrorMessages
from evalbench.metrics.custom.custom_metrics import load_custom_metrics

def evaluate_module(module, **kwargs):
    if not module:
        raise MetricError(MetricErrorMessages.MISSING_REQUIRED_PARAM, param='module')

    results = []
    for name, metric in evalbench.metric_registry.items():
        if metric.get('module') in module:
            required_args = metric['required_args']
            try:
                args = {arg: kwargs[arg] for arg in required_args}
                result = metric['func'](**args)
                results.append({'metric': name, 'result': result})
            except Exception as e:
                results.append({'metric': name, 'error': str(e)})

    return results