from colav_protobuf_utils import ProtoType
from colav_protobuf_utils.deserialization import deserialize_protobuf
from rclpy.node import Node
from colav_interfaces.msg import MissionRequest, Waypoints
from std_msgs.msg import Header
from .utils import parse_vessel, parse_point, parse_waypoints, parse_stamp
from builtin_interfaces.msg import Time

def parse_mission_request(msg: bytes) -> MissionRequest:
    """Parse mission request protobuf to ros"""
    try: 
        protobuf_mission_request = deserialize_protobuf(msg, ProtoType.MISSION_REQUEST)
        return MissionRequest(
                stamp = parse_stamp(protobuf_mission_request.stamp),
                goal_waypoints = Waypoints(waypoints=parse_waypoints((list(protobuf_mission_request.goal_waypoints)))),
        )
    except Exception as e: 
        raise ValueError(f"Error parsing mission request: {e}") from e