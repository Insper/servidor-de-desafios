from io import TextIOWrapper
import pandas as pd
from django.contrib import admin, messages
from django.forms import ModelForm, FileField
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ngettext

from code_challenge.repo import update_from_git
from .models import FrontendUpdateUrl, PyGymUser, Concept, ChallengeRepo, UserTag, Semester


class UserInline(admin.TabularInline):
    model = PyGymUser.tags.through
    extra = 0
    classes = ['collapse']


class UserTagForm(ModelForm):
    blackboard_file = FileField(required=False)

    class Meta:
        model = UserTag
        fields = '__all__'


class UserTagAdmin(admin.ModelAdmin):
    inlines = (UserInline, )
    fieldsets = ((None, {
        'fields': (
            'tag',
            'slug',
        )
    }), ('Blackboard user file', {
        'fields': ('blackboard_file', )
    }))

    form = UserTagForm

    def add_tag(self, blackboard_file, tag):
        if blackboard_file is None:
            return
        text_f = TextIOWrapper(blackboard_file, encoding='utf-16')
        df = pd.read_csv(text_f, sep='\t')

        for user_data in df.iterrows():
            username = user_data[1]['Nome do usuário']
            user = PyGymUser.objects.filter(username__iexact=username).last()
            if user:
                user.tags.add(tag)
                user.save()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        self.add_tag(form.cleaned_data.get('blackboard_file'), obj)


def resetar_usuarios(modeladmin, request, queryset):
    for old_user in queryset:
        new_user = PyGymUser()
        new_user.username = old_user.username
        new_user.first_name = old_user.first_name
        new_user.last_name = old_user.last_name
        new_user.email = old_user.email
        new_user.password = old_user.password
        new_user.additional_quiz_time_percent = old_user.additional_quiz_time_percent
        new_user.additional_quiz_time_absolute = old_user.additional_quiz_time_absolute
        old_user.username = old_user.username + '_old'
        old_user.save()
        new_user.save()


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('tags',)
    list_filter = UserAdmin.list_filter + ('tags',)
    fieldsets = UserAdmin.fieldsets + (('Tags', { 'fields': ('tags',) }),('Quiz time', { 'fields': ('additional_quiz_time_percent'
, 'additional_quiz_time_absolute')}))
    actions = [resetar_usuarios]

    def tags(self):
        return ','.join(tag for tag in self.tags.all())




class ChallengeRepoAdmin(admin.ModelAdmin):
    actions = ['update_data']

    def update_data(self, request, queryset):
        for repo in queryset:
            update_from_git(repo)
        n_repos = len(queryset)
        self.message_user(request, ngettext(
            f'{n_repos} repo was successfully updated.',
            f'{n_repos} repos were successfully updated.',
            n_repos,
        ), messages.SUCCESS)
    update_data.short_description = 'Update data from selected repositories'


admin.site.register(PyGymUser, CustomUserAdmin)
admin.site.register(Concept)
admin.site.register(ChallengeRepo, ChallengeRepoAdmin)
admin.site.register(FrontendUpdateUrl)
admin.site.register(UserTag, UserTagAdmin)
admin.site.register(Semester)
