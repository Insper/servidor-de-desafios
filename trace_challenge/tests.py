from django.test import TestCase
import unittest
from trace_challenge.trace_controller import extract_fillable_memory, extract_fillable_state


def create_state(line_i=0, line=None, name_dicts=None, call_line_i=None, retval=None, stdout=None):
    if not name_dicts:
        name_dicts = {}
    if not stdout:
        stdout = []
    return {
        "line_i": line_i,
        "line": line,
        "name_dicts": name_dicts,
        "call_line_i": call_line_i,
        "retval": retval,
        "stdout": stdout,
    }


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
            'function': {
                'x': 2,
                'y': 1,
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
