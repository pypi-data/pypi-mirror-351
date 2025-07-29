from colav_bridge.proto_to_ros import parse_agent_update
from colav_protobuf.examples import agent_update
from colav_protobuf_utils.serialization import serialize_protobuf
from colav_protobuf_utils import ProtoType
from rclpy.node import Node

def test_parse_agent_update():
    parsed_agent_update = parse_agent_update(serialize_protobuf(agent_update))

    assert parsed_agent_update.mission_tag == agent_update.mission_tag
    assert parsed_agent_update.agent_tag == agent_update.agent_tag
    assert parsed_agent_update.header.stamp.sec == agent_update.stamp.sec
    assert parsed_agent_update.header.stamp.nanosec == agent_update.stamp.nanosec
    assert parsed_agent_update.header.frame_id == 'map'

    assert parsed_agent_update.pose.position.x == agent_update.state.pose.position.x
    assert parsed_agent_update.pose.position.y == agent_update.state.pose.position.y
    assert parsed_agent_update.pose.position.z == agent_update.state.pose.position.z
    
    assert parsed_agent_update.pose.orientation.x == agent_update.state.pose.orientation.x
    assert parsed_agent_update.pose.orientation.y == agent_update.state.pose.orientation.y
    assert parsed_agent_update.pose.orientation.z == agent_update.state.pose.orientation.z
    assert parsed_agent_update.pose.orientation.w == agent_update.state.pose.orientation.w

    assert parsed_agent_update.velocity == agent_update.state.velocity
    assert parsed_agent_update.yaw_rate == agent_update.state.yaw_rate
    assert parsed_agent_update.acceleration == agent_update.state.acceleration

    assert parsed_agent_update.__module__ == 'colav_interfaces.msg._agent_update'