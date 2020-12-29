import asyncio
from django.conf import settings
import json
from trace_challenge.memory_compare import compare
from trace_challenge.error_code import RET_ERR
if settings.USE_AWS:
    from core.aws import call_lambda


async def compare_memories(expected, received):
    if settings.USE_AWS:
        return await compare_memories_remote(expected, received)
    else:
        # await asyncio.sleep(2)
        return await compare_memories_local(expected, received)


async def compare_memories_local(expected, received):
    return compare(expected, received)


async def compare_memories_remote(expected, received):
    expected_json = json.dumps(expected)
    received_json = json.dumps(received)

    payload = json.dumps({
        'expected': expected_json,
        'received': received_json,
    })
    response = await call_lambda('mem_test', payload)

    if 'Task timed out after' in response.get('errorMessage', '') or response.get('statusCode') != 200:
        return {'code': RET_ERR}
    return json.loads(response['body'])

