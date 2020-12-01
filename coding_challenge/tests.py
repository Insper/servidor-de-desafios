from django.test import TestCase
from coding_challenge.models import Tag


class TagTestCase(TestCase):
    def test_slug_auto_create(self):
        '''Tags without slug are assigned an automatic slug.'''
        tag = Tag.objects.create(name='Tail Recursion')
        self.assertEqual('tail-recursion', tag.slug)

        tag = Tag.objects.create(name='Memoization', slug='algo-memoization')
        self.assertEqual('algo-memoization', tag.slug)

    def test_ordering(self):
        '''Tags are initially ordered by the attribute order, and then by slug.'''
        tag2 = Tag.objects.create(name='tag-a', order=2)
        tag4 = Tag.objects.create(name='tag-c')
        tag3 = Tag.objects.create(name='tag-b')
        tag1 = Tag.objects.create(name='tag-d', order=1)
        expected = [tag1, tag2, tag3, tag4]
        for exp, got in zip(expected, Tag.objects.all()):
            self.assertEqual(exp, got)
