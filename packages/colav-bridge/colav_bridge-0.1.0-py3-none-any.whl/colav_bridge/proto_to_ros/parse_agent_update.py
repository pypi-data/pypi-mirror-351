from rclpy.node import Node
from colav_interfaces.msg import AgentUpdate
from colav_protobuf_utils import ProtoType
from colav_protobuf import AgentUpdate as AgentUpdateProto
from colav_protobuf_utils.deserialization import deserialize_protobuf
from std_msgs.msg import Header
from .utils import parse_pose, parse_stamp
from builtin_interfaces.msg import Time

def parse_agent_update(msg: bytes) -> AgentUpdate:
    """Parse agent update protobuf to ROS"""
    try:
        protobuf_agent_update = deserialize_protobuf(msg, ProtoType.AGENT_UPDATE)
        return AgentUpdate(
            header = Header(
                stamp = parse_stamp(protobuf_agent_update.stamp),
                frame_id = "map"
            ),
            mission_tag=protobuf_agent_update.mission_tag,
            agent_tag=protobuf_agent_update.agent_tag,
            pose=parse_pose(protobuf_agent_update.state.pose),
            velocity=protobuf_agent_update.state.velocity,
            acceleration=protobuf_agent_update.state.acceleration,
            yaw_rate=protobuf_agent_update.state.yaw_rate
        )
    except Exception as e:
        raise ValueError(f"Error parsing agent protobuf: {e}") from e