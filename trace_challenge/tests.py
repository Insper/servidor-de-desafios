from django.test import TestCase
import unittest
from core.models import PyGymUser, Concept, UserConceptInteraction, ChallengeRepo
from trace_challenge.trace_controller import extract_fillable_memory, extract_fillable_state, create_state, extract_fillable_stdout, compare_terminal, stringify_memory
from trace_challenge.models import TraceChallenge, TraceStateSubmission, UserTraceChallengeInteraction
from trace_challenge.error_code import RET_DIFF, RET_DIFF_WHITE, RET_OK, RET_SHOULD_BE_INACTIVE, RET_SHOULD_BE_ACTIVE, RET_MISSING_QUOTES, RET_WRONG_TYPE
from trace_challenge.memory_compare import compare_repr_value, compare


class SubmissionSignalTestCase(TestCase):
    def assertInteractions(self, user, challenge, challenge_attempts,
            successful_challenge_attempts, latest_state, completed, concept_attempts, successful_concept_attempts,
            total_challenges, successful_challenges):
        user_challenge = UserTraceChallengeInteraction.objects.get(user=user, challenge=challenge)
        self.assertEqual(challenge_attempts, user_challenge.attempts)
        self.assertEqual(successful_challenge_attempts, user_challenge.successful_attempts)
        self.assertEqual(latest_state, user_challenge.latest_state)
        self.assertEqual(completed, user_challenge.completed)

        user_concept = UserConceptInteraction.objects.get(user=user, concept=challenge.concept)
        self.assertEqual(concept_attempts, user_concept.attempts)
        self.assertEqual(successful_concept_attempts, user_concept.successful_attempts)
        self.assertEqual(total_challenges, user_concept.total_challenges)
        self.assertEqual(successful_challenges, user_concept.successful_challenges)

    def test_should_send_signal_when_created(self):
        '''When a challenge submission is created for a new challenge, a user-challenge interaction and user-concept interaction are created.'''
        user = PyGymUser.objects.create_user(username='user', password='1234')
        repo = ChallengeRepo.objects.create()
        concept = Concept.objects.create(name='Memoization', slug='algo-memoization')
        challenge = TraceChallenge.objects.create(title="Challenge", slug="challenge", repo=repo, concept=concept)

        TraceStateSubmission.objects.create(challenge=challenge, author=user, state={}, state_index=0, success=False)

        self.assertInteractions(user, challenge, 1, 0, -1, False, 0, 0, 1, 0)

    def test_should_update_interactions_when_created(self):
        '''When a challenge submission is created for a challenge, the user-challenge interaction and user-concept interaction are updated.'''
        user = PyGymUser.objects.create_user(username='user', password='1234')
        repo = ChallengeRepo.objects.create()
        concept = Concept.objects.create(name='Memoization', slug='algo-memoization')
        other_concept = Concept.objects.create(name='Recursion', slug='recursion')
        main_challenge = TraceChallenge.objects.create(title="Main Challenge", slug="main-challenge", repo=repo, concept=concept)
        other_challenge = TraceChallenge.objects.create(title="Other Challenge", slug="other-challenge", repo=repo, concept=concept)
        challenge_in_other_concept = TraceChallenge.objects.create(title="Challenge in other concept", slug="third-challenge", repo=repo, concept=other_concept)

        # Interactions should be created
        TraceStateSubmission.objects.create(challenge=other_challenge, author=user, state={}, state_index=0, success=False)
        TraceStateSubmission.objects.create(challenge=challenge_in_other_concept, author=user, state={}, state_index=0, success=False)
        TraceStateSubmission.objects.create(challenge=main_challenge, author=user, state={}, state_index=0, success=False)

        self.assertInteractions(user, main_challenge, 1, 0, -1, False, 0, 0, 2, 0)

        # Now the interactions should be updated
        TraceStateSubmission.objects.create(challenge=other_challenge, author=user, state={}, state_index=0, success=True)
        TraceStateSubmission.objects.create(challenge=challenge_in_other_concept, author=user, state={}, state_index=0, success=True)
        TraceStateSubmission.objects.create(challenge=main_challenge, author=user, state={}, state_index=0, success=True)

        self.assertInteractions(user, main_challenge, 2, 1, 0, False, 0, 0, 2, 0)

        # Successful count shouldn't change
        TraceStateSubmission.objects.create(challenge=other_challenge, author=user, state={}, state_index=1, success=False)
        TraceStateSubmission.objects.create(challenge=challenge_in_other_concept, author=user, state={}, state_index=1, success=False)
        TraceStateSubmission.objects.create(challenge=main_challenge, author=user, state={}, state_index=1, success=False)

        self.assertInteractions(user, main_challenge, 3, 1, 0, False, 0, 0, 2, 0)

        # Successful count should change
        TraceStateSubmission.objects.create(challenge=other_challenge, author=user, state={}, state_index=1, is_last=False, success=True)
        TraceStateSubmission.objects.create(challenge=challenge_in_other_concept, author=user, state={}, state_index=1, is_last=True, success=True)
        TraceStateSubmission.objects.create(challenge=main_challenge, author=user, state={}, state_index=1, is_last=True, success=True)

        self.assertInteractions(user, main_challenge, 4, 2, 1, True, 0, 0, 2, 1)

        # Successful count should change
        TraceStateSubmission.objects.create(challenge=other_challenge, author=user, state={}, state_index=2, is_last=True, success=True)
        TraceStateSubmission.objects.create(challenge=challenge_in_other_concept, author=user, state={}, state_index=1, is_last=True, success=True)
        TraceStateSubmission.objects.create(challenge=main_challenge, author=user, state={}, state_index=1, is_last=True, success=True)

        self.assertInteractions(user, main_challenge, 5, 3, 1, True, 0, 0, 2, 2)

    def test_should_update_state_in_interaction(self):
        '''When a challenge submission is created for a challenge, the latest state of the user-challenge interaction must be updated.'''
        user = PyGymUser.objects.create_user(username='user', password='1234')
        repo = ChallengeRepo.objects.create()
        concept = Concept.objects.create(name='Memoization', slug='algo-memoization')
        challenge = TraceChallenge.objects.create(title="Challenge", slug="challenge", repo=repo, concept=concept)

        TraceStateSubmission.objects.create(challenge=challenge, author=user, state={}, state_index=0, success=False)

        self.assertInteractions(user, challenge, 1, 0, -1, False, 0, 0, 1, 0)


