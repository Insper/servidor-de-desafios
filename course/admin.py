from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from .models import Class

class ClassAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name',)
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

admin.site.register(Class, ClassAdmin)
