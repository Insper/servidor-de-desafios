from django.apps import AppConfig


class TraceChallengeConfig(AppConfig):
    name = 'trace_challenge'

    def ready(self):
        import trace_challenge.signals
