from django.test import TestCase
from core.models import Concept


class ConceptTestCase(TestCase):
    def test_slug_auto_create(self):
        '''Concepts without slug are assigned an automatic slug.'''
        concept = Concept.objects.create(name='Tail Recursion')
        self.assertEqual('tail-recursion', concept.slug)

        concept = Concept.objects.create(name='Memoization', slug='algo-memoization')
        self.assertEqual('algo-memoization', concept.slug)

    def test_ordering(self):
        '''Concepts are initially ordered by the attribute order, and then by slug.'''
        concept2 = Concept.objects.create(name='concept-a', order=2)
        concept4 = Concept.objects.create(name='concept-c')
        concept3 = Concept.objects.create(name='concept-b')
        concept1 = Concept.objects.create(name='concept-d', order=1)
        expected = [concept1, concept2, concept3, concept4]
        for exp, got in zip(expected, Concept.objects.all()):
            self.assertEqual(exp, got)
