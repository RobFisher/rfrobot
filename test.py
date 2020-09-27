import time
from adafruit_motorkit import MotorKit

kit = MotorKit()
kit.motor1.throttle = 1.0
kit.motor4.throttle = 0.965
time.sleep(2)
kit.motor1.throttle = 0.0
kit.motor4.throttle = 0.0

