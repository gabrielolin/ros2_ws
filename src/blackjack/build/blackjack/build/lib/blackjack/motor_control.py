#!/usr/bin/env python3
# Below imports all neccessary packages to make this Python Script run
import numpy as np

import time
import board
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from RPLCD.i2c import CharLCD


# Initialize global variables
global gesture_last
gesture_last = ""
global count_gesture
count = 0
global current_location
current_location = 0
kit = MotorKit(i2c = board.I2C())

# Subscriber class
class MotorController(Node):
    def __init__(self):
        super().__init__('motor_controller')
        self.subscription = self.create_subscription(String, 'my_turn', self.listener_callback, 10)
        self.subscription

    def listener_callback(self, msg):
        global gesture_last
        global count_gesture
        if msg.data == gesture_last:
            count_gesture+=1
        else:
            count_gesture = 0

        gesture_last = msg.data
        self.get_logger().info('I heard:test "%s"' % msg.data)

# Functions
def shoot_card():
    time.sleep(1)
    kit.motor1.throttle = -1
    time.sleep(.15)
    kit.motor1.throttle = 1
    time.sleep(0.15)
    kit.motor1.throttle = 0

def rotate(location, speed):
    global current_location
    distance = min(abs(current_location-location), abs((current_location-200)-location), abs(current_location-(location-200)))
    if location >= current_location and (location-current_location) < 100:
        for i in range(distance):
            kit.stepper2.onestep()
            time.sleep(1/(speed*10))
        current_location = location
    elif location >= current_location and (location-current_location) >= 100:
        for i in range(distance):
            kit.stepper2.onestep(direction=stepper.BACKWARD)
            time.sleep(1/(speed*10))
        current_location = location
    elif location < current_location and (current_location-location) < 100:
        for i in range(distance):
            kit.stepper2.onestep(direction=stepper.BACKWARD)
            time.sleep(1/(speed*10))
        current_location = location
    elif location < current_location and (current_location-location) >= 100:
        for i in range(distance):
            kit.stepper2.onestep()
            time.sleep(1/(speed*10))
        current_location = location
        
        
def check_for_player(motor_controller):
    count_hand = 0
    for i in range(20):
        rclpy.spin_once(motor_controller)
        if gesture_last != "none":
            count_hand+=1
        else:
            count_hand = 0
        if count_hand == 6:
            return True
        
    return False

def main():
    rclpy.init()
    motor_controller = MotorController()
    
    while rclpy.ok():
        #initialize screen
        lcd=CharLCD(i2c_expander='PCF8574',address=0x27,port=1,cols=16,rows=2,dotsize=8)
        lcd.clear()
        # Show code is working
        rotate(100, 10)
        time.sleep(1.0)
        rotate(0, 10)
        rclpy.spin_once(motor_controller)
        # Initialize variables
        global current_location
        num_players = 0
        player_locations = np.zeros(6)

        # Count players
        i = 1
        while True:
            time.sleep(2.0)
            lcd.clear()
            if check_for_player(motor_controller):
                num_players+=1
                player_locations[i-1] = 1
            rotate(40*i,10)
            lcd.write_string(str(player_locations[i-1]))
            i=i+1
            if i==7:
                i=1
            lcd.write_string('outside loop')
            for j in range(2):
                for i in range(6):
                    if player_locations[i-1]:
                        lcd.write_string('inside loop')
                        rotate(40*i,10)
                i=1
                rclpy.spin_once(motor_controller)
                time.sleep(1.0)
    rclpy.shutdown()


if __name__ == '__main__':
    main()


# Get inputs from player
#while(num_players <= 0 or num_players > 8):
#	num_players = int(input("Enter number of players: "))
#	if (num_players <= 0):
#		print("Not enough players")
#	if(num_players > 8):
#		print("Too many players")



