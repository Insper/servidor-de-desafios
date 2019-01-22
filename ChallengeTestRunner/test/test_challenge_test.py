import unittest
from challenge_test_lib import challenge_test


TEST_CODE = '''
from challenge_test_lib import challenge_test

class TestCase(challenge_test.TestCaseWrapper):
    TIMEOUT = 1

    @challenge_test.error_message('Não funcionou para caso com zero.')
    def test_numbers_3_0(self):
        self.assertEqual(self.challenge_fun(3,0), 3)

    def test_numbers_3_4(self):
        self.assertEqual(self.challenge_fun(3,4), 4, 'Não funcionou para caso com dois números positivos.')
'''

CHALLENGE_CODE_1 = '''
def ex1(a, b):
    return max(a, b)
'''

CHALLENGE_CODE_2 = '''
def ex1(a, b):
    while True:
        pass
    return max(a, b)
'''

CHALLENGE_CODE_3 = '''
def ex1(a, b):
    if b == 0:
        return 0
    return max(a, b)
'''

CHALLENGE_CODE_4 = '''
def ex1(a, b):
    return a / 0
'''


class ChallengeTestTest(unittest.TestCase):
    def test_pass_all_tests(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_1, TEST_CODE, 'ex1')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertTrue(result.success)
        self.assertEqual(0, len(result.failure_msgs))

    def test_timeout(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_2, TEST_CODE, 'ex1')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertFalse(result.success)
        self.assertEqual(2, len(result.failure_msgs))
        self.assertEqual(challenge_test.TIME_LIMIT_EXCEEDED, result.failure_msgs[0])
        self.assertEqual(challenge_test.TIME_LIMIT_EXCEEDED, result.failure_msgs[1])

    def test_one_failure(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_3, TEST_CODE, 'ex1')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertFalse(result.success)
        self.assertEqual(1, len(result.failure_msgs))
        self.assertEqual('Não funcionou para caso com zero.', result.failure_msgs[0])

    def test_division_by_zero(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_4, TEST_CODE, 'ex1')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertFalse(result.success)
        self.assertEqual(2, len(result.failure_msgs))
        self.assertEqual('Não funcionou para caso com zero.', result.failure_msgs[0])
        self.assertEqual(challenge_test.DEFAULT_MSG, result.failure_msgs[1])

if __name__ == '__main__':
    unittest.main()
