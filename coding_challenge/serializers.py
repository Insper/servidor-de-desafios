from .models import Tag, CodingChallenge, CodingChallengeSubmission
from rest_framework.serializers import ModelSerializer, SerializerMethodField


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
    stacktraces = SerializerMethodField()
    stdouts = SerializerMethodField()

    def get_stacktraces(self, obj):
        return obj.safe_stack_traces

    def get_stdouts(self, obj):
        return obj.safe_stdouts

    class Meta:
        model = CodingChallengeSubmission
        fields = ['id', 'creation_date', 'success', 'stacktraces', 'stdouts']
