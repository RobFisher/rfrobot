import time
import us100
import motor_speed_controller


DEFAULT_SHORT_DISTANCE_THRESHOLD=70
DEFAULT_LONG_DISTANCE_THRESHOLD=250


class Robot:
    def __init__(self):
        self._left_motor = motor_speed_controller.MotorSpeedController(4)
        self._right_motor = motor_speed_controller.MotorSpeedController(1)

    def stop(self, time_ms=None, short_distance_threshold=DEFAULT_SHORT_DISTANCE_THRESHOLD, long_distance_threshold=None):
        elapsed_time = 0.0
        if time_ms is not None:
            while elapsed_time < time_ms:
                try:
                    distance = us100.get_distance()
                except IndexError:
                    print("Distance sensor fail")
                    break
                print(distance)
                if short_distance_threshold is not None and distance < short_distance_threshold:
                    break
                if long_distance_threshold is not None and distance > long_distance_threshold:
                    break
                time.sleep(0.05)
                elapsed_time += 50
                if self._left_motor.update_speed(50) == False:
                    print("Left stall!")
                    break
                if self._right_motor.update_speed(50) == False:
                    print("Right stall!")
                    break
        self._left_motor.stop()
        self._right_motor.stop()

    def forward(self, speed, time_until_stop_ms=None, short_distance_threshold=DEFAULT_SHORT_DISTANCE_THRESHOLD, long_distance_threshold=None):
        print("forward {}".format(speed))
        direction = False
        if speed > 0.0:
            direction = True
        self._left_motor.set_speed(abs(speed * 80), direction)
        self._right_motor.set_speed(abs(speed * 80), direction)
        if time_until_stop_ms is not None:
            self.stop(time_until_stop_ms, short_distance_threshold=short_distance_threshold, long_distance_threshold=long_distance_threshold)

    def spin(self, speed, time_until_stop_ms=None, short_distance_threshold=DEFAULT_SHORT_DISTANCE_THRESHOLD, long_distance_threshold=None):
        self._left_motor.set_speed(abs(speed * 80), True if speed > 0 else False)
        self._right_motor.set_speed(abs(speed * 80), False if speed > 0 else True)
        if time_until_stop_ms is not None:
            self.stop(time_until_stop_ms, short_distance_threshold=short_distance_threshold, long_distance_threshold=long_distance_threshold)

    def dance(self):
        self.forward(0.8, 1000)
        self.forward(-0.5, 500)
        self.spin(0.8, 500)
        self.spin(-0.8, 500)
        self.forward(-1.0, 750)
        self.spin(0.8, 1500)
    
    def get_distance(self):
        return us100.get_distance()

    def get_wheel_count(self):
        return self._left_motor._encoder_count, self._right_motor._encoder_count


if __name__ == '__main__':
    robot = Robot()
    robot.dance()

