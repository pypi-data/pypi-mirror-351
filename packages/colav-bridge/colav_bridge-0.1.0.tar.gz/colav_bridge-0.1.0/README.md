# colav-bridge

[![PyPI - Version](https://img.shields.io/pypi/v/colav-bridge.svg)](https://pypi.org/project/colav-bridge)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/colav-bridge.svg)](https://pypi.org/project/colav-bridge)
<!--[![PyPI - Protobuf Version]()]-->
This package contains functions which bridge colav_protobuf messages to ros_interfaces and vice versa. 

-----

## Table of Contents

- [Installation](#installation)
- [Structure](#structure)
- [Usage](#usage)
- [License](#license)

## Installation

```bash
pip install colav-bridge
```

## Structure
The src code in [colav-bridge](https://github.com/RyanMcKeeQUB/colav_protobuf) shows that the project is organised into main directories: 
- [Tests](https://github.com/RyanMcKeeQUB/colav_protobuf/tree/main/tests): The tests directory contains a variety of unit tests ensuring that the pkg is working as expected and are called as apart of the CI/CD pipeline defined by the [github_action](./.github/workflows/workflow.yml)

## Usage
When pkg is installed, Using it is simple imports are as follows. 

```python
from colav_bridge.proto_to_ros import (
    parse_agent_update,
    parse_mission_request,
    parse_obstacles_update
)
from colav_bridge.ros_to_proto import (
    parse_controller_feedback
)
```

Here is an example of one of these colav_bridge parsers being used: 

```python
    from colav_protobuf.examples import agent_update as proto_agent_update
    from colav_protobuf_utils.serializer import serializer_protobuf

    ros_agent_update = parse_agent_update(serialize_protobuf(proto_agent_update))
```


## License

`colav-bridge` is distributed under the terms of the [MIT](https://github.com/RyanMcKeeQUB/colav_bridge/tree/main/LICENSE) license.
