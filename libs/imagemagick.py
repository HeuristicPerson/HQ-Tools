# -*- coding: utf-8 -*-

"""
Library with ImageMagic transformations
"""

import math
import os
import random

import cmd
import cons
import files
import geom

# CONSTANTS
#=======================================================================================================================
u_CWD = os.path.dirname(os.path.abspath(__file__))
u_MEDIA_ROOT = os.path.join(u_CWD, '..', 'media')

tu_VALID_EXTS = ('bmp', 'gif', 'jpg', 'png')
tu_CNV_MODES = ('frame', 'magcover')


# CLASSES
#=======================================================================================================================
class ImgConvCfgGenerator(object):
    """
    Class to store ImageConvert proto-configuration with associated random values. Before using the configuration, the
    random values need to be applied and then that final already-randomized configuration object will be used for the
    image manipulation.
    """
    def __init__(self):
        self.u_bgcolor = u'#808080ff'    # Background color in RGBA format.
        self._tf_aspect = (0, 0)         # Aspect ratio: x, y
        self.tf_focus = (0, 0, 0, 0)     # Focus point (relative): x, y, random_x, random_y
        self.tf_rotation = (0, 0)        # Rotation: θ, random_θ
        self.ti_size = (500, 500, 0, 0)  # Size: x, y, random_x, random_y
        self.u_format = None             # File extension

    def __str__(self):
        u_output = u''
        u_output += u'<ImgConvCfgGenerator>\n'
        u_output += u'  .tf_aspect:   %s  (x, y)\n' % str(self._tf_aspect)
        u_output += u'  .tf_focus:    %s  (x, y, Rx, Ry)\n' % str(self.tf_focus)
        u_output += u'  .tf_rotation: %s  (θ, Rθ)\n' % str(self.tf_rotation)
        u_output += u'  .ti_size:     %s  (x, y, Rx, Ry)\n' % str(self.ti_size)
        u_output += u'  .u_format:    %s' % self.u_format

        return u_output.encode('utf8')

    def randomize(self):
        """
        Method to randomize the randomizable values and generate a static ImgConvCfgGenerator.

        :return: An ImgConvCfg object with all the random properties already applied.
        """
        o_img_convert_cfg = ImgConvertCfg()
        o_img_convert_cfg.u_bgcolor = self.u_bgcolor
        o_img_convert_cfg.f_rotation = _randomize(self.tf_rotation[0], self.tf_rotation[1])
        o_img_convert_cfg.tf_focus = (_randomize(self.tf_focus[0], self.tf_focus[2]),
                                      _randomize(self.tf_focus[1], self.tf_focus[3]))
        o_img_convert_cfg.tf_aspect = self._tf_aspect
        o_img_convert_cfg.ti_size = (max(int(_randomize(self.ti_size[0], self.ti_size[2])), 0),
                                     max(int(_randomize(self.ti_size[1], self.ti_size[3])), 0))
        o_img_convert_cfg.u_format = self.u_format

        return o_img_convert_cfg

    def _get_aspect(self):
        return self._tf_aspect

    def _set_aspect(self, px_value):
        """
        Method to allow setting the aspect using nicknames and actual values.
        """
        if _is_valid_tuple(px_value, 2, int, float):
            self._tf_aspect = px_value
        elif px_value in cons.do_platforms:
            self._tf_aspect = (cons.do_platforms[px_value].i_WIDTH, cons.do_platforms[px_value].i_HEIGHT)
        else:
            raise ValueError('Expecting a tuple of 2 integers or a string between %s' % ', '.join(cons.do_platforms))

    tf_aspect = property(_get_aspect, _set_aspect)


class ImgConvertCfg():
    """
    A configuration object for the cnv_img function.
    """
    def __init__(self):
        self.u_bgcolor = u'80808080'  # Background color
        self.tf_focus = (0.0, 0.0)    # relative focus point (center point for certain effects): x, y (0.0 to 1.0)
        self.tf_aspect = (0.0, 0.0)   # aspect ratio: x, y
        self.ti_size = (500, 500)     # Image size: x, y (pixels)
        self.f_rotation = 0           # Image rotation: θ (anti-clockwise degrees)
        self.u_format = None          # Image format. i.e. 'png', 'gif', 'jpg'...

    def __str__(self):
        u_output = u''
        u_output += u'<ImgConvertCfg>\n'
        u_output += u'  .f_rotation: %s\n' % self.f_rotation
        u_output += u'  .tf_focus:   %s  (x, y)\n' % str(self.tf_focus)
        u_output += u'  .tf_aspect:  %s  (x, y)\n' % str(self.tf_aspect)
        u_output += u'  .ti_size:    %s  (x,y)\n' % str(self.ti_size)
        u_output += u'  .u_bgcolor:  %s\n' % self.u_bgcolor
        u_output += u'  .u_format:   %s' % self.u_format

        return u_output.encode('utf8')


