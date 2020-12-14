import asyncio
import functools
from django.conf import settings
from strtest import str_test
import json
from collections import namedtuple


async def run_tests(solution_code, test_code, function_name=None):
    if settings.PRODUCTION:
        return await run_tests_remote(solution_code, test_code, function_name)
    else:
        return run_tests_local(solution_code, test_code, function_name)


def run_tests_local(solution_code, test_code, function_name=None):
    return str_test.run_tests(solution_code, test_code, function_name)


async def run_tests_remote(solution_code, test_code, function_name=None):
    lamb = AWSLambda()
    feedback = await lamb.run(solution_code, test_code, function_name)

    if isinstance(feedback, dict) and 'Task timed out after' in feedback['errorMessage']:
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
        feedback = json.loads(feedback)
    return str_test.TestResults(None, **feedback)


class AWSLambda:
    def __init__(self):
        import boto3

        kwargs = {
            'region_name': 'us-east-1',
        }
        if settings.USE_AWS:
            kwargs['aws_access_key_id'] = settings.AWS_ACCESS_KEY
            kwargs['aws_secret_access_key'] = settings.AWS_SECRET_KEY
        self.client =  boto3.client('lambda', **kwargs)

    async def run(self, solution_code, test_code, function_name=None):
        args = {
            'answer': solution_code,
            'test_code': test_code,
            'function_name': function_name,
        }

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, functools.partial(self.client.invoke, FunctionName="testRunner",
                                InvocationType='RequestResponse',
                                Payload=json.dumps(args)))
        return json.loads(response['Payload'].read().decode('utf-8'))
