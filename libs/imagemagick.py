# -*- coding: utf-8 -*-

"""
Library with ImageMagic transformations
"""

import math
import os
import random
from PIL import Image


import cmd
import geom

# CONSTANTS
#=======================================================================================================================
u_CWD = os.path.dirname(os.path.abspath(__file__))
u_MEDIA_ROOT = os.path.join(u_CWD, '..', 'media')

tu_CNV_MODES = ('frame', 'magcover')


# CLASSES
#=======================================================================================================================
class ImgConvertRandomCfg():
    """
    Class to store ImageConvert proto-configuration with associated random values. Before using the configuration, the
    random values need to be applied and then that final already-randomized configuration object will be used for the
    image manipulation.
    """
    def __init__(self):
        self.ti_aspect = (0, 0)          # aspect ratio: x, y
        self.ti_offset = (0, 0, 0, 0)    # offset: x, y, random_x, random_y
        self.tf_rotation = (0, 0)        # rotation: θ, random_θ
        self.ti_size = (500, 500, 0, 0)  # size: x, y, random_x, random_y
        self.u_grab = 'center'

    def randomize(self):
        """
        Method to randomize the randomizable values and generate a static ImgConvertRandomCfg.

        :return: An ImgConvertRandomCfg object with all the random properties already applied.
        """
        o_img_convert_cfg = ImgConvertCfg()
        o_img_convert_cfg.f_rotation = _randomize(self.tf_rotation[0], self.tf_rotation[1])
        o_img_convert_cfg.ti_aspect = self.ti_aspect
        o_img_convert_cfg.ti_size = (max(int(_randomize(self.ti_size[0], self.ti_size[2])), 0),
                                     max(int(_randomize(self.ti_size[1], self.ti_size[3])), 0))

        #TODO: Decide if ti_offset and u_grab are relevant to be kept to randomize them or not.

        return o_img_convert_cfg

    def __str__(self):
        u_output = u''
        u_output += u'[ImgConvertRandomCfg]\n'
        u_output += u'  .ti_aspect = %s  (x, y)\n' % str(self.ti_aspect)
        u_output += u'  .ti_offset = %s  (x, y, Rx, Ry)\n' % str(self.ti_offset)
        u_output += u'  .tf_rotation = %s  (θ, Rθ)\n' % str(self.tf_rotation)
        u_output += u'  .ti_size = %s  (x, y)' % str(self.ti_size)

        return u_output.encode('utf8')

    def valid_cfg(self):
        """
        Method to check if the configuration is valid or not.

        :return: True if the configuration is right, False in other case.
        """
        pass


class ImgConvertCfg():
    def __init__(self):
        self.ti_aspect = (0, 0)     # aspect ratio: x, y
        self.ti_offset = (0, 0)     # aspect ratio: x, y
        self.ti_size = (500, 500)   # Image size: x, y
        self.f_rotation = 0         # Image rotation: θ (anti-clockwise)


class ImgKeyCoords():
    """
    Class to store information about the transformation an image suffered.
    """
    def __init__(self):

        self.ti_size = (0, 0)         # Image size

        # It's better to keep coordinates as decimal numbers from 0.0 to 1.0 so in case of resizing the final image the
        # relative coordinates will remain the same.
        self.tf_top_left = (0, 0)      # Top-left corner coordinates
        self.tf_top = (0, 0)          # Top (center) coordinates
        self.tf_top_right = (0, 0)     # Top-right corner coordinates

        self.tf_left = (0, 0)         # Left (center) coordinates
        self.tf_center = (0, 0)       # Center coordinates
        self.tf_right = (0, 0)        # Right (center) coordinates

        self.tf_bottom_left = (0, 0)   # Bottom-left coordinates
        self.tf_bottom = (0, 0)       # Bottom (center) coordinates
        self.tf_bottom_right = (0, 0)  # Bottom-right coordinates

    def __str__(self):
        u_output = u'<ImgKeyCoords>\n'
        u_output += u'  .ti_size:         %s\n' % str(self.ti_size)
        u_output += u'  .tf_top_left:     %s\n' % str(self.tf_top_left)
        u_output += u'  .tf_top:          %s\n' % str(self.tf_top)
        u_output += u'  .tf_top_right:    %s\n' % str(self.tf_top_right)
        u_output += u'  .tf_left:         %s\n' % str(self.tf_left)
        u_output += u'  .tf_center:       %s\n' % str(self.tf_center)
        u_output += u'  .tf_right:        %s\n' % str(self.tf_right)
        u_output += u'  .tf_bottom_left:  %s\n' % str(self.tf_bottom_left)
        u_output += u'  .tf_bottom:       %s\n' % str(self.tf_bottom)
        u_output += u'  .tf_bottom_right: %s' % str(self.tf_bottom_right)

        return u_output.encode('utf8')