class ImgKeyCoords():
    """
    Class to store information about the transformation an image suffered.
    """
    def __init__(self):

        self.o_path = None             # Image path
        self.ti_size = (0, 0)          # Image size

        # It's better to keep coordinates as decimal numbers from 0.0 to 1.0 so in case of resizing the final image the
        # relative coordinates will remain the same.
        self.tf_top_left = (0, 0)      # Top-left corner coordinates
        self.tf_top = (0, 0)           # Top (center) coordinates
        self.tf_top_right = (0, 0)     # Top-right corner coordinates

        self.tf_left = (0, 0)          # Left (center) coordinates
        self.tf_center = (0, 0)        # Center coordinates
        self.tf_right = (0, 0)         # Right (center) coordinates

        self.tf_bottom_left = (0, 0)   # Bottom-left coordinates
        self.tf_bottom = (0, 0)        # Bottom (center) coordinates
        self.tf_bottom_right = (0, 0)  # Bottom-right coordinates

    def __str__(self):
        u_output = u'<ImgKeyCoords>\n'
        u_output += u'  .o_path:          <FilePath: %s>\n' % self.o_path.u_path
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
def cnv_img(pu_mode, po_src_file, po_dst_file, po_random_precfg):
    """
    Main convert function that will call different sub-convert functions depending on the value of pu_mode.

    :param pu_mode: Mode of image conversion. i.e. 'frame'

    :param pu_src_file: Source file for conversion. i.e. '/home/john/original_picture.jpg'

    :param pu_dst_file: Destination file for conversion. i.e. '/home/john/final_picture.jpg'

    :param po_random_precfg: Configuration object with main options for conversion (size, rotation, grab point...)

    :return:
    """

    if not po_src_file.has_exts(*tu_VALID_EXTS):
        raise ValueError('Not a valid src file extension (%s); valid ones are %s.' % (po_src_file.u_ext,
                                                                                      str(tu_VALID_EXTS)))
    else:
        o_cfg = po_random_precfg.randomize()

        # Extension change if it's forced
        if o_cfg.u_format:
            po_dst_file.u_ext = po_random_precfg.u_format

        # Automatic aspect ratio (zero in any of the aspect ratios x,y) fixing
        if 0.0 in o_cfg.tf_aspect:
            o_cfg.tf_aspect = _img_get_size(po_src_file.u_path)

        # Aspect ratio "inversion" if the image is rotated
        ti_src_img_size = _img_get_size(po_src_file.u_path)

        b_src_img_landscape = True
        if ti_src_img_size[0] < ti_src_img_size[1]:
            b_src_img_landscape = False

        b_cfg_ratio_landscape = True
        if o_cfg.tf_aspect[0] < o_cfg.tf_aspect[1]:
            b_cfg_ratio_landscape = False

        if b_src_img_landscape ^ b_cfg_ratio_landscape:
            o_cfg.tf_aspect = (o_cfg.tf_aspect[1], o_cfg.tf_aspect[0])

        # Error handling code
        if pu_mode not in tu_CNV_MODES:
            raise ValueError('pu_mode must be one of the these: %s' % ', '.join(tu_CNV_MODES))

        # Calling to sub-functions
        elif pu_mode == 'frame':
            o_transformation = _cnv_frame(po_src_file, po_dst_file, o_cfg)
        elif pu_mode == 'magcover':
            o_transformation = _cnv_magcover(po_src_file, po_dst_file, o_cfg)

        o_transformation.o_path = po_dst_file

    return o_transformation


