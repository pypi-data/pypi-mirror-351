# from colav_bridge.proto_to_ros import parse_mission_request
# from colav_protobuf.examples import mission_request
# from colav_protobuf_utils.serialization import serialize_protobuf
# from colav_protobuf_utils import VesselType

# def test_parse_mission_request():
#     parsed_mission_request = parse_mission_request(serialize_protobuf(mission_request))
    
#     assert parsed_mission_request.tag == mission_request.tag
#     assert parsed_mission_request.header.stamp.sec == mission_request.stamp.sec
#     assert parsed_mission_request.header.stamp.nanosec == mission_request.stamp.nanosec
#     assert parsed_mission_request.header.frame_id == 'map'
    
#     assert parsed_mission_request.vessel.tag == mission_request.vessel.tag
#     # assert parsed_mission_request.vessel.type == VesselType[mission_request.vessel.type] # TODO: FIX THSI
#     assert parsed_mission_request.vessel.constraints.max_acceleration == mission_request.vessel.constraints.max_acceleration 
#     assert parsed_mission_request.vessel.constraints.max_deceleration == mission_request.vessel.constraints.max_deceleration 
#     assert parsed_mission_request.vessel.constraints.max_velocity == mission_request.vessel.constraints.max_velocity 
#     assert parsed_mission_request.vessel.constraints.min_velocity == mission_request.vessel.constraints.min_velocity 
#     assert parsed_mission_request.vessel.constraints.max_yaw_rate == mission_request.vessel.constraints.max_yaw_rate 
#     assert parsed_mission_request.vessel.geometry.safety_radius == mission_request.vessel.geometry.safety_radius
#     assert parsed_mission_request.vessel.geometry.loa == mission_request.vessel.geometry.loa
#     assert parsed_mission_request.vessel.geometry.beam == mission_request.vessel.geometry.beam

#     assert parsed_mission_request.init_position.x == mission_request.init_position.x
#     assert parsed_mission_request.init_position.y == mission_request.init_position.y
#     assert parsed_mission_request.init_position.z == mission_request.init_position.z

#     assert parsed_mission_request.goal_waypoints[0].position.x == mission_request.goal_waypoints[0].position.x
#     assert parsed_mission_request.goal_waypoints[0].position.y == mission_request.goal_waypoints[0].position.y
#     assert parsed_mission_request.goal_waypoints[0].position.z == mission_request.goal_waypoints[0].position.z
#     assert parsed_mission_request.goal_waypoints[0].acceptance_radius == mission_request.goal_waypoints[0].acceptance_radius

#     assert parsed_mission_request.__module__ == 'colav_interfaces.msg._mission_request'