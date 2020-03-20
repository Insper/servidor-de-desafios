from challenge_test_lib import challenge_test as ch
import json


def handle(event, context):
    answer = event['answer']
    test_code = event['test_code']
    function_name = event['function_name']

    result = ch.run_tests(answer, test_code, function_name)
    retval = {
        'failure_msgs': result.failure_msgs,
        'success': result.success,
        'stack_traces': result.stack_traces,
        'stdouts': result.stdouts,
    }

    return json.dumps(retval)
