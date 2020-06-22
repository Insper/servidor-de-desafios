import unittest
from io import StringIO, UnsupportedOperation, SEEK_END
from collections import namedtuple
import signal
from contextlib import contextmanager
import builtins
from itertools import cycle
import traceback
import functools
import imp
from challenge_test_lib.mock_import import register_module, deactivate_custom_imports

# This might be useful someday: https://docs.python.org/3/library/unittest.mock.html#mock-open

TestResults = namedtuple(
    'TestResults', 'result_obj,failure_msgs,success,stack_traces,stdouts')
START_SEP = '<|><'
END_SEP = '><|>'
TIME_LIMIT_EXCEEDED = 'Tempo limite excedido'
SYNTAX_ERROR = 'Erro de sintaxe (código Python inválido)'
DEFAULT_MSG = 'Não funcionou para algum teste'
FILE_STR = 'File "<string>", '


def error_message(msg=''):
    def anotate(fun):
        fun.msg = msg
        return fun

    return anotate


def get_message(test_case):
    test_method = getattr(test_case, test_case._testMethodName)
    return getattr(test_method, 'msg', DEFAULT_MSG)


def get_stdout(test_case):
    return test_case.stdout


def format_message(msg):
    if not msg:
        return ''
    return START_SEP + msg + END_SEP


def run_tests(challenge_code, test_code, challenge_name):
    try:
        # test_code MUST define a class named TestCase
        # It should be ok to use globals here because this code is provided by the instructors, not students
        exec(test_code, globals())

        # Setup
        if challenge_name:
            TestCase.CHALLENGE_FUN_NAME = challenge_name
        if TestCase.CHALLENGE_CODE is None:
            TestCase.CHALLENGE_CODE = challenge_code

        stream = StringIO()

        runner = unittest.TextTestRunner(stream=stream)
        result = runner.run(unittest.makeSuite(TestCase))
        stream.seek(0)
        msgs = {}
        success = result.wasSuccessful()
        for failure in result.failures + result.errors:
            st = failure[1]
            fm = get_message(failure[0])
            stdout = get_stdout(failure[0])
            if START_SEP in st and END_SEP in st:
                fm = st[st.find(START_SEP) + len(START_SEP):st.find(END_SEP)]
            elif 'TimeoutError' in st:
                fm = TIME_LIMIT_EXCEEDED
            elif 'SyntaxError: invalid syntax' in st:
                fm = SYNTAX_ERROR
                if FILE_STR in st:
                    st = st[st.rindex(FILE_STR) + len(FILE_STR):]
            if 'PriorityError' in st:
                st = st[st.rindex('PriorityError'):st.index(START_SEP)]
            if (fm, st) not in msgs:
                msgs[(fm, st)] = stdout
            success = False
        # Filter repeated messages
        if msgs:
            failure_msgs, stack_traces = zip(*msgs)
            stdouts = list(msgs.values())
        else:
            failure_msgs, stack_traces, stdouts = [], [], []
        return TestResults(result, failure_msgs, success, stack_traces,
                           stdouts)
    except:
        return TestResults(None, ['Código com erros de sintaxe'], False,
                           [traceback.format_exc()], [''])


@contextmanager
def timeout(time):
    '''Code from: https://www.jujens.eu/posts/en/2018/Jun/02/python-timeout-function/'''

    has_signals = True
    try:
        # Register a function to raise a TimeoutError on the signal.
        signal.signal(signal.SIGALRM, raise_timeout)
        # Schedule the signal to be sent after ``time``.
        signal.alarm(time)
    except ValueError:
        has_signals = False
        print('Timeout not working :( Signals only work in the main thread...')

    try:
        yield
    except TimeoutError:
        raise TimeoutError
    finally:
        # Unregister the signal so it won't be triggered
        # if the timeout is not reached.
        if has_signals:
            signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError


def timeout_decorator(time):
    def anotate(fun):
        def timed_fun(*args, **kwargs):
            with timeout(time):
                fun(*args, **kwargs)

        # Copy attributes from fun to timed_fun
        for attr in dir(fun):
            if not attr.startswith('__'):
                setattr(timed_fun, attr, getattr(fun, attr))
        return timed_fun

    return anotate


