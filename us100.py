import time
import serial

s = serial.Serial(
    port = '/dev/ttyS0',
    baudrate = 9600,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    bytesize = serial.EIGHTBITS,
    timeout = 1
)


def get_distance():
    s.write(b'\x55')
    time.sleep(0.01)
    result = s.read(size=2)
    distance_mm = (int(result[0]) * 256) + int(result[1])
    return distance_mm


if __name__ == '__main__':
    while True:
        print('{}mm'.format(get_distance()))
        time.sleep(0.2)
