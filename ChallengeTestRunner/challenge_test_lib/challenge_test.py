import unittest
from io import StringIO
from collections import namedtuple
import signal
from contextlib import contextmanager


TestResults = namedtuple('TestResults', 'result_obj,failure_msgs,success,stack_traces')
START_SEP = '<|><'
END_SEP = '><|>'
TIME_LIMIT_EXCEEDED = 'Tempo limite excedido'
DEFAULT_MSG = 'Não funcionou para algum teste'


def error_message(msg=''):
    def anotate(fun):
        fun.msg = msg
        return fun
    return anotate


def get_message(test_case):
    test_method = getattr(test_case, test_case._testMethodName)
    return getattr(test_method, 'msg', DEFAULT_MSG)


def run_tests(challenge_code, test_code, challenge_name):
    exec(challenge_code, locals())
    # test_code MUST define a class named TestCase
    # It should be ok to use globals here because this code is provided by the instructors, not students
    exec(test_code, globals())

    # Setup
    if TestCase.CHALLENGE_FUN is None:
        try:
            TestCase.CHALLENGE_FUN = eval(challenge_name)
        except NameError:
            return TestResults(None, ['Função não encontrada. Sua função deveria se chamar {}'.format(challenge_name)], False, [])

    stream = StringIO()

    runner = unittest.TextTestRunner(stream=stream)
    result = runner.run(unittest.makeSuite(TestCase))
    stream.seek(0)
    failure_msgs = []
    stack_traces = []
    success = result.wasSuccessful()
    for failure in result.failures + result.errors:
        st = failure[1]
        fm = get_message(failure[0])
        stack_traces.append(st)
        if START_SEP in st and END_SEP in st:
            fm = st[st.find(START_SEP) + len(START_SEP):st.find(END_SEP)]
        elif 'TimeoutError' in st:
            fm = TIME_LIMIT_EXCEEDED
        failure_msgs.append(fm)
        success = False
    return TestResults(result, failure_msgs, success, stack_traces)


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


class TestCaseWrapper(unittest.TestCase):
    CHALLENGE_FUN = None
    TIMEOUT = 3

    @classmethod
    def setUpClass(cls):
        # Decorate all tests with timeout
        for attr in dir(cls):
            if attr.startswith('test_'):
                fun = getattr(cls, attr)
                fun = timeout_decorator(cls.TIMEOUT)(fun)
                setattr(cls, attr, fun)

    def challenge_fun(self, *args, **kwargs):
        # We need the __class__ because in that way it doesn't pass self as argument to the function
        return self.__class__.CHALLENGE_FUN(*args, **kwargs)

    def _formatMessage(self, msg, standardMsg):
        # Include message separators in all messages and ignore standardMsg
        if not msg:
            return ''
        return START_SEP + super()._formatMessage(msg, '') + END_SEP
