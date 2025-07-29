from colav_bridge.proto_to_ros.utils import parse_polygon
from colav_protobuf import ObstaclesUpdate

def test_parse_polygon():
    point = ObstaclesUpdate.Point
    polyshape = [
        point(x=float(1), y=float(2), z=float(3)),
        point(x=float(4), y=float(5), z=float(6))
    ]
    
    parsed_polyshape = parse_polygon(polyshape)
    
    assert len(parsed_polyshape.points) == 2
    assert parsed_polyshape.points[0].x == 1
    assert parsed_polyshape.points[0].y == 2
    assert parsed_polyshape.points[0].z == 3
    assert parsed_polyshape.points[1].x == 4
    assert parsed_polyshape.points[1].y == 5
    assert parsed_polyshape.points[1].z == 6
    assert parsed_polyshape.__module__ == 'geometry_msgs.msg._polygon'

# TODO: Add test for exception
def test_parse_polygon_exception():
    pass