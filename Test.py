#!/usr/bin/micropython
from math import pi
import time

from ev3dev2.motor import SpeedPercent

from printer import Printer
from Sketcher import Sketcher

p = Printer(False)
s = Sketcher(p)

p.all_off()


def do_test(spd, motor):
    target_pos = motor.position + 720
    t1 = time.time()
    motor.on(SpeedPercent(spd))
    while motor.position <= target_pos:
        pass
    motor.off()
    t2 = time.time()

    time.sleep(0.2)

    target_pos -= 1200
    t3 = time.time()
    motor.on(SpeedPercent(-spd))
    while motor.position >= target_pos:
        pass
    motor.off()
    t4 = time.time()

    time.sleep(0.2)

    return t2 - t1, t4 - t3


def go(motor):
    print("Angle\tSpeed\tTime +\tTime -")

    speed_var = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40, 45, 50, 55, 60, 65, 70, 75, 80,
                 85, 90, 95, 100]

    for speed in speed_var:
        results = do_test(speed, motor)
        print("{}\t{}\t{}\t{}".format(1200, speed, results[0], results[1]).replace('.', ','))


if __name__ == '__main__':
    go(p._in)
    print()
    go(p._out)


def draw_spiral(max=100):
    a = True
    for i in range(max, 0, -10):
        if a:
            s.carriage_millimeter(i)
            s.roller_millimeter(i)
            a = False
        else:
            s.carriage_millimeter(-i)
            s.roller_millimeter(-i)
            a = True
