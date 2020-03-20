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

TEST_CODE5 = '''
from challenge_test_lib import challenge_test
import re

class TestCase(challenge_test.TestCaseWrapper):
    def test_open_called(self):
        words_str = 'some,words,separated,by,comma\\nwith,some,new,lines\\n\\n'
        words = [w for w in re.split(',|\\n', words_str) if w]
        self.mock_open.files['words.csv'] =  words_str
        self.challenge_program()
        self.assertEqual(self.mock_open.calls, 1)
        self.assertEqual(len(self.mock_open.opened), 0)
        printed = [word.strip() for word in self.mock_print.printed if word.strip()]
        self.assertEqual(printed, words)
'''

CHALLENGE_CODE_11 = '''
f = open('words.csv', 'r')
words = []
for line in f:
    words += line.split(',')
words = [word.strip() for word in words if word]
for word in words:
    print(word)
f.close()
'''

CHALLENGE_CODE_12 = '''
with open('words.csv', 'r') as f:
    words = []
    for line in f:
        words += [w.strip() for w in line.split(',') if w.strip()]
    for word in words:
        print(word)
'''

CHALLENGE_CODE_13 = '''
with open('file_that_doesnt_exist.txt', 'r') as f:
    words = []
    for line in f:
        words += line.split(',')
    for word in words:
        print(word)
'''

CHALLENGE_CODE_14 = '''
with open('words.csv', 'w') as f:
    words = []
    for line in f:
        words += [w.strip() for w in line.split(',') if w.strip()]
    for word in words:
        print(word)
'''

CHALLENGE_CODE_15 = '''
with open('words.csv', 'a') as f:
    words = []
    for line in f:
        words += [w.strip() for w in line.split(',') if w.strip()]
    for word in words:
        print(word)
'''

CHALLENGE_CODE_16 = '''
with open('words.csv', 'r') as f:
    f.write("Shouldn't work")
'''

TEST_CODE6 = '''
from challenge_test_lib import challenge_test
import re

class TestCase(challenge_test.TestCaseWrapper):
    def test_write(self):
        self.challenge_program()
        self.assertEqual(self.mock_open.calls, 1)
        self.assertEqual(len(self.mock_open.opened), 0)
        self.assertEqual(self.mock_open.files['newfile.txt'], 'New content')
'''

CHALLENGE_CODE_17 = '''
with open('newfile.txt', 'w') as f:
    f.write('New content')
'''

TEST_CODE7 = '''
from challenge_test_lib import challenge_test
import re

class TestCase(challenge_test.TestCaseWrapper):
    def test_write(self):
        self.mock_open.files['test.txt'] = 'Old content'
        self.challenge_program()
        self.assertEqual(self.mock_open.calls, 1)
        self.assertEqual(len(self.mock_open.opened), 0)
        self.assertEqual(self.mock_open.files['test.txt'], 'Old content\\nNew content')
'''

CHALLENGE_CODE_18 = '''
with open('test.txt', 'a') as f:
    f.write('\\nNew content')
'''

TEST_CODE8 = '''
from challenge_test_lib import challenge_test

class TestCase(challenge_test.TestCaseWrapper):
    def test_do_nothing(self):
        self.challenge_fun(0)
'''

CHALLENGE_CODE_19 = '''
def do_nothing(arg):
    return arg

arg = input('Should not use input in function questions: ')
print(do_nothing(arg))
'''

TEST_CODE9 = '''
from challenge_test_lib import challenge_test

class TestCase(challenge_test.TestCaseWrapper):
    def test_random_int(self):
        numbers = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
        self.mock_random.randint[(1, 20)] = numbers
        for n in numbers:
            recebido = self.challenge_fun()
            self.assertEqual(n, recebido, 'ESPERAVA OUTRO NUMERO. RECEBI: {0}, QUERIA: {1}'.format(recebido, n))
        self.assertEqual(len(numbers), self.mock_random.randint.calls)
'''

CHALLENGE_CODE_20 = '''
import random

def random_int():
    return random.randint(1, 20)
'''

CHALLENGE_CODE_21 = '''
from random import randint

def random_int():
    return randint(1, 20)
'''

CHALLENGE_CODE_22 = '''
from random import randint

def random_int():
    return randint(1, 10)
'''

