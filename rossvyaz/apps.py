from django.apps import AppConfig


class RossvyazConfig(AppConfig):
    name = 'rossvyaz'

    def ready(self):
        from rossvyaz.core import info
        from django.db import connection
        if 'rossvyaz_phone' in connection.introspection.table_names():
            info.update_info()
