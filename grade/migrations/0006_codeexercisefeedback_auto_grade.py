# Generated by Django 3.1.3 on 2021-05-05 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grade', '0005_auto_20210505_1757'),
    ]

    operations = [
        migrations.AddField(
            model_name='codeexercisefeedback',
            name='auto_grade',
            field=models.FloatField(null=True),
        ),
    ]
