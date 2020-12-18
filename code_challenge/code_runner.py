import asyncio
from django.conf import settings
from strtest import str_test
import json
if settings.USE_AWS:
    import aioboto3


if settings.USE_AWS:
    LAMBDA_KWARGS = {
        'region_name': 'us-east-1',
    }
    LAMBDA_KWARGS['aws_access_key_id'] = settings.AWS_ACCESS_KEY
    LAMBDA_KWARGS['aws_secret_access_key'] = settings.AWS_SECRET_KEY


async def run_tests(solution_code, test_code, function_name=None):
    if settings.USE_AWS:
        return await run_tests_remote(solution_code, test_code, function_name)
    else:
        await asyncio.sleep(2)
        return run_tests_local(solution_code, test_code, function_name)


def run_tests_local(solution_code, test_code, function_name=None):
    return str_test.run_tests(solution_code, test_code, function_name)


async def run_tests_remote(solution_code, test_code, function_name=None):
    feedback = await run_aws_lambda(solution_code, test_code, function_name)

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


async def run_aws_lambda(solution_code, test_code, function_name):
    async with aioboto3.client('lambda', **LAMBDA_KWARGS) as client:
        response = await client.invoke(
            FunctionName="str_test",
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'code': solution_code,
                'test_code': test_code,
                'function_name': function_name,
            })
        )
        payload = await response['Payload'].read()
        return json.loads(payload.decode('utf-8'))
