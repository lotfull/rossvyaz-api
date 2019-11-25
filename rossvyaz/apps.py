from django.apps import AppConfig


class RossvyazConfig(AppConfig):
    name = 'rossvyaz'

    def ready(self):
        from . import info
        info.update_nums_df()
