# -*- coding: utf-8 -*-
"""
Some basic and general purpose geometric functions and classes.
"""

import re


class Coord():
    """
    Generic coordinates object that will store x,y coordinates and dx,dy deltas for each one. The reason to store those
    deltas is because they can be used to store extra information like deltas (of course) but for also for more
    interesting things like random positions (i.e. x ± random(dx)), etc...

    I think that 2D is enough by now but maybe in the future this class should be converted to two different classes
    like "Coord" and "Coords". "Coord" to store one coordinate (x axis, for example) and its delta and "Coords" to store
    the group of 3 or more axis.
    """
    def __init__(self, pf_x=0.0, pf_dx=0.0, pf_y=0.0, pf_dy=0.0):
        self.f_x = pf_x
        self.f_dx = pf_dx
        self.f_y = pf_y
        self.f_dy = pf_dy

    def __str__(self):
        u_output = u'<Coord: x+dx = %s+%s  y+dy = %s+%s>' % (self.f_x, self.f_dx, self.f_y, self.f_dy)
        return u_output.encode('ascii')

    def from_str(self, pu_str):
        """
        Method to populate the coordinates from a string with the format x±dx,y±dy.
        """

        self.f_x, self.f_dx, self.f_y, self.f_dy = _parse_coords_chunk(pu_str)


def is_valid_coord_string(pu_string):
    """
    Function to check if a string is a valid coordinates string.

    :param pu_string: Coordinate string. i.e. "1+4,4-0.5". The coordinates are x±dx,y±dy, where x,y are the standard
                      horizontal-vertical coordinates and dx,dy are deltas to x,y coordinates.

    :return: True if the string is a valid coordinate string, False in other case.
    """
    try:
        f_x, f_dx, f_y, f_dy = _parse_coords_chunk(pu_string)
        b_is_valid_coord_string = True
    except ValueError:
        b_is_valid_coord_string = False

    return b_is_valid_coord_string


def _parse_coords_chunk(pu_coords_chunk):
    """
    Function to parse a 2D MULTIPLE coordinates chunk. i.e. "4+0.1,3+4" in the form of x+dx,y+dy.

    :param pu_coords_chunk:
    :return:
    """

    # Parameter validation
    # ...1st check: only "digits", "+", "-", ".", and ","
    o_match = re.findall(r'[^\d+\-\.,]', pu_coords_chunk)
    if o_match:
        raise ValueError('Invalid characters: %s' % ', '.join(o_match))

    # ...2nd check: simplifying double sign symbols
    u_coords_chunk = pu_coords_chunk
    u_coords_chunk = u_coords_chunk.replace(u'-+', u'-')
    u_coords_chunk = u_coords_chunk.replace(u'+-', u'-')
    u_coords_chunk = u_coords_chunk.replace(u'--', u'+')
    u_coords_chunk = u_coords_chunk.replace(u'++', u'+')

    # 1st coordinate (x) is mandatory
    u_x_chunk = u_coords_chunk.partition(u',')[0]
    f_x, f_dx = _parse_coord_chunk(u_x_chunk)

    # while second one (y) can exist or not
    try:
        u_y_chunk = u_coords_chunk.partition(u',')[2]
        f_y, f_dy = _parse_coord_chunk(u_y_chunk)
    except IndexError:
        f_y, f_dy = 0.0, 0.0

    return f_x, f_dx, f_y, f_dy


def _parse_coord_chunk(pu_coord_chunk):
    """
    Function to parse a SINGLE coordinate string. i.e. "4+0.1" or "-100+20" where the first part is the coordinate
    itself and the second part after the sign is a delta value.

    :param pu_coord_chunk: Coordinate string. i.e. '15+3'.

    :return: The parsed coordinate as a dictionary. i.e. {'f_coor': 15, 'f_delta': 3}
    """

    lu_values = re.findall(r'([+\-]?\d+)', pu_coord_chunk)

    # 1st element, the actual coordinate, is mandatory
    f_coord = float(lu_values[0])

    # While the second one, the delta, can exist or not
    try:
        f_delta = float(lu_values[1])
    except IndexError:
        f_delta = 0.0

    return f_coord, f_delta


def max_in_rect(ptf_rect=(0.0, 0.0), ptf_aspect=(0.0, 0.0)):
    """
    Function to determine the biggest rectangle with certain aspect ratio that fits inside another rectangle.

    :param ptf_rect: Container rectangle size (width, height). i.e. (1920.0, 1080.0)

    :param ptf_aspect: Inner rectangle aspect ratio (width, height). i.e. (4.0, 3.0)

    :return: A tuple with the (width, height) of the maximum size rectangle. i.e. (1440, 1080)
    """

    # Option 1: Make inner width = container width
    #---------------------------------------------
    f_width_1 = ptf_rect[0]
    f_height_1 = f_width_1 * ptf_aspect[1] / ptf_aspect[0]

    # Option 2: Make inner height = container height
    #-----------------------------------------------
    f_height_2 = ptf_rect[1]
    f_width_2 = f_height_2 * ptf_aspect[0] / ptf_aspect[1]

    if f_width_1 <= ptf_rect[0] and f_height_1 <= ptf_rect[1]:
        tf_in_rect = (f_width_1, f_height_1)
    else:
        tf_in_rect = (f_width_2, f_height_2)

    return tf_in_rect