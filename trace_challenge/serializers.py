from rest_framework.serializers import ModelSerializer, SerializerMethodField
from core.serializers import ConceptSerializer
from .models import TraceChallenge, UserTraceChallengeInteraction
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


class UserTraceChallengeInteractionSerializer(ModelSerializer):
    challenge = ShortTraceChallengeSerializer(read_only=True)  # TODO This is not ideal (will require joins), it's probably better to update only the new submissions

    class Meta:
        model = UserTraceChallengeInteraction
        fields = ['challenge', 'attempts', 'successful_attempts', 'completed']
