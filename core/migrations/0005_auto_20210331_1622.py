# Generated by Django 3.1.3 on 2021-03-31 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20210209_2212'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=128)),
                ('slug', models.SlugField(max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='pygymuser',
            name='tags',
            field=models.ManyToManyField(related_name='users', to='core.UserTag'),
        ),
    ]