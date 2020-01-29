from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
import pandas as pd
from pathlib import Path
from course.models import Class


class Command(BaseCommand):
    help = 'Create users from Blackboard file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='Indicates the file to be used')
        parser.add_argument('course', type=str, help='Indicates the name of the course to add the students')

    def handle(self, *args, **kwargs):
        filename = Path(kwargs['filename'])
        coursename = kwargs['course']
        if 'csv' in filename.suffix:
            df = pd.read_csv(filename)
        elif 'xls' in filename.suffix:
            df = pd.read_excel(filename)
        else:
            return
        course = Class.objects.get(name=coursename)
        for user_data in df.iterrows():
            first_name = user_data[1]['Nome']
            try:
                last_name = user_data[1]['Sobrenome']
            except:
                first_name = first_name.split(' ')[0]
                last_name = ' '.join(first_name.split(' ')[1:])
            username = user_data[1]['Nome do usuário']
            email = username + '@al.insper.edu.br'
            users_same_name = User.objects.filter(username=username)
            if not users_same_name:
                print('Creating user: {0}'.format(username))
                User.objects.create_user(username=username, email=email, password=username, first_name=first_name, last_name=last_name)
            user = User.objects.get(username=username)
            if user not in course.students.all():
                print('Adding {0} in {1}'.format(username, coursename))
                course.students.add(user)
        course.save()
