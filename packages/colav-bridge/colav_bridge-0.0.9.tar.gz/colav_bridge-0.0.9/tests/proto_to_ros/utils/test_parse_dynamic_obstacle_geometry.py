from colav_bridge.proto_to_ros.utils import parse_dynamic_obstacle_geometry
from colav_protobuf import ObstaclesUpdate

def test_parse_dynamic_obstacle_geometry():
    obstacle_geometry = ObstaclesUpdate.DynamicObstacleGeometry (
        loa = float(10),
        beam = float(5),
        safety_radius  = float(10)
    )
    
    parsed_obstacle_geometry = parse_dynamic_obstacle_geometry(
        obstacle_geometry
    )
    
    assert parsed_obstacle_geometry.loa == 10
    assert parsed_obstacle_geometry.beam == 5
    assert parsed_obstacle_geometry.safety_radius == 10
    assert parsed_obstacle_geometry.__module__ == 'colav_interfaces.msg._dynamic_obstacle_geometry'
    
# TODO: Add test for exception
def test_parse_dynamic_obstacle_geometry_exception():
    pass