from colav_bridge.proto_to_ros.utils import parse_pose
from colav_protobuf import AgentUpdate

def test_parse_pose():
    pose = AgentUpdate.Pose(position=AgentUpdate.Pose.Position(x=1, y=2, z=2), orientation=AgentUpdate.Pose.Orientation(x=1, y=2, z=2, w=1))
    parsed_pose = parse_pose(pose)
    assert parsed_pose.position.x == 1
    assert parsed_pose.position.y == 2
    assert parsed_pose.position.z == 2
    assert parsed_pose.orientation.x == 1
    assert parsed_pose.orientation.y == 2
    assert parsed_pose.orientation.z == 2
    assert parsed_pose.orientation.w == 1
    assert parsed_pose.__module__ == 'geometry_msgs.msg._pose'
    