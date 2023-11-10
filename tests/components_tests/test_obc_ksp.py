import krpc

from llmsat.components import OBC


def test_get_spacecraft_properties():
    conn = krpc.connect(name="Hello World")
    vessel = conn.space_center.active_vessel
    print(vessel.name)

    obc = OBC(vessel=vessel)

    print(obc.get_spacecraft_properties())

    conn.close()
