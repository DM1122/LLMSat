from datetime import datetime, timedelta
from llmsat.components.alarm_manager import AlarmManager
import pytest


@pytest.fixture
def alarm_manager():
    return AlarmManager()


def test_get_set_alarm(alarm_manager: AlarmManager):
    alarms = alarm_manager.get_alarms()
    assert len(alarms) == 0

    alarm_manager.set_alarm(name="Test", description="Test Alarm", epoch=datetime.now())

    alarms = alarm_manager.get_alarms()
    print(alarms)
    assert len(alarms) == 1


def test_delete_alarm(alarm_manager: AlarmManager):
    alarm_manager.set_alarm(name="Test", description="Test Alarm", epoch=datetime.now())
    assert len(alarm_manager.get_alarms()) == 1

    alarm_manager.delete_alarm(id=0)
    assert len(alarm_manager.get_alarms()) == 0


def test_check_alarms(alarm_manager: AlarmManager):
    now = datetime.now()
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)

    alarm_manager.set_alarm(name="Past", description="Past Alarm", epoch=past)
    alarm_manager.set_alarm(name="Future", description="Future Alarm", epoch=future)

    expired_alarms = alarm_manager.check_alarms(now)
    assert len(expired_alarms) == 1
    assert expired_alarms[0].name == "Past"
    assert len(alarm_manager.get_alarms()) == 1
    assert 0 not in alarm_manager.get_alarms()
