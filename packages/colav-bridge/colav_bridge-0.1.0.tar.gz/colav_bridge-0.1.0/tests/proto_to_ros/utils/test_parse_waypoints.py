from colav_bridge.proto_to_ros.utils import parse_waypoints
from colav_protobuf import MissionRequest

def test_parse_waypoints():
    waypoint = MissionRequest.GoalWaypoint (
        position = MissionRequest.Point(
            x = float(1),
            y = float(2),
            z = float(3)
        ),
        acceptance_radius = float(10)
    )
    
    waypoints = [waypoint]
    parsed_waypoints = parse_waypoints(waypoints)
    assert len(parsed_waypoints) == 1
    assert parsed_waypoints[0].position.x == 1
    assert parsed_waypoints[0].position.y == 2
    assert parsed_waypoints[0].position.z == 3
    assert parsed_waypoints[0].acceptance_radius == 10
    
    assert parsed_waypoints[0].__module__ == 'colav_interfaces.msg._waypoint'
