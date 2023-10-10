import krpc
from llmsat.components.eps_ksp import EPS


def test_get_electrical_charge_level():
    conn = krpc.connect(name="Hello World")
    vessel = conn.space_center.active_vessel
    print(vessel.name)

    eps = EPS(vessel=vessel)

    print(eps.get_total_electric_charge())

    conn.close()
