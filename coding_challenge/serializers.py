from .models import Tag, CodingChallenge
from rest_framework.serializers import ModelSerializer


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name', 'slug', 'order']


class FullCodingChallengeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = CodingChallenge
        fields = ['title', 'slug', 'question', 'tags', 'function_name']


class ShortCodingChallengeSerializer(ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = CodingChallenge
        fields = ['title', 'slug', 'tags']
