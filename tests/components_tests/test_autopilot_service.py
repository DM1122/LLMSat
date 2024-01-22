from typing import List

import krpc
import pytest

from llmsat.components.autpilot import AutopilotService, Node
from llmsat.libs import utils


@pytest.fixture(scope="session")
def ksp_connection():
    """Manage KSP connection"""
    if not utils.is_ksp_running():
        print("KSP is not running. Run KSP and enter a flight scenario to run tests.")
        pytest.exit("Exiting due to lack of KSP connection.", 1)

    connection = krpc.connect(name="Testing")
    yield connection
    connection.close()


def test_plan_apoapsis_maneuver(ksp_connection):
    service = AutopilotService(ksp_connection)

    nodes: List[Node] = service.plan_apoapsis_maneuver(50)
    print(nodes)


def test_execute_maneuver_nodes(ksp_connection):
    service = AutopilotService(ksp_connection)

    new_orbit: Orbit = service.execute_maneuver_nodes()
    print(new_orbit)


def test_get_nodes(ksp_connection):
    service = AutopilotService(ksp_connection)

    output = service.get_nodes()

    print(output)


def test_remove_nodes(ksp_connection):
    service = AutopilotService(ksp_connection)

    output = service.remove_nodes()

    print(output)


def test_launch(krpc_connection):
    service = AutopilotService(ksp_connection)

    output = service.launch()


def test_landing(krpc_connection):
    service = AutopilotService(ksp_connection)

    output = service.land()
