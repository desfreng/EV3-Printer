# coding=utf-8

"""The Printer module is made of classes witch allow to interact at and low level with the printer."""

from time import sleep, time

from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent
from ev3dev2.sensor.lego import TouchSensor, ColorSensor

debug_enabled = False
_time = time()


def _debug(obj, msg, begin_time=_time):
    if debug_enabled:
        print("[{}]({}) {}".format(time() - begin_time, obj.__class__.__name__, msg))


class Pen:
    default_power = 20

    def __init__(self, power=default_power):
        _debug(self, "Creating Pen instance")
        self.default_power = power

        self._pen_up_position = 0  # Lambda values. Needed to setup before !
        self._pen_down_position = 40

        self._m = LargeMotor(OUTPUT_C)
        self._m.stop_action = LargeMotor.STOP_ACTION_HOLD
        self.reset()

    def up(self, power=default_power):
        """ Set pen to 'up' position (only if is not already)

        :param power: Power of the rotation
        """
        if not self.is_up:
            self._m.on_to_position(power, self._pen_up_position)

    def down(self, power=default_power):
        """ Set pen to 'down' position (only if is not already)

        :param power: Power of the rotation
        """
        if self.is_up:
            self._m.on_to_position(power, self._pen_down_position)

    @property
    def is_up(self):
        """ Get the pen position

        :return: True if pen up, False otherwise
        """
        return self._m.position < self._pen_up_position + 15

    def toggle(self):
        """ Change pen position to the opposite

        Pen Up ==> Pen Down
        Pen Down ==> Pen Up
        """
        if self.is_up:
            self.down()
        else:
            self.up()

    def reset(self, power=default_power):
        """Reset the pen position (set it to 'up')

        :param power: Power used to move the pen
        """
        self._m.on(-power)
        self._m.wait_until_not_moving()
        self._m.off()
        self._m.on_for_degrees(power, 20)
        sleep(1)

    def setup(self, validator):
        """ Setup the pen, define up and down position.

        """
        self.reset()
        self._pen_up_position = self._m.position
        self._m.off(False)

        while not validator():
            sleep(0.1)

        self._pen_down_position = self._m.position
        self.up()


class Carriage:
    default_power = 30

    def __init__(self, power=default_power):
        self.default_power = power
        self._delta = 0

        self._m = LargeMotor(OUTPUT_B)
        self.reset()

    def reset(self, power=default_power):
        """Reset the carriage position and define a new origin for carriage's position

        :param power: Power used to move the carriage
        """

        self.right_limit(power=power, soft_limit=False)
        self._m.on_for_degrees(power, 50)
        self._delta = self._m.position

        self.go_to(0, power)

    def left(self, power=default_power):
        """Move carriage (pen will move too) to the 'left'

        :param power: Power of the rotation
        """
        self._m.on(power)

    def right(self, power=default_power):
        """Move carriage (pen will move too) to the 'right'

        :param power: Power of the rotation
        """
        self._m.on(-power)2

    def stop(self):
        """ Stop moving carriage

        """
        self._m.off()

    @property
    def position(self):
        """ Get carriage position

        :return: carriage position
        """
        return self._m.position - self._delta

    @position.setter
    def position(self, value):
        """ Set carriage position

        :param value: New carriage position"""
        self.go_to(value)

    def go_to(self, position, power=default_power, override=False):
        _debug(self, "Reached position is {}".format(position))

        if (not override) and (not -50 < position < 1240):
            raise ValueError("Position is out of reachable bounds.")

        self._m.on_to_position(power, position + self._delta)

    def move(self, position, power=default_power, override=False):
        self.go_to(self.position + position, power, override)

    def save_energy(self):
        self._m.off(False)

    def right_limit(self, soft_limit=True, power=default_power):
        self.right(power)

        self._m.wait_until_not_moving()
        self.stop()
        if soft_limit:
            self.move(50, power)

    def left_limit(self, soft_limit=True, power=default_power):
        self.left(power)

        self._m.wait_until_not_moving()
        self.stop()

        if soft_limit:
            self.move(-50, power)