TEST_CODE10 = '''
from challenge_test_lib import challenge_test as ch
from itertools import cycle


class TestCase(ch.TestCaseWrapper):
    TIMEOUT = 2

    def test_1(self):
        self.mock_input.input_list = cycle(['sim', 'talvez', 'ainda um pouco', 'não'])
        self.challenge_program()
        self.assertEqual(
            self.mock_input.calls, 4,
            'Número de chamadas para o input foi diferente do esperado')
        self.assertEqual(self.mock_print.calls, 4,
                         'Use exatamente um print por resposta do usuário')
        for i in range(3):
            self.assertTrue('Pratique mais' in self.mock_print.printed[i])
        self.assertTrue('Até a próxima' in self.mock_print.printed[-1])

    def test_de_primeira(self):
        self.mock_input.input_list = cycle(['não'])
        self.challenge_program()
        self.assertEqual(
            self.mock_input.calls, 1,
            'Número de chamadas para o input foi diferente do esperado')
        self.assertEqual(self.mock_print.calls, 1,
                         'Use exatamente um print por resposta do usuário')
        self.assertTrue('Até a próxima' in self.mock_print.printed[-1])
'''

CHALLENGE_CODE_23 = '''
resp_aluno = True
while resp_aluno == True:
    resp_D_aluno = input("Você tem mais dúvidas? ")
    if resp_D_aluno == "não":
        resp_aluno = False
        print ("Até a próxima")
    else:
        print("Pratique mais")
'''

TEST_CODE11 = '''
from challenge_test_lib import challenge_test as ch


class TestCase(ch.TestCaseWrapper):
    TIMEOUT = 2

    def test_1(self):
        self.mock_input.input_list = cycle(['sim', 'sim', 'não'])
        self.challenge_program()
        self.assertFalse(True)
'''

CHALLENGE_CODE_24 = '''
print('Começando')
continuar = True
while continuar:
    if input('Continuar? ') != 'sim':
        continuar = False
print('Fim')
'''


class ChallengeTestTest(unittest.TestCase):
    def test_doesnt_break_with_syntax_error(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_0, TEST_CODE1, 'ex1')
        self.assertFalse(result.success)
        self.assertEqual(1, len(result.failure_msgs))
        self.assertEqual('Erro de sintaxe (código Python inválido)',
                         result.failure_msgs[0])

    def test_doesnt_break_with_missing_function(self):
        f_name = 'wrong_name'
        result = challenge_test.run_tests(CHALLENGE_CODE_1, TEST_CODE1, f_name)
        self.assertFalse(result.success)
        self.assertEqual(1, len(result.failure_msgs))
        self.assertEqual(
            'Função não encontrada. Sua função deveria se chamar {}'.format(
                f_name), result.failure_msgs[0])

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
        self.assertEqual(challenge_test.TIME_LIMIT_EXCEEDED,
                         result.failure_msgs[0])
        self.assertEqual(challenge_test.TIME_LIMIT_EXCEEDED,
                         result.failure_msgs[1])

    def test_one_failure(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_3, TEST_CODE1, 'ex1')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertFalse(result.success)
        self.assertEqual(1, len(result.failure_msgs))
        self.assertEqual('Não funcionou para caso com zero.',
                         result.failure_msgs[0])

    def test_division_by_zero(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_4, TEST_CODE1, 'ex1')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertFalse(result.success)
        self.assertEqual(2, len(result.failure_msgs))
        self.assertEqual('Não funcionou para caso com zero.',
                         result.failure_msgs[0])
        self.assertEqual(challenge_test.DEFAULT_MSG, result.failure_msgs[1])

    def test_print(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_5, TEST_CODE2,
                                          'code_with_print')
        self.assertEqual(1, result.result_obj.testsRun)
        self.assertTrue(result.success)

    def test_print_failure(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_6, TEST_CODE2,
                                          'code_with_print')
        self.assertEqual(1, result.result_obj.testsRun)
        self.assertFalse(result.success)

    def test_input(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_7, TEST_CODE3,
                                          'input_and_sum')
        self.assertEqual(2, result.result_obj.testsRun)
        self.assertTrue(result.success)

    def test_fail_input(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_8, TEST_CODE3,
                                          'input_and_sum')
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
            self.assertEqual('Não funcionou para algum teste',
                             result.failure_msgs[i])

    def test_open(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_11, TEST_CODE5, None)
        self.assertTrue(result.success)

    def test_with_open(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_12, TEST_CODE5, None)
        self.assertTrue(result.success)

    def test_open_file_that_doesnt_exist(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_13, TEST_CODE5, None)
        self.assertFalse(result.success)
        self.assertTrue('FileNotFoundError' in result.stack_traces[0])

    def test_read_file_opened_for_writing(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_14, TEST_CODE5, None)
        self.assertFalse(result.success)
        self.assertTrue('UnsupportedOperation' in result.stack_traces[0])
        self.assertTrue('not readable' in result.stack_traces[0])

    def test_read_file_opened_for_appending(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_15, TEST_CODE5, None)
        self.assertFalse(result.success)
        self.assertTrue('UnsupportedOperation' in result.stack_traces[0])
        self.assertTrue('not readable' in result.stack_traces[0])

    def test_write_file_opened_for_reading(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_16, TEST_CODE5, None)
        self.assertFalse(result.success)
        self.assertTrue('UnsupportedOperation' in result.stack_traces[0])
        self.assertTrue('not writable' in result.stack_traces[0])

    def test_write(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_17, TEST_CODE6, None)
        self.assertTrue(result.success)

    def test_append(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_18, TEST_CODE7, None)
        self.assertTrue(result.success)

    def test_doesnt_allow_input_in_function_challenge(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_19, TEST_CODE8,
                                          'do_nothing')
        self.assertFalse(result.success)
        self.assertTrue('input' in result.failure_msgs[0])

    def test_use_random_randint(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_20, TEST_CODE9,
                                          'random_int')
        self.assertTrue(result.success)

        result = challenge_test.run_tests(CHALLENGE_CODE_21, TEST_CODE9,
                                          'random_int')
        self.assertTrue(result.success)

        result = challenge_test.run_tests(CHALLENGE_CODE_22, TEST_CODE9,
                                          'random_int')
        self.assertFalse(result.success)
        self.assertTrue('Não deveria executar o randint com os argumentos 1,10'
                        in result.failure_msgs[0])

    def test_doesnt_break_with_multiple_inputs(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_23, TEST_CODE10, None)
        self.assertTrue(result.success)

    def test_get_stdout(self):
        result = challenge_test.run_tests(CHALLENGE_CODE_24, TEST_CODE11, None)
        self.assertFalse(result.success)
        self.assertEqual([('Começando', ), ('Continuar? ', 'sim'),
                          ('Continuar? ', 'sim'), ('Continuar? ', 'não'),
                          ('Fim', )], result.stdouts[0])


