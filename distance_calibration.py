import robot

r = robot.Robot()

left_count, right_count = r.get_wheel_count()
distance = r.get_distance()

r.forward(1.0, 1000)
new_left_count, new_right_count = r.get_wheel_count()
new_distance = r.get_distance()

print("Travelled {}mm in 1s. Left wheel count {}; right wheel count {}.".format(
    distance - new_distance,
    new_left_count - left_count,
    new_right_count - right_count,
))
