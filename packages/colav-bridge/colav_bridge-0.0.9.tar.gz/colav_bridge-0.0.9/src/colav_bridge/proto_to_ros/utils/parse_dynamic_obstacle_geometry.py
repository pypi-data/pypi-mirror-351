from geometry_msgs.msg import Polygon
from colav_interfaces.msg import DynamicObstacleGeometry

def parse_dynamic_obstacle_geometry(geometry) -> Polygon:
    """Convert protobuf geometry to ROS Polygon"""
    try:
        return DynamicObstacleGeometry(
            loa = geometry.loa,
            beam = geometry.beam,
            safety_radius = geometry.safety_radius
        )
    except Exception as e: 
        raise ValueError("Error parsing dynamic obstacle geometry") from e
    
