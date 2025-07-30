# SC010 Controller Library

A Python library for controlling and managing SC010 AV over IP controllers using Telnet.

## Features

- Easy-to-use interface for SC010 controller management
- Automatic device discovery on the network
- Comprehensive device and system information retrieval
- Matrix switching control
- Video wall configuration
- Device status monitoring
- Scene management
- CEC control support
- Robust error handling and connection management

## Installation

```bash
pip install sc010-controller
```

## Quick Start

```python
from sc010 import Controller, ConnectionConfig

# Find controller on network
controller_info = Controller.find_controller()
if controller_info:
    print(f"Found controller at IP: {controller_info['ip']}")
    print(f"Controller MAC: {controller_info['mac']}")

# Connect to controller
config = ConnectionConfig(
    ip="192.168.50.200",
    timeout=2.0,
    max_retries=3,
    retry_delay=1.0,
    gather_info=True
)

# Using context manager for automatic connection/disconnection
with Controller(config=config) as controller:
    # Get device list
    devices = controller.get_devicelist()
    print("Available devices:", devices)

    # Get device names and aliases
    device_names = controller.get_device_name()
    for device in device_names:
        print(f"{device['trueName']} -> {device['alias']}")

    # Control matrix switching
    controller.set_matrix("TX1 RX1 RX2", "TX2 RX3 RX4")

    # Get video wall configuration
    vw_config = controller.get_vw()
    print("Video wall config:", vw_config)
```

## Documentation

### Connection Configuration

The `ConnectionConfig` class allows you to customize the connection settings:

```python
config = ConnectionConfig(
    ip="192.168.50.200",  # Controller IP address
    port=23,              # Telnet port (default: 23)
    timeout=1.0,          # Connection timeout in seconds
    max_retries=3,        # Number of connection retries
    retry_delay=1.0,      # Delay between retries in seconds
    gather_info=True      # Whether to gather device info on connection
)
```

### Main Features

- **Device Discovery**: Find controllers on the network
- **Device Management**: Get device lists, names, and status
- **Matrix Control**: Configure video routing
- **Video Wall**: Set up and manage video walls
- **CEC Control**: Send CEC commands to displays
- **System Configuration**: Manage network settings and system parameters

### Error Handling

The library includes comprehensive error handling:

```python
from sc010 import SC010Error, ConnectionError, CommandError, ParseError

try:
    with Controller(config=config) as controller:
        # Your code here
except ConnectionError as e:
    print(f"Connection failed: {e}")
except CommandError as e:
    print(f"Command failed: {e}")
except ParseError as e:
    print(f"Parse error: {e}")
except SC010Error as e:
    print(f"General error: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Developed for use with SC010 AV over IP controllers
- Compatible with various IP-based video distribution systems 