class MockFunction:
    def __init__(self):
        self.calls = 0
        self.args = []
        self.kwargs = []

    def __call__(self, *args, **kwargs):
        self.args.append(args)
        self.kwargs.append(kwargs)
        self.calls += 1


class MockPrint(MockFunction):
    def __init__(self, python_print, stdout):
        super().__init__()
        self.printed = []
        self.stdout = stdout
        self.python_print = python_print

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        # There is probably a more reliable way to do this...
        printed = ' '.join([str(arg) for arg in args])
        self.stdout.append((printed, ))
        self.printed.append(printed)
        self.python_print(*args, **kwargs)


class MockRandint(MockFunction):
    def __init__(self):
        super().__init__()
        self._numbers = {}

    def __setitem__(self, key, value):
        self._numbers[key] = iter(cycle(value))

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        if args in self._numbers:
            return next(self._numbers[args])
        else:
            raise PriorityError(
                '',
                'Não deveria executar o randint com os argumentos {}'.format(
                    ', '.join(str(arg) for arg in args)))


class PriorityError(AssertionError):
    def __init__(self, msg, formated_msg):
        super().__init__(msg + format_message(formated_msg))


class ForbiddenInputError(AssertionError):
    def __init__(self, msg):
        super().__init__(msg)


class ForbiddenInput:
    def __call__(self, *args, **kwargs):
        raise ForbiddenInputError('Should not call input in this challenge')


class MockInput(MockFunction):
    def __init__(self, stdout):
        super().__init__()
        self._input_list = []
        self.stdout = stdout
        self.il_iter = iter(self._input_list)

    @property
    def input_list(self):
        return self._input_list

    @input_list.setter
    def input_list(self, il):
        self._input_list = il
        self.il_iter = iter(self._input_list)

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        try:
            retval = next(self.il_iter)
        except StopIteration:
            retval = ''
        self.stdout.append((' '.join([str(arg) for arg in args]), retval))
        return str(retval)


class MockOpen(MockFunction):
    '''
    Currently supported modes: r, w, a
    Not supported: x, b, +
    '''
    def __init__(self):
        super().__init__()
        self.files = {}
        self._opened = []

    def __call__(self,
                 file,
                 mode='r',
                 buffering=-1,
                 encoding=None,
                 errors=None,
                 newline=None,
                 closefd=True,
                 opener=None):
        args = [file]
        kwargs = {
            'mode': mode,
            'buffering': buffering,
            'encoding': encoding,
            'errors': errors,
            'newline': newline,
            'closefd': closefd,
            'opener': opener
        }
        super().__call__(*args, **kwargs)
        if file not in self.files and 'r' in mode:
            raise FileNotFoundError(
                "[Errno 2] No such file or directory: '{0}'".format(file))
        outfile = MockFile(file, self.files.get(file, ''), self, **kwargs)
        self._opened.append(outfile)
        return outfile

    @property
    def opened(self):
        '''List of opened files that have not been closed.'''
        self._opened = [f for f in self._opened if not f.closed]
        return self._opened


class MockFile(StringIO):
    def __init__(self, filename, content, mock_open, **kwargs):
        super().__init__(content, kwargs.get('newline'))
        self.filename = filename
        self.mock_open = mock_open
        self._mode = kwargs.get('mode', 'r')
        if 'a' in self._mode:
            self.seek(0, SEEK_END)

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if attr:
            if 'read' in name and 'r' not in self._mode:
                raise UnsupportedOperation('not readable')
            elif 'write' in name and 'w' not in self._mode and 'a' not in self._mode:
                raise UnsupportedOperation('not writable')
        return attr

    def close(self):
        self.mock_open.files[self.filename] = self.getvalue()
        super().close()


