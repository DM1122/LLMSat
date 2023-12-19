from datetime import datetime

import krpc
import pytest

from llmsat import utils
from llmsat.components.alarm_manager import AlarmManager


@pytest.fixture(scope="session")
def ksp_connection():
    """Manage KSP connection"""
    if not utils.is_ksp_running():
        print("KSP is not running. Run KSP and enter a flight scenario to run tests.")
        pytest.exit("Exiting due to lack of KSP connection.", 1)

    connection = krpc.connect(name="Testing")
    yield connection
    connection.close()


def test_get_alarms(ksp_connection):
    service = AlarmManager(ksp_connection)

    output = service.get_alarms()
    print(output)


def test_add_alarm(ksp_connection):
    service = AlarmManager(ksp_connection)

    output = service.add_alarm(
        name="TestAlarm", time=60, description="Some description"
    )
    print(output)
