from django.apps import AppConfig


class RossvyazConfig(AppConfig):
    name = 'rossvyaz'

    def ready(self):
        from rossvyaz.core import info
        info.update_info()
