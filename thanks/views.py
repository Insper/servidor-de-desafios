from pathlib import Path
import json
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def index(request):
    thanks_dir = Path(__file__).parent / 'static' / 'thanks'
    authors = []
    for fname in sorted(thanks_dir.glob('*.json')):
        with open(fname) as f:
            authors.append(json.load(f))
    return Response(authors)
