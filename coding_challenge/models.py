from django.db import models
from django.utils.text import slugify
import markdown


class Tag(models.Model):
    name = models.CharField(max_length=128)
    slug = models.CharField(max_length=128)
    order = models.IntegerField(default=99)

    class Meta:
        ordering = ['order', 'slug']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ChallengeRepo(models.Model):
    remote = models.URLField()
    slug = models.SlugField()
    last_commit = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.slug} ({self.remote})'


class CodingChallenge(models.Model):
    title = models.CharField(max_length=1024)
    slug = models.SlugField()
    repo = models.ForeignKey(ChallengeRepo, on_delete=models.CASCADE)
    question = models.TextField()
    published = models.BooleanField(default=True)
    show_stdout = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag)
    function_name = models.CharField(max_length=50, blank=True)
    deleted = models.BooleanField(default=False)

    @property
    def question_html(self):
        return markdown.markdown(self.question, extensions=['extra', 'codehilite'])

    def __str__(self):
        return self.title