class TraceControllerTestCase(unittest.TestCase):
    def test_extract_fillable_memory_should_keep_previous_values(self):
        prev_state = {
            '<module>': {
                'a': 1,
                'b': 2,
            },
            'function': {
                'x': 2,
                'y': 1,
            },
        }
        cur_state = {
            '<module>': {
                'a': 2,
                'b': 3,
            },
            'function': {
                'x': 3,
                'y': 2,
            },
        }
        expected = prev_state
        extracted = extract_fillable_memory(prev_state, cur_state)
        self.assertEqual(extracted, expected)

    def test_extract_fillable_memory_should_create_empty_new_values(self):
        prev_state = {
            '<module>': {
                'a': 1,
                'b': 2,
            },
            'function': {
                'x': 2,
                'y': 1,
            },
        }
        cur_state = {
            '<module>': {
                'a': 1,
                'b': 2,
                'c': 3,
            },
            'function': {
                'x': 2,
                'y': 1,
                'z': 0,
            },
        }
        expected = {
            '<module>': {
                'a': 1,
                'b': 2,
                'c': None,
            },
            'function': {
                'x': 2,
                'y': 1,
                'z': None,
            },
        }
        extracted = extract_fillable_memory(prev_state, cur_state)
        self.assertEqual(extracted, expected)

    def test_extract_fillable_memory_should_create_new_memory_once_found(self):
        prev_state = {
            '<module>': {
                'a': 1,
                'b': 2,
            },
        }
        cur_state = {
            '<module>': {
                'a': 1,
                'b': 2,
            },
            'function': {
                'x': 2,
                'y': 1,
            },
        }
        expected = {
            '<module>': {
                'a': 1,
                'b': 2,
            },
            'function': {
                'x': None,
                'y': None,
            },
        }
        extracted = extract_fillable_memory(prev_state, cur_state)
        self.assertEqual(extracted, expected)

    def test_extract_fillable_memory_should_keep_memory_if_died(self):
        prev_state = {
            '<module>': {
                'a': 1,
                'b': 2,
            },
            'function': {
                'x': 2,
                'y': 1,
            },
        }
        cur_state = {
            '<module>': {
                'a': 1,
                'b': 2,
            },
        }
        expected = {
            '<module>': {
                'a': 1,
                'b': 2,
            },
        }
        extracted = extract_fillable_memory(prev_state, cur_state)
        self.assertEqual(extracted, expected)

    def test_extract_fillable_memory_should_work_without_prev_memory(self):
        cur_state = {
            '<module>': {
                'a': 1,
                'b': 2,
            },
        }
        expected = {
            '<module>': {
                'a': None,
                'b': None,
            },
        }
        extracted = extract_fillable_memory(None, cur_state)
        self.assertEqual(extracted, expected)

    def test_extract_fillable_state_sets_has_retval_and_removes_retval(self):
        prev_state = create_state()

        result = extract_fillable_state(prev_state, create_state(retval=10))
        self.assertTrue(result['has_retval'])
        self.assertIsNone(result['retval'])

        result = extract_fillable_state(prev_state, create_state())
        self.assertFalse(result['has_retval'])
        self.assertIsNone(result['retval'])

    def test_extract_fillable_stdout(self):
        self.assertEqual([], extract_fillable_stdout(None, []))

        prev = []
        cur = []
        self.assertEqual(prev, extract_fillable_stdout(prev, cur))

        # Add a line
        new_line = {'out': 'test', 'in': None}
        prev = [l for l in cur]
        cur += [new_line]
        self.assertEqual(prev, extract_fillable_stdout(prev, cur))

        # Add a line
        new_line = {'out': 'test', 'in': 'test'}
        prev = [l for l in cur]
        cur += [new_line]
        self.assertEqual(prev + [new_line], extract_fillable_stdout(prev, cur))

        # Add a line
        new_line = {'out': 'test'}
        prev = [l for l in cur]
        cur += [new_line]
        self.assertEqual(prev, extract_fillable_stdout(prev, cur))

    def test_compare_terminal(self):
        s = 'test'
        o = {'out': s}
        o_none = {'out': s, 'in': None}
        io = {'out': s, 'in': str(reversed(s))}

        self.assertEqual(RET_OK, compare_terminal('', ''))
        self.assertEqual(RET_OK, compare_terminal([o], s))
        self.assertEqual(RET_OK, compare_terminal(s, [o]))
        self.assertEqual(RET_OK, compare_terminal(s, [o_none]))
        self.assertEqual(RET_OK, compare_terminal([o, o], s, prefix2=[o]))
        self.assertEqual(RET_OK, compare_terminal([o, o], '', prefix2=[o, o]))
        self.assertEqual(RET_OK, compare_terminal([o, o, io], '', prefix2=[o, o, io]))
        self.assertEqual(RET_OK, compare_terminal([o, o, io, o], s, prefix2=[o, o, io]))

        self.assertEqual(RET_DIFF, compare_terminal('', s))
        self.assertEqual(RET_DIFF, compare_terminal([o], ''))
        self.assertEqual(RET_DIFF, compare_terminal([], [o]))
        self.assertEqual(RET_DIFF, compare_terminal([o, o], '', prefix2=[o]))
        self.assertEqual(RET_DIFF, compare_terminal([o, o], s, prefix2=[o, o]))
        self.assertEqual(RET_DIFF, compare_terminal([o, o, io], s, prefix2=[o, o, io]))
        self.assertEqual(RET_DIFF, compare_terminal([o, o, io, o], s+s, prefix2=[o, o, io]))

        self.assertEqual(RET_DIFF_WHITE, compare_terminal('\n', ' '))
        self.assertEqual(RET_DIFF_WHITE, compare_terminal([o], s + '\n'))
        self.assertEqual(RET_DIFF_WHITE, compare_terminal(s + ' ', [o]))
        self.assertEqual(RET_DIFF_WHITE, compare_terminal([o, o], s + '\n', prefix2=[o]))
        self.assertEqual(RET_DIFF_WHITE, compare_terminal([o, o], '\n', prefix2=[o, o]))
        self.assertEqual(RET_DIFF_WHITE, compare_terminal([o, o, io], ' ', prefix2=[o, o, io]))
        self.assertEqual(RET_DIFF_WHITE, compare_terminal([o, o, io, o], s + ' \n', prefix2=[o, o, io]))

    def test_stringify_memory(self):
        states = [
            {
                "line_i": 1,
                "line": "y = 4",
                "name_dicts": {
                    "<module>": {
                        "x": 3,
                        "y": '4',
                    },
                    "<module>,crazy_function": {
                        "z": [1,2,3],
                        "w": ['1', '2', '3'],
                        "m": {"1": "abc"},
                    }
                },
                "call_line_i": 2,
                "retval": 3,
                "stdout": [{"out": "Output", "in": "Input"}]
            },
            {
                "line_i": 2,
                "line": "y = 5",
                "name_dicts": {
                    "<module>": {
                        "x": 4,
                        "y": '5',
                    },
                    "<module>,crazy_function": {
                        "z": [4,5,6],
                        "w": ['2', '3', '4'],
                        "m": {"abc": "def"},
                        "n": None,
                    }
                },
                "call_line_i": 3,
                "retval": 4,
                "stdout": [{"out": "Output 2", "in": "Input 2"}]
            },
        ]
        expected = [
            {
                "line_i": 1,
                "line": "y = 4",
                "name_dicts": {
                    "<module>": {
                        "x": '3',
                        "y": "'4'",
                    },
                    "<module>,crazy_function": {
                        "z": '[1, 2, 3]',
                        "w": "['1', '2', '3']",
                        "m": "{'1': 'abc'}",
                    }
                },
                "call_line_i": 2,
                "retval": 3,
                "stdout": [{"out": "Output", "in": "Input"}]
            },
            {
                "line_i": 2,
                "line": "y = 5",
                "name_dicts": {
                    "<module>": {
                        "x": '4',
                        "y": "'5'",
                    },
                    "<module>,crazy_function": {
                        "z": '[4, 5, 6]',
                        "w": "['2', '3', '4']",
                        "m": "{'abc': 'def'}",
                        "n": '',
                    }
                },
                "call_line_i": 3,
                "retval": 4,
                "stdout": [{"out": "Output 2", "in": "Input 2"}]
            },
        ]
        self.assertEqual(expected, stringify_memory(states))



