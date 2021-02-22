from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request, *args, **kwarsg):
    return render(request, 'frontend/index.html')
