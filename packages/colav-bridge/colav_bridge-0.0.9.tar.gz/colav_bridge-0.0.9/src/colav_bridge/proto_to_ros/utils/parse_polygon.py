from geometry_msgs.msg import Polygon, Point32

def parse_polygon(points) -> Polygon:
    """Parse a list of points into a Polygon message."""
    try:
        points = [Point32(x=point.x, y=point.y, z=point.z) for point in points]
        return Polygon(points=points)
    except Exception as e:
        raise ValueError(f"Failed to parse polygon: {e}") from e