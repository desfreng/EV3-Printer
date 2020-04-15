# coding=utf-8

"""The Printer module is a set of classes witch allow interacting at a low level with the printer.
"""

from time import sleep, time

from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
from ev3dev2.sensor.lego import ColorSensor

DEBUG = True
_TIME = time()


def _debug(obj, msg, begin_time=_TIME):
    if DEBUG:
        print("[{}]({}) {}".format(time() - begin_time, obj.__class__.__name__, msg))


class Pen:
    """Pen class witch allow managing the pen position. """

    def __init__(self, power=20):
        _debug(self, "Creating Pen instance")
        self.default_power = power

        self._pen_up_position = 0  # Lambda values. Needed to be set before !
        self._pen_down_position = 40

        self._m = LargeMotor(OUTPUT_C)
        self._m.stop_action = LargeMotor.STOP_ACTION_HOLD
        self.reset()

    def up(self, power=None):
        """ Set pen to 'up' position (only if is not already)

        :param power: Power of the rotation
        """
        if power is None:
            power = self.default_power

        if not self.is_up:
            self._m.on_to_position(power, self._pen_up_position)

    def down(self, power=None):
        """ Set pen to 'down' position (only if is not already)

        :param power: Power of the rotation
        """
        if power is None:
            power = self.default_power

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

    def reset(self, power=None):
        """Reset the pen position (set it to 'up')

        :param power: Power used to move the pen
        """
        if power is None:
            power = self.default_power

        self._m.on(-power)
        self._m.wait_until_not_moving()
        self._m.off()
        self._m.on_for_degrees(power, 20)
        sleep(1)

    def setup(self, validator):
        """ Setup the pen, define up and down position.

        :param validator: A callable objet used to validate the pen down position.
        When `True` is returned, the pen position will be saved to the down position."""
        self.reset()
        self._pen_up_position = self._m.position
        self._m.off(False)

        while not validator():
            sleep(0.1)

        self._pen_down_position = self._m.position
        self.up()

    def save_energy(self):
        """Save energy and release motor's holding state"""
        self._m.off(False)


class Carriage:
    """Carriage class witch allow managing the position. """

    def __init__(self, power=30):
        _debug(self, "Creating Carriage instance")

        self.default_power = power
        self._delta = 0

        self._m = LargeMotor(OUTPUT_B)
        self.reset()

    def reset(self, power=None):
        """Reset the carriage position and define a new origin for carriage's position

        :param power: Power used to move the carriage
        """
        if power is None:
            power = self.default_power

        self.right_limit(power=power, soft_limit=False)
        self._m.on_for_degrees(power, 50)
        self._delta = self._m.position

        self.go_to(0, power)

    def left(self, power=None):
        """Move carriage (pen will move too) to the 'left'

        :param power: Power of the rotation
        """
        if power is None:
            power = self.default_power

        self._m.on(power)

    def right(self, power=None):
        """Move carriage (pen will move too) to the 'right'

        :param power: Power of the rotation
        """
        if power is None:
            power = self.default_power

        self._m.on(-power)

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

        :param value: Reached position"""
        self.go_to(value)

    def go_to(self, position, power=None, block=True, override=False):
        """Move carriage to absolute position `position`

        :param position: Position reached
        :param power: Power used to move
        :param block: If True, fonction will end at the end of the rotation
        :param override: if true, bypass limits"""

        if power is None:
            power = self.default_power

        _debug(self, "Reached position is {}".format(position))

        if (not override) and (not -50 <= position <= 1240):
            raise ValueError("Position is out of reachable bounds.")

        self._m.on_to_position(power, position + self._delta, block=block)

    def move(self, value, power=None, block=True, override=False):
        """Move carriage of `value` degrees

        :param value: Position reached
        :param power: Power used to move
        :param block: If True, fonction will end at the end of the rotation
        :param override: if true, bypass limits"""
        if power is None:
            power = self.default_power

        self.go_to(self.position + value, power, block, override)

    def save_energy(self):
        """Save energy and release motor's holding state"""
        self._m.off(False)

    def right_limit(self, soft_limit=True, power=None):
        """Go to the right limit

        :param soft_limit: If True, carriage will move backward to avoid motor forcing
        :param power: power used to move"""

        if power is None:
            power = self.default_power

        self.right(power)

        self._m.wait_until_not_moving()
        self.stop()
        if soft_limit:
            self.move(50, power)

    def left_limit(self, soft_limit=True, power=None):
        """Go to the left limit

        :param soft_limit: If True, carriage will move backward to avoid motor forcing
        :param power: power used to move"""
        if power is None:
            power = self.default_power

        self.left(power)

        self._m.wait_until_not_moving()
        self.stop()

        if soft_limit:
            self.move(-50, power)


