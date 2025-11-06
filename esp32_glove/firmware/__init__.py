from machine import Pin, ADC, PWM, SoftI2C, I2C
from time import sleep
from mpu9250 import MPU9250 
from ak8963 import AK8963
from math import sqrt, atan2, pi, copysign, sin, cos
import socket
import ssd1306
from ssd1306 import *