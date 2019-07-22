import json
from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from .models import Class, ChallengeBlock
from challenges.models import Challenge


def _make_add_or_change_context(extra_context, class_id=None):
        extra_context = extra_context or {}
        challenges = Challenge.all_published()
        blocks = ChallengeBlock.objects.filter(block_class__id=class_id)
        unavailable_challenges_ids = set([c['id'] for b in blocks for c in b.challenges.values()])
        available_challenges = [c for c in challenges if c.id not in unavailable_challenges_ids]
        extra_context['challenges'] = challenges
        extra_context['blocks'] = blocks
        extra_context['available_challenges'] = available_challenges
        return extra_context


class ClassAdmin(admin.ModelAdmin):
    change_form_template = 'admin/course/course_change_form.html'

    fieldsets = (
        (None, {
            'fields': ('name', 'start_date', 'end_date',)
        }),
        ('Students', {
            'classes': ('collapse',),
            'fields': ('students',),
        }),
    )

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'students':
            kwargs['widget'] = CheckboxSelectMultiple()
            kwargs['help_text'] = ''

        return db_field.formfield(**kwargs)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = _make_add_or_change_context(extra_context)
        return super().add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = _make_add_or_change_context(extra_context, object_id)
        return super().change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Always delete all previous blocks because we don't want to keep this history (just trash)
        ChallengeBlock.objects.filter(block_class__id=obj.id).delete()
        blocks = json.loads(request.POST['blocks'])
        for block in blocks:
            new_block = ChallengeBlock(name=block['name'], release_date=block['release_date'], block_class=obj)
            new_block.save()
            for challenge_id in block['challenges']:
                new_block.challenges.add(challenge_id)
            new_block.save()

admin.site.register(Class, ClassAdmin)
