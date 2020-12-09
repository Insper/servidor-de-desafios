from .models import PyGymUser
from rest_framework.serializers import ModelSerializer


class UserSerializer(ModelSerializer):
    class Meta:
        model = PyGymUser
        fields = ['username', 'first_name', 'last_name']
