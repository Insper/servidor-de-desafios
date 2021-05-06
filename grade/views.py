from django.http import Http404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from core.models import Semester, PyGymUser
from grade.models import CodeExerciseGrade, CourseGrade, SubChallengeAutoFeedback, SubChallengeGrade, CodeExerciseFeedback
from quiz.models import QuizChallengeFeedback
from code_challenge.models import CodeChallengeSubmission
from quiz.serializers import QuizChallengeFeedbackSerializer
from grade.serializers import CodeExerciseGradeSerializer, CodeExerciseFeedbackSerializer


def load_grade_schema(semester):
    course_grade = CourseGrade.objects.filter(semester=semester).last()
    quiz_grades = course_grade.quizzes.filter(available=True).prefetch_related('quiz')
    exam_grades = course_grade.exams.filter(available=True).prefetch_related('quiz')

    return {
        "semester": str(semester),
        "quiz_weight": course_grade.quiz_weight,
        "quizzes": [
            {
                "title": grade.quiz.title,
                "quiz_slug": grade.quiz.slug,
                "weight": grade.weight,
                "has_manual_assessment": grade.quiz.has_manual_assessment,
            } for grade in quiz_grades
        ],
        "exams": [
            {
                "title": grade.quiz.title,
                "quiz_slug": grade.quiz.slug,
                "weight": grade.weight,
                "has_manual_assessment": grade.quiz.has_manual_assessment,
            } for grade in exam_grades
        ],
    }

def load_user_grades(semester, username):
    course_grade = CourseGrade.objects.filter(semester=semester).last()
    quiz_grades = course_grade.quizzes.filter(available=True).prefetch_related('quiz')
    exam_grades = course_grade.exams.filter(available=True).prefetch_related('quiz')

    # Get submissions
    quizzes = [quiz_grade.quiz for quiz_grade in quiz_grades]
    exams = [exam_grade.quiz for exam_grade in exam_grades]

    all_quiz_feedbacks = QuizChallengeFeedback.objects.filter(quiz__in=quizzes + exams, user__username=username).prefetch_related('quiz', 'challenge')

    # Serialize all quizzes
    quizzes_serialized = {}
    for quiz_feedback in all_quiz_feedbacks:
        quiz_slug = quiz_feedback.quiz.slug
        challenge_slug = quiz_feedback.challenge.slug
        quiz_grade = (quiz_feedback.auto_grade or 0) + (quiz_feedback.manual_grade or 0)
        quizzes_serialized.setdefault(quiz_slug, {})[challenge_slug] = quiz_grade
    return quizzes_serialized



def get_semester_grades(semester, user=None):
    course_grade = CourseGrade.objects.filter(semester=semester).last()
    quiz_grades = course_grade.quizzes.filter(available=True).prefetch_related('quiz')
    exam_grades = course_grade.exams.filter(available=True).prefetch_related('quiz')
    code_exercise_grades = course_grade.code_exercises.filter(available=True)

    # Get submissions
    quizzes = [quiz_grade.quiz for quiz_grade in quiz_grades]
    exams = [exam_grade.quiz for exam_grade in exam_grades]
    all_subchallenges = sum([list(grade.subchallenges.all()) for grade in code_exercise_grades], [])
    code_challenges = [challenge.challenge for challenge in all_subchallenges]

    all_quiz_feedbacks = QuizChallengeFeedback.objects.filter(quiz__in=quizzes + exams)
    # all_code_exercise_feedbacks = UserChallengeInteraction.objects.filter(challenge__in=code_challenges)
    if user:
        all_quiz_feedbacks = all_quiz_feedbacks.filter(user=user)
        # all_code_exercise_feedbacks = all_code_exercise_feedbacks.filter(user=user)
    all_quiz_feedbacks_serialized = QuizChallengeFeedbackSerializer(all_quiz_feedbacks, many=True).data

    # Serialize all quizzes
    quizzes_serialized = {}
    for quiz_feedback in all_quiz_feedbacks_serialized:
        quiz_slug = quiz_feedback["quiz_slug"]
        challenge_slug = quiz_feedback["challenge_slug"]
        username = quiz_feedback["user"]["username"]
        if user:
            del quiz_feedback["user"]
            del quiz_feedback["challenge_slug"]
            del quiz_feedback["quiz_slug"]
            del quiz_feedback["graded"]
            del quiz_feedback["id"]
        else:
            quiz_feedback = [quiz_feedback["auto_grade"], quiz_feedback["manual_grade"]]
        quizzes_serialized.setdefault(username, {}).setdefault(quiz_slug, {})[challenge_slug] = quiz_feedback

    # Serialize all code challenges
    # challenges_serialized = {}
    # for feedback in all_code_exercise_feedbacks:
    #     feedback.user.username
    #     challenge_slug = feedback.challenge.slug
    #     submission = feedback.latest_submission
    #     challenges_serialized.setdefault(username, {})[challenge_slug] = {"id": submission.id, "success": submission.success}

    return {
        "quizzes": quizzes_serialized,
        # "code_challenges": challenges_serialized,
        "schema": {
            "semester": str(semester),
            "quiz_weight": course_grade.quiz_weight,
            "quizzes": [
                {
                    "title": grade.quiz.title,
                    "quiz_slug": grade.quiz.slug,
                    "weight": grade.weight,
                    "has_manual_assessment": grade.quiz.has_manual_assessment,
                } for grade in quiz_grades
            ],
            "exams": [
                {
                    "title": grade.quiz.title,
                    "quiz_slug": grade.quiz.slug,
                    "weight": grade.weight,
                    "has_manual_assessment": grade.quiz.has_manual_assessment,
                } for grade in exam_grades
            ],
            # "code_exercises": [
            #     {
            #         "name": grade.name,
            #         "manual_grade_weight": grade.manual_grade_weight,
            #         "weight": grade.weight,
            #         "feedback": grade.feedback,
            #         "subchallenges": [
            #             {
            #                 "challenge_slug": subchallenge.challenge.slug,
            #                 "weight": subchallenge.weight,
            #             } for subchallenge in grade.subchallenges.all()
            #         ]
            #     } for grade in code_exercise_grades
            # ],
        }
    }


