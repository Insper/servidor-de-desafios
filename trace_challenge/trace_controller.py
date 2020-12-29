from django.conf import settings
import json
from trace_challenge.error_code import RET_OK, RET_DIFF, RET_DIFF_WHITE


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


def extract_fillable_stdout(prev_stdout, cur_stdout):
    if not prev_stdout:
        prev_stdout = []
    diff = cur_stdout[len(prev_stdout):]
    last_input = -1
    for i, line in reversed(list(enumerate(diff))):
        if line.get('in'):
            last_input = i
            break
    return prev_stdout + diff[:last_input + 1]


def extract_fillable_state(prev_state, cur_state):
    if not prev_state:
        prev_state = {}
    fillable_state = {**cur_state}
    fillable_state['name_dicts'] = extract_fillable_memory(prev_state.get('name_dicts'), cur_state['name_dicts'])
    fillable_state['stdout'] = extract_fillable_stdout(prev_state.get('stdout', []), cur_state['stdout'])
    fillable_state['has_retval'] = bool(cur_state['retval'])
    fillable_state['retval'] = None

    return fillable_state


def create_state(line_i=0, line=None, name_dicts=None, call_line_i=None, retval=None, stdout=None):
    if not name_dicts:
        name_dicts = {}
    if not stdout:
        stdout = []
    return {
        "line_i": line_i,
        "line": line,
        "name_dicts": name_dicts,
        "call_line_i": call_line_i,
        "retval": retval,
        "stdout": stdout,
    }


def _fixtype(term):
    if isinstance(term, list):
        return '\n'.join(l.get('out') if l.get('out') else '' + l.get('in') if l.get('in') else '' for l in term)
    if term:
        return term
    return ''


def compare_terminal(term1, term2, prefix1=None, prefix2=None):
    term1, term2, prefix1, prefix2 = map(_fixtype, (term1, term2, prefix1, prefix2))

    if prefix1:
        term1 = '\n'.join([prefix1, term1]) if term1 else prefix1
    if prefix2:
        term2 = '\n'.join([prefix2, term2]) if term2 else prefix2

    if term1 != term2:
        if term1.strip() == term2.strip():
            return RET_DIFF_WHITE
        return RET_DIFF
    return RET_OK


def get_compare_code(expected, received):
    if expected == received:
        return RET_OK
    return RET_DIFF