def _cnv_frame(po_src_file, po_dst_file, po_cfg):
    """
    Image conversion that adds a picture frame around the image and soft reflections.

    Focus point is used to set the center of the reflection image.

    :param po_src_file: Input file. i.e. '/home/john/original_picture.jpg'

    :param po_dst_file: Output file. i.e. '/home/john/modified_picture.png'

    :param po_cfg: Configuration object. See hq_img_convert to see

    :return: An ImgKeyCoords object containing the relative coordinates (0.0-1.0) of 9 key positions (top-left, top,
             top-right, left, center, right, bottom-left, bottom, bottom-right.
    """

    # Media preparation
    #------------------
    o_img_light = files.FilePath(u_MEDIA_ROOT, 'frame', 'brightness.png')
    o_img_light.absfile()
    u_img_light = o_img_light.u_path.decode('utf8')

    # Variables preparation for imagemagick command
    #----------------------------------------------
    ti_img_size = geom.max_in_rect(po_cfg.ti_size, po_cfg.tf_aspect)
    i_light_size = 2 * max(ti_img_size[0], ti_img_size[1])
    f_aspect_ratio = po_cfg.tf_aspect[0] / po_cfg.tf_aspect[1]
    f_gb_aspect_ratio = 160.0 / 144.0

    # Real location (x,y) in pixels of the focus point of the image
    ti_focus = (int(po_cfg.tf_focus[0] * ti_img_size[0]), int(po_cfg.tf_focus[1] * ti_img_size[1]))

    # Then, the offsets are calculated to make the center of the light image fall over that point. Imagemagick format
    # for offsets in geometry is +x+y when moving the top-left corner of the overlay image x pixels to the right and y
    # pixels to the bottom.
    ti_foc_img_off = (- 0.5 * i_light_size + ti_focus[0], - 0.5 * i_light_size + ti_focus[1])
    if ti_foc_img_off[0] >= 0:
        u_foc_img_extra_x = u'+'
    else:
        u_foc_img_extra_x = u''

    if ti_foc_img_off[1] >= 0:
        u_foc_img_extra_y = u'+'
    else:
        u_foc_img_extra_y = u''

    u_foc_img_off = u'%s%i%s%i' % (u_foc_img_extra_x, ti_foc_img_off[0], u_foc_img_extra_y, ti_foc_img_off[1])

    # Frame configuration
    i_frame_thickness = math.ceil(0.03 * min(po_cfg.ti_size))
    u_frame_color = u'#f0f0f0'
    ti_frame_size = (ti_img_size[0] + 2 * i_frame_thickness, ti_img_size[1] + 2 * i_frame_thickness)

    # Shadow configuration
    i_shadow_dist = math.ceil(0.005 * min(po_cfg.ti_size))
    i_shadow_opac = 60                                                                       # 0-100
    i_shadow_blur = math.ceil(0.0025 * max(po_cfg.ti_size))

    # Sin and Cos of the rotation are going to be used several times so I pre-calculate them to make the script a bit
    # faster.
    f_sin = math.sin(math.radians(po_cfg.f_rotation))
    f_cos = math.cos(math.radians(po_cfg.f_rotation))

    # Number of image colors to colorize gameboy screenshots
    i_colors = _img_count_colors(po_src_file.u_path)
    b_grayscale = _img_is_grayscale(po_src_file.u_path)

    # Command line build
    #-------------------
    u_cmd = u'convert '
    u_cmd += u'"%s" ' % po_src_file.u_path                                                   # Source file

    if f_aspect_ratio == f_gb_aspect_ratio and i_colors <= 4 and b_grayscale:                # GameBoy (mono) color tint
        u_cmd += u'+level-colors "#0f380e,#9bbb0e" '

    u_cmd += u'-resize %ix%i! ' % (ti_img_size[0], ti_img_size[1])                           # Resizing
    u_cmd += u'-background transparent '                                                     # Transparent background

    u_cmd += u'\( "%s" -resize %ix%i! -geometry %s \) -composite ' % (u_img_light,
                                                                      i_light_size,
                                                                      i_light_size,
                                                                      u_foc_img_off)         # Light/shadow add

    u_cmd += u'-bordercolor \'%s\' -border %i ' % (u_frame_color, i_frame_thickness)         # Frame border
    u_cmd += u'-rotate %f ' % -po_cfg.f_rotation                                             # Rotation
    u_cmd += u'\( -clone 0 -background black -shadow %ix%i+0+%i \) ' % (i_shadow_opac,
                                                                        i_shadow_blur,
                                                                        i_shadow_dist)       # Shadow creation
    u_cmd += u'-reverse -background none -layers merge +repage '                             # Shadow composition

    u_cmd += u'-background "#%s" -flatten ' % po_cfg.u_bgcolor                               # Background color
    u_cmd += u'"%s"' % po_dst_file.u_path                                                    # Output file

    # Command line execution
    #-----------------------
    du_output = cmd.execute(u_cmd)

    if du_output['u_stderr']:
        print du_output['u_stderr']

    # Coordinates calculation after image manipulation
    #-------------------------------------------------
    ti_img_size = _img_get_size(po_dst_file.u_path)

    i_extra_top = max(0, i_shadow_blur - i_shadow_dist)
    i_extra_bottom = max(0, i_shadow_blur + i_shadow_dist)

    # Delta distances in rotated image in screen coordinates
    tf_dx = (0.5 * ti_frame_size[0] * f_cos, 0.5 * ti_frame_size[0] * f_sin)
    tf_dy = (0.5 * ti_frame_size[1] * f_sin, 0.5 * ti_frame_size[1] * f_cos)

    # Absolute offsets of image key-positions
    tf_center = (0.5 * ti_img_size[0], 0.5 * (ti_img_size[1] - i_extra_top - i_extra_bottom) + i_extra_top)
    tf_left = (tf_center[0] - tf_dx[0], tf_center[1] + tf_dx[1])
    tf_right = (tf_center[0] + tf_dx[0], tf_center[1] - tf_dx[1])

    tf_bottom = (tf_center[0] + tf_dy[0], tf_center[1] + tf_dy[1])
    tf_bottom_left = (tf_bottom[0] - tf_dx[0], tf_bottom[1] + tf_dx[1])
    tf_bottom_right = (tf_bottom[0] + tf_dx[0], tf_bottom[1] - tf_dx[1])

    tf_top = (tf_center[0] - tf_dy[0], tf_center[1] - tf_dy[1])
    tf_top_left = (tf_top[0] - tf_dx[0], tf_top[1] + tf_dx[1])
    tf_top_right = (tf_top[0] + tf_dx[0], tf_top[1] - tf_dx[1])

    # Transformation object result
    o_img_transformation = ImgKeyCoords()
    o_img_transformation.ti_size = ti_img_size
    o_img_transformation.tf_top_left = (tf_top_left[0] / ti_img_size[0], tf_top_left[1] / ti_img_size[1])
    o_img_transformation.tf_top = (tf_top[0] / ti_img_size[0], tf_top[1] / ti_img_size[1])
    o_img_transformation.tf_top_right = (tf_top_right[0] / ti_img_size[0], tf_top_right[1] / ti_img_size[1])
    o_img_transformation.tf_left = (tf_left[0] / ti_img_size[0], tf_left[1] / ti_img_size[1])
    o_img_transformation.tf_center = (tf_center[0] / ti_img_size[0], tf_center[1] / ti_img_size[1])
    o_img_transformation.tf_right = (tf_right[0] / ti_img_size[0], tf_right[1] / ti_img_size[1])
    o_img_transformation.tf_bottom_left = (tf_bottom_left[0] / ti_img_size[0], tf_bottom_left[1] / ti_img_size[1])
    o_img_transformation.tf_bottom = (tf_bottom[0] / ti_img_size[0], tf_bottom[1] / ti_img_size[1])
    o_img_transformation.tf_bottom_right = (tf_bottom_right[0] / ti_img_size[0], tf_bottom_right[1] / ti_img_size[1])

    # Debug code to overlay image regions
    # draw_coordinates(pu_dst_file, o_img_transformation)

    return o_img_transformation


