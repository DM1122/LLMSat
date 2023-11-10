import krpc
from llmsat import utils
from llmsat.components import EPS

import pytest


@pytest.fixture(scope="session")
def ksp_connection():
    if not utils.is_ksp_running():
        print("KSP is not running. Run KSP and enter a flight scenario to run tests.")
        pytest.exit("Exiting due to lack of KSP connection.", 1)

    connection = krpc.connect(name="Testing")
    yield connection
    connection.close()


def test_get_parts_tree(ksp_connection):
    vessel = ksp_connection.space_center.active_vessel

    

    print(vessel.name)
