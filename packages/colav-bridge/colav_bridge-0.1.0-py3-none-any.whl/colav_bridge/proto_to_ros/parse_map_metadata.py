from colav_protobuf_utils import ProtoType
from colav_protobuf_utils.deserialization import deserialize_protobuf
from nav_msgs.msg import MapMetaData as ROSMapMetadata
from .utils import parse_pose, parse_stamp


def parse_map_metadata(msg: bytes) -> ROSMapMetadata:
    """Parse agent update protobuf to ROS"""
    try:
        protobuf_map_metadata = deserialize_protobuf(msg, ProtoType.MAP_METADATA)
        return ROSMapMetadata(
            map_load_time = parse_stamp(protobuf_map_metadata.map_load_time),
            resolution = protobuf_map_metadata.resolution,
            width = int(protobuf_map_metadata.width),
            height = int(protobuf_map_metadata.height),
            origin = parse_pose(protobuf_map_metadata.origin)
        )
    except Exception as e:
        raise ValueError(f"Error parsing agent protobuf: {e}") from e