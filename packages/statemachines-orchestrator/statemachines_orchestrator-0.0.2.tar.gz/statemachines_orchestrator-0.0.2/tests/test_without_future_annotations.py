from statemachines_orchestrator.orchestrator import Orchestrator
from tests.test_orchestrator import Machine1


def test_orchestrator_with_state_machine_type_annotation_should_compile():
    class _StateMachineOrchestrator(Orchestrator):
        machine1: Machine1