class Rollers:
    """Rollers class witch allow managing paper. """

    def __init__(self, power=30, prevent_paper_blocking=False):
        _debug(self, "Creating Rollers instance")

        self.default_power = power
        self._delta_in = 0
        self._delta_out = 0

        self._in = LargeMotor(OUTPUT_A)
        self._in.polarity = LargeMotor.POLARITY_NORMAL
        self._out = LargeMotor(OUTPUT_D)
        self._out.polarity = LargeMotor.POLARITY_INVERSED

        self._col = ColorSensor()
        self._col.mode = ColorSensor.MODE_COL_COLOR

        self._paper_taken = self._col.color == 6

        self.reset(prevent_paper_blocking)

    def reset(self, prevent_paper_blocking=False, power=None):
        """Eject paper if present and prevent paper blocking

        :param prevent_paper_blocking: if true, roller will move to avoid paper blocking
        :param power: Power used to move rollers
        """
        if power is None:
            power = self.default_power

        if self._paper_taken:
            self.eject_paper()
        elif prevent_paper_blocking:
            self._in.on_for_rotations(power, 3, block=False)
            self._out.on_for_rotations(power, 3)

    def up(self, power=None):
        """Move paper to the 'up'

        :param power: Power of the rotation
        """
        if power is None:
            power = self.default_power

        self._in.on(power)
        self._out.on(power)

    def down(self, power=None):
        """Move paper to the 'down'

        :param power: Power of the rotation
        """
        if power is None:
            power = self.default_power

        self._in.on(-power)
        self._out.on(-power)

    def stop(self):
        """ Stop moving rollers

        """
        self._in.off()
        self._out.off()

    def save_energy(self):
        """Save energy and release motor's holding state"""
        self._in.off(False)
        self._out.off(False)

    @property
    def has_paper(self):
        """ Get the paper state

        :return True if paper present"""
        return self._paper_taken

    @property
    def position(self):
        """ Get rollers position

        :return: rollers position
        """
        if not self.has_paper:
            return None

        return self._in.position - self._delta_in, self._out.position - self._delta_out

    @position.setter
    def position(self, value):
        """ Set Rollers position

        :param value: position reached"""
        self.go_to(value)

    def go_to(self, position, power=None, block=True, override=False):
        """Go to absolute position `position`

        :param position: Position Reached
        :param power: Power used to move
        :param block: If True, fonction will end at the end of the rotation
        :param override: if true, bypass limits"""

        if not self.has_paper:
            raise ValueError("There is no paper.")

        if power is None:
            power = self.default_power

        target_in = self._delta_in + position
        target_out = self._delta_out + position

        _debug(self, "Reached position is {}".format(position))

        _debug(self, "Target In {}".format(target_in))
        _debug(self, "Target Out {}".format(target_out))

        if (not override) and (not 0 <= position <= 515):
            raise ValueError("Position is out of reachable bounds.")

        self._in.on_to_position(power, target_in, block=False)
        self._out.on_to_position(power, target_out, block=block)

    def move(self, value, power=None, block=True):
        """Move rollers (and paper if present) of `value` degrees

        :param value: Degrees to move
        :param power; Power used to move
        :param block: If True, fonction will end at the end of the rotation"""
        if power is None:
            power = self.default_power

        self._in.on_to_position(power, self._in.position + value, block=False)
        self._out.on_to_position(power, self._out.position + value, block=block)

    def up_limit(self, power=None):
        """Go to paper up limit

        :param power: Power used to move"""

        self.go_to(0, power)

    def down_limit(self, power=None):
        """Go to paper down limit

        :param power: Power used to move"""
        self.go_to(515, power)

    def take_paper(self, power=None, power_grip=15):
        """ Take paper into printer and stretch it

        :param power: Power used to take paper
        :param power_grip: Power used to stretch paper
        """
        self.up(power)

        while self._col.color != 6:
            sleep(0.1)

        self.stop()
        self._out.on_for_seconds(power_grip, 1)
        self._paper_taken = self._col.color == 6

        self.move(-130)
        sleep(0.2)
        self._delta_in = self._in.position
        self._delta_out = self._out.position

    def eject_paper(self, power=None):
        """ Eject paper

        :param power: Power used to eject paper
        """
        self.up(power)
        sleep(0.5)

        while self._col.color == 6:
            sleep(0.1)
            _debug(self, "Color : {}".format(self._col.color))

        _debug(self, "Color : {}".format(self._col.color))
        sleep(0.5)
        self.stop()
        _debug(self, "Color : {}".format(self._col.color))
        self._paper_taken = False
        _debug(self, "Color : {}".format(self._col.color))
        self._delta_in = 0
        self._delta_out = 0


class Printer:
    """A Basic Printer class to interact with the printer at low level. Use this only if you need
    to interact exactly with the printer. """
    #
    # def __init__(self, prevent_paper_blocking=True):
    #     """ Constructor of Printer class
    #
    #
    #     :param prevent_paper_blocking: Set it to 'False' in order to disable roller move
    #     """
    #     pass
