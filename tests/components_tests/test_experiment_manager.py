from typing import List

import krpc
import pytest

from llmsat.components.experiment_manager import (
    DataProperties,
    Experiment,
    ExperimentManager,
)
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


def test_get_experiments(ksp_connection):
    service = ExperimentManager(ksp_connection)

    output: dict[str, Experiment] = service.get_experiments()
    print(output)


def test_run_experiment(ksp_connection):
    service = ExperimentManager(ksp_connection)

    output: DataProperties = service.run_experiment("Temperature Scan")
    print(output)
