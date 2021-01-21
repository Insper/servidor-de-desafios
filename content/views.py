from django.conf import settings
from django.http import Http404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import content.content_controller as controller
from core.models import ChallengeRepo


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_contents(request):
    contents = controller.list_contents(settings.CHALLENGES_DIR)
    return Response(contents)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pages(request):
    all_pages = []
    for repo in ChallengeRepo.objects.all():
        all_pages += controller.list_pages(settings.CHALLENGES_DIR / repo.slug / 'pages')
    return Response(all_pages)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_page(request, content_slug, page_slug=None):
    for repo in ChallengeRepo.objects.all():
        dirname = settings.CHALLENGES_DIR / repo.slug / 'pages' / content_slug
        for fname in [page_slug, 'index', 'handout']:
            try:
                with open(dirname / f'{fname}.md') as f:
                    return Response(f.read())
            except FileNotFoundError:
                pass
    raise Http404('')