# MAIN CONVERTER FUNCTIONS
#=======================================================================================================================
def cnv_img(pu_mode, pu_input_file, pu_output_file, po_random_precfg):
    """
    Main convert function that will call different sub-convert functions depending on the value of pu_mode.

    :param pu_mode: Mode of image conversion. i.e. 'frame'

    :param pu_input_file: Source file for conversion. i.e. '/home/john/original_picture.jpg'

    :param pu_output_file: Destination file for conversion. i.e. '/home/john/final_picture.jpg'

    :param po_random_precfg: Configuration object with main options for conversion (size, rotation, grab point...)

    :return:
    """

    o_cfg = po_random_precfg.randomize()

    # Automatic aspect ratio (zero in any of the aspect ratios x,y) fixing
    if 0.0 in o_cfg.ti_aspect:
        o_img = Image.open(pu_input_file, 'r')
        o_cfg.ti_aspect = o_img.size
        o_img.close()

    # Error handling code
    if pu_mode not in tu_CNV_MODES:
        raise ValueError('pu_mode must be one of the these: %s' % ', '.join(tu_CNV_MODES))

    # Calling to sub-functions
    elif pu_mode == 'frame':
        o_transformation = _cnv_frame(pu_input_file, pu_output_file, o_cfg)

    return o_transformation


