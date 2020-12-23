from rest_framework.serializers import ModelSerializer, SerializerMethodField
from core.serializers import ConceptSerializer
from .models import TraceChallenge
from .trace_controller import code_for


class ShortTraceChallengeSerializer(ModelSerializer):
    concept = ConceptSerializer(read_only=True)

    class Meta:
        model = TraceChallenge
        fields = ['title', 'slug', 'concept']


class FullTraceChallengeSerializer(ModelSerializer):
    concept = ConceptSerializer(read_only=True)
    code = SerializerMethodField()

    def get_code(self, obj):
        return code_for(obj)

    class Meta:
        model = TraceChallenge
        fields = ['title', 'slug', 'concept', 'code']
