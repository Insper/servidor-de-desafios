import os
import json
import functools
from strtest import str_test
from trace_challenge.memory_compare import compare


APP_TOKEN = os.environ.get('APP_TOKEN')


def require_token(func):
    @functools.wraps(func)
    def wrapper(event, context):
        data = json.loads(event['body'])
        if data.get('app_token') != APP_TOKEN:
            return {'statusCode': 403}
        return func(event, context)
    return wrapper


@require_token
def post_code(event, context):
    data = json.loads(event['body'])
    code = data['code']
    test_code = data['test_code']
    function_name = data.get('function_name')

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


@require_token
def post_memory(event, context):
    data = json.loads(event['body'])
    expected = json.loads(data['expected'])
    received = json.loads(data['received'])

    retval = compare(expected, received)

    return {
        'statusCode': 200,
        'body': json.dumps(retval)
    }


def get_test(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({'Test': 'OK'})
    }


ROUTES = {
    '/code': post_code,
    '/memory': post_memory,
    '/test': get_test,
}


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        API Gateway Lambda Proxy Input Format

        Event doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html#api-gateway-simple-proxy-for-lambda-input-format

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    Returns
    ------
    API Gateway Lambda Proxy Output Format: dict

        Return doc: https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html
    """
    route = ROUTES.get(event['path'])
    if route:
        return route(event, context)
    return {
        'statusCode': 404,
    }
