from django.apps import AppConfig


class RossvyazConfig(AppConfig):
    name = 'rossvyaz'

    def ready(self):
        from . import info, timeloop
        info.update_info(True)
