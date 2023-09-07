from datetime import datetime, timedelta
from llmsat.components.obc import AlarmManager
import pytest


@pytest.fixture
def alarm_manager():
    return AlarmManager()

def test_get_alarms(alarm_manager: AlarmManager):
    assert alarm_manager.get_alarms() == {}

def test_set_alarm(alarm_manager: AlarmManager):
    now = datetime.now()
    alarm_manager.set_alarm(name="Test", "Test Alarm", now)
    alarms = alarm_manager.get_alarms()
    assert len(alarms) == 1
    alarm = alarms[0]
    assert alarm.name == "Test"
    assert alarm.description == "Test Alarm"
    assert alarm.epoch == now

def test_delete_alarm(alarm_manager: AlarmManager):
    now = datetime.now()
    alarm_manager.set_alarm(name="Test", description="Test Alarm", epoch=now)
    assert len(alarm_manager.get_alarms()) == 1
    alarm_manager.delete_alarm(0)
    assert len(alarm_manager.get_alarms()) == 0

def test_get_expired_alarms(alarm_manager: AlarmManager):
    now = datetime.now()
    past = now - timedelta(days=1)
    future = now + timedelta(days=1)
    
    alarm_manager.set_alarm(name="Past", description="Past Alarm", epoch=past)
    alarm_manager.set_alarm(name="Future", description="Future Alarm", epoch=future)
    
    expired_alarm = alarm_manager.get_expired_alarms(now)
    assert expired_alarm.name == "Past"
    assert len(alarm_manager.get_alarms()) == 1
    assert 0 not in alarm_manager.get_alarms()