class TestCaseWrapper(unittest.TestCase):
    CHALLENGE_CODE = None
    CHALLENGE_FUN = None
    CHALLENGE_FUN_NAME = None
    TIMEOUT = 3

    @classmethod
    def setUpClass(cls):
        # Decorate all tests with timeout
        for attr in dir(cls):
            if attr.startswith('test_'):
                fun = getattr(cls, attr)
                fun = timeout_decorator(cls.TIMEOUT)(fun)
                setattr(cls, attr, fun)
        cls.func_loading_errors = []

    def setUp(self):
        self.stdout = []

        # Replace builtin print
        self.python_print = builtins.print
        self.mock_print = MockPrint(self.python_print, self.stdout)
        builtins.print = self.mock_print

        # Replace builtin input
        self.python_input = builtins.input
        self.mock_input = MockInput(self.stdout)
        builtins.input = self.mock_input

        # Replace builtin open
        self.python_open = builtins.open
        self.mock_open = MockOpen()
        builtins.open = self.mock_open

        # Replace random module
        self.mock_random = register_module('random',
                                           {'randint': MockRandint()})

    def tearDown(self):
        # Restore builtin print
        builtins.print = self.python_print

        # Restore builtin input
        builtins.input = self.python_input

        # Restore builtin open
        builtins.open = self.python_open

        # Restore random module
        deactivate_custom_imports()

    @property
    def module(self):
        if not hasattr(self, '_module'):
            self._module = imp.new_module('user_module')
            exec(self.CHALLENGE_CODE, self._module.__dict__)
        return self._module

    def challenge_program(self):
        return exec(self.CHALLENGE_CODE, locals())

    def challenge_fun(self, *args, **kwargs):
        # We need the __class__ because in that way it doesn't pass self as argument to the function
        if not self.__class__.CHALLENGE_FUN:
            python_input = builtins.input
            try:
                builtins.input = ForbiddenInput()
                exec(self.__class__.CHALLENGE_CODE, locals())
                if self.__class__.CHALLENGE_FUN_NAME:
                    self.__class__.CHALLENGE_FUN = eval(
                        self.__class__.CHALLENGE_FUN_NAME)
            except ForbiddenInputError:
                self.func_loading_errors.append(
                    PriorityError(
                        'Esse desafio não espera nenhuma chamada da função input. Você pode utilizá-la em seu código para testes, mas envie o código sem o input para o servidor.',
                        'Não deveria usar input neste código.'))
            except NameError:
                self.func_loading_errors.append(
                    PriorityError(
                        'Função inexistente ou com o nome errado.',
                        'Função não encontrada. Sua função deveria se chamar {}'
                        .format(self.__class__.CHALLENGE_FUN_NAME)))
            finally:
                builtins.input = python_input
        for err in self.func_loading_errors:
            raise err
        return self.__class__.CHALLENGE_FUN(*args, **kwargs)

    @functools.lru_cache()
    def str_dist(self, s, t):
        # http://rosettacode.org/wiki/Levenshtein_distance#Memoized_recursion
        if not s:
            return len(t)
        if not t:
            return len(s)
        if s[0] == t[0]:
            return self.str_dist(s[1:], t[1:])
        l1 = self.str_dist(s, t[1:])
        l2 = self.str_dist(s[1:], t)
        l3 = self.str_dist(s[1:], t[1:])
        return 1 + min(l1, l2, l3)

    def assert_similar(self, string1, string2, dist_max=1, case_sensitive=False, msg=None):
        if not string1:
            return len(string2)
        if not string2:
            return len(string1)
        if not case_sensitive:
            string1 = string1.lower()
            string2 = string2.lower()
        dist = self.str_dist(string1,string2)
        if(dist > dist_max):
            if not msg:
                msg = self._formatMessage("Strings não são similares.")
            msg = self._formatMessage(msg)
            self.fail(msg)
            
    def assert_printed(self, value, index=None, msg=None):
        if index is not None:
            if not msg:
                msg = 'O valor {0} não foi impresso na {1}a chamada da função print'.format(
                    value, index)
            return self.assert_printed_all(
                [value], msg, printed=self.mock_print.printed[index:index + 1])

        self.assert_printed_all([value], msg)

    def assert_printed_all(self, values, msg=None, **kwargs):
        printed_values = self.mock_print.printed
        if 'printed' in kwargs:
            printed_values = kwargs['printed']
        str_values = [str(value) for value in values]
        i = 0
        j = 0
        while i < len(printed_values) and j < len(str_values):
            printed = printed_values[i]
            str_value = str_values[j]

            if str_value in printed:
                j += 1
            else:
                i += 1

        if j < len(str_values):
            if not msg:
                msg = 'Era esperada uma chamada da função print com o valor: {0}'.format(
                    str_values[j])
            msg = self._formatMessage(msg)
            self.fail(msg)

    def _formatMessage(self, msg, standardMsg=None):
        # Include message separators in all messages and ignore standardMsg
        return format_message(msg)
