from .models import CodeChallenge, CodeChallengeSubmission, UserChallengeInteraction
from rest_framework.serializers import ModelSerializer, SerializerMethodField, ReadOnlyField
from core.serializers import ConceptSerializer


class FullestCodeChallengeSerializer(ModelSerializer):
    concept = ConceptSerializer(read_only=True)
    test_code = ReadOnlyField(source='test_code')

    class Meta:
        model = CodeChallenge
        fields = ['title', 'slug', 'question', 'concept', 'function_name', 'test_code']

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


class UserChallengeInteractionSerializer(ModelSerializer):
    challenge = ShortCodeChallengeSerializer(read_only=True)  # TODO This is not ideal (will require joins), it's probably better to update only the new submissions

    class Meta:
        model = UserChallengeInteraction
        fields = ['challenge', 'attempts', 'successful_attempts', 'completed']
