import os
from unittest import TestCase
import requests
import json

"""
You can set the base url with the env variable AWS_LAMBDA_BASE.
"""

BASE_URL = os.environ.get("AWS_LAMBDA_BASE")
if not BASE_URL:
    print("Cannot find env var AWS_LAMBDA_BASE. Using default: localhost:3000.")
    BASE_URL = 'http://127.0.0.1:3000'
APP_TOKEN = os.environ.get("APP_TOKEN", "CHANGETHIS")

TEST_CODE = '''
from strtest import str_test
class TestCase(str_test.TestCaseWrapper):
    TIMEOUT = 3
    def test_1(self):
        resultado_obtido = self.function(4)
        self.assertAlmostEqual(27.5, resultado_obtido, msg=f'O resultado obtido foi diferente do esperado. Esperado: 27.5. Obtido: {resultado_obtido}', places=1)

    def test_2(self):
        resultado_obtido = self.function(0)
        self.assertEqual(0, resultado_obtido, msg=f'O resultado obtido foi diferente do esperado. Esperado: 0. Obtido: {resultado_obtido}')

    def test_3(self):
        resultado_obtido = self.function(8)
        self.assertAlmostEqual(110.1, resultado_obtido, msg=f'O resultado obtido foi diferente do esperado. Esperado: 110. Obtido: {resultado_obtido}',places=0)
'''

class TestLocalLambda(TestCase):
    def test_reject_code_without_token(self):
        code = '''
def area_pentagono(a):
    return 1 / 4 * a**2 * (5 * (5 + 2 * 5**.5))**.5
'''
        data = {
            "code": code,
            "test_code": TEST_CODE,
            "function_name": "area_pentagono",
        }
        res = requests.post(f'{BASE_URL}/code', data=json.dumps(data))
        assert res.status_code == 403

    def test_passing_test(self):
        code = '''
def area_pentagono(a):
    return 1 / 4 * a**2 * (5 * (5 + 2 * 5**.5))**.5
'''
        data = {
            "code": code,
            "test_code": TEST_CODE,
            "function_name": "area_pentagono",
            "app_token": APP_TOKEN,
        }
        res = requests.post(f'{BASE_URL}/code', data=json.dumps(data))
        data = res.json()

        assert res.status_code == 200
        assert data["failure_msgs"] == []
        assert data["success"] == True
        assert data["stack_traces"] == []
        assert data["stdouts"] == []
        assert data["total_tests"] == 3

    def test_not_passing_test(self):
        code = '''
def area_pentagono(a):
    print('Debug')
    return a
'''
        data = {
            "code": code,
            "test_code": TEST_CODE,
            "function_name": "area_pentagono",
            "app_token": APP_TOKEN,
        }
        res = requests.post(f'{BASE_URL}/code', data=json.dumps(data))
        data = res.json()

        assert res.status_code == 200
        assert data["failure_msgs"] == [
            'O resultado obtido foi diferente do esperado. Esperado: 27.5. Obtido: 4',
            'O resultado obtido foi diferente do esperado. Esperado: 110. Obtido: 8',
        ]
        assert data["success"] == False
        assert len(data["stack_traces"]) == 2
        assert data["stdouts"] == [[['Debug']], [['Debug']]]
        assert data["total_tests"] == 3

    def test_reject_memory_without_token(self):
        data = {
            "expected": "{\"<module>\":{\"x\": 1,\"y\": 3.1415}}",
            "received": "{\"<module>\":{\"x\": \"1.2\",\"y\": \"wrong\"}}",
        }
        res = requests.post(f'{BASE_URL}/memory', data=json.dumps(data))
        assert res.status_code == 403

    def test_memory_diff(self):
        data = {
            "expected": "{\"<module>\":{\"x\": 1,\"y\": 3.1415}}",
            "received": "{\"<module>\":{\"x\": \"1.2\",\"y\": \"wrong\"}}",
            "app_token": APP_TOKEN,
        }
        res = requests.post(f'{BASE_URL}/memory', data=json.dumps(data))
        data = res.json()

        assert res.status_code == 200
        assert data["code"] == 1
        self.assertDictEqual(data.get("value_errors", {}), {'<module>': {'x': 6, 'y': 6}})
        assert data.get('activate_errors', {}) == {}

    def test_memory_eq(self):
        data = {
            "expected": "{\"<module>\":{\"x\": 1,\"y\": 3.1415}}",
            "received": "{\"<module>\":{\"x\": \"1\",\"y\": \"3.1415\"}}",
            "app_token": APP_TOKEN,
        }
        res = requests.post(f'{BASE_URL}/memory', data=json.dumps(data))
        data = res.json()

        assert res.status_code == 200
        assert data["code"] == 0
        assert data.get("value_errors", {}) == {}
        assert data.get('activate_errors', {}) == {}
