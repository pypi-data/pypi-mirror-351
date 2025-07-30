from typing import List, Union, Tuple
from evalbench.error_handling.custom_error import MetricError, MetricErrorMessages

def validate_num_args(*args: Tuple, length: int):
    if len(args[0]) != length:
        raise MetricError(MetricErrorMessages.MISSING_REQUIRED_PARAM)

def validate_type_list_non_empty(*args: Tuple[str, Union[List[str], List[List[str]]]]):
    for param_name, arg in args:
        if not isinstance(arg, list) or len(arg) == 0:
            raise MetricError(MetricErrorMessages.INVALID_LIST, param=param_name)

def validate_type_string_non_empty(*args: Tuple):
    for param_name, arg in args:
        if not isinstance(arg, str) or not arg.strip():
            raise MetricError(MetricErrorMessages.INVALID_STRING, param=param_name)

def validate_type_int_positive_integer(value: int, param_name: str):
    if not isinstance(value, int) or value <= 0:
        raise MetricError(MetricErrorMessages.INVALID_INT, param=param_name)

def validate_list_length(*args: Tuple):
    if len(args[0]) != len(args[1]):
        raise MetricError(MetricErrorMessages.LIST_LENGTH_MISMATCH)

def validate_batch_inputs(*args: Tuple[str, Union[List[str], List[List[str]]]]):
    validate_num_args(args, length=2)

    (param_1, batch_1), (param_2, batch_2) = args

    validate_type_list_non_empty((param_1, batch_1), (param_2, batch_2))
    validate_list_length((param_1, batch_1), (param_2, batch_2))

    for idx, item in enumerate(batch_1):
        if isinstance(item, str):
            validate_type_string_non_empty((param_1, item))
        elif isinstance(item, list):
            for jdx, inner_item in enumerate(item):
                validate_type_string_non_empty((param_1, inner_item))

    for idx, item in enumerate(batch_2):
        if isinstance(item, str):
            validate_type_string_non_empty((param_2, item))
        elif isinstance(item, list):
            for jdx, inner_item in enumerate(item):
                validate_type_string_non_empty((param_2, inner_item))