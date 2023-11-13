import krpc

from llmsat.components.autpilot import AutopilotService


def test_execute_maneuver():
    connection = krpc.connect(name="Test")

    service = AutopilotService(connection)

    service.execute_maneuver()

    connection.close()
