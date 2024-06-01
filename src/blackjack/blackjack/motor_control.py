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
global gesture_current
gesture_current = ""
global current_location
current_location = 0
kit = MotorKit(i2c = board.I2C())

# Subscriber class
class MotorController(Node):
    def __init__(self):
        super().__init__('motor_controller')
        self.subscription = self.create_subscription(String, 'my_turn', self.listener_callback, 1)
        self.subscription

    def listener_callback(self, msg):
        global gesture_current
        gesture_current = msg.data
        self.get_logger().info('I heard:test "%s"' % msg.data)

# Functions
def shoot_card():
    time.sleep(1)
    kit.motor2.throttle = -1
    time.sleep(.15)
    kit.motor2.throttle = 1
    time.sleep(0.15)
    kit.motor2.throttle = 0

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
        if gesture_current != "none":
            count_hand+=1
        else:
            count_hand = 0
        if count_hand == 7:
            return True
    return False

def check_for_gesture(motor_controller):
    global gesture_current
    gesture_last = ""
    count_gesture = 0
    while True:
        rclpy.spin_once(motor_controller)
        if gesture_current == gesture_last and gesture_current != "none":
            count_gesture+=1
        else:
            count_gesture = 0
        if count_gesture == 7:
            return gesture_current
        gesture_last = gesture_current

def main():
    rclpy.init()
    motor_controller = MotorController()
    # Initialize variables
    global current_location
    num_players = 0
    player_locations = np.zeros(6)
    # Show code is working
    rotate(100, 10)
    rotate(0, 10)
    #initialize screen
    lcd=CharLCD(i2c_expander='PCF8574',address=0x27,port=1,cols=16,rows=2,dotsize=8)
    lcd.clear()
    # Count players
    for i in range(5):
        lcd.clear()
        rotate(40*i,10)
        if check_for_player(motor_controller):
            num_players+=1
            player_locations[i] = 1
            lcd.write_string("Player " + str(i+1) + " is playing")
        else:
            lcd.write_string("Player " + str(i+1) + " is not playing")
        time.sleep(1)
    lcd.clear()
    time.sleep(1)
    # Start game
    # Shoot out all cards
    for j in range(2):
        for i in range(5):
            if player_locations[i]:
                rotate(40*(i),10)
                lcd.write_string("Player " + str(i+1))
                time.sleep(0.5)
                shoot_card()
                time.sleep(0.5)
                lcd.clear()
    # Play through the game
    for i in range(5):
        gesture = ""
        previous_gesture = ""
        if player_locations[i]:
            rotate(40*(i),10)
            while True:
                lcd.write_string("Player " + str(i+1) + " get busy")
                gesture = check_for_gesture(motor_controller)
                lcd.clear()
                time.sleep(0.5)
                if gesture == "Hit":
                    lcd.write_string("Player " + str(i+1) + " hits")
                    time.sleep(0.5)
                    shoot_card()
                    time.sleep(1)
                    lcd.clear()
                    time.sleep(0.5)
                    previous_gesture = "Hit"
                    continue
                if gesture == "Double" and previous_gesture != "Hit":
                    lcd.write_string("Player " + str(i+1) + " doubles")
                    time.sleep(0.5)
                    shoot_card()
                    time.sleep(1)
                    lcd.clear()
                    time.sleep(0.5)
                    break
                if gesture == "Split" and previous_gesture != "Hit":
                    lcd.write_string("Player " + str(i+1) + " splits")
                    time.sleep(0.5)
                    break
                if gesture == "Stand":
                    lcd.write_string("Player " + str(i+1) + " stands")
                    time.sleep(1)
                    lcd.clear()
                    time.sleep(0.5)
                    break
    lcd.write_string("Game over")



if __name__ == '__main__':
    main()


# Get inputs from player
#while(num_players <= 0 or num_players > 8):
#	num_players = int(input("Enter number of players: "))
#	if (num_players <= 0):
#		print("Not enough players")
#	if(num_players > 8):
#		print("Too many players")



