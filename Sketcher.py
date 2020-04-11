# coding=utf-8
from printer import Printer


class Sketcher:
    def __init__(self, printer):
        if not isinstance(printer, Printer):
            return

        self._p = printer
        self._x_pos = 0
        self._y_pos = 0

    def carriage_millimeter(self, distance):
        self._p.left_degrees(distance*360/78)

    def roller_millimeter(self, distance):
        self._p.up_degrees(distance*360/132)
