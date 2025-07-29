from builtin_interfaces.msg import Time

def parse_stamp(protobuf_stamp) -> Time:
    """Parse a protobuf timestamp to ros."""
    try: 
        return Time(
            sec = protobuf_stamp.sec,
            nanosec = protobuf_stamp.nanosec
        )
    except Exception as e: 
        raise ValueError(f"Error parsing stamp: {e}") from e