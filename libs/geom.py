# -*- coding: utf-8 -*-
"""
Some basic and general purpose geometric functions and classes.
"""

import math
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
    def __init__(self, pu_string=None):
        self.f_x = None
        self.f_dx = None
        self.f_y = None
        self.f_dy = None

        try:
            tf_parsed_numbers = _parse_coords_chunk(pu_string)
            self.f_x = tf_parsed_numbers[0]
            self.f_dx = tf_parsed_numbers[1]
            self.f_y = tf_parsed_numbers[2]
            self.f_dy = tf_parsed_numbers[3]
        except ValueError:
            raise ValueError

    def __str__(self):
        u_output = u'<Coord: x+dx = %s+%s  y+dy = %s+%s>' % (self.f_x, self.f_dx, self.f_y, self.f_dy)
        return u_output.encode('ascii')


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

    lu_values = re.findall(r'([+\-]?\d+\.?\d*)', pu_coord_chunk)

    # 1st element, the actual coordinate, is mandatory
    f_coord = float(lu_values[0])

    # While the second one, the delta, can exist or not
    try:
        f_delta = float(lu_values[1])
    except IndexError:
        f_delta = 0.0

    return f_coord, f_delta


def max_rect_in(ptf_rec_out=(0.0, 0.0), pf_rot_in=0.0, ptf_asp_in=(0.0, 0.0)):
    """
    Function to determine the biggest rectangle with certain aspect ratio that fits inside another rectangle.

    :param ptf_rec_out: Container rectangle size (width, height). i.e. (1920.0, 1080.0)

    :param pf_rot_in: Rotation of the inner rectangle in degrees. i.e. 23.5

    :param ptf_asp_in: Inner rectangle aspect ratio (width, height). i.e. (4.0, 3.0)

    :return: A tuple with the (width, height) of the maximum size rectangle. i.e. (1440, 1080)
    """

    # TODO: Create a private function for 0º rotation and then extend functionality for rotation angle here.

    # Option 1: Make inner width = container width
    #---------------------------------------------
    f_width_1 = ptf_rec_out[0]
    f_height_1 = f_width_1 * ptf_asp_in[1] / ptf_asp_in[0]

    # Option 2: Make inner height = container height
    #-----------------------------------------------
    f_height_2 = ptf_rec_out[1]
    f_width_2 = f_height_2 * ptf_asp_in[0] / ptf_asp_in[1]

    if f_width_1 <= ptf_rec_out[0] and f_height_1 <= ptf_rec_out[1]:
        tf_in_rect = (f_width_1, f_height_1)
    else:
        tf_in_rect = (f_width_2, f_height_2)

    return tf_in_rect


def min_rect_out(ptf_rec_in=(0.0, 0.0), pf_rot_out=0.0, ptf_asp_out=None):
    """
    Function that returns the minimum rotated outer rectangle WITH CERTAIN ASPECT RATIO of another rectangle.

    :param ptf_rec_in: Size of the inner rectangle (width, height). i.e. (20.0, 13.5)
    :param pf_rot_out: Rotation of the outer rectangle in degrees. i.e. 15.0
    :param ptf_asp_out: Aspect ratio of the outer rectangle (width, height). i.e. (4.0, 3.0)
    :return: A tuple with the width and height of the outer rectangle (width, height). i.e. (40.0, 23.2)
    """
    tf_min_rec = _min_rect_out(ptf_rec_in=ptf_rec_in, pf_rot_out=pf_rot_out)

    if not ptf_asp_out:
        tf_output = tf_min_rec

    else:
        f_min_rec_ratio = tf_min_rec[0] / tf_min_rec[1]
        f_desired_ratio = ptf_asp_out[0] / ptf_asp_out[1]

        if f_desired_ratio > f_min_rec_ratio:
            tf_output = (f_desired_ratio * tf_min_rec[1], tf_min_rec[1])
        else:
            tf_output = (tf_min_rec[0], tf_min_rec[0] / f_desired_ratio)

    return tf_output


def _min_rect_out(ptf_rec_in=(0.0, 0.0), pf_rot_out=0.0):
    """
    Function to obtain the width and height of the minimum rotated angle that contains the given rectangle.

    ptf_rec_in: Inner rectangle dimensions tuple (width, height). i.e. (20.0, 16.3)

    ptf_asp_out: Outer rectangle aspect (width, height). i.e. (4.0, 3.0)

    pf_rot_out: Outer rectangle rotation in degrees. i.e. 15.0
    """

    # Rotation angle of the outer rectangle
    f_rot_outer = math.radians(float(pf_rot_out) % 180)

    # Length of the diagonals
    f_diag_inner = (ptf_rec_in[0] ** 2 + ptf_rec_in[1] ** 2) ** 0.5

    # Angle of the top-right diagonal
    f_beta1 = math.atan(float(ptf_rec_in[1]) / float(ptf_rec_in[0]))
    f_beta2 = math.pi - f_beta1

    # Width, Height of the outer rectangle
    b_reverse = False
    if f_rot_outer >= 0.5 * math.pi:
        f_rot_outer -= 0.5 * math.pi
        b_reverse = True

    f_width_outer = f_diag_inner * math.cos(f_beta1 - f_rot_outer)
    f_height_outer = f_diag_inner * math.cos(f_beta2 - 0.5 * math.pi - f_rot_outer)

    if not b_reverse:
        tf_output = (f_width_outer, f_height_outer)
    else:
        tf_output = (f_height_outer, f_width_outer)

    return tf_output


def t_sum(pt_tuple_1, pt_tuple_2):
    """
    Function to sum tuples by components.

    :param pt_tuple_1:
    :param pt_tuple_2:
    :return:
    """
    # TODO