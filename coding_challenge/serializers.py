from .models import Tag, CodingChallenge, CodingChallengeSubmission
from rest_framework.serializers import ModelSerializer


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name', 'slug', 'order']


class FullCodingChallengeSerializer(ModelSerializer):
    tag = TagSerializer(read_only=True)

    class Meta:
        model = CodingChallenge
        fields = ['title', 'slug', 'question', 'tag', 'function_name']


class ShortCodingChallengeSerializer(ModelSerializer):
    tag = TagSerializer(read_only=True)

    class Meta:
        model = CodingChallenge
        fields = ['title', 'slug', 'tag']


class CodingChallengeSubmissionSerializer(ModelSerializer):
    class Meta:
        model = CodingChallengeSubmission
        fields = ['id', 'creation_date', 'success', 'safe_feedback', 'safe_stack_traces', 'safe_stdouts']
