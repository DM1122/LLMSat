import krpc
import pytest

from llmsat.components.orbit_propagator import OrbitPropagator
from llmsat.libs import utils
from datetime import datetime, timedelta


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


def test_radius_at(ksp_connection):
    service = OrbitPropagator(ksp_connection)

    # Define the fixed start time: January 3, 2045, 19:35
    date_start = datetime(2045, 1, 3, 19, 35)
    date_end = date_start + timedelta(minutes=60)

    output = service.radius_at(date=date_start, date_end=date_end)

    print(output)


def test_validate_orbit(ksp_connection):
    service = OrbitPropagator(ksp_connection)

    output = service.validate_orbit()

    print(output)
