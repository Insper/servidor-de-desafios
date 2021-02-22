from strtest import str_test
import json


def lambda_handler(event, context):
    code = event['code']
    test_code = event['test_code']
    function_name = event.get('function_name')

    result = str_test.run_tests(code, test_code, function_name)
    retval = {
        'failure_msgs': result.failure_msgs,
        'success': result.success,
        'stack_traces': result.stack_traces,
        'stdouts': result.stdouts,
        'total_tests': result.total_tests,
    }

    return {
        'statusCode': 200,
        'body': json.dumps(retval)
    }
