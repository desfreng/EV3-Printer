#!/usr/bin/micropython
import printer

p = printer.Pen()
c = printer.Carriage()
r = printer.Rollers()

o = r._out
o.polarity = printer.LargeMotor.POLARITY_INVERSED
i = r._in
i.polarity = printer.LargeMotor.POLARITY_NORMAL

delta_in = 0
delta_out = 0


def sync(pos):
    delta_in = i.position - pos
    delta_out = o.position - pos


def motor_go_to(pos, power=100):
    i.on_to_position(power, pos, block=False)
    o.on_to_position(power, pos, block=False)


def go_to(pos, power=100):
    i.on_to_position(power, pos + delta_in, block=False)
    o.on_to_position(power, pos + delta_out, block=False)


def position():
    return i.position - delta_in, o.position - delta_out
