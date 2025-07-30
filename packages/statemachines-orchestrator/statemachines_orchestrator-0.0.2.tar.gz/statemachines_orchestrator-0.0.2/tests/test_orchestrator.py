from __future__ import annotations

import pytest
from statemachine import StateMachine, State

from statemachines_orchestrator.exceptions import (
    StateFieldIsNotUnique,
    NoMachinesOnOrchestrator,
    AnnotationIsNotAStateMachine,
)
from statemachines_orchestrator.orchestrator import Orchestrator
from tests.utils import missing_module


class Machine1(StateMachine):
    A1 = State("A1", initial=True)
    B1 = State("B1")
    C1 = State("C1", final=True)

    a1_to_b1 = A1.to(B1)
    b1_to_c1 = B1.to(C1)

    @staticmethod
    def after_a1_to_b1(orc: "OrchestratedStateMachines") -> None:
        orc.machine2.a2_to_b2()


class Machine2(StateMachine):
    A2 = State("A2", initial=True)
    B2 = State("B2", final=True)

    a2_to_b2 = A2.to(B2)

    @staticmethod
    def after_a2_to_b2(orc: "OrchestratedStateMachines") -> None:
        orc.machine1.b1_to_c1()


class OrchestratedStateMachines(
    Orchestrator,
    orchestrator_name="orc",  # can be omitted and defaults to "orc"
):
    machine1: Machine1
    machine2: Machine2


class Model:
    pass


def test_orchestrator():
    model = Model()
    orc = OrchestratedStateMachines(
        machine1=Machine1(model=model, state_field="machine1_state"),
        machine2=Machine2(model=model, state_field="machine2_state"),
    )

    assert orc.machine1.current_state_value == "A1"
    assert orc.machine2.current_state_value == "A2"

    orc.machine1.a1_to_b1()

    assert orc.machine1.current_state_value == "C1"
    assert orc.machine2.current_state_value == "B2"


def test_orchestrator_with_two_state_machines_having_the_same_state_field_should_raise():
    model = Model()
    with pytest.raises(StateFieldIsNotUnique):
        OrchestratedStateMachines(
            machine1=Machine1(model=model),
            machine2=Machine2(model=model),
        )

    with pytest.raises(StateFieldIsNotUnique):
        OrchestratedStateMachines(
            machine1=Machine1(model=model, state_field="same_state"),
            machine2=Machine2(model=model, state_field="same_state"),
        )


def test_orchestrator_with_no_machines_should_raise():
    with pytest.raises(NoMachinesOnOrchestrator):

        class _NoMachinesOrchestrator(Orchestrator):
            pass


def test_orchestrator_with_non_state_machines_type_annotations_should_raise():
    with pytest.raises(AnnotationIsNotAStateMachine):

        class _NonStateMachineOrchestrator(Orchestrator):
            machine1: str


def test_orchestrator_with_state_machine_type_annotation_should_compile():
    class _StateMachineOrchestrator(Orchestrator):
        machine1: Machine1


def test_should_raise_if_typing_module_is_missing():
    with pytest.raises(ModuleNotFoundError):
        with missing_module("typing"):

            class _StateMachineOrchestrator(Orchestrator):
                machine1: Machine1
