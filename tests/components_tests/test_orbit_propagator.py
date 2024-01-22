import krpc
import pytest

from llmsat.components.orbit_propagator import OrbitPropagator
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


def test_get_orbit(ksp_connection):
    service = OrbitPropagator(ksp_connection)

    output = service.get_orbit()

    print(output)
