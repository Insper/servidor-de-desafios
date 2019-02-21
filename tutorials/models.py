from django.db import models
from django.contrib.auth.models import User
import markdown


class Tutorial(models.Model):
    release = models.DateTimeField('date released', auto_now=True)
    title = models.CharField(max_length=1024, blank=True)
    description = models.TextField(blank=False)
    replit_url = models.CharField(max_length=1024, blank=True)

    @property
    def full_title(self):
        title = 'Tutorial {0}'.format(self.id)
        if self.title:
            title += ': {0}'.format(self.title)
        return title

    def __str__(self):
        return self.full_title

    @property
    def html_description(self):
        return markdown.markdown(self.description, extensions=['extra', 'codehilite'])


class TutorialAccess(models.Model):
    first_access = models.DateTimeField('first accessed', auto_now_add=True)
    last_access = models.DateTimeField('first accessed', auto_now=True)
    access_count = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE)
