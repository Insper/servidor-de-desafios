from rest_framework.serializers import ModelSerializer
from .models import CodeExerciseFeedback, CodeExerciseGrade
from core.serializers import UserSerializer


class CodeExerciseGradeSerializer(ModelSerializer):
    class Meta:
        model = CodeExerciseGrade
        fields = ['manual_grade_weight', 'weight', 'available', 'name', 'slug', 'deadline']


class CodeExerciseFeedbackSerializer(ModelSerializer):
    user = UserSerializer()
    grade_schema = CodeExerciseGradeSerializer()

    class Meta:
        model = CodeExerciseFeedback
        fields = ['user', 'grade_schema', 'feedback', 'auto_grade', 'manual_grade']
