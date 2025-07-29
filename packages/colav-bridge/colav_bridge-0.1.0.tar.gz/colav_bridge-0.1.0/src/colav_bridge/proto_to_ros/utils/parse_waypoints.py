from colav_interfaces.msg import Waypoint
from .parse_point import parse_point

def parse_waypoints(waypoints):
    """Parse a list of protobuf waypoints to ros."""
    try:
        waypoints_list = []
        for waypoint in waypoints:
            waypoints_list.append(
                Waypoint(
                    position=parse_point(waypoint.position),
                    acceptance_radius=waypoint.acceptance_radius
                )
            ) 
            
        return waypoints_list
    except Exception as e:
        raise ValueError(f"Error parsing waypoints: {e}") from e
