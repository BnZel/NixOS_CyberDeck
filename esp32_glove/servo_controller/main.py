'''
REFERENCES:
    - https://github.com/jefmenegazzo/mpu-i2c-drivers-python

    - https://github.com/adafruit/Adafruit_CircuitPython_PCA9685/blob/main/examples/pca9685_servo.py

    - https://github.com/pyenv/pyenv?tab=readme-ov-file#installation
'''

from curses.ascii import isdigit
import dataclasses
from hashlib import sha1
import time, socket
import board, busio, digitalio

from adafruit_servokit import ServoKit
import adafruit_pca9685, adafruit_motor.servo

from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250


def init_servos(num_servos=15):
    '''
    initializes servos connected to PCA9685
    '''
    s = [0] * num_servos
    if num_servos <= 0:
        return s

    for i in range(num_servos):
        s[i] = servo.Servo(pca.channels[i])
        s[i].angle = 0
        print(f"Servo {i} angle: {s[i].angle}")

    print(f"Number of servos intialized: {len(s)}")
    return s


def control(servos):
    '''
    Control servo angles
    and limit their angles (0 - 180)
    '''
    for i in range(len(servos)):
        servo[i].angle = limit(servos[i])

    print(f"(A3) S0: {servo[0].angle} | (A4) S1: {servo[1].angle} | (D32) S2: {servo[2].angle} | (D33) S3: {servo[3].angle}")


def limit(angle):
    if angle >= 180:
        angle = 180
        return angle
    elif angle <= 0:
        angle = 0
        return angle
    else:
        return angle
    

def connect(host="10.0.0.245",port=1234):
    '''
    Connect to NixStick TCP server port 1234
    '''

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host,port))

        ack = client.recv(4096)
        print(f"Server acknowledgment: {ack.decode().strip()}")
        
        while True:           
            client.send("SERVERDECK".encode())
            recv_ = client.recv(4096)

            # strip csv and unpack data into 
            # 4 active servos on PCA9685:
            #   s1 => index finger
            #   s2 => middle finger
            #   s3 => ring finger
            #   s4 => pinky finger
            s1,s2,s3,s4 = recv_.decode().strip().split(",")
            servos = [
                      int(s1),
                      int(s2),
                      int(s3),
                      int(s4)
                    ]
                        
            control(servos)


if __name__ == "__main__":
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c)
    kit = ServoKit(channels=16)

    servo = init_servos(4)
    connect()