def _cnv_magcover(po_src_file, po_dst_file, po_cfg):
    """
    :param po_src_file:
    :param po_dst_file:
    :param po_cfg:
    :return:
    """

    # Media preparation
    #------------------
    o_img_light = files.FilePath(u_MEDIA_ROOT, 'magcover', 'brightness.png')
    o_img_light.absfile()
    u_img_light = o_img_light.u_path.decode('utf8')

    # Variables preparation
    #----------------------
    ti_img_size = geom.max_in_rect(po_cfg.ti_size, po_cfg.ti_aspect)

    # Command line build
    #-------------------
    u_cmd = u'convert '
    u_cmd += u'"%s" ' % po_src_file.u_path                                                   # Source file
    u_cmd += u'-resize %ix%i! ' % (ti_img_size[0], ti_img_size[1])                           # Resizing
    u_cmd += u'-background transparent '                                                     # Transparent background

    u_cmd += u'\( "%s" -resize %ix%i! -geometry %s \) -composite ' % (u_img_light,
                                                                      i_light_size,
                                                                      i_light_size,
                                                                      u_foc_img_off)         # Light/shadow add


# HELPER GENERIC FUNCTIONS
#=======================================================================================================================
def _is_valid_tuple(tx_tuple, pi_dim, *p_type):
    """
    Function to check if a tuple has the right dimension and the right type values.
    """
    b_is_valid = False

    if isinstance(tx_tuple, tuple) and len(tx_tuple) == pi_dim:
        i_valid_elems = 0
        for x_elem in tx_tuple:
            if isinstance(x_elem, p_type):
                i_valid_elems += 1

        if i_valid_elems == pi_dim:
            b_is_valid = True

    return b_is_valid


