from django.apps import AppConfig


class TesteDeMesaConfig(AppConfig):
    name = 'teste_de_mesa'

    def ready(self):
        import teste_de_mesa.signals