class TestCaseWrapperTest(unittest.TestCase):
    def setUp(self):
        self.test_case_wrapper = challenge_test.TestCaseWrapper()
        self.test_case_wrapper.setUp()

    def test_assert_printed_string(self):
        expected_print = 'Who watches Bleach in 2019?'
        print(expected_print)
        self.test_case_wrapper.assert_printed(expected_print)

    def test_assert_printed_number(self):
        expected_print = 42
        print(expected_print)
        self.test_case_wrapper.assert_printed(expected_print)
        self.test_case_wrapper.assert_printed(str(expected_print))

    def test_assert_printed_substring(self):
        complete_print = 'Bleach was fine until Aizen'
        print(complete_print)
        self.test_case_wrapper.assert_printed(complete_print[2:8])

    def test_assert_printed_index(self):
        print('First string')
        print('Second string')
        self.test_case_wrapper.assert_printed('First', 0)
        self.test_case_wrapper.assert_printed('Second', 1)

    def test_assert_printed_all(self):
        print('Not related')
        print('First string')
        print('Other random')
        print('Second string')
        print('Some more prints')
        self.test_case_wrapper.assert_printed_all(['First', 'Second'])

    def test_assert_printed_all_exactly(self):
        print(10)
        print(20)
        self.test_case_wrapper.assert_printed_all([10, '20'])

    def test_assert_printed_all_not_correct_order(self):
        print('Not related')
        print('Second string')
        print('Other random')
        print('First string')
        print('Some more prints')
        with self.assertRaises(AssertionError):
            self.test_case_wrapper.assert_printed_all(['First', 'Second'])

    def test_assert_printed_fails_string(self):
        print('Ora ora ora')
        with self.assertRaises(AssertionError):
            self.test_case_wrapper.assert_printed('Yare yare daze')

    def test_assert_printed_fails_number(self):
        print(42)
        with self.assertRaises(AssertionError):
            self.test_case_wrapper.assert_printed(666)

        with self.assertRaises(AssertionError):
            self.test_case_wrapper.assert_printed('666')

    def test_assert_printed_fails_substring(self):
        print('Ora ora ora')
        with self.assertRaises(AssertionError):
            self.test_case_wrapper.assert_printed('Yare')

    def test_assert_printed_fails_index(self):
        print('Ora ora ora')
        print('Yare yare daze')
        with self.assertRaises(AssertionError):
            self.test_case_wrapper.assert_printed('Yare', 0)

        with self.assertRaises(AssertionError):
            self.test_case_wrapper.assert_printed('Ora', 1)


if __name__ == '__main__':
    unittest.main()
