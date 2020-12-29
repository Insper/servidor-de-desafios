from collections import defaultdict
from trace_challenge.error_code import RET_OK, RET_DIFF, RET_DIFF_WHITE, RET_SHOULD_BE_INACTIVE, RET_SHOULD_BE_ACTIVE, RET_MISSING_QUOTES, RET_WRONG_TYPE


def compare(expected, received):
    value_errors = defaultdict(lambda: {})
    activate_errors = {}
    names = expected.keys() | received.keys()
    for name in names:
        expected_memory = expected.get(name, {})
        received_memory = received.get(name, {})
        if (not expected_memory) and received_memory:
            activate_errors[name] = RET_SHOULD_BE_INACTIVE
        elif expected_memory and (not received_memory):
            activate_errors[name] = RET_SHOULD_BE_ACTIVE
        else:
            for var_name, var_value_str in received_memory.items():
                try:
                    var_value = None
                    expected_var_value = expected_memory[var_name]
                    if var_value_str:
                        expected_type = type(expected_var_value)
                        if expected_type in [int, float]:
                            var_value = expected_type(var_value_str)
                        elif expected_type == bool:
                            if var_value_str not in ['True', 'False']:
                                raise ValueError(f'{var_value_str} is not a boolean')
                            var_value = eval(var_value_str)
                        else:
                            var_value = eval(var_value_str)

                    if expected_var_value != var_value:
                        value_errors[name][var_name] = RET_DIFF
                except NameError:
                    value_errors[name][var_name] = RET_MISSING_QUOTES
                except ValueError:
                    value_errors[name][var_name] = RET_WRONG_TYPE
                except:
                    value_errors[name][var_name] = RET_DIFF
    if not value_errors and not activate_errors:
        return {
            'code': RET_OK,
        }
    return {
        'code': RET_DIFF,
        'value_errors': dict(value_errors),
        'activate_errors': activate_errors,
    }
