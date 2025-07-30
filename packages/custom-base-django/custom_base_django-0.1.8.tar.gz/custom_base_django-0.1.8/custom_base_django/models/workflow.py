from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q, F
from ..language_utils import translate as _
from .base import BaseModelWitDateNotFiscalDelete, BaseModelContentType
from .choices import ChoiceForeignKey
from django.contrib.auth import get_user_model

User = get_user_model()


class Workflow(BaseModelWitDateNotFiscalDelete):
    name = models.CharField(max_length=100, verbose_name="workflow_name")
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))
    # content_type_wf = models.ForeignKey(ContentType, verbose_name=_('related model'), on_delete=models.CASCADE)
    transition_status = ChoiceForeignKey(verbose_name=_('transition status'), limit_title='transition_status',
                                         related_name='transition_status')

    def __str__(self):
        return f'{self.name}--{self.content_type_wf.model}'

    @property
    def urls(self):
        urls = {
            'create_url': f'/workflows/{self.id}/{self.name}/create/1',
            'update_url': f'/workflows/{self.id}/{self.name}/update/{self.pk}',
            'delete_url': f'/workflows/{self.id}/{self.name}/delete/{self.pk}',
            'get_url': f'/workflows/{self.id}/{self.name}/get/{self.pk}',
        }
        url = urls.get('create_url')

        return url, urls