def current_semester():
    return Semester.objects.latest('year', 'semester')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_grades(request):
    semester = current_semester()
    user = request.user
    if not user:
        raise Http404()
    return Response(get_semester_grades(semester, user))


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def all_current_grades(request):
    semester = current_semester()
    return Response(get_semester_grades(semester))


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_grade_schema(request):
    semester = current_semester()
    return Response(load_grade_schema(semester))


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_user_grade(request, username):
    semester = current_semester()
    return Response(load_user_grades(semester, username))


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def all_current_code_grades(request):
    semester = current_semester()
    code_grades = CodeExerciseGrade.objects.filter(course_grade__semester=semester)
    return Response(CodeExerciseGradeSerializer(code_grades, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_ungraded_users(request, code_exercise_slug):
    # TODO list only current students
    try:
        code_exercise_grade = CodeExerciseGrade.objects.get(slug=code_exercise_slug)
    except CodeExerciseGrade.DoesNotExist:
        raise Http404()
    all_students = PyGymUser.objects.filter(is_staff=False)
    graded_students_ids = CodeExerciseFeedback.objects.filter(grade_schema=code_exercise_grade).values_list('user__id').distinct()
    return Response(all_students.exclude(id__in=graded_students_ids).values_list('username', flat=True))


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def grade_code_exercise(request, code_exercise_slug, username):
    try:
        code_exercise_grade = CodeExerciseGrade.objects.get(slug=code_exercise_slug)
        user = PyGymUser.objects.get(username=username)
    except (CodeExerciseGrade.DoesNotExist, PyGymUser.DoesNotExist):
        raise  Http404()

    try:
        feedback = CodeExerciseFeedback.objects.get(user=user, grade_schema__slug=code_exercise_slug)
        changed = False
        if 'manual_grade' in request.data:
            feedback.manual_grade = request.data['manual_grade']
            changed = True
        if 'feedback' in request.data:
            feedback.feedback = request.data['feedback']
            changed = True
        if changed:
            feedback.save()
        return Response(CodeExerciseFeedbackSerializer(feedback).data)
    except CodeExerciseFeedback.DoesNotExist:
        pass

    full_feedback = CodeExerciseFeedback.objects.create(user=user, grade_schema=code_exercise_grade)
    auto_grade = 0

    for subchallenge_grade in SubChallengeGrade.objects.filter(code_exercise=code_exercise_grade):
        filters = {'author': user, 'challenge': subchallenge_grade.challenge}
        if code_exercise_grade.deadline:
            filters['creation_date__lte'] = code_exercise_grade.deadline
        try:
            submission = CodeChallengeSubmission.objects.filter(**filters).latest('creation_date')
            SubChallengeAutoFeedback.objects.create(user=user, submission=submission, grade_schema=subchallenge_grade, full_feedback=full_feedback)
            auto_grade += submission.success * subchallenge_grade.weight / 10
        except CodeChallengeSubmission.DoesNotExist:
            pass

    full_feedback.auto_grade = auto_grade
    full_feedback.save()

    return Response(CodeExerciseFeedbackSerializer(full_feedback).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_code_feedbacks(request, code_exercise_slug):
    try:
        code_exercise_grade = CodeExerciseGrade.objects.get(slug=code_exercise_slug)
    except CodeExerciseGrade.DoesNotExist:
        raise  Http404()

    feedbacks = CodeExerciseFeedback.objects.filter(grade_schema=code_exercise_grade).prefetch_related('grade_schema')
    return Response(CodeExerciseFeedbackSerializer(feedbacks, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_code_grade(request, code_exercise_slug):
    try:
        code_exercise_grade = CodeExerciseGrade.objects.get(slug=code_exercise_slug)
        return Response(CodeExerciseGradeSerializer(code_exercise_grade).data)
    except CodeExerciseGrade.DoesNotExist:
        raise  Http404()
