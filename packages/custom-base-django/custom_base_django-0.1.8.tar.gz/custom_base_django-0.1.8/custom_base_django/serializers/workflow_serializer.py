from os import access
from django.apps import apps

from .state_serializer import StateSerializer
from ..models import Workflow, WorkflowState, WorkflowHistory
from ..models.base import CustomGenericRelation
from ..utils import first_upper

_workflow_serializer_classes = dict()


class WorkFlowSerializer:
    workflow: Workflow = None
    nested_serializer_classes = dict()
    serializers = list()

    @staticmethod
    def get_name(workflow_name, method):
        serializer_name = f'{first_upper(workflow_name)}{first_upper(method)}Serializer'
        return serializer_name

    @classmethod
    def get_class_serializers(cls, wf_name, method="get"):
        class_name = cls.get_name(workflow_name=wf_name, method=method)
        if class_name not in _workflow_serializer_classes.keys():
            wf_class_serializer = type(class_name, (cls,), {})
            wf_class_serializer.workflow = Workflow.objects.filter(name=wf_name).first()
            wf_class_serializer.all_states = wf_class_serializer.workflow.states.all().order_by("order_number")
            wf_class_serializer.workflow_history = WorkflowHistory.objects.filter(
                workflow=wf_class_serializer.workflow).order_by('-id')
            wf_class_serializer.wf_history_serializer_class = WorkflowHistory.get_serializer(method=method)
            wf_class_serializer.wf_state_serializer_class = WorkflowState.get_serializer(method=method)
            wf_class_serializer.state_serializers = None
            wf_class_serializer.wf_history_serializer = None
            wf_class_serializer.wf_first_history_serializer = None
            _workflow_serializer_classes[class_name] = wf_class_serializer
        return _workflow_serializer_classes[class_name]

    def __init__(self, object_id=None, user=None, data=None, ):
        self.method = getattr(self, 'method', 'get')
        self.object_id = object_id
        self.workflow_history = self.workflow_history.filter(object_id=object_id)
        last_workflow_history = self.workflow_history.first()
        self.current_state = last_workflow_history.state if last_workflow_history else self.all_states.first()
        self.main_serializers_class = StateSerializer.get_class_serializer(state=self.current_state,
                                                                            method=self.method)
        self.errors = {}
        self._data = data

    def run_validation(self, data=None):
        data = data or self._data or {}
        _errors = {}
        _serializers = {}
        self.serializers = list()
        if data.get('main_data', {}):
            self.state_serializers = self.main_serializers_class(pk=self.object_id, data=data.get('main_data', {}))
            _serializers.update({'main_data': self.state_serializers})
        self.wf_history_instance = WorkflowHistory(workflow=self.workflow, object_id=self.object_id)
        self.wf_history_instance.previous_state = self.current_state
        wf_data = data.get('wf_data', {})
        wf_history_count = self.workflow_history.count()
        if wf_data:
            self.wf_history_serializer = self.wf_history_serializer_class(instance=self.wf_history_instance,
                                                                          data=data.get('wf_data', {}))
            _serializers.update({'wf_data':self.wf_history_serializer})
        if not wf_history_count and (not wf_data or (wf_data and wf_data.get('target_state'))):
            self.wf_first_history_serializer = self.wf_history_serializer_class(instance=self.wf_history_instance,
                                                                                data=data.get('wf_data', {}))
            _serializers.update({'wf_data':self.wf_first_history_serializer})

        for key, serializer in _serializers.items():
            if serializer.is_valid():
                self.serializers.append(serializer)

    def is_valid(self):
        if not self.serializers:
            self.run_validation(self._data)
        return not self.errors

    def to_representation(self, **kwargs):
        data = {}
        wf_serializer_instance = WorkflowHistory(workflow=self.workflow, object_id=self.object_id, state=self.current_state)
        data["wf_data"] = self.wf_history_serializer_class(instance=wf_serializer_instance).data
        # to do - update choice of state based allowed ...
        data["wf-history"] = self.wf_history_serializer_class(instance=self.workflow_history, with_nested=False,include_metadata=False).data
        data["wf-states"] = self.wf_state_serializer_class(self.all_states).data
        data["main_data"] = self.main_serializers_class(pk=self.object_id,).data
        return data

    def save(self, **kwargs):
        if self.is_valid():
            for serializer in self.serializers:
                serializer.save(**kwargs)
