import json
from trace_challenge.error_code import RET_OK
from rest_framework.views import APIView
from django.http import Http404, HttpResponseForbidden
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from .models import TraceChallenge, TraceStateSubmission, UserTraceChallengeInteraction
from .serializers import ShortTraceChallengeSerializer, FullTraceChallengeSerializer, UserTraceChallengeInteractionSerializer
from .trace_controller import compare_terminal, states_for, states_from_slug, extract_fillable_state, extract_fillable_stdout, get_compare_code, stringify_memory
from .memory_compare import compare_repr_value


class TraceChallengeListView(APIView):
    """
    List all challenges.
    """
    permission_classes = (IsAuthenticated,)

    @method_decorator(cache_page(60*60*2))
    def get(self, request, format=None):
        concept_slug = request.query_params.get('concept')
        query = {
            'deleted': False,
            'published': True,
        }
        if concept_slug:
            query['concept__slug'] = concept_slug
        challenges = TraceChallenge.objects.filter(**query)
        serializer = ShortTraceChallengeSerializer(challenges, many=True)
        return Response(serializer.data)


def get_challenge_or_404(slug):
    try:
        challenge = TraceChallenge.objects.get(slug=slug)
        if not challenge.deleted and challenge.published:
            return challenge
    except TraceChallenge.DoesNotExist:
        pass
    raise Http404(f'There is no trace with slug {slug}')


class TraceChallengeView(APIView):
    """
    Get challenge.
    """
    permission_classes = (IsAuthenticated,)

    @method_decorator(cache_page(60*60*2))
    def get(self, request, slug, format=None):
        challenge = get_challenge_or_404(slug)
        if 'short' in request.GET:
            serializer = ShortTraceChallengeSerializer(challenge)
        else:
            serializer = FullTraceChallengeSerializer(challenge)
        return Response(serializer.data)

    def validate_state_index(self, state_index, user, trace):
        try:
            user_trace = UserTraceChallengeInteraction.objects.get(user=user, challenge=trace)
            latest_accepted = user_trace.latest_state
        except UserTraceChallengeInteraction.DoesNotExist:
            latest_accepted = -1
        if state_index > latest_accepted + 1:
            raise HttpResponseForbidden('Invalid state index')

    def post(self, request, slug, format=None):
        trace = get_challenge_or_404(slug)
        states = states_for(trace)

        state_index = request.data.get('state_index')
        memory = request.data.get('memory')
        memory_code = request.data.get('memory_code')
        terminal = request.data.get('terminal')
        next_line = request.data.get('next_line')
        retval = request.data.get('retval')
        received_state = {
            "name_dicts": memory,
            "retval": retval,
            "stdout": terminal,
        }

        self.validate_state_index(state_index, request.user, trace)

        cur_state = states[state_index]
        prev_state = {}
        if state_index > 0:
            prev_state = states[state_index - 1]
        next_state = {}
        if state_index < len(states) - 1:
            next_state = states[state_index + 1]

        prev_stdout = prev_state.get('stdout', [])
        cur_stdout = cur_state.get('stdout', [])
        fillable_stdout = extract_fillable_stdout(prev_stdout, cur_stdout)
        if isinstance(next_line, int):
            # We store it zero-indexed
            next_line -= 1

        errors = {
            'memory_code': memory_code,
            'terminal_code': compare_terminal(cur_stdout, terminal, prefix2=fillable_stdout),
            'retval_code': compare_repr_value(cur_state.get('retval'), retval),
            'next_line_code': get_compare_code(next_state.get('line_i'), next_line),
        }
        has_errors = errors['memory_code']['code'] != RET_OK or errors['terminal_code'] != RET_OK or errors['retval_code'] != RET_OK or errors['next_line_code'] != RET_OK

        TraceStateSubmission.objects.create(
            author=request.user,
            challenge=trace,
            success=not has_errors,
            state=received_state,
            state_index=state_index,
            is_last=state_index==len(states)-1,
        )

        return Response(errors)


class TraceStateListView(APIView):
    """
    List all states already completed by the user.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, slug, format=None):
        trace = get_challenge_or_404(slug)
        states = states_for(trace)
        current_state = {}
        try:
            latest_state = UserTraceChallengeInteraction.objects.get(user=request.user, challenge=trace).latest_state
        except UserTraceChallengeInteraction.DoesNotExist:
            latest_state = -1
        if latest_state < len(states) - 1:
            prev_state = None
            if latest_state >= 0:
                prev_state = states[latest_state]
            current_state = extract_fillable_state(prev_state, states[latest_state + 1])
        completed_states = states[:latest_state + 1]
        completed_states.append(current_state)

        return Response({
            'states': stringify_memory(completed_states),
            'totalStates': len(states),
            'latestState': latest_state,
        })


class TraceInteractionListView(APIView):
    """
    List all user-trace interactions for this user.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        interactions = UserTraceChallengeInteraction.objects.filter(user=user)
        serializer = UserTraceChallengeInteractionSerializer(interactions, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@cache_page(60*60*2)
def get_memory(request, slug, state_index):
    states = states_from_slug(slug)
    cur_state = states[state_index]
    return Response(json.dumps(cur_state['name_dicts']))
