from colav_interfaces.msg import Vessel, VesselConstraints, VesselGeometry
from colav_protobuf.missionRequest_pb2 import MissionRequest

def parse_vessel(vessel):
    """Parse vessel protobuf to ros"""
    try:
        return Vessel(
            tag = vessel.tag,
            type = MissionRequest.Vessel.VesselType.Name(
                vessel.type
            ),
            constraints = VesselConstraints(
                max_acceleration = vessel.constraints.max_acceleration,
                max_deceleration = vessel.constraints.max_deceleration,
                max_velocity = vessel.constraints.max_velocity,
                min_velocity = vessel.constraints.min_velocity,
                max_yaw_rate = vessel.constraints.max_yaw_rate,
            ),
            geometry = VesselGeometry(
                loa = vessel.geometry.loa, #ProtoToROSUtils._parse_polygon(vessel.vessel_geometry.polyshape_points),
                beam = vessel.geometry.beam,
                safety_radius = vessel.geometry.safety_radius 
            )
        )
    except Exception as e:
        raise ValueError(f"Error parsing vessel: {e}") from e