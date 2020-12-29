from django.conf import settings
import aioboto3
import json


LAMBDA_KWARGS = {
    'region_name': 'us-east-1',
}
LAMBDA_KWARGS['aws_access_key_id'] = settings.AWS_ACCESS_KEY
LAMBDA_KWARGS['aws_secret_access_key'] = settings.AWS_SECRET_KEY


async def call_lambda(function_name, payload):
    async with aioboto3.client('lambda', **LAMBDA_KWARGS) as client:
        response = await client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=payload,
        )
        response_payload = await response['Payload'].read()
        return json.loads(response_payload.decode('utf-8'))
