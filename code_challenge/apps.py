from django.apps import AppConfig


class CodeChallengeConfig(AppConfig):
    name = 'code_challenge'

    def ready(self):
        import code_challenge.signals
