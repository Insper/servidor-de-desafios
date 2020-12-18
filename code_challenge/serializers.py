from .models import CodeChallenge, CodeChallengeSubmission
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from core.serializers import ConceptSerializer


class FullCodeChallengeSerializer(ModelSerializer):
    concept = ConceptSerializer(read_only=True)

    class Meta:
        model = CodeChallenge
        fields = ['title', 'slug', 'question', 'concept', 'function_name']


class ShortCodeChallengeSerializer(ModelSerializer):
    concept = ConceptSerializer(read_only=True)

    class Meta:
        model = CodeChallenge
        fields = ['title', 'slug', 'concept']


class CodeChallengeSubmissionSerializer(ModelSerializer):
    stacktraces = SerializerMethodField()

    def get_stacktraces(self, obj):
        return obj.safe_stack_traces

    class Meta:
        model = CodeChallengeSubmission
        fields = ['id', 'creation_date', 'success', 'stacktraces', 'stdouts']
