from django.apps import AppConfig


class CodingChallengeConfig(AppConfig):
    name = 'coding_challenge'

    def ready(self):
        import coding_challenge.signals
