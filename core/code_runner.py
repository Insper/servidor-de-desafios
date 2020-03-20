from django.conf import settings
from challenge_test_lib import challenge_test as ch

if not settings.DEV_SERVER:
    import boto3
    import json
    from collections import namedtuple

    TestResults = namedtuple('TestResults',
                             'failure_msgs,success,stack_traces,stdouts')


def executa_codigo(exercicio, resposta):
    resposta = resposta.decode('utf-8')
    testes = exercicio.testes.read().decode('utf-8')
    if settings.DEV_SERVER:
        return ch.run_tests(resposta, testes, exercicio.nome_funcao)
    else:
        kwargs = {
            'region_name': 'us-east-1',
        }
        if settings.AWS_ACCESS_KEY:
            kwargs['aws_access_key_id'] = settings.AWS_ACCESS_KEY
        if settings.AWS_SECRET_KEY:
            kwargs['aws_secret_access_key'] = settings.AWS_SECRET_KEY
        lamb = boto3.client('lambda', **kwargs)
        args = {
            'answer': resposta,
            'test_code': testes,
            'function_name': exercicio.nome_funcao,
        }

        response = lamb.invoke(FunctionName="testRunner",
                               InvocationType='RequestResponse',
                               Payload=json.dumps(args))
        feedback = response['Payload'].read().decode('utf-8')
        feedback = json.loads(feedback)
        if isinstance(
                feedback,
                dict) and 'Task timed out after' in feedback['errorMessage']:
            msg = feedback['errorMessage']
            msg = msg[msg.index('Task timed out'):]
            feedback = {
                'success': False,
                'failure_msgs': [ch.TIME_LIMIT_EXCEEDED],
                'stack_traces': [msg],
                'stdouts': [''],
            }
        else:
            feedback = json.loads(feedback)
        return TestResults(feedback['failure_msgs'], feedback['success'],
                           feedback['stack_traces'], feedback['stdouts'])
