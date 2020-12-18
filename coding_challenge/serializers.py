from .models import CodingChallenge, CodingChallengeSubmission
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from core.serializers import ConceptSerializer


class FullCodingChallengeSerializer(ModelSerializer):
    concept = ConceptSerializer(read_only=True)

    class Meta:
        model = CodingChallenge
        fields = ['title', 'slug', 'question', 'concept', 'function_name']


class ShortCodingChallengeSerializer(ModelSerializer):
    concept = ConceptSerializer(read_only=True)

    class Meta:
        model = CodingChallenge
        fields = ['title', 'slug', 'concept']


class CodingChallengeSubmissionSerializer(ModelSerializer):
    stacktraces = SerializerMethodField()

    def get_stacktraces(self, obj):
        return obj.safe_stack_traces

    class Meta:
        model = CodingChallengeSubmission
        fields = ['id', 'creation_date', 'success', 'stacktraces', 'stdouts']
