from django.conf import settings
import json


def code_for(challenge):
    challenges_dir = settings.CHALLENGES_DIR / challenge.repo.slug / 'traces'
    code_file = challenges_dir / challenge.slug / 'code.py'
    try:
        with open(code_file) as f:
            return f.read()
    except FileNotFoundError:
        raise RuntimeError(f'No code found for trace challenge {challenge.slug}')


def states_for(trace):
    traces_dir = settings.CHALLENGES_DIR / trace.repo.slug / 'traces'
    code_file = traces_dir / trace.slug / 'trace.json'
    try:
        with open(code_file) as f:
            return json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f'No states found for trace challenge {trace.slug}')


def extract_fillable_memory(prev_memory, cur_memory):
    fillable = {**prev_memory} if prev_memory else {}

    for name, memory in cur_memory.items():
        prev = fillable.setdefault(name, {})
        for var_name in memory:
            prev.setdefault(var_name, None)

    return fillable


def extract_fillable_state(prev_state, cur_state):
    if not prev_state:
        prev_state = {}
    fillable_state = {**cur_state}
    fillable_state['name_dicts'] = extract_fillable_memory(prev_state.get('name_dicts'), cur_state['name_dicts'])
    fillable_state['stdout'] = prev_state.get('stdout', [])
    fillable_state['has_retval'] = bool(cur_state['retval'])
    fillable_state['retval'] = None

    return fillable_state
