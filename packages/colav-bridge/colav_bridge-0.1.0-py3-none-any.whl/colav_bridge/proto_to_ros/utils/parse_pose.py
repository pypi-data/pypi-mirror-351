from geometry_msgs.msg import Pose, Point, Quaternion

def parse_pose(pose) -> Pose:
    """Convert protobuf pose to ROS msg"""
    try:
        return Pose(
            position=Point(x=pose.position.x, y=pose.position.y, z=pose.position.z),
            orientation=Quaternion(x=pose.orientation.x, y=pose.orientation.y, z=pose.orientation.z, w=pose.orientation.w)
        )
    except Exception as e:
        raise ValueError("Error parsing pose") from e