# Generated by Django 3.1.3 on 2021-08-05 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0008_auto_20210312_2102'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]