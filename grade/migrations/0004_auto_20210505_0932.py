# Generated by Django 3.1.3 on 2021-05-05 12:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('grade', '0003_auto_20210504_1735'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='codeexercisegrade',
            name='feedback',
        ),
        migrations.CreateModel(
            name='CodeExerciseFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback', models.TextField(blank=True)),
                ('manual_grade', models.FloatField()),
                ('grade_schema', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grade.codeexercisegrade')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='subchallengeautofeedback',
            name='full_feedback',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='grade.codeexercisefeedback'),
            preserve_default=False,
        ),
    ]