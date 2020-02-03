from django.conf import settings
from challenge_test_lib import challenge_test as ch

if not settings.DEV_SERVER:
    import boto3
    import json
    from collections import namedtuple

    TestResults = namedtuple('TestResults',
                             'failure_msgs,success,stack_traces')


def executa_codigo(exercicio, resposta):
    resposta = resposta.decode('utf-8')
    testes = exercicio.testes.read().decode('utf-8')
    if settings.DEV_SERVER:
        return ch.run_tests(resposta, testes, exercicio.nome_funcao)
    else:
        lamb = boto3.client('lambda')
        args = {
            'answer': resposta,
            'test_code': testes,
            'function_name': exercicio.nome_funcao,
        }

        response = lamb.invoke(FunctionName="testRunner",
                               InvocationType='RequestResponse',
                               Payload=json.dumps(args))
        feedback = response['Payload'].read().decode('utf-8')
        feedback = json.loads(json.loads(feedback))
        return TestResults(feedback['failure_msgs'], feedback['success'],
                           feedback['stack_traces'])
