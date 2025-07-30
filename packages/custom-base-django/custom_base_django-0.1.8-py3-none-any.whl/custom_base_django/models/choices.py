from unicodedata import category

from .base import BaseModelFiscalDelete, BaseModelWitDateNotFiscalDelete
from django.db import models
from django.db.models import QuerySet, Q
from ..utils import Defaults
from .base import BaseModelWitDateNotFiscalDelete
from ..language_utils import translate as _


class Choice(BaseModelFiscalDelete):
    migratable_data = True
    title = models.CharField(max_length=255, verbose_name="Choice Title")
    title_en = models.CharField(max_length=255, verbose_name="Choice Name (English)")
    title_fa = models.CharField(max_length=255, verbose_name="Choice Name (Farsi)")
    title_bz = models.CharField(max_length=255, verbose_name="Choice Name (Native)")

    @property
    def category(self):
        return self.title

    @category.setter
    def category(self, value):
        self.title = value

    @property
    def choice_value(self):
        return self.title_en

    @choice_value.setter
    def value(self, value):
        self.title_en = value

    @classmethod
    def _get_model_serializer(cls, method: str, struct_name, serializer_base_class=None):
        if struct_name == 'default':
            serializer_base_class.fields = ['category', 'choice_value']
        super()._get_model_serializer(method, struct_name, serializer_base_class)

    def __str__(self):
        return f'{self.title_en}'


class ChoiceForeignKey(models.ForeignKey):
    def __init__(self,
                 limit_title=None,
                 **kwargs,
                 ):
        limit_choices_to = kwargs.get('limit_choices_to')
        if limit_title or limit_choices_to:
            kwargs['limit_choices_to'] = limit_choices_to if limit_choices_to else Q(title=limit_title)
        kwargs['default'] = kwargs.get('default', Defaults(model=Choice, filters=Q(title=limit_title)).object)
        kwargs['default'] = Defaults(model=Choice, filters=Q(title=limit_title)).object
        kwargs['blank'] = kwargs.get('blank', True)
        kwargs['null'] = kwargs.get('null', True)
        kwargs['on_delete'] = kwargs.get('on_delete', models.SET_NULL)
        kwargs['related_name'] = kwargs.get('related_name', None) or kwargs.get(f'related_{limit_choices_to}', None)
        kwargs.pop('to', None)
        super().__init__('custom_base_django.Choice', **kwargs)
