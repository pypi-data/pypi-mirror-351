# BonicBot Python Library

[![PyPI version](https://badge.fury.io/py/bonicbot.svg)](https://badge.fury.io/py/bonicbot)
[![Python versions](https://img.shields.io/pypi/pyversions/bonicbot.svg)](https://pypi.org/project/bonicbot/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python library for controlling BonicBot humanoid robots via serial communication. This library provides intuitive methods to control individual servos, coordinate complex movements, and manage the robot's base motors.

## Features

- **Individual Servo Control**: Precise control of each servo with custom angles, speeds, and acceleration
- **Group Control**: Coordinated control of head, left hand, right hand, and base motors
- **GUI Interface**: User-friendly graphical interface for real-time robot control
- **Preset Positions**: Built-in preset positions and custom position saving/loading
- **Serial Communication**: Robust serial communication with error handling
- **Type Hints**: Full type annotations for better IDE support and code reliability

## Installation

### From PyPI (Recommended)

```bash
pip install bonicbot

# Test your installation
bonicbot-test
```

### For GUI support

The GUI requires tkinter, which is **not installable via pip**. Install it through your system package manager:

```bash
# Install bonicbot first
pip install bonicbot

# Then install tkinter (system-dependent):
# Ubuntu/Debian:
sudo apt-get install python3-tk

# CentOS/RHEL:
sudo yum install python3-tkinter

# Fedora:
sudo dnf install python3-tkinter

# macOS (if missing):
brew install python-tk

# Windows: Usually included with Python
```

### Development Installation

```bash
git clone https://github.com/yourusername/bonicbot.git
cd bonicbot
pip install -e .[dev]
```

## Quick Start

### Basic Usage

```python
from bonicbot import BonicBotController

# Connect to robot
bot = BonicBotController('/dev/ttyUSB0')  # Linux/Mac
# bot = BonicBotController('COM3')        # Windows

# Control individual servo
bot.control_servo('headPan', angle=45.0, speed=200)

# Control head movement
bot.control_head(pan_angle=30.0, tilt_angle=-10.0)

# Control left hand
bot.control_left_hand(gripper_angle=90.0, elbow_angle=45.0)

# Move the robot base
bot.move_forward(speed=100)
bot.turn_left(speed=50)
bot.stop()

# Close connection
bot.close()
```

### Using Context Manager

```python
from bonicbot import BonicBotController

with BonicBotController('/dev/ttyUSB0') as bot:
    bot.control_head(pan_angle=45.0)
    bot.control_left_hand(gripper_angle=90.0)
    # Connection automatically closed
```

# Launch GUI

**Note**: GUI requires tkinter (see installation instructions above)

```bash
# From command line (if tkinter available)
bonicbot-gui

# Or from Python
from bonicbot.gui import run_servo_controller
run_servo_controller()

# Check if GUI is available
from bonicbot import is_gui_available
if is_gui_available():
    print("GUI available!")
else:
    print("Core functionality available, GUI needs tkinter")
```

## Core vs GUI Functionality

| Feature | Core Library | GUI Required |
|---------|-------------|--------------|
| Robot control | ✅ Always works | N/A |
| Individual servo control | ✅ Always works | N/A |
| Head/hand movements | ✅ Always works | N/A |
| Base motor control | ✅ Always works | N/A |
| Examples and scripts | ✅ Always works | N/A |
| Visual control interface | ❌ Needs tkinter | ✅ |
| Real-time sliders | ❌ Needs tkinter | ✅ |
| Preset position GUI | ❌ Needs tkinter | ✅ |

## Available Servos

The library supports the following servos:

**Head**:
- `headPan`: Head rotation left/right (-90° to 90°)
- `headTilt`: Head tilt up/down (-38° to 45°)

**Left Arm**:
- `leftGripper`: Left gripper open/close (-90° to 90°)
- `leftWrist`: Left wrist rotation (-90° to 90°)
- `leftElbow`: Left elbow bend (-90° to 0°)
- `leftSholderPitch`: Left shoulder pitch (-45° to 180°)
- `leftSholderYaw`: Left shoulder yaw (-90° to 90°)
- `leftSholderRoll`: Left shoulder roll (-3° to 144°)

**Right Arm**:
- `rightGripper`: Right gripper open/close (-90° to 90°)
- `rightWrist`: Right wrist rotation (-90° to 90°)
- `rightElbow`: Right elbow bend (-90° to 0°)
- `rightSholderPitch`: Right shoulder pitch (-45° to 180°)
- `rightSholderYaw`: Right shoulder yaw (-90° to 90°)
- `rightSholderRoll`: Right shoulder roll (-3° to 144°)

## API Reference

### BonicBotController Class

#### Constructor
```python
BonicBotController(port: str, baudrate: int = 115200, timeout: float = 1.0)
```

#### Individual Servo Control
```python
control_servo(servo_id: str, angle: float, speed: int = 200, acc: int = 20)
```

#### Group Controls
```python
control_head(pan_angle: float = 0.0, tilt_angle: float = 0.0, ...)
control_left_hand(gripper_angle: float = 0.0, wrist_angle: float = 0.0, ...)
control_right_hand(gripper_angle: float = 0.0, wrist_angle: float = 0.0, ...)
control_base(left_motor_speed: int = 0, right_motor_speed: int = 0)
```

#### Movement Methods
```python
move_forward(speed: int = 100)
move_backward(speed: int = 100)
turn_left(speed: int = 100)
turn_right(speed: int = 100)
stop()
```

## Examples

See the `examples/` directory for more comprehensive examples:

- `basic_control.py`: Basic servo and movement control
- `head_movements.py`: Head tracking and scanning patterns
- `hand_gestures.py`: Hand gestures and manipulation tasks
- `base_movement.py`: Navigation and movement patterns

## Hardware Requirements

- BonicBot humanoid robot
- USB to serial adapter (if not built-in)
- Python 3.7 or higher

## Why isn't tkinter in requirements.txt?

**tkinter is part of Python's standard library** and cannot be installed via pip. It comes bundled with Python on Windows/macOS, but Linux distributions often package it separately for size optimization. This design allows:

✅ **Core functionality works everywhere** - Robot control without GUI dependencies  
✅ **Lightweight installations** - Perfect for headless servers and containers  
✅ **Platform flexibility** - Users install GUI support as needed  

**Bottom line**: You get full robot control immediately, GUI is optional!

## Supported Platforms

- Linux (Raspberry Pi recommended)
- Windows 10/11
- macOS

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

1. Check the [documentation](docs/)
2. Search [existing issues](https://github.com/yourusername/bonicbot/issues)
3. Create a [new issue](https://github.com/yourusername/bonicbot/issues/new)

## Testing Your Installation

After installation, test that everything is working:

```python
# Comprehensive installation test
from bonicbot.test_installation import test
test()
```

This will test:
- ✅ Core imports (BonicBotController, ServoID)
- ✅ ServoID enumeration 
- ✅ GUI availability (tkinter detection)
- 📋 Platform-specific installation help if needed

**Quick tests:**
```python
# Test core functionality
from bonicbot import BonicBotController
print("✅ Core functionality works!")

# Test GUI availability  
from bonicbot import is_gui_available
print("GUI available:", is_gui_available())
```

## Troubleshooting

### "No module named '_tkinter'" Error
This means the GUI component isn't available. **The core robot control still works!** To fix:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Test again
bonicbot-test
```

### Serial Port Permission Issues
```bash
# Linux: Add user to dialout group
sudo usermod -a -G dialout $USER
# Then log out and back in
```