#!/usr/bin/micropython
import time

from printer import Printer
from ev3dev2.sensor.lego import InfraredSensor

ir = InfraredSensor()
ir.mode = ir.MODE_IR_REMOTE
pr = Printer(False)

print("Ready")
pr.ts.wait_for_pressed()
print("Let's Go")

pr.take_paper()

print("Press to start commanding...")

pr.ts.wait_for_pressed()

print("Commanding !")

while ir.value() != 9:
    if ir.value() == 0:
        pr.stop_all()
    elif ir.value() == 1:
        pr.stop_carriage()
        pr.up_forever()
    elif ir.value() == 2:
        pr.stop_carriage()
        pr.down_forever()
    elif ir.value() == 3:
        pr.stop_roller()
        pr.left_forever()
    elif ir.value() == 4:
        pr.stop_roller()
        pr.right_forever()
    elif ir.value() == 5:
        pr.toggle_pen()

print("End of commanding")
print("Press to eject paper...")
pr.ts.wait_for_pressed()

# End !

pr.eject_paper()
pr.stop_all()

print("End !")
