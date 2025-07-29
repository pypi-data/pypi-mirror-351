# from colav_bridge.ros_to_proto import parse_controller_feedback
# from colav_protobuf.examples import controller_feedback
# from colav_interfaces.msg import ControllerFeedback
# from std_msgs.msg import Header
# from builtin_interfaces.msg import Time
# from colav_interfaces.msg import CmdVelYaw, ControlMode, ControlStatus


# def test_controller_feedback_parser():
#     ros_controller_feedback = ControllerFeedback(
#         header = Header(
#             stamp = Time(
#                 sec = controller_feedback.stamp.sec,
#                 nanosec = controller_feedback.stamp.nanosec 
#             ),
#             frame_id = 'map'
#         ),
#         mission_tag = controller_feedback.mission_tag,
#         agent_tag = controller_feedback.agent_tag,
#         cmd = CmdVelYaw(
#             velocity=float(20),
#             yaw_rate=float(0.2)
#         ),
#         mode = ControlMode(
#             type = ControlMode.CRUISE
#         ),
#         status = ControlStatus(
#             type = ControlStatus.ACTIVE,
#             message = "Hybrid Automaton is ACTIVE"
#         ) 
#     )

#     parsed_controller_feedback = parse_controller_feedback(ros_controller_feedback)

#     assert parsed_controller_feedback.stamp.sec == ros_controller_feedback.header.stamp.sec
#     assert parsed_controller_feedback.stamp.nanosec == ros_controller_feedback.header.stamp.nanosec
#     assert parsed_controller_feedback.mission_tag == ros_controller_feedback.mission_tag
#     assert parsed_controller_feedback.agent_tag == ros_controller_feedback.agent_tag
#     assert round(parsed_controller_feedback.cmd.velocity, 3) == round(ros_controller_feedback.cmd.velocity, 3)
#     assert round(parsed_controller_feedback.cmd.yaw_rate, 3) == round(ros_controller_feedback.cmd.yaw_rate, 3)
#     assert parsed_controller_feedback.mode == ros_controller_feedback.mode.type
#     assert parsed_controller_feedback.status == ros_controller_feedback.status.type
    
#     assert parsed_controller_feedback.__module__ == 'controllerFeedback_pb2'
