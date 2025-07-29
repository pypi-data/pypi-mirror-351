from colav_interfaces.msg import ControllerFeedback as ROSControllerFeedback
from colav_protobuf_utils.protobuf_generator import gen_controller_feedback, CtrlMode, CtrlStatus
from colav_protobuf import ControllerFeedback as ProtoControllerFeedback

def parse_controller_feedback(msg:ROSControllerFeedback) -> ProtoControllerFeedback:
    """Parse controller feedback to ROS message"""
    try: 

        return gen_controller_feedback(
            mission_tag= msg.mission_tag,
            agent_tag= msg.agent_tag,
            mode= CtrlMode(msg.mode.type),
            status = CtrlStatus(msg.status.type),
            velocity = msg.cmd.velocity,
            yaw_rate = msg.cmd.yaw_rate,
            stamp=msg.header.stamp
        )
    except Exception as e:
        raise ValueError(f"Failed to parse exception: {e}") from e