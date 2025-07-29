from rclpy.node import Node
from colav_interfaces.msg import ObstaclesUpdate, DynamicObstacle, StaticObstacle
from colav_protobuf import ObstaclesUpdate as ProtoObstaclesUpdate
from .utils import parse_point, parse_pose, parse_dynamic_obstacle_geometry, parse_static_obstacle_geometry, parse_stamp
from std_msgs.msg import Header
from colav_protobuf_utils.deserialization import deserialize_protobuf
from colav_protobuf_utils import ProtoType
from builtin_interfaces.msg import Time

def parse_obstacles_update(msg: bytes) -> ObstaclesUpdate:
    """Parse Obstacle update received via protobuf and publish it to ros topic"""
    try:
        protobuf_obstacles_update = deserialize_protobuf(msg, ProtoType.OBSTACLES_UPDATE)
        return ObstaclesUpdate(
            header=Header(
                stamp = parse_stamp(protobuf_obstacles_update.stamp),
                frame_id = "map"
            ),
            mission_tag=protobuf_obstacles_update.mission_tag,
            dynamic_obstacles=_parse_dynamic_obstacles(protobuf_obstacles_update.dynamic_obstacles),
            static_obstacles=_parse_static_obstacles(protobuf_obstacles_update.static_obstacles),
        )
    except Exception as e:
        raise ValueError(f"Error parsing obstacles protobuf: {e}") from e
    
def _parse_dynamic_obstacles(dynamic_obstacles) -> list[DynamicObstacle]:
    """Convert dynamic obstacles from protobuf to ROS"""
    try: 
        return [
            DynamicObstacle(
                tag=dynamic_obstacle.tag,
                type=ProtoObstaclesUpdate.DynamicObstacleType.Name(dynamic_obstacle.type),
                pose=parse_pose(dynamic_obstacle.state.pose),
                velocity=dynamic_obstacle.state.velocity,
                acceleration=float(0), # TODO: Add acceleration to protobuf for future reference
                yaw_rate=dynamic_obstacle.state.yaw_rate,
                geometry=parse_dynamic_obstacle_geometry(dynamic_obstacle.geometry),
            )
            for dynamic_obstacle in dynamic_obstacles
        ]
    except Exception as e:
        raise ValueError(f"Error parsing dynamic obstacles: {e}") from e
    
def _parse_static_obstacles(static_obstacles) -> list[StaticObstacle]:
    """Convert static obstacles from protobuf to ROS"""
    try: 
        return [
            StaticObstacle(
                tag=static_obstacle.tag,
                type=ProtoObstaclesUpdate.StaticObstacleType.Name(static_obstacle.type),
                pose=parse_pose(static_obstacle.pose),
                geometry=parse_static_obstacle_geometry(static_obstacle.geometry),
            )
            for static_obstacle in static_obstacles
        ]
    except Exception as e:
        raise ValueError(f"Error parsing static obstacles: {e}") from e
