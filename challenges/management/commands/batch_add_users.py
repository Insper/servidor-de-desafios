from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
import pandas as pd
from pathlib import Path


class Command(BaseCommand):
    help = 'Create users from Blackboard file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='Indicates the file to be used')

    def handle(self, *args, **kwargs):
        filename = Path(kwargs['filename'])
        if 'csv' in filename.suffix:
            df = pd.read_csv(filename)
        elif 'xls' in filename.suffix:
            df = pd.read_excel(filename)
        else:
            return
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
