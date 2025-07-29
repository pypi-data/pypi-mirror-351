from geometry_msgs.msg import Point32

def parse_point(point):
    """Parse a protobuf point to ros."""
    try: 
        return Point32(
            x=point.x,
            y=point.y,
            z=point.z
        )
    except Exception as e: 
        raise ValueError("Error parsing point") from e
