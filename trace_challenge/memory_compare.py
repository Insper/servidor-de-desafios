from collections import defaultdict
from trace_challenge.error_code import RET_OK, RET_DIFF, RET_DIFF_WHITE, RET_SHOULD_BE_INACTIVE, RET_SHOULD_BE_ACTIVE, RET_MISSING_QUOTES, RET_WRONG_TYPE


def compare_repr_value(value, repr_str):
    try:
        var_value = None

        if repr_str:
            expected_type = type(value)
            if expected_type in [int, float]:
                var_value = expected_type(repr_str)
            elif expected_type == bool:
                if repr_str not in ['True', 'False']:
                    raise ValueError(f'{repr_str} is not a boolean')
                var_value = eval(repr_str)
            else:
                var_value = eval(repr_str)

        if value != var_value:
            return RET_DIFF
    except NameError:
        return RET_MISSING_QUOTES
    except ValueError:
        return RET_WRONG_TYPE
    except:
        return RET_DIFF
    return RET_OK


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
                    expected_var_value = expected_memory[var_name]
                    ret = compare_repr_value(expected_var_value, var_value_str)
                    if ret != RET_OK:
                        value_errors[name][var_name] = ret
                except KeyError:
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
