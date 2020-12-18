from .models import PyGymUser, Concept
from rest_framework.serializers import ModelSerializer


class UserSerializer(ModelSerializer):
    class Meta:
        model = PyGymUser
        fields = ['username', 'first_name', 'last_name']


class ConceptSerializer(ModelSerializer):
    class Meta:
        model = Concept
        fields = ['name', 'slug', 'order']
