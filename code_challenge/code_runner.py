import asyncio
from django.conf import settings
from strtest import str_test
import json
if settings.USE_AWS:
    from core.aws import call_lambda


async def run_tests(solution_code, test_code, function_name=None):
    if settings.USE_AWS:
        return await run_tests_remote(solution_code, test_code, function_name)
    else:
        await asyncio.sleep(2)
        return run_tests_local(solution_code, test_code, function_name)


def run_tests_local(solution_code, test_code, function_name=None):
    return str_test.run_tests(solution_code, test_code, function_name)


async def run_tests_remote(solution_code, test_code, function_name=None):
    payload = json.dumps({
        'code': solution_code,
        'test_code': test_code,
        'function_name': function_name,
    })
    feedback = await call_lambda('str_test', payload)

    if 'Task timed out after' in feedback.get('errorMessage', ''):
        msg = feedback['errorMessage']
        msg = msg[msg.index('Task timed out'):]
        feedback = {
            'success': False,
            'failure_msgs': ['Time limit exceeded'],
            'stack_traces': [msg],
            'stdouts': [''],
            'total_tests': 1,
        }
    else:
        feedback = json.loads(feedback['body'])
    return str_test.TestResults(None, **feedback)

