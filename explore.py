import time
import random
import robot
import atexit

movement_speed = 0.8

r = robot.Robot()
def stop():
    r.stop()
atexit.register(stop)

if __name__ == '__main__':
    while True:
        r.forward(movement_speed, 4000)
        time.sleep(0.5)
        print("reversing")
        r.forward(0-movement_speed, short_distance_threshold=None)
        time.sleep(0.5)
        r.stop()
        time.sleep(random.randrange(10) * 0.5 + 0.5)
        direction = bool(random.getrandbits(1))
        print("spinning")
        spin_speed = 0.8 if direction else -0.8
        r.spin(spin_speed)
        time.sleep(0.5)
        r.spin(spin_speed, 2000, short_distance_threshold=None, long_distance_threshold=400)
        time.sleep(0.5)
