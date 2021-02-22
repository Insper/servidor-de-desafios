from trace_challenge.memory_compare import compare
import json


def lambda_handler(event, context):
    expected = json.loads(event['expected'])
    received = json.loads(event['received'])

    retval = compare(expected, received)

    return {
        'statusCode': 200,
        'body': json.dumps(retval)
    }
