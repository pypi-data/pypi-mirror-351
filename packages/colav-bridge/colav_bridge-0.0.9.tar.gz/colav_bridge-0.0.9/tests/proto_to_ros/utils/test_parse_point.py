from colav_bridge.proto_to_ros.utils import parse_point
from colav_protobuf import MissionRequest

def test_parse_point():
    point = MissionRequest.Point(x=1, y=2, z=2)
    parsed_point = parse_point(point)
    assert parsed_point.x == 1
    assert parsed_point.y == 2
    assert parsed_point.z == 2
    assert parsed_point.__class__.__name__ == 'Point32'
    assert parsed_point.__module__ == 'geometry_msgs.msg._point32'
    
    
# TODO: Exception test
def test_parse_point_exception():
    pass