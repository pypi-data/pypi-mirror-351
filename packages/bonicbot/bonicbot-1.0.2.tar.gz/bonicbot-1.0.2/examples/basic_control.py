#!/usr/bin/env python3
"""
Basic BonicBot Control Example

This example demonstrates basic control of the BonicBot robot including:
- Connecting to the robot
- Individual servo control
- Group control methods
- Basic movements

Make sure to adjust the serial port for your system:
- Linux/Mac: '/dev/ttyUSB0' or '/dev/ttyACM0'
- Windows: 'COM3' or similar
"""

import time
from bonicbot import BonicBotController, ServoID

def main():
    # Adjust port for your system
    PORT = '/dev/ttyUSB0'  # Change this to your robot's port
    
    print("BonicBot Basic Control Example")
    print("==============================")
    
    try:
        # Connect to robot using context manager
        with BonicBotController(PORT) as bot:
            print(f"✓ Connected to robot on {PORT}")
            
            # Individual servo control examples
            print("\n1. Individual Servo Control")
            print("Moving head pan to 45 degrees...")
            bot.control_servo(ServoID.HEAD_PAN, angle=45.0, speed=200)
            time.sleep(2)
            
            print("Moving head tilt to 20 degrees...")
            bot.control_servo('headTilt', angle=20.0, speed=150)
            time.sleep(2)
            
            # Group control examples
            print("\n2. Group Control - Head")
            print("Moving head to look around...")
            positions = [
                (45, 10),   # Look right and up
                (-45, 10),  # Look left and up
                (0, -20),   # Look forward and down
                (0, 0)      # Center position
            ]
            
            for pan, tilt in positions:
                print(f"Head position: pan={pan}°, tilt={tilt}°")
                bot.control_head(pan_angle=pan, tilt_angle=tilt)
                time.sleep(1.5)
            
            print("\n3. Hand Control")
            print("Moving left hand...")
            bot.control_left_hand(
                gripper_angle=45.0,
                elbow_angle=-30.0,
                shoulder_pitch=45.0
            )
            time.sleep(2)
            
            print("Moving right hand...")
            bot.control_right_hand(
                gripper_angle=-45.0,
                elbow_angle=30.0,
                shoulder_pitch=-45.0
            )
            time.sleep(2)
            
            print("\n4. Base Movement")
            print("Moving forward...")
            bot.move_forward(speed=80)
            time.sleep(1)
            
            print("Turning left...")
            bot.turn_left(speed=60)
            time.sleep(1)
            
            print("Turning right...")
            bot.turn_right(speed=60)
            time.sleep(1)
            
            print("Moving backward...")
            bot.move_backward(speed=80)
            time.sleep(1)
            
            print("Stopping...")
            bot.stop()
            
            print("\n5. Return to Home Position")
            # Return all servos to neutral position
            bot.control_head(pan_angle=0.0, tilt_angle=0.0)
            bot.control_left_hand()  # All parameters default to 0
            bot.control_right_hand()
            
            print("✓ Returned to home position")
            print("✓ Example completed successfully!")
            
    except FileNotFoundError:
        print(f"✗ Error: Could not find serial port {PORT}")
        print("  Please check your connection and adjust the PORT variable")
    except PermissionError:
        print(f"✗ Error: Permission denied for port {PORT}")
        print("  Try running with sudo or check port permissions")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        print("  Please check your robot connection and try again")

if __name__ == "__main__":
    main()