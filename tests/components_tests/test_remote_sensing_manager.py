import krpc
import pytest

from llmsat.components.remote_sensing_manager import RemoteSensingManager
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


def test_run_scanner(ksp_connection):
    service = RemoteSensingManager(ksp_connection)

    output = service.get_module()
    print(output)
