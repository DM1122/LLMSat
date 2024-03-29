import krpc
import pytest

from llmsat.components.spacecraft_manager import SpacecraftManager
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


def test_get_spacecraft_properties(ksp_connection):
    service = SpacecraftManager(ksp_connection)

    properties = service.get_spacecraft_properties()
    print(properties)


def test_get_parts_tree(ksp_connection):
    service = SpacecraftManager(ksp_connection)

    output = service.get_parts_tree()
    print(output)


def test_get_met(ksp_connection):
    service = SpacecraftManager(ksp_connection)

    output = service.get_met()
    print(output)


def test_get_ut(ksp_connection):
    service = SpacecraftManager(ksp_connection)

    output = service.get_ut()
    print(output)


def test_get_resources(ksp_connection):
    service = SpacecraftManager(ksp_connection)

    output = service.get_resources()
    print(output)
