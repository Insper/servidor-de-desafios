import json

import pytest

from challenge_tester import app


@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""

    return {
        "body": '{"code": "def area_pentagono(a):\\n    return 1 / 4 * a**2 * (5 * (5 + 2 * 5**.5))**.5", "test_code": "from strtest import str_test\\nclass TestCase(str_test.TestCaseWrapper):\\n    TIMEOUT = 3\\n    def test_1(self):\\n        resultado_obtido = self.function(4)\\n        self.assertAlmostEqual(27.5, resultado_obtido, msg=f\'O resultado obtido foi diferente do esperado. Esperado: 27.5. Obtido: {resultado_obtido}\', places=1)\\n    def test_2(self):\\n        resultado_obtido = self.function(0)\\n        self.assertEqual(0, resultado_obtido, msg=f\'O resultado obtido foi diferente do esperado. Esperado: 0. Obtido: {resultado_obtido}\')\\n    def test_3(self):\\n        resultado_obtido = self.function(8)\\n        self.assertAlmostEqual(110.1, resultado_obtido, msg=f\'O resultado obtido foi diferente do esperado. Esperado: 110. Obtido: {resultado_obtido}\',places=0)", "function_name": "area_pentagono"}',
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": "",
            },
            "stage": "prod",
        },
        "queryStringParameters": {"foo": "bar"},
        "headers": {
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "false",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country": "US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-Port": "443",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "X-Forwarded-Proto": "https",
            "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer": "false",
            "Cache-Control": "max-age=0",
            "User-Agent": "Custom User Agent String",
            "CloudFront-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, sdch",
        },
        "pathParameters": {"proxy": "/examplepath"},
        "httpMethod": "POST",
        "stageVariables": {"baz": "qux"},
        "path": "/examplepath",
    }


def test_lambda_handler(apigw_event, mocker):

    ret = app.lambda_handler(apigw_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "failure_msgs" in ret["body"]
    assert data["failure_msgs"] == []
    assert "success" in ret["body"]
    assert data["success"] == True
    assert "stack_traces" in ret["body"]
    assert data["stack_traces"] == []
    assert "stdouts" in ret["body"]
    assert data["stdouts"] == []
    assert "total_tests" in ret["body"]
    assert data["total_tests"] == 3