class Rollers:
    default_power = 30

    def __init__(self, power=default_power):
        self.default_power = power
        self._delta = 0

        self._m = LargeMotor(OUTPUT_B)
        self.reset()

    def reset(self, power=default_power):
        """Reset the carriage position and define a new origin for carriage's position

        :param power: Power used to move the carriage
        """

        self.right_limit(power=power, soft_limit=False)
        self._m.on_for_degrees(power, 50)
        self._delta = self._m.position

        self.go_to(0, power)

    def up(self, power=default_power):
        """Move carriage (pen will move too) to the 'left'

        :param power: Power of the rotation
        """
        self._m.on(power)

    def down(self, power=default_power):
        """Move carriage (pen will move too) to the 'right'

        :param power: Power of the rotation
        """
        self._m.on(-power)2

    def stop(self):
        """ Stop moving carriage

        """
        self._m.off()

    @property
    def position(self):
        """ Get carriage position

        :return: carriage position
        """
        return self._m.position - self._delta

    @position.setter
    def position(self, value):
        """ Set carriage position

        :param value: New carriage position"""
        self.go_to(value)

    def go_to(self, position, power=default_power, override=False):
        _debug(self, "Reached position is {}".format(position))

        if (not override) and (not -50 < position < 1240):
            raise ValueError("Position is out of reachable bounds.")

        self._m.on_to_position(power, position + self._delta)

    def move(self, position, power=default_power, override=False):
        self.go_to(self.position + position, power, override)

    def save_energy(self):
        self._m.off(False)

    def up_limit(self, soft_limit=True, power=default_power):
        self.right(power)

        self._m.wait_until_not_moving()
        self.stop()
        if soft_limit:
            self.move(50, power)

    def down_limit(self, soft_limit=True, power=default_power):
        self.left(power)

        self._m.wait_until_not_moving()
        self.stop()

        if soft_limit:
            self.move(-50, power)

class Printer:
    """A Basic Printer class to interact with the printer at low level. Use this only if you need to interact exactly
    with the printer. """

    power_roller = 30
    power_grip = 15
    power_carriage = 30
    power_pen = 20

    def __init__(self, prevent_paper_blocking=True):
        """ Constructor of Printer class


        :param prevent_paper_blocking: Set it to 'False' in order to disable roller move
        """
        self.debug = debug
        self._delta_carriage = 0
        self._delta_pen = 0

        self._pen_up_position = 8  # From Test for a pen
        self._pen_down_position = 65  # From Test for a pen

        self._in = LargeMotor(OUTPUT_A)
        self._out = LargeMotor(OUTPUT_D)

        self.color = ColorSensor()
        self.touch_sensor = TouchSensor()

        self.color.mode = ColorSensor.MODE_COL_COLOR

        self._in.stop_action = LargeMotor.STOP_ACTION_HOLD
        self._out.stop_action = LargeMotor.STOP_ACTION_HOLD

        if prevent_paper_blocking:
            self._debug("Eject Paper")
            self._in.on_for_seconds(SpeedPercent(-100), 5, block=False)
            self._out.on_for_seconds(SpeedPercent(100), 5, block=False)

        if prevent_paper_blocking:
            self._in.wait_until_not_moving()
            self._out.wait_until_not_moving()

    def _debug(self, msg):
        if self.debug:
            print(msg)

    # Roller Methods

    def up_degrees(self, deg, power=power_roller):
        """ Turn Roller to make paper go 'up'

        :param deg: Degrees of the rotation
        :param power: Power of the rotation
        """
        self._in.on_for_degrees(SpeedPercent(power), deg, block=False)
        self._out.on_for_degrees(SpeedPercent(-power), deg)

    def down_degrees(self, deg, power=power_roller):
        """ Turn Roller to make paper go 'down'

        :param deg: Degrees of the rotation
        :param power: Power of the rotation
        """
        self._in.on_for_degrees(SpeedPercent(-power), deg, block=False)
        self._out.on_for_degrees(SpeedPercent(power), deg)

    def up_forever(self, power=power_roller):
        """Turn Roller to make paper go 'up'

        :param power: Power of the rotation
        """
        self._in.on(SpeedPercent(power))
        self._out.on(SpeedPercent(-power))

    def down_forever(self, power=power_roller):
        """Turn Roller to make paper go 'down'

        :param power: Power of the rotation
        """
        self._in.on(SpeedPercent(-power))
        self._out.on(SpeedPercent(power))

    # Carriage Methods

    # Pen Methods

    # Reset & Setup Methods

    def reset_roller(self, power=power_roller):
        """Reset the roller position and define a new origin for roller's position

        :param power: Power used to move rollers
        """
        pass

    # Stop Methods

    def stop_roller(self):
        """ Stop moving roller

        """
        self._in.off()
        self._out.off()

    def stop_all(self):
        """ Stop all motor

        """
        self.stop_roller()

    # Position Methods

    @property
    def roller_position(self):
        """ Get roller position

        :return: roller position
        """
        return

    # Advanced Methods

    def take_paper(self, power_p=power_roller, power_g=power_grip):
        """ Take paper into printer and stretch it

        :param power_p: Power used to take paper
        :param power_g: Power used to stretch paper
        """
        self.up_forever(power_p)

        while self.color.color != 6:
            sleep(0.1)

        self.stop_roller()
        self._out.on_for_seconds(SpeedPercent(-power_g), 1)

    def eject_paper(self, power=power_roller):
        """ Eject from the printer

        :param power: Power used to eject paper
        """
        self.up_forever(power)
        sleep(0.5)

        while self.color.color == 6:
            self.up_forever(power)

        self.stop_roller()
