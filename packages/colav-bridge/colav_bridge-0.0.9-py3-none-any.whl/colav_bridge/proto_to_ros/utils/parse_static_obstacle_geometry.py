from colav_interfaces.msg import StaticObstacleGeometry
from geometry_msgs.msg import Polygon, Point32 

def parse_static_obstacle_geometry(geometry) -> StaticObstacleGeometry:
    """Convert protobuf geometry to ROS StaticObstacleGeometry"""
    try:
        return StaticObstacleGeometry( 
            polyshape = Polygon(points=[Point32(x=point.x, y=point.y, z=point.z) for point in geometry.polyshape_points]),
            inflation_radius = geometry.inflation_radius
        )
    except Exception as e: 
        raise ValueError("Error parsing static obstacle geometry") from e