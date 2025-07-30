from django.apps import AppConfig

from .services import setup_renderer


class VueSSRConfig(AppConfig):
    name = "vue_ssr"
    verbose_name = "Vue SSR"

    def ready(self):
        setup_renderer()
