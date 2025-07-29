from colav_bridge.proto_to_ros import parse_obstacles_update
from colav_protobuf.examples import obstacles_update
from colav_protobuf_utils.serialization import serialize_protobuf

def test_parse_obstacles_update():
    parsed_obstacles_update = parse_obstacles_update(serialize_protobuf(obstacles_update))    
    
    assert parsed_obstacles_update.mission_tag == obstacles_update.mission_tag
    assert parsed_obstacles_update.header.stamp.sec == obstacles_update.stamp.sec
    assert parsed_obstacles_update.header.stamp.nanosec == obstacles_update.stamp.nanosec
    assert parsed_obstacles_update.header.frame_id == 'map'

    # validate parsing of static obstacles
    assert len(parsed_obstacles_update.static_obstacles) == len(obstacles_update.static_obstacles)
    for idx in range(len(parsed_obstacles_update.static_obstacles)):
        parsed_static_obstacle = parsed_obstacles_update.static_obstacles[idx]
        static_obstacle = obstacles_update.static_obstacles[idx]

        assert parsed_static_obstacle.tag == static_obstacle.tag
        # assert parsed_static_obstacle.type == static_obstacle.type # TODO: Need to fix this
        assert parsed_static_obstacle.pose.position.x == static_obstacle.pose.position.x
        assert parsed_static_obstacle.pose.position.y == static_obstacle.pose.position.y
        assert parsed_static_obstacle.pose.position.z == static_obstacle.pose.position.z

        assert parsed_static_obstacle.pose.orientation.x == static_obstacle.pose.orientation.x
        assert parsed_static_obstacle.pose.orientation.y == static_obstacle.pose.orientation.y
        assert parsed_static_obstacle.pose.orientation.z == static_obstacle.pose.orientation.z
        assert parsed_static_obstacle.pose.orientation.w == static_obstacle.pose.orientation.w
        # TODO: NEED TO CHECK POLYSHAPE
        assert parsed_static_obstacle.geometry.inflation_radius == static_obstacle.geometry.inflation_radius


    # validate parsing of dynamic obstacles
    assert len(parsed_obstacles_update.dynamic_obstacles) == len(obstacles_update.dynamic_obstacles)
    for idx in range(len(parsed_obstacles_update.dynamic_obstacles)):
        parsed_dynamic_obstacle = parsed_obstacles_update.dynamic_obstacles[idx]
        dynamic_obstacle = obstacles_update.dynamic_obstacles[idx]

        assert parsed_dynamic_obstacle.tag == dynamic_obstacle.tag
        # assert parsed_static_obstacle.type == static_obstacle.type # TODO: Need to fix this
        assert parsed_dynamic_obstacle.pose.position.x == dynamic_obstacle.state.pose.position.x
        assert parsed_dynamic_obstacle.pose.position.y == dynamic_obstacle.state.pose.position.y
        assert parsed_dynamic_obstacle.pose.position.z == dynamic_obstacle.state.pose.position.z

        assert parsed_dynamic_obstacle.pose.orientation.x == dynamic_obstacle.state.pose.orientation.x
        assert parsed_dynamic_obstacle.pose.orientation.y == dynamic_obstacle.state.pose.orientation.y
        assert parsed_dynamic_obstacle.pose.orientation.z == dynamic_obstacle.state.pose.orientation.z
        assert parsed_dynamic_obstacle.pose.orientation.w == dynamic_obstacle.state.pose.orientation.w

        assert parsed_dynamic_obstacle.velocity == dynamic_obstacle.state.velocity
        assert parsed_dynamic_obstacle.yaw_rate == dynamic_obstacle.state.yaw_rate


    assert parsed_obstacles_update.__module__ == 'colav_interfaces.msg._obstacles_update'