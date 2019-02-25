import unittest
from challenge_test_lib import challenge_test


TEST_CODE1 = '''
from challenge_test_lib import challenge_test

class TestCase(challenge_test.TestCaseWrapper):
    TIMEOUT = 1

    @challenge_test.error_message('Não funcionou para caso com zero.')
    def test_numbers_3_0(self):
        self.assertEqual(self.challenge_fun(3,0), 3)

    def test_numbers_3_4(self):
        self.assertEqual(self.challenge_fun(3,4), 4, 'Não funcionou para caso com dois números positivos.')
'''

CHALLENGE_CODE_0 = '''
def ex1(a, b)
    return max(a, b)
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

TEST_CODE2 = '''
from challenge_test_lib import challenge_test

class TestCase(challenge_test.TestCaseWrapper):
    def test_print_called(self):
        for i in range(5):
            text = 'hi{0}'.format(i)
            self.challenge_fun(text)
            self.assertEqual(self.mock_print.calls, i+1)
            self.assertEqual(self.mock_print.printed[i], text) 
'''

CHALLENGE_CODE_5 = '''
def code_with_print(a):
    print(a)
'''

CHALLENGE_CODE_6 = '''
def code_with_print(a):
    pass
'''

TEST_CODE3 = '''
from challenge_test_lib import challenge_test

class TestCase(challenge_test.TestCaseWrapper):
    def test_input_called(self):
        self.mock_input.input_list = ['3', 2, 5, '1'] 
        result = self.challenge_fun()
        self.assertEqual(self.mock_input.calls, 4)
        self.assertEqual(result, 8)

    def test_no_sum(self):
        self.mock_input.input_list = [0] 
        result = self.challenge_fun()
        self.assertEqual(self.mock_input.calls, 1)
        self.assertEqual(result, 0) 
'''

CHALLENGE_CODE_7 = '''
def input_and_sum():
    n = int(input('N?'))
    result = 0
    while n > 0:
        result += int(input('Type a number'))
        n -= 1
    return result
'''

CHALLENGE_CODE_8 = '''
def input_and_sum():
    n = input('N?')
    result = 0
    while n > 0:
        result += input('Type a number')
        n -= 1
    return result
'''

TEST_CODE4 = '''
from challenge_test_lib import challenge_test

class TestCase(challenge_test.TestCaseWrapper):
    def test_print_called(self):
        self.mock_input.input_list = ['Inspermon'] 
        self.challenge_program()
        self.assertEqual(self.mock_input.calls, 1)
        self.assertEqual(self.mock_print.calls, 1)
        self.assertEqual(self.mock_print.printed[0], 'Hello Inspermon!')
    
    def test_hello_world(self):
        self.mock_input.input_list = ['World'] 
        self.challenge_program()
        self.assertEqual(self.mock_input.calls, 1)
        self.assertEqual(self.mock_print.calls, 1)
        self.assertEqual(self.mock_print.printed[0], 'Hello World!') 
'''

CHALLENGE_CODE_9 = '''
name = input('Name? ')
print('Hello {0}!'.format(name))
'''

CHALLENGE_CODE_10 = '''
name = input('Name? ')
pritn('Hello {0}!'.format(name))
'''


class ChallengeTestTest(unittest.TestCase):
    def test_doesnt_break_with_syntax_error(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_0, TEST_CODE1, 'ex1')
        self.assertFalse(result.success)
        self.assertEqual(1, len(result.failure_msgs))
        self.assertEqual('Código com erros de sintaxe', result.failure_msgs[0])

    def test_doesnt_break_with_missing_function(self):
        f_name = 'wrong_name'
        result = challenge_test.run_tests(CHALLENGE_CODE_1, TEST_CODE1, f_name)
        self.assertFalse(result.success)
        self.assertEqual(1, len(result.failure_msgs))
        self.assertEqual('Função não encontrada. Sua função deveria se chamar {}'.format(f_name), result.failure_msgs[0])

    def test_pass_all_tests(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_1, TEST_CODE1, 'ex1')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertTrue(result.success)
        self.assertEqual(0, len(result.failure_msgs))

    def test_timeout(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_2, TEST_CODE1, 'ex1')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertFalse(result.success)
        self.assertEqual(2, len(result.failure_msgs))
        self.assertEqual(challenge_test.TIME_LIMIT_EXCEEDED, result.failure_msgs[0])
        self.assertEqual(challenge_test.TIME_LIMIT_EXCEEDED, result.failure_msgs[1])

    def test_one_failure(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_3, TEST_CODE1, 'ex1')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertFalse(result.success)
        self.assertEqual(1, len(result.failure_msgs))
        self.assertEqual('Não funcionou para caso com zero.', result.failure_msgs[0])

    def test_division_by_zero(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_4, TEST_CODE1, 'ex1')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertFalse(result.success)
        self.assertEqual(2, len(result.failure_msgs))
        self.assertEqual('Não funcionou para caso com zero.', result.failure_msgs[0])
        self.assertEqual(challenge_test.DEFAULT_MSG, result.failure_msgs[1])

    def test_print(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_5, TEST_CODE2, 'code_with_print')
        self.assertEqual(1, result.result_obj.testsRun)
        self.assertTrue(result.success)

    def test_print_failure(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_6, TEST_CODE2, 'code_with_print')
        self.assertEqual(1, result.result_obj.testsRun)
        self.assertFalse(result.success)

    def test_input(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_7, TEST_CODE3, 'input_and_sum')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertTrue(result.success)

    def test_fail_input(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_8, TEST_CODE3, 'input_and_sum')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertFalse(result.success)

    def test_run_program_if_no_function(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_9, TEST_CODE4, '')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertTrue(result.success)

    def test_run_program_if_none_function(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_9, TEST_CODE4, None)
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertTrue(result.success)

    def test_run_program_with_error(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_10, TEST_CODE4, None)
        self.assertFalse(result.success)
        self.assertEqual(2, len(result.failure_msgs))
        for i in range(2):
            self.assertEqual('Não funcionou para algum teste', result.failure_msgs[i])


if __name__ == '__main__':
    unittest.main()
