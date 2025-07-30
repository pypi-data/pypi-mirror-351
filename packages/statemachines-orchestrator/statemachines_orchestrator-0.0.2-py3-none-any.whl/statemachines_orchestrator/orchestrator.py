import sys
import typing
from functools import partial, wraps
from typing import Any

from statemachine import StateMachine
from statemachine.event_data import TriggerData

from statemachines_orchestrator.exceptions import (
    StateFieldIsNotUnique,
    AnnotationIsNotAStateMachine,
    NoMachinesOnOrchestrator,
)
from statemachines_orchestrator.utils import (
    _set_new_attribute,
    _create_fn,
    _get_machines_annotations,
)

DUNDER_INIT = "__init__"
MACHINE_CLASSES = "_machine_classes"
ORCHESTRATOR_NAME = "_orchestrator_name"
DEFAULT_ORCHESTRATOR_NAME = "orc"
DEFAULT_MACHINE_STATE_FIELD = "state"


class _OrchestratorType(type):
    def _add_init_method(cls, machine_classes: dict[str, type[StateMachine]]):
        body_lines = []

        for machine_name, machine_class in machine_classes.items():
            body_lines.append(f"self.{machine_name} = {machine_name}")

        if not body_lines:
            raise NoMachinesOnOrchestrator(f"{cls.__name__} has no machines")

        body_lines += ["self._patch_machines()", "self._perform_initial_checks()"]

        print(len(sys.modules.keys()))

        print(cls.__module__)

        _globals = sys.modules[cls.__module__].__dict__
        _locals: dict = {}

        args = ["self"] + list(
            f"{machine_name}: {machine_class.__name__}"
            for machine_name, machine_class in machine_classes.items()
        )

        _set_new_attribute(
            cls,
            DUNDER_INIT,
            _create_fn(
                DUNDER_INIT,
                args,
                body_lines,
                locals=_locals,
                globals=_globals,
                return_type=None,
            ),
        )

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        *,
        orchestrator_name: str = DEFAULT_ORCHESTRATOR_NAME,
    ) -> type:
        if not bases:
            return super().__new__(mcs, name, bases, namespace)

        cls = super().__new__(mcs, name, bases, namespace)

        cls_annotations = namespace.get("__annotations__", {})

        maybe_machine_classes = _get_machines_annotations(
            cls,
            cls_annotations,
        )

        machine_classes: dict[str, type[StateMachine]] = {}
        for machine_name, machine_class in maybe_machine_classes.items():
            if not issubclass(machine_class, StateMachine):
                raise AnnotationIsNotAStateMachine(
                    f"{machine_name} is not a subclass of {StateMachine.__name__}"
                )

            machine_classes[machine_name] = machine_class

        setattr(cls, MACHINE_CLASSES, machine_classes)
        setattr(cls, ORCHESTRATOR_NAME, orchestrator_name)

        cls._add_init_method(machine_classes)

        return cls


@typing.dataclass_transform()
class Orchestrator(metaclass=_OrchestratorType):
    """The state machines orchestrator class."""

    @property
    def machine_classes(self) -> dict[str, type[StateMachine]]:
        return getattr(self.__class__, MACHINE_CLASSES)

    @property
    def orchestrator_name(self) -> str:
        return getattr(self.__class__, ORCHESTRATOR_NAME)

    @property
    def machines(self) -> dict[str, StateMachine]:
        return {
            machine_name: getattr(self, machine_name)
            for machine_name in self.machine_classes.keys()
        }

    def _patch_send(self) -> None:
        for machine_name, machine_instance in self.machines.items():
            method = machine_instance.send
            setattr(
                machine_instance,
                "send",
                partial(method, **{self.orchestrator_name: self}),
            )

    def _patch_put_nonblocking(self) -> None:
        """
        This method patches the `_put_nonblocking` method of the state machines
        to add the orchestrator instance to the trigger data, making it accessible
        from the callbacks.
        """
        for machine_name, machine_instance in self.machines.items():
            method = machine_instance._put_nonblocking

            @wraps(method)
            def patched_method(trigger_data: TriggerData):
                trigger_data.kwargs[self.orchestrator_name] = self
                # Events and transitions rely on a proxy of the state machine,
                # therefore, the appending to `machine_instance._engine` will
                # not add the event to the right state machine engine.
                # We operate on the engine directly as we don't want to
                # create an infinite loop.
                trigger_data.machine._engine.put(trigger_data)

            machine_instance._put_nonblocking = patched_method  # type: ignore[method-assign]

    def _patch_machines(self) -> None:
        """
        This method performs the patches for the state machines.

        It is called in the generated Orchestrator.__init__ method.
        """
        self._patch_send()
        self._patch_put_nonblocking()

    def _check_all_machines_state_fields_are_unique(self) -> None:
        state_fields = set()
        for machine_name, machine_instance in self.machines.items():
            state_field = getattr(machine_instance, "state_field")
            if state_field in state_fields:
                if state_field == DEFAULT_MACHINE_STATE_FIELD:
                    raise StateFieldIsNotUnique(
                        f"state_field '{state_field}' is not unique for '{machine_name}'.\nHint: you should override the default by providing a `state_field` argument on '{machine_name}' initialization."
                    )
                raise StateFieldIsNotUnique(
                    f"state_field '{state_field}' is not unique for '{machine_name}'"
                )
            state_fields.add(state_field)

    def _perform_initial_checks(self) -> None:
        """
        This method performs initial checks on the state machines.
        Ensuring that no unexpected behavior occurs from machine definition.

        It is called in the generated Orchestrator.__init__ method.
        """
        self._check_all_machines_state_fields_are_unique()
