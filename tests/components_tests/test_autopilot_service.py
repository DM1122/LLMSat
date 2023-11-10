import krpc
from llmsat.components import AutpilotService


def test_get_spacecraft_properties():
    conn = krpc.connect(name="Test")
    vessel = conn.space_center.active_vessel

    
    autopilot = AutpilotService(pilot=)

    print(obc.get_spacecraft_properties())

    conn.close()
