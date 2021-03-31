from .models import PyGymUser, UserTag, Concept
from rest_framework.serializers import ModelSerializer


class UserTagSerializer(ModelSerializer):
    class Meta:
        model = UserTag
        fields = ['tag', 'slug']


class UserSerializer(ModelSerializer):
    tags = UserTagSerializer(many=True)

    class Meta:
        model = PyGymUser
        fields = ['username', 'first_name', 'last_name', 'is_staff', 'tags']


class ConceptSerializer(ModelSerializer):
    class Meta:
        model = Concept
        fields = ['name', 'slug', 'order']
