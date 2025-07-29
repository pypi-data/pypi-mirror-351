from colav_bridge.proto_to_ros.utils import parse_vessel
from colav_protobuf import MissionRequest

def test_parse_vessel():
    vessel = MissionRequest.Vessel(
        tag = "EF12_WORKBOAT",
        type = MissionRequest.Vessel.VesselType.HYDROFOIL,
        constraints = MissionRequest.Vessel.VesselConstraints(
            max_acceleration = 2.0,
            max_deceleration = -1.0,
            max_velocity = 30.0,
            min_velocity = 15.0,
            max_yaw_rate = 0.2
        ),
        geometry = MissionRequest.Vessel.VesselGeometry (
            safety_radius = 5,
            loa = 12.0,
            beam = 4.0
        )
    )
    parsed_vessel = parse_vessel(vessel)
    
    assert parsed_vessel.tag == "EF12_WORKBOAT"
    assert MissionRequest.Vessel.VesselType.Value(parsed_vessel.type) == MissionRequest.Vessel.VesselType.HYDROFOIL
    assert round(parsed_vessel.constraints.max_acceleration, 3) == 2.00
    assert round(parsed_vessel.constraints.max_deceleration, 3) == -1.00
    assert round(parsed_vessel.constraints.max_velocity, 3) == 30.0
    assert round(parsed_vessel.constraints.min_velocity, 3) == 15.0
    assert round(parsed_vessel.constraints.max_yaw_rate, 3) == 0.200
    assert round(parsed_vessel.geometry.safety_radius, 3) == 5.00
    assert round(parsed_vessel.geometry.loa, 3) == 12.0
    assert round(parsed_vessel.geometry.beam, 3) == 4.00
    assert parsed_vessel.__module__ == 'colav_interfaces.msg._vessel'