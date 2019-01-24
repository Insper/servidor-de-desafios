from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
import pandas as pd


class Command(BaseCommand):
    help = 'Create users from Blackboard file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='Indicates the file to be used')

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']
        df = pd.read_csv(filename)
        for user_data in df.iterrows():
            first_name = user_data[1]['Nome']
            last_name = user_data[1]['Sobrenome']
            username = user_data[1]['Nome do usuário']
            email = username + '@al.insper.edu.br'
            users_same_name = User.objects.filter(username=username)
            if not users_same_name:
                print('Creating user: {0}'.format(username))
                User.objects.create_user(username=username, email=email, password=username, first_name=first_name, last_name=last_name)