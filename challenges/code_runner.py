from django.conf import settings
from challenge_test_lib import challenge_test as ch

if not settings.DEV_SERVER:
    import boto3
    import json
    from collections import namedtuple

    TestResults = namedtuple('TestResults', 'failure_msgs,success,stack_traces')


def run_code(challenge, answer):
    answer = answer.decode('utf-8')
    test_code = challenge.test_file.read().decode('utf-8')
    if settings.DEV_SERVER:
        return ch.run_tests(answer, test_code, challenge.function_name)
    else:
        lamb = boto3.client('lambda')
        args = {
            'answer': answer,
            'test_code': test_code,
            'function_name': challenge.function_name,
        }

        response = lamb.invoke(FunctionName="testRunner", InvocationType='RequestResponse', Payload=json.dumps(args))
        feedback = response['Payload'].read().decode('utf-8')
        feedback = json.loads(json.loads(feedback))
        print(feedback)
        return TestResults(feedback['failure_msgs'], feedback['success'], feedback['stack_traces'])