def _cnv_frame(pu_src_file, pu_dst_file, po_cfg):
    """
    Image conversion that adds a picture frame around the image and soft reflections.

    :param pu_src_file: Input file. i.e. '/home/john/original_picture.jpg'

    :param pu_dst_file: Output file. i.e. '/home/john/modified_picture.png'

    :param po_cfg: Configuration object. See hq_img_convert to see

    :return: An ImgKeyCoords object containing the relative coordinates (0.0-1.0) of 9 key positions (top-left, top,
             top-right, left, center, right, bottom-left, bottom, bottom-right.
    """

    # Media preparation
    u_img_light = os.path.join(u_MEDIA_ROOT, 'frame', 'white-add.png')
    u_img_light = u_img_light.decode('utf8')

    # Variables preparation for imagemagick command
    i_width, i_height = geom.max_in_rect(po_cfg.ti_size, po_cfg.ti_aspect)

    i_frame_thickness = math.ceil(0.03 * min(po_cfg.ti_size))
    u_frame_color = u'#f0f0f0'
    i_frame_width = i_width + 2 * i_frame_thickness
    i_frame_height = i_height + 2 * i_frame_thickness

    i_shadow_dist = math.ceil(0.005 * min(po_cfg.ti_size))
    i_shadow_opac = 60                                                                   # 0-100
    i_shadow_blur = math.ceil(0.0025 * max(po_cfg.ti_size))

    f_sin = math.sin(math.radians(po_cfg.f_rotation))
    f_cos = math.cos(math.radians(po_cfg.f_rotation))

    # Command line build
    #-------------------
    u_cmd = u'convert '
    u_cmd += u'"%s" ' % pu_src_file                                                      # Source file
    u_cmd += u'-resize %ix%i! ' % (i_width, i_height)                                    # Resizing
    u_cmd += u'-background transparent '                                                 # Transparent background
    u_cmd += u'"%s" -resize %ix -composite ' % (u_img_light, i_width)                    # Light/shadow add
    u_cmd += u'-bordercolor \'%s\' -border %i ' % (u_frame_color, i_frame_thickness)     # Frame border
    u_cmd += u'-rotate %f ' % -po_cfg.f_rotation                                         # Rotation
    u_cmd += u'\( -clone 0 -background black -shadow %ix%i+0+%i \) ' % (i_shadow_opac,
                                                                        i_shadow_blur,
                                                                        i_shadow_dist)   # Shadow creation
    u_cmd += u'-reverse -background none -layers merge +repage '                         # Shadow composition
    u_cmd += u'"%s" ' % pu_dst_file                                                      # Output file

    # Command line execution
    #-----------------------
    du_output = cmd.execute(u_cmd)

    if du_output['u_stderr']:
        print du_output['u_stderr']

    # Coordinates calculation after image manipulation
    #-------------------------------------------------
    o_img = Image.open(pu_dst_file, 'r')
    ti_size = o_img.size
    o_img.close()

    i_extra_top = max(0, i_shadow_blur - i_shadow_dist)
    i_extra_bottom = max(0, i_shadow_blur + i_shadow_dist)

    # Delta distances in rotated image in screen coordinates
    tf_dx = (0.5 * i_frame_width * f_cos, 0.5 * i_frame_width * f_sin)
    tf_dy = (0.5 * i_frame_height * f_sin, 0.5 * i_frame_height * f_cos)

    # Absolute offsets of image key-positions
    tf_center = (0.5 * ti_size[0], 0.5 * (ti_size[1] - i_extra_top - i_extra_bottom) + i_extra_top)
    tf_left = (tf_center[0] - tf_dx[0], tf_center[1] + tf_dx[1])
    tf_right = (tf_center[0] + tf_dx[0], tf_center[1] - tf_dx[1])

    tf_bottom = (tf_center[0] + tf_dy[0], tf_center[1] + tf_dy[1])
    tf_bottom_left = (tf_bottom[0] - tf_dx[0], tf_bottom[1] + tf_dx[1])
    tf_bottom_right = (tf_bottom[0] + tf_dx[0], tf_bottom[1] - tf_dx[1])

    tf_top = (tf_center[0] - tf_dy[0], tf_center[1] - tf_dy[1])
    tf_top_left = (tf_top[0] - tf_dx[0], tf_top[1] + tf_dx[1])
    tf_top_right = (tf_top[0] + tf_dx[0], tf_top[1] - tf_dx[1])

    # Relative (0.0 to 1.0) offsets of image key-positions
    o_img_transformation = ImgKeyCoords()
    o_img_transformation.ti_size = ti_size
    o_img_transformation.tf_top_left = (tf_top_left[0] / ti_size[0], tf_top_left[1] / ti_size[1])
    o_img_transformation.tf_top = (tf_top[0] / ti_size[0], tf_top[1] / ti_size[1])
    o_img_transformation.tf_top_right = (tf_top_right[0] / ti_size[0], tf_top_right[1] / ti_size[1])
    o_img_transformation.tf_left = (tf_left[0] / ti_size[0], tf_left[1] / ti_size[1])
    o_img_transformation.tf_center = (tf_center[0] / ti_size[0], tf_center[1] / ti_size[1])
    o_img_transformation.tf_right = (tf_right[0] / ti_size[0], tf_right[1] / ti_size[1])
    o_img_transformation.tf_bottom_left = (tf_bottom_left[0] / ti_size[0], tf_bottom_left[1] / ti_size[1])
    o_img_transformation.tf_bottom = (tf_bottom[0] / ti_size[0], tf_bottom[1] / ti_size[1])
    o_img_transformation.tf_bottom_right = (tf_bottom_right[0] / ti_size[0], tf_bottom_right[1] / ti_size[1])

    # Debug code to overlay image regions
    # draw_coordinates(pu_dst_file, o_img_transformation)

    return o_img_transformation


