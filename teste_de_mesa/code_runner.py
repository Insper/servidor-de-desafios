from django.conf import settings
import json

from collections import namedtuple

ResultadoDeComparacao = namedtuple('ResultadoDeComparacao',
                                   'sucesso,mensagens')

if not settings.DEV_SERVER:
    import boto3


def verifica_memorias(recebido, esperado):
    recebido_json = json.dumps(recebido)
    esperado_json = json.dumps(esperado)

    if settings.DEV_SERVER:
        return compara_memorias(recebido_json, esperado_json)
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
            'recebido_json': recebido_json,
            'esperado_json': esperado_json,
        }

        response = lamb.invoke(FunctionName="comparaMemorias",
                               InvocationType='RequestResponse',
                               Payload=json.dumps(args))
        resultado = response['Payload'].read().decode('utf-8')
        return json.loads(json.loads(resultado))


def compara_memorias(recebido_json, esperado_json):
    recebido = json.loads(recebido_json)
    esperado = json.loads(esperado_json)
    mensagens = []
    keys = esperado.keys() | recebido.keys()
    for k in keys:
        v_esperado = esperado.get(k, {})
        v_recebido = recebido.get(k, {})
        if (not v_esperado) and v_recebido:
            mensagens.append(
                'Alguma parte da memória não deveria estar mais ativa.')
        elif v_esperado and (not v_recebido):
            mensagens.append('A memória desativada ainda está ativa.')
        else:
            try:
                v_recebido = {
                    r_k: eval(r_v) if r_v else None
                    for r_k, r_v in v_recebido.items()
                }
                if v_esperado != v_recebido:
                    mensagens.append(
                        'Pelo menos um valor na memória está incorreto.')
            except NameError:
                mensagens.append(
                    'Não consegui entender algum dos valores da memória. Você não esqueceu as aspas em alguma string?'
                )
    return ResultadoDeComparacao(len(mensagens) == 0, mensagens)