class WorkflowState(BaseModelWitDateNotFiscalDelete):
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="states")
    name = models.CharField(max_length=100, verbose_name=_("WorkflowState_name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("description"))
    can_transition_to = models.ManyToManyField('self', blank=True, verbose_name=_("can_transition_to"))
    next_state = models.ForeignKey('self', on_delete=models.CASCADE, related_name="self_next_state",
                                   verbose_name=_("next_state"), blank=True, null=True)
    previous_state = models.ForeignKey('self', on_delete=models.CASCADE, related_name="self_previous_state",
                                       verbose_name=_("previous_state"), blank=True, null=True)
    serializer_struct = models.JSONField(verbose_name=_("form_struct"), default=list)
    extra_data = models.JSONField(verbose_name=_("extra_data"), default=dict, null=True, blank=True)
    order_number = models.IntegerField(verbose_name=_("order_number"), default=0)
    get_single_form = models.BooleanField(default=False, verbose_name=_("get_single_form"))

    def __str__(self):
        return f'{self.name}'

    @property
    def get_workflow_states(self):
        return self.workflow.states.all()

    @property
    def is_first_state(self):
        first_state = WorkflowState.objects.filter(workflow_id=self.workflow.id).order_by('order_number').first()
        return first_state and first_state.id == self.id, first_state

    @property
    def is_last_state(self):
        last_state = WorkflowState.objects.filter(workflow_id=self.workflow.id).order_by('-order_number').first()
        return last_state and last_state.id == self.id, last_state

    @property
    def get_next_state(self):
        return WorkflowState.objects.filter(
            workflow=self.workflow,
            order_number__gt=self.order_number
        ).annotate(distance=F('order_number') - self.order_number).order_by('distance').first()

    @property
    def get_previous_state(self):
        return WorkflowState.objects.filter(
            workflow=self.workflow,
            order_number__lt=self.order_number
        ).annotate(distance=self.order_number - F('order_number')).order_by('distance').first()

    def auto_transition(self, direction='next'):
        if direction == 'next':
            func_res = self.call_transition_method('next_state_func')
            return func_res if func_res else (None if self.is_last_state()[0] else self.get_next_state())

        elif direction == 'previous':
            func_res = self.call_transition_method('previous_state_func')
            return func_res if func_res else (None if self.is_first_state()[0] else self.get_previous_state())

    @staticmethod
    def execute_action_from_function(method, **kwargs):
        method_func = globals()[method]
        if callable(method_func):
            return method_func(state=kwargs.pop('state'), **kwargs)

    def call_transition_method(self, func_name=None, **kwargs):
        if func_name:
            check_transition_method = self.extra_data.get(func_name, {})
            if check_transition_method:
                method_func = self.execute_action_from_function(check_transition_method, state=self, **kwargs)
                return method_func
        return dict()


    def get_allowed_states(self, list_states=None):
        try:
            all_states = list(self.get_workflow_states().values('id', 'name', 'order_number')) or list_states

            tran_status = self.workflow.transition_status.choice_value
            all_states.sort(key=lambda x: x['order_number'])

            allowed_states = {state['id']: state for state in
                              self.can_transition_to.values('id', 'name', 'order_number')}

            def calculate_enable(state):
                if tran_status == "enable":
                    return 'True' if state['id'] in allowed_states else 'False'
                elif tran_status == "next_enable":
                    return 'True' if state['id'] in allowed_states and state[
                        'order_number'] > self.order_number else 'False'
                elif tran_status == "previous_enable":
                    return 'True' if state['id'] in allowed_states and state[
                        'order_number'] < self.order_number else 'False'
                return 'False'

            final_states = [
                {**state, 'verbose_name': _(state['name']), 'enable': calculate_enable(state)}
                for state in all_states
            ]
        except Exception as e:
            raise e
        finally:
            return final_states

    @property
    def state_extra_data(self):
        return {
            'next_state': self.next_state.name if self.last_state.next_state else None,
            'previous_state': self.previous_state.name if self.previous_state else None,
            'is_first_state': self.is_first_state[0],
            'is_last_state': self.is_last_state[0]
        }

    def get_meta_datas(self, fields=None, base_access=None, **kwargs):
        super().get_meta_datas(fields)
        self._meta_datas['state'] = self.state_value_meta_data()
        return self._meta_datas

    def state_value_meta_data(self, default=""):
        res = {
            "verbose_name": _('state'),
            "required": False,
            "validators": [],
            "read_only": True,
            "type": None,
            'default': default or {"id": self.id, "value": str(self)},
        }

        allowed_states = self.get_allowed_states()

        res.update({'type': 'list', 'choice': allowed_states})
        return res


class WorkflowHistory(BaseModelContentType):
    TYPE = (
        ('update', _('Update')),
        ('create', _('Create'))
    )
    workflow = models.ForeignKey(Workflow, on_delete=models.DO_NOTHING, related_name="workflow_histories")
    state = models.ForeignKey(WorkflowState, on_delete=models.DO_NOTHING, related_name="state_histories",
                              null=True, blank=True)
    action_type = models.CharField(max_length=100, choices=TYPE, verbose_name=_("action_type")
                                   , default='update', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_histories",
                             verbose_name=_("creator user"))
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_histories",
                                verbose_name=_("assign to user"), null=True, blank=True)
    additional_data = models.JSONField(default=dict, blank=True, verbose_name=_("additional data"))
    description = models.CharField(max_length=255, verbose_name=_("description"), null=True, blank=True)
    deadline = models.DateTimeField(verbose_name=_("deadline"), null=True, blank=True)
    target_state = None

    def get_meta_datas(self, fields=None, base_access=None, **kwargs):
        super().get_meta_datas(fields)
        if self.pk and self.previous_state:
            default = {"id": self.previous_state.id, "value": str(self.self.previous_state)} if self.self.previous_state else ''
            self._meta_datas['state_value'] = self.previous_state.state_value_meta_data(default=default)
        return self._meta_datas

    @property
    def previous_state(self):
        return self.state

    @property
    def target_state(self):
        return self.target_state

    @target_state.setter
    def target_state(self, value):
        previous_state = self.previous_state
        allowed_state = previous_state.get_allowed_states()

        if any([value == 'next', value == 'previous']):
            state = previous_state.auto_transition(direction=value)

        elif isinstance(value, int) and value != previous_state.id:
            state = WorkflowState.objects.filter(id=value).order_by('id').first()

        else:
            state = previous_state

        state.call_transition_method()
        self.check_transition_method(allowed_state=allowed_state, state=state)

    def check_transition_method(self, allowed_state=None, state=None, **kwargs):
        target_state = state
        previous_state = self.state or self.current_state
        can_transition_to_id = list(
            previous_state.can_transition_to.values_list('id', flat=True)) if previous_state.can_transition_to else []

        current_choice = next(
            (choice for choice in allowed_state if
             target_state.id and choice['id'] == int(target_state.id) and choice['enable'] == 'True'),
            None
        )

        try:
            if current_choice and current_choice.get('id') in can_transition_to_id or int(
                    target_state.id) == self.state.id:
                target_state = current_choice
        except Exception:
            self.raise_validation_error('access error', f'you dont have access to state ({state.name})')
        func_res = self.state.call_transition_method(func_name='check_transition_func', **kwargs)
        return func_res or target_state

    @classmethod
    def get_serializer(cls, struct_name='default', method='get', **kwargs):

        serializer_name = cls.serializer_name(method, struct_name)

        if serializer_name not in cls.serializer_classes().keys():
            serializer_base_class = cls.serializer_base_struct.get_serializer_base_class(struct_name)

            return super()._get_model_serializer(struct_name=struct_name, method=method,
                                                 serializer_base_class=serializer_base_class, **kwargs)
        return super().get_serializer(method=method, struct_name=struct_name, **kwargs)

    def __str__(self):
        return f'{self.state} : {self.description}'

    def save(self, *args, **kwargs):
        if not self.action_type:
            self.action_type = 'create'
        super().save(*args, **kwargs)