# HELPER IMAGE FUNCTIONS
#=======================================================================================================================
def _draw_coordinates(u_img, o_img_transform):
    """
    Function to show the location of the image transform points over the image and the regions defined by them using
    overlay colors.

    :param u_img: File name of the image. i.e. "/home/john/picture.png"

    :param o_img_transform: ImageTransformation object containing the image's key-coordinates.

    :return: Nothing, the image will be modified in-place.
    """

    # Coordinates strings preparation
    u_tl = u'%i,%i' % (o_img_transform.ti_size[0] * o_img_transform.tf_top_left[0],
                       o_img_transform.ti_size[1] * o_img_transform.tf_top_left[1])
    u_t = u'%i,%i' % (o_img_transform.ti_size[0] * o_img_transform.tf_top[0],
                      o_img_transform.ti_size[1] * o_img_transform.tf_top[1])
    u_tr = u'%i,%i' % (o_img_transform.ti_size[0] * o_img_transform.tf_top_right[0],
                       o_img_transform.ti_size[1] * o_img_transform.tf_top_right[1])
    u_l = u'%i,%i' % (o_img_transform.ti_size[0] * o_img_transform.tf_left[0],
                      o_img_transform.ti_size[1] * o_img_transform.tf_left[1])
    u_c = u'%i,%i' % (o_img_transform.ti_size[0] * o_img_transform.tf_center[0],
                      o_img_transform.ti_size[1] * o_img_transform.tf_center[1])
    u_r = u'%i,%i' % (o_img_transform.ti_size[0] * o_img_transform.tf_right[0],
                      o_img_transform.ti_size[1] * o_img_transform.tf_right[1])
    u_br = u'%i,%i' % (o_img_transform.ti_size[0] * o_img_transform.tf_bottom_right[0],
                       o_img_transform.ti_size[1] * o_img_transform.tf_bottom_right[1])
    u_b = u'%i,%i' % (o_img_transform.ti_size[0] * o_img_transform.tf_bottom[0],
                      o_img_transform.ti_size[1] * o_img_transform.tf_bottom[1])
    u_bl = u'%i,%i' % (o_img_transform.ti_size[0] * o_img_transform.tf_bottom_left[0],
                       o_img_transform.ti_size[1] * o_img_transform.tf_bottom_left[1])

    # Imagemagick command for sectors overlaying
    u_cmd = u'convert '
    u_cmd += u'%s ' % u_img

    u_cmd += u'-stroke lime -fill "#ff000080" '
    u_cmd += u'-draw "polygon %s %s %s %s" ' % (u_tl, u_t, u_c, u_l)

    u_cmd += u'-stroke lime -fill "#00ff0080" '
    u_cmd += u'-draw "polygon %s %s %s %s" ' % (u_t, u_tr, u_r, u_c)

    u_cmd += u'-stroke lime -fill "#0000ff80" '
    u_cmd += u'-draw "polygon %s %s %s %s" ' % (u_l, u_c, u_b, u_bl)

    u_cmd += u'-stroke lime -fill "#ff00ff80" '
    u_cmd += u'-draw "polygon %s %s %s %s" ' % (u_c, u_r, u_br, u_b)

    u_cmd += u'%s' % u_img

    cmd.execute(u_cmd)


def _randomize(pf_x, pf_dx):
    """
    Function to sum a constant values and a maximum random value.

    :param pf_x: Constant value. i.e. 5.0

    :param pf_dx: Random value to add. i.e. 0.5 (which means you are adding something between -0.5 and +0.5.

    :return: The sum of the above as a float.
    """
    f_output = pf_x + pf_dx * random.choice((1.0, -1.0)) * random.random()
    return f_output