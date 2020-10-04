from adafruit_motorkit import MotorKit
import gpiozero


THROTTLE_SETTLE_SAMPLE = 10


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
        self._throttle_memory = {}
        self._num_iterations = 0
        self._max_throttle = 0.0
        self._run_time_ms = 0
    
    def stop(self):
        if self._motor_throttle != 0:
            print("Stopping. Starting throttle: {} Max throttle: {} Encoder count: {} Run time: {}ms".format(
                self._throttle_memory.get(self.speed, 'not set'),
                self._max_throttle,
                self._encoder_count,
                self._run_time_ms
            ))
        self._motor.throttle = 0
        self._motor_throttle = 0
        self.speed = 0
        self._integral_sum = 0
        self._encoder_count = 0
        self._last_encoder_count = 0
    
    def set_speed(self, speed, direction):
        self._run_time_ms = 0
        self._integral_sum = 0
        self._encoder_count = 0
        self._last_encoder_count = 0
        throttle_guess = max(0.0, self._throttle_memory.get(speed, min(float(speed) / 80, 1.0)))
        self._motor_throttle = throttle_guess
        self._max_throttle = throttle_guess
        if direction:
            self._motor.throttle = self._motor_throttle
        else:
            self._motor.throttle = 0.0 - self._motor_throttle
        self.speed = speed
        self.direction = direction
        self._stall_count = 0
        self._num_iterations = 0

    def update_speed(self, elapsed_ms):
        self._run_time_ms += elapsed_ms
        correct_distance = float(elapsed_ms) / 1000.0 * self.speed
        distance_moved = self._encoder_count - self._last_encoder_count
        if distance_moved == 0 or self._motor_throttle > 0.95:
            self._stall_count += 1
        else:
            self._stall_count = 0
        if self._stall_count > 3:
            print("Stall detected.")
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
        self._max_throttle = max(self._max_throttle, self._motor_throttle)
        #print("distance: {} error: {} correction: {} throttle: {}".format(
        #    distance_moved,
        #    error,
        #    correction,
        #    self._motor_throttle
        #))
        self._num_iterations += 1
        if self._num_iterations == THROTTLE_SETTLE_SAMPLE:
            self._throttle_memory[self.speed] = self._motor_throttle
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
