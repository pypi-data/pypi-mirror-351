
from django.apps import AppConfig
from .utils import add_dynamic_property


class CustomBaseDjango(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_base_django'

    def ready(self):
        add_dynamic_property()
        from . import functions
        # from .serializers.base import DynamicFieldsModelSerializer
        # class XTR:
        #     base = DynamicFieldsModelSerializer.BaseStruct()
        # x = XTR()
        # x.base.get_serializer_base_class("default")

        # from .models.choices import Choice
        # Choice.serializerBaseStruct.get_serializer_base_class('default')
