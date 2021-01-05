from pages.pages_controller import list_pages
from django.test import TestCase
from pathlib import Path
import shutil, tempfile
import unittest


class ChallengeControllerTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Create a temporary directory
        self.tmp_path = Path(tempfile.mkdtemp())

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.tmp_path)

    def create_temp_tree(self, tree, root=None):
        if root is None:
            root = self.tmp_path

        for p, value in tree.items():
            if isinstance(value, str):
                with open(root / p, 'w') as f:
                    f.write(value)
            elif isinstance(value, dict):
                cur_dir = root / p
                cur_dir.mkdir()
                self.create_temp_tree(value, cur_dir)


    def test_list_pages(self):
        self.create_temp_tree({
            'variables': {
                'handout.md': 'Some markdown',
                'raw': {
                    'test.txt': 'Some text',
                },
            },
            'functions': {
                'handout.md': 'Some markdown',
                'example.md': 'Some markdown',
            },
            'while': {
                'example.md': 'Some markdown',
            },
            'raw': {
                'nothing.md': 'Should ignore this',
            },
            'nothing': {},
        })
        received_pages = list_pages(self.tmp_path)
        self.assertEqual(4, len(received_pages))
        for expected in ['variables/handout', 'functions/handout', 'functions/example', 'while/example']:
            self.assertIn(expected, received_pages)
