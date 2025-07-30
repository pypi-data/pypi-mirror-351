"""
BonicBot Control Library

A Python library for controlling BonicBot servos via serial communication.
Provides methods to control individual servos or groups of servos (head, hands, base).
"""

import json
import serial
import time
from typing import Dict, Optional, Union
from enum import Enum


class ServoID(Enum):
    """Enumeration of all available servo IDs"""
    RIGHT_GRIPPER = "rightGripper"
    RIGHT_WRIST = "rightWrist"
    RIGHT_ELBOW = "rightElbow"
    RIGHT_SHOULDER_YAW = "rightSholderYaw"
    RIGHT_SHOULDER_ROLL = "rightSholderRoll"
    RIGHT_SHOULDER_PITCH = "rightSholderPitch"
    LEFT_GRIPPER = "leftGripper"
    LEFT_WRIST = "leftWrist"
    LEFT_ELBOW = "leftElbow"
    LEFT_SHOULDER_YAW = "leftSholderYaw"
    LEFT_SHOULDER_ROLL = "leftSholderRoll"
    LEFT_SHOULDER_PITCH = "leftSholderPitch"
    HEAD_PAN = "headPan"
    HEAD_TILT = "headTilt"


class BonicBotController:
    """
    Main controller class for BonicBot servo control via serial communication.
    
    Usage:
        bot = BonicBotController(port='/dev/ttyUSB0', baudrate=115200)
        bot.control_servo('headPan', angle=45.0, speed=200, acc=20)
        bot.control_head(pan_angle=30.0, tilt_angle=-10.0)
        bot.control_left_hand(gripper_angle=90.0, elbow_angle=45.0)
    """
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        """
        Initialize the BonicBot controller.
        
        Args:
            port: Serial port name (e.g., '/dev/ttyUSB0', 'COM3')
            baudrate: Serial communication baud rate
            timeout: Serial communication timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial = None
        self._connect()
    
    def _connect(self):
        """Establish serial connection"""
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(2)  # Allow connection to stabilize
        except serial.SerialException as e:
            raise ConnectionError(f"Failed to connect to {self.port}: {e}")
    
    def _send_command(self, command: Dict):
        """
        Send JSON command via serial connection.
        
        Args:
            command: Dictionary containing the command structure
        """
        if not self._serial or not self._serial.is_open:
            raise ConnectionError("Serial connection not established")
        
        try:
            json_command = json.dumps(command)
            self._serial.write(json_command.encode('utf-8'))
            self._serial.flush()
        except Exception as e:
            raise RuntimeError(f"Failed to send command: {e}")
    
    def control_servo(self, servo_id: Union[str, ServoID], angle: float, 
                     speed: int = 200, acc: int = 20):
        """
        Control an individual servo.
        
        Args:
            servo_id: Servo identifier (string or ServoID enum)
            angle: Target angle in degrees
            speed: Movement speed
            acc: Acceleration value
        """
        if isinstance(servo_id, ServoID):
            servo_id = servo_id.value
        
        # Validate servo ID
        valid_ids = [servo.value for servo in ServoID]
        if servo_id not in valid_ids:
            raise ValueError(f"Invalid servo ID: {servo_id}. Valid IDs: {valid_ids}")
        
        command = {
            "commandType": "command",
            "dataType": "servo",
            "payload": {
                "angle": float(angle),
                "speed": int(speed),
                "acc": int(acc),
                "id": servo_id
            },
            "interval": 0
        }
        
        self._send_command(command)
    
    def control_head(self, pan_angle: float = 0.0, tilt_angle: float = 0.0,
                    pan_speed: int = 200, pan_acc: int = 20,
                    tilt_speed: int = 200, tilt_acc: int = 50,
                    mode: str = "None"):
        """
        Control head servos (pan and tilt).
        
        Args:
            pan_angle: Head pan angle in degrees
            tilt_angle: Head tilt angle in degrees
            pan_speed: Pan movement speed
            pan_acc: Pan acceleration
            tilt_speed: Tilt movement speed
            tilt_acc: Tilt acceleration
            mode: Head control mode
        """
        command = {
            "commandType": "command",
            "dataType": "head",
            "payload": {
                "mode": mode,
                "headPan": {
                    "angle": float(pan_angle),
                    "speed": int(pan_speed),
                    "acc": int(pan_acc)
                },
                "headTilt": {
                    "angle": float(tilt_angle),
                    "speed": int(tilt_speed),
                    "acc": int(tilt_acc)
                }
            },
            "interval": 0
        }
        
        self._send_command(command)
    
    def control_left_hand(self, gripper_angle: float = 0.0, wrist_angle: float = 0.0,
                         elbow_angle: float = 0.0, shoulder_pitch: float = 0.0,
                         shoulder_yaw: float = 0.0, shoulder_roll: float = 0.0,
                         gripper_speed: int = 200, wrist_speed: int = 800,
                         elbow_speed: int = 200, shoulder_pitch_speed: int = 200,
                         shoulder_yaw_speed: int = 750, shoulder_roll_speed: int = 200,
                         gripper_acc: int = 20, wrist_acc: int = 20,
                         elbow_acc: int = 20, shoulder_pitch_acc: int = 20,
                         shoulder_yaw_acc: int = 80, shoulder_roll_acc: int = 20):
        """
        Control all left hand servos.
        
        Args:
            *_angle: Target angles for each servo in degrees
            *_speed: Movement speeds for each servo
            *_acc: Acceleration values for each servo
        """
        command = {
            "commandType": "command",
            "dataType": "leftHand",
            "payload": {
                "leftGripper": {
                    "angle": float(gripper_angle),
                    "speed": int(gripper_speed),
                    "acc": int(gripper_acc)
                },
                "leftWrist": {
                    "angle": float(wrist_angle),
                    "speed": int(wrist_speed),
                    "acc": int(wrist_acc)
                },
                "leftElbow": {
                    "angle": float(elbow_angle),
                    "speed": int(elbow_speed),
                    "acc": int(elbow_acc)
                },
                "leftSholderPitch": {
                    "angle": float(shoulder_pitch),
                    "speed": int(shoulder_pitch_speed),
                    "acc": int(shoulder_pitch_acc)
                },
                "leftSholderYaw": {
                    "angle": float(shoulder_yaw),
                    "speed": int(shoulder_yaw_speed),
                    "acc": int(shoulder_yaw_acc)
                },
                "leftSholderRoll": {
                    "angle": float(shoulder_roll),
                    "speed": int(shoulder_roll_speed),
                    "acc": int(shoulder_roll_acc)
                }
            },
            "interval": 0
        }
        
        self._send_command(command)
    
    def control_right_hand(self, gripper_angle: float = 0.0, wrist_angle: float = 0.0,
                          elbow_angle: float = 0.0, shoulder_pitch: float = 0.0,
                          shoulder_yaw: float = 0.0, shoulder_roll: float = 0.0,
                          gripper_speed: int = 200, wrist_speed: int = 750,
                          elbow_speed: int = 200, shoulder_pitch_speed: int = 200,
                          shoulder_yaw_speed: int = 200, shoulder_roll_speed: int = 200,
                          gripper_acc: int = 20, wrist_acc: int = 20,
                          elbow_acc: int = 20, shoulder_pitch_acc: int = 20,
                          shoulder_yaw_acc: int = 20, shoulder_roll_acc: int = 20):
        """
        Control all right hand servos.
        
        Args:
            *_angle: Target angles for each servo in degrees
            *_speed: Movement speeds for each servo
            *_acc: Acceleration values for each servo
        """
        command = {
            "commandType": "command",
            "dataType": "rightHand",
            "payload": {
                "rightGripper": {
                    "angle": float(gripper_angle),
                    "speed": int(gripper_speed),
                    "acc": int(gripper_acc)
                },
                "rightWrist": {
                    "angle": float(wrist_angle),
                    "speed": int(wrist_speed),
                    "acc": int(wrist_acc)
                },
                "rightElbow": {
                    "angle": float(elbow_angle),
                    "speed": int(elbow_speed),
                    "acc": int(elbow_acc)
                },
                "rightSholderPitch": {
                    "angle": float(shoulder_pitch),
                    "speed": int(shoulder_pitch_speed),
                    "acc": int(shoulder_pitch_acc)
                },
                "rightSholderYaw": {
                    "angle": float(shoulder_yaw),
                    "speed": int(shoulder_yaw_speed),
                    "acc": int(shoulder_yaw_acc)
                },
                "rightSholderRoll": {
                    "angle": float(shoulder_roll),
                    "speed": int(shoulder_roll_speed),
                    "acc": int(shoulder_roll_acc)
                }
            },
            "interval": 0
        }
        
        self._send_command(command)
    
    def control_base(self, left_motor_speed: int = 0, right_motor_speed: int = 0):
        """
        Control base motors.
        
        Args:
            left_motor_speed: Left motor speed
            right_motor_speed: Right motor speed
        """
        command = {
            "commandType": "command",
            "dataType": "base",
            "payload": {
                "leftMotor": {
                    "speed": int(left_motor_speed)
                },
                "rightMotor": {
                    "speed": int(right_motor_speed)
                }
            },
            "interval": 0
        }
        
        self._send_command(command)
    
    def move_forward(self, speed: int = 100):
        """Move the robot forward"""
        self.control_base(speed, speed)
    
    def move_backward(self, speed: int = 100):
        """Move the robot backward"""
        self.control_base(-speed, -speed)
    
    def turn_left(self, speed: int = 100):
        """Turn the robot left"""
        self.control_base(-speed, speed)
    
    def turn_right(self, speed: int = 100):
        """Turn the robot right"""
        self.control_base(speed, -speed)
    
    def stop(self):
        """Stop all base motors"""
        self.control_base(0, 0)
    
    def close(self):
        """Close the serial connection"""
        if self._serial and self._serial.is_open:
            self._serial.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Convenience functions for quick access
def create_controller(port: str, baudrate: int = 115200) -> BonicBotController:
    """
    Create a BonicBot controller instance.
    
    Args:
        port: Serial port name
        baudrate: Serial baud rate
    
    Returns:
        BonicBotController instance
    """
    return BonicBotController(port, baudrate)


# Example usage and testing functions
if __name__ == "__main__":
    # Example usage
    try:
        # Create controller (adjust port as needed)
        with BonicBotController('/dev/ttyUSB0') as bot:
            
            # Control individual servo
            bot.control_servo('headPan', angle=45.0, speed=200, acc=20)
            time.sleep(1)
            
            # Control head
            bot.control_head(pan_angle=30.0, tilt_angle=-10.0)
            time.sleep(2)
            
            # Control left hand
            bot.control_left_hand(gripper_angle=90.0, elbow_angle=45.0)
            time.sleep(2)
            
            # Control right hand
            bot.control_right_hand(gripper_angle=45.0, wrist_angle=30.0)
            time.sleep(2)
            
            # Move base
            bot.move_forward(speed=50)
            time.sleep(1)
            bot.stop()
            
    except Exception as e:
        print(f"Error: {e}")
