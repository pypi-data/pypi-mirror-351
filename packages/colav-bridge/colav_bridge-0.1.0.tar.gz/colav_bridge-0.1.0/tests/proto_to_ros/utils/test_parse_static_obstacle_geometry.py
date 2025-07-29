from colav_bridge.proto_to_ros.utils import parse_static_obstacle_geometry
from colav_protobuf import ObstaclesUpdate

def test_parse_static_obstacle_geometry():
    obstacle_geometry = ObstaclesUpdate.StaticObstacleGeometry(
        inflation_radius = float(10)
    )
    obstacle_geometry.polyshape_points.extend([
        ObstaclesUpdate.Point(x=float(1), y=float(2), z=float(3)),
        ObstaclesUpdate.Point(x=float(4), y=float(5), z=float(6))
    ])

    parsed_static_obstacle_geom = parse_static_obstacle_geometry(
        obstacle_geometry
    )
    
    assert parsed_static_obstacle_geom.inflation_radius == 10
    assert len(parsed_static_obstacle_geom.polyshape.points) == 2
    assert parsed_static_obstacle_geom.polyshape.points[0].x == 1
    assert parsed_static_obstacle_geom.polyshape.points[0].y == 2
    assert parsed_static_obstacle_geom.polyshape.points[0].z == 3
    assert parsed_static_obstacle_geom.polyshape.points[1].x == 4
    assert parsed_static_obstacle_geom.polyshape.points[1].y == 5
    assert parsed_static_obstacle_geom.polyshape.points[1].z == 6
    assert parsed_static_obstacle_geom.__module__ == 'colav_interfaces.msg._static_obstacle_geometry'