class MemoryCompareTestCase(unittest.TestCase):
    def setUp(self):
        self.py_memory = {
            'x': 1,
            'y': 3.1415,
            'z': 'test',
            'l': [1,'2',3.14,[4],[[5]]],
            'd': {'asd': [1,"123",3.141592]},
            'b': False,
        }
        self.repr_memory = {
            'x': '1',
            'y': '3.1415',
            'z': '"test"',
            'l': "[1,'2',3.14,[4],[[5]]]",
            'd': '{\'asd\': [1,"123",3.141592]}',
            'b': 'False',
        }

    def test_compare_repr_value(self):
        self.assertEqual(RET_OK, compare_repr_value(10, '10'))
        self.assertEqual(RET_WRONG_TYPE, compare_repr_value(10, '10.0'))
        self.assertEqual(RET_OK, compare_repr_value(10.0, '10'))
        self.assertEqual(RET_OK, compare_repr_value(10.0, '10.0'))
        self.assertEqual(RET_OK, compare_repr_value(3.14, '3.14'))
        self.assertEqual(RET_OK, compare_repr_value('10', '"10"'))
        self.assertEqual(RET_OK, compare_repr_value('10', "'10'"))
        self.assertEqual(RET_DIFF, compare_repr_value('10', '10'))
        self.assertEqual(RET_OK, compare_repr_value([0, 3.14, 'string', [[10]]], "[0, 3.14, 'string', [[10]]]"))
        self.assertEqual(RET_MISSING_QUOTES, compare_repr_value([0, 3.14, 'string', [[10]]], "[0, 3.14, string, [[10]]]"))

    def test_compare_equal_memories(self):
        expected = {
            '<module>': self.py_memory,
            '<module>.crazy_function': self.py_memory,
        }
        received = {
            '<module>': self.repr_memory,
            '<module>.crazy_function': self.repr_memory,
        }
        self.assertEqual({'code': RET_OK}, compare(expected, received))

    def test_compare_memories_missing_context(self):
        expected = {
            '<module>': self.py_memory,
            '<module>.crazy_function': self.py_memory,
        }
        received = {
            '<module>': self.repr_memory,
        }
        result = compare(expected, received)
        self.assertEqual(RET_DIFF, result['code'])
        self.assertEqual({}, result['value_errors'])
        self.assertEqual({'<module>.crazy_function': RET_SHOULD_BE_ACTIVE}, result['activate_errors'])

    def test_compare_memories_extra_context(self):
        expected = {
            '<module>': self.py_memory,
        }
        received = {
            '<module>': self.repr_memory,
            '<module>.crazy_function': self.repr_memory,
        }
        result = compare(expected, received)
        self.assertEqual(RET_DIFF, result['code'])
        self.assertEqual({}, result['value_errors'])
        self.assertEqual({'<module>.crazy_function': RET_SHOULD_BE_INACTIVE}, result['activate_errors'])

    def test_compare_different_memory_values(self):
        expected = {
            '<module>': {
                'x': 3,
                'y': 3.1415,
                'z': 'test',
                'l': [1,'2',3.14,[4],[[5]]],
                'd': {'asd': [1,"123",3.141592]},
            },
        }
        received = {
            '<module>': {
                'x': '4',
                'y': '3.1416',
                'z': '"tezt"',
                'l': "[1,'3',3.14,[4],[[5]]]",
                'd': "{'asd': [2,'123',3.141592]}",
            },
        }
        result = compare(expected, received)
        self.assertEqual(RET_DIFF, result['code'])
        self.assertEqual({'<module>': {
            'x': RET_DIFF,
            'y': RET_DIFF,
            'z': RET_DIFF,
            'l': RET_DIFF,
            'd': RET_DIFF,
        }}, result['value_errors'])
        self.assertEqual({}, result['activate_errors'])

    def test_compare_different_memory_types(self):
        expected = {
            '<module>': {
                'x': 3,
                'y': 4,
                'z': True,
            },
        }
        received = {
            '<module>': {
                'x': '"3"',
                'y': '3.1415',
                'z': '4 > 3',
            },
        }
        result = compare(expected, received)
        self.assertEqual(RET_DIFF, result['code'])
        self.assertEqual({'<module>': {
            'x': RET_WRONG_TYPE,
            'y': RET_WRONG_TYPE,
            'z': RET_WRONG_TYPE,
        }}, result['value_errors'])
        self.assertEqual({}, result['activate_errors'])

    def test_compare_memory_missing_quotes(self):
        expected = {
            '<module>': {
                'x': 'test',
            },
        }
        received = {
            '<module>': {
                'x': 'test',
            },
        }
        result = compare(expected, received)
        self.assertEqual(RET_DIFF, result['code'])
        self.assertEqual({'<module>': {
            'x': RET_MISSING_QUOTES,
        }}, result['value_errors'])
        self.assertEqual({}, result['activate_errors'])

    def test_compare_memory_syntax_error(self):
        expected = {
            '<module>': {
                'x': [1,2,3],
            },
        }
        received = {
            '<module>': {
                'x': '[1,2,3',
            },
        }
        result = compare(expected, received)
        self.assertEqual(RET_DIFF, result['code'])
        self.assertEqual({'<module>': {
            'x': RET_DIFF,
        }}, result['value_errors'])
        self.assertEqual({}, result['activate_errors'])
