from adafruit_motorkit import MotorKit
import gpiozero


class MotorSpeedController:
    def _encoder_input_changed(self, a, b):
        self._encoder_count += 1

    def __init__(self, motor):
        self._kit = MotorKit()
        if motor == 1:
            self._motor = self._kit.motor1
            self._encoder = gpiozero.DigitalInputDevice(17)
        else:
            self._motor = self._kit.motor4
            self._encoder = gpiozero.DigitalInputDevice(27)
        self.speed = 0
        self.direction = True
        self._error = 0
        self._integral_sum = 0
        self._motor.throttle = 0
        self._encoder_count = 0
        self._last_encoder_count = 0
        self._last_error = 0
        self._stall_count = 0
        self._encoder.pin.when_changed = self._encoder_input_changed
    
    def stop(self):
        self._motor.throttle = 0
        self._motor_throttle = 0
        self.speed = 0
        self._integral_sum = 0
        self._encoder_count = 0
        self._last_encoder_count = 0
    
    def set_speed(self, speed, direction):
        self._integral_sum = 0
        self._encoder_count = 0
        self._last_encoder_count = 0
        throttle_guess = max(0.0, min(float(speed) / 80, 1.0))
        self._motor_throttle = throttle_guess
        if direction:
            self._motor.throttle = self._motor_throttle
        else:
            self._motor.throttle = 0.0 - self._motor_throttle
        self.speed = speed
        self.direction = direction
        self._stall_count = 0

    def update_speed(self, elapsed_ms):
        correct_distance = float(elapsed_ms) / 1000.0 * self.speed
        distance_moved = self._encoder_count - self._last_encoder_count
        if distance_moved == 0:
            self._stall_count += 1
        else:
            self._stall_count = 0
        if self._stall_count > 2:
            self.stop()
            return False
        self._last_encoder_count = self._encoder_count
        error = correct_distance - distance_moved
        self._integral_sum += error
        derivative = self._last_error - error
        self._last_error = error
        correction = (error * 0.04) + (self._integral_sum * 0.004) + (derivative * 0.004)
        if abs(correction) > 0.01:
            self._motor_throttle = max(0.0, min(1.0, self._motor_throttle + correction))
            if self.direction:
                self._motor.throttle = self._motor_throttle
            else:
                self._motor.throttle = 0.0 - self._motor_throttle
        print("distance: {} error: {} correction: {} throttle: {}".format(
            distance_moved,
            error,
            correction,
            self._motor_throttle
        ))
        return True


if __name__ == '__main__':
    import time
    c = MotorSpeedController(1)
    c.set_speed(40, False)
    for i in range(500):
        time.sleep(0.050)
        try:
            if c.update_speed(50) == False:
                break
        except ValueError:
            break
    c.stop()