# HELPER IMAGE FUNCTIONS
#=======================================================================================================================
def _draw_coordinates(o_img_file, o_img_transform):
    """
    Function to show the location of the image transform points over the image and the regions defined by them using
    overlay colors.

    :param o_img_file: ImageFile object as defined in files.py. i.e. "/home/john/picture.png"

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
    u_cmd += u'%s ' % o_img_file.u_path

    u_cmd += u'-stroke lime -fill "#ff000080" '
    u_cmd += u'-draw "polygon %s %s %s %s" ' % (u_tl, u_t, u_c, u_l)

    u_cmd += u'-stroke lime -fill "#00ff0080" '
    u_cmd += u'-draw "polygon %s %s %s %s" ' % (u_t, u_tr, u_r, u_c)

    u_cmd += u'-stroke lime -fill "#0000ff80" '
    u_cmd += u'-draw "polygon %s %s %s %s" ' % (u_l, u_c, u_b, u_bl)

    u_cmd += u'-stroke lime -fill "#ff00ff80" '
    u_cmd += u'-draw "polygon %s %s %s %s" ' % (u_c, u_r, u_br, u_b)

    u_cmd += u'%s' % o_img_file.u_path

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


def _img_count_colors(pu_image):
    """
    Function to count the number of colors of an image using imagemagick "identify" tool.
    :param pu_image: File name of the image. i.e. "/home/john/picture.gif"
    :return: An integer representing the number of colors. i.e. 4.
    """

    # TODO: Check problematic files.
    # In certain circumstances, an image with 4 colors can contain unused colors (256 color images) and apparently the
    # command below don't check the actual colors used but the color depth of the image. This program MUST obtain the
    # number of colors actually used in the image.

    u_cmd = u'identify -format %%k "%s"' % pu_image
    du_output = cmd.execute(u_cmd)
    i_colors = int(du_output['u_stdout'])

    return i_colors


def _img_is_grayscale(pu_image):
    """
    Function to check if an image is a pure greyscale image using imagemagick.
    :param pu_image: File name
    :return: True if the image is greyscale.
    """

    u_cmd = u'convert "%s" -colorspace HSL -verbose info:' % pu_image
    du_output = cmd.execute(u_cmd)

    # The output of the above command gives information about RGB channels but actually they are HSL. According to
    # http://www.imagemagick.org/discourse-server/viewtopic.php?t=19580, we're interested in the "green" (saturation)
    # channel. The information to parse is:
    #
    #     ...
    #     Green:
    #       min: 0 (0)
    #       max: 0 (0)
    #       mean: 0 (0)
    #       standard deviation: 0 (0)
    #       kurtosis: 0
    #       skewness: 0
    #     Blue:
    #     ...
    #
    # If max is 0, the image is 100% greyscale.
    i_start = du_output['u_stdout'].find('Green:') + len('Green:')
    i_end = du_output['u_stdout'].find('Blue:')
    u_green_info = du_output['u_stdout'][i_start:i_end]

    lu_green_info = u_green_info.splitlines()

    b_info_found = False

    for u_line in lu_green_info:
        if 'max:' in u_line:
            b_info_found = True
            i_max = int(u_line.split()[1])

    if b_info_found:
        if i_max == 0:
            b_grayscale = True
        else:
            b_grayscale = False

        return b_grayscale

    else:
        raise IOError('Te file provided doesn\'t seem to be a valid image for imagemagick: %s' % pu_image)


def _img_get_size(pu_image):
    """
    Function to get the size of an image file.
    :param pu_image: Image file. i.e. '/home/john/my_face.jpg'
    :return: A tuple of integers with width and height. i.e. (640, 480)
    """

    u_cmd = u'identify -format %%G "%s"' % pu_image
    du_output = cmd.execute(u_cmd)

    # The standard output of the command above is widthxheight. i.e. 640x906. So, it's easy to parse.
    i_width = int(du_output['u_stdout'].partition('x')[0])
    i_height = int(du_output['u_stdout'].partition('x')[2])

    return i_width, i_height