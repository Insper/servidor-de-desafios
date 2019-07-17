from django.db import models
from django.contrib.auth.models import User
import markdown


class Tutorial(models.Model):
    release = models.DateTimeField('date released', auto_now=True)
    title = models.CharField(max_length=1024, blank=True)
    description = models.TextField(blank=False)
    replit_url = models.CharField(max_length=1024, blank=True)
    published = models.BooleanField(default=True)

    @classmethod
    def all_published(cls):
        return Tutorial.objects.filter(published=True)

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
        replacements = [
            ('<span class="o">&amp;</span><span class="n">gt</span><span class="p">;</span>', '>'),
            ('<span class="o">&amp;</span><span class="n">lt</span><span class="p">;</span>', '<'),
        ]
        result = markdown.markdown(self.description, extensions=['codehilite'])
        with_div = ''
        slide_id = 1
        for line in result.split('\n'):
            if '---slide---' in line:
                if slide_id > 1:
                    with_div += '</div>\n'
                with_div += '<div class="slide" id="slide{0}">\n'.format(slide_id)
                slide_id += 1
            else:
                for text, replacement in replacements:
                    line = line.replace(text, replacement)
                with_div += line + '\n'
        if slide_id > 1:
            with_div += '</div>\n'
        return with_div


class TutorialAccess(models.Model):
    first_access = models.DateTimeField('first accessed', auto_now_add=True)
    last_access = models.DateTimeField('last accessed', auto_now=True)
    access_count = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tutorial = models.ForeignKey(Tutorial, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username}: Tutorial {self.tutorial.id} First Access[{self.first_access}] Last Access[{self.last_access}] Access Count[{self.access_count}]'
