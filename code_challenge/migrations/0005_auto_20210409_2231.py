# Generated by Django 3.1.3 on 2021-04-10 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('code_challenge', '0004_userchallengeinteraction_latest_submission'),
    ]

    operations = [
        migrations.AddField(
            model_name='codechallenge',
            name='difficulty',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='codechallenge',
            name='weight',
            field=models.IntegerField(default=1),
        ),
    ]