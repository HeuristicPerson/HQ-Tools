# -*- coding: utf-8 -*-

"""
Library with ImageMagic transformations
"""

import math
import random

import cmd
import cons
import files
import geom

# CONSTANTS
#=======================================================================================================================
o_CF_FP = files.FilePath(__file__.decode('utf8'))
o_MEDIA_ROOT_FP = files.FilePath(o_CF_FP.u_root, u'..', u'media')

tu_VALID_EXTS = ('bmp', 'gif', 'jpg', 'png')
tu_CNV_MODES = ('enclose', 'frame', 'hbars', 'magcover', 'mosaic', 'reduce', 'vbars')


# CLASSES
#=======================================================================================================================
class ImgConvCfgGenerator(object):
    """
    Class to store ImageConvert proto-configuration with associated random values. Before using the configuration, the
    random values need to be applied and then that final already-randomized configuration object will be used for the
    image manipulation.
    """
    def __init__(self):
        self.u_color = u'808080ff'              # Color in RGBA format.
        self._tf_aspect = (0.0, 0.0)            # Aspect ratio: x, y
        self.tf_options = (0.0, 0.0, 0.0, 0.0)  # Focus point (relative): x, y, random_x, random_y
        self.tf_rotation = (0.0, 0.0)           # Rotation: θ, random_θ
        self.ti_size = (500, 500, 0, 0)         # Size: x, y, random_x, random_y
        self.u_format = None                    # File extension

    def __str__(self):
        u_output = u''
        u_output += u'<ImgConvCfgGenerator>\n'
        u_output += u'  .tf_aspect:   %s  (x, y)\n' % str(self._tf_aspect)
        u_output += u'  .tf_options:  %s  (x, y, Rx, Ry)\n' % str(self.tf_options)
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
        o_img_convert_cfg.u_color = self.u_color
        o_img_convert_cfg.f_rotation = _randomize(self.tf_rotation[0], self.tf_rotation[1])
        o_img_convert_cfg.tf_options = (_randomize(self.tf_options[0], self.tf_options[2]),
                                        _randomize(self.tf_options[1], self.tf_options[3]))
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
            self._tf_aspect = (float(cons.do_platforms[px_value].i_WIDTH), float(cons.do_platforms[px_value].i_HEIGHT))
        else:
            raise ValueError('Expecting a tuple of 2 integers or a string between %s' % ', '.join(cons.do_platforms))

    tf_aspect = property(_get_aspect, _set_aspect)


class ImgConvertCfg:
    """
    A configuration object for the cnv_img function.
    """
    def __init__(self):
        self.u_color = u'80808080'    # Background color
        self.tf_options = (0.0, 0.0)  # Extra options for certain effects
        #TODO: Add code to make automatic int->float conversion for .tf_aspect
        self.tf_aspect = (0.0, 0.0)   # aspect ratio: x, y
        self.ti_size = (500, 500)     # Image size: x, y (pixels)
        self.f_rotation = 0           # Image rotation: θ (anti-clockwise degrees)
        self.u_format = None          # Image format. i.e. 'png', 'gif', 'jpg'...

    def __str__(self):
        u_output = u''
        u_output += u'<ImgConvertCfg>\n'
        u_output += u'  .f_rotation: %s\n' % self.f_rotation
        u_output += u'  .tf_options: %s (x, y)\n' % str(self.tf_options)
        u_output += u'  .tf_aspect:  %s (x, y)\n' % str(self.tf_aspect)
        u_output += u'  .ti_size:    %s (x,y)\n' % str(self.ti_size)
        u_output += u'  .u_color:    %s\n' % self.u_color
        u_output += u'  .u_format:   %s' % self.u_format

        return u_output.encode('utf8')


class ImgKeyCoords:
    """
    Class to store information about the transformation an image suffered.
    """
    def __init__(self):

        self.o_path = None                 # Image path
        self.ti_size = (0, 0)              # Image size

        # It's better to keep coordinates as decimal numbers from 0.0 to 1.0 so in case of resizing the final image the
        # relative coordinates will remain the same.
        self.tf_top_left = (0.0, 0.0)      # Top-left corner coordinates
        self.tf_top = (0.5, 0.0)           # Top (center) coordinates
        self.tf_top_right = (1.0, 0.0)     # Top-right corner coordinates

        self.tf_left = (0.0, 0.5)          # Left (center) coordinates
        self.tf_center = (0.5, 0.5)        # Center coordinates
        self.tf_right = (1.0, 0.5)         # Right (center) coordinates

        self.tf_bottom_left = (0.0, 1.0)   # Bottom-left coordinates
        self.tf_bottom = (0.5, 1.0)        # Bottom (center) coordinates
        self.tf_bottom_right = (1.0, 1.0)  # Bottom-right coordinates

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
def cnv_img(pu_mode, pu_src_file, pu_dst_file, po_random_precfg):
    """
    Main convert function that will call different sub-convert functions depending on the value of pu_mode.

    :param pu_mode: Mode of image conversion. i.e. 'frame'

    :param pu_src_file: Source file for conversion. i.e. '/home/john/original_picture.jpg'

    :param pu_dst_file: Destination file for conversion. i.e. '/home/john/final_picture.jpg'

    :param po_random_precfg: Configuration object with main options for conversion (size, rotation, grab point...)

    :return:
    """

    o_src_img_fp = files.FilePath(pu_src_file)
    o_dst_img_fp = files.FilePath(pu_dst_file)

    if not o_src_img_fp.has_exts(*tu_VALID_EXTS):
        raise ValueError('Not a valid src file extension (%s); valid ones are %s.' % (o_src_img_fp.u_ext,
                                                                                      str(tu_VALID_EXTS)))
    else:
        o_cfg = po_random_precfg.randomize()

        # Extension change if it's forced
        if o_cfg.u_format:
            o_dst_img_fp.u_ext = po_random_precfg.u_format

        ti_src_img_size = _img_get_size(o_src_img_fp.u_path)

        # Automatic aspect ratio (zero in any of the aspect ratios x,y) fixing
        if 0.0 in o_cfg.tf_aspect:
            o_cfg.tf_aspect = (float(ti_src_img_size[0]), float(ti_src_img_size[1]))

        # Aspect ratio "inversion" if the image is rotated
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

        elif pu_mode == 'enclose':
            o_transformation = _cnv_enclose(o_src_img_fp, o_dst_img_fp, o_cfg)
        elif pu_mode == 'frame':
            o_transformation = _cnv_frame(o_src_img_fp, o_dst_img_fp, o_cfg)
        elif pu_mode == 'hbars':
            o_transformation = _cnv_hbars(o_src_img_fp, o_dst_img_fp, o_cfg)
        elif pu_mode == 'magcover':
            o_transformation = _cnv_magcover(o_src_img_fp, o_dst_img_fp, o_cfg)
        elif pu_mode == 'mosaic':
            o_transformation = _cnv_mosaic(o_src_img_fp, o_dst_img_fp, o_cfg)
        elif pu_mode == 'reduce':
            o_transformation = _cnv_reduce(o_src_img_fp, o_dst_img_fp, o_cfg)
        elif pu_mode == 'vbars':
            o_transformation = _cnv_vbars(o_src_img_fp, o_dst_img_fp, o_cfg)
        else:
            o_transformation = None

        o_transformation.o_path = files.FilePath(pu_dst_file)

    return o_transformation


def _cnv_enclose(po_src_file, po_dst_file, po_cfg):
    """
    Simple transformation that increases the canvas size of an image leaving the original image centered.
    :param po_src_file:
    :param po_dst_file:
    :type po_cfg ImgConvertCfg:
    :return:
    """

    # Variables preparation
    #----------------------
    ti_src_size = _img_get_size(po_src_file.u_path)
    ti_delta_size = (po_cfg.ti_size[0] - ti_src_size[0], po_cfg.ti_size[1] - ti_src_size[1])

    # Gravity
    tf_grab = (po_cfg.tf_options[0], po_cfg.tf_options[1])

    # Pixels to add or remove from each side
    i_pix_up = int(tf_grab[1] * ti_delta_size[1])
    i_pix_do = ti_delta_size[1] - i_pix_up
    i_pix_le = int(tf_grab[0] * ti_delta_size[0])
    i_pix_ri = ti_delta_size[0] - i_pix_le

    #print
    #print '  (X, Y): %s' % str(tf_grab)
    #print '(dX, dY): %s' % str(ti_delta_size)
    #print 'dX (l/r): (%i, %i)' % (i_pix_le, i_pix_ri)
    #print 'dY (t/b): (%i, %i)' % (i_pix_up, i_pix_do)

    # Command line build
    #-------------------
    u_cmd = u'convert '
    u_cmd += u'"%s" ' % cmd.sanitize_path(po_src_file.u_path)

    # Background color
    u_cmd += u'-background "#%s" ' % po_cfg.u_color

    # Increasing/Decreasing the image borders until reaching the desired canvas size

    # Adding/Removing pixels from the top
    if i_pix_up != 0:
        u_cmd += u'-gravity North '
        if i_pix_up >= 0:
            u_cmd += u'-splice 0x%i ' % i_pix_up
        else:
            u_cmd += u'-chop 0x%i ' % -i_pix_up

    # Adding/Removing pixels from the bottom
    if i_pix_do != 0:
        u_cmd += u'-gravity South '
        if i_pix_do >= 0:
            u_cmd += u'-splice 0x%i ' % i_pix_do
        else:
            u_cmd += u'-chop 0x%i ' % -i_pix_do

    # Adding/Removing pixels from the left
    if i_pix_le != 0:
        u_cmd += u'-gravity West '
        if i_pix_le >= 0:
            u_cmd += u'-splice %ix0 ' % i_pix_le
        else:
            u_cmd += u'-chop %ix0 ' % -i_pix_le

    # Adding/Removing pixels from the right
    if i_pix_ri != 0:
        u_cmd += u'-gravity East '
        if i_pix_ri >= 0:
            u_cmd += u'-splice %ix0 ' % i_pix_ri
        else:
            u_cmd += u'-chop %ix0 ' % -i_pix_ri

    # Final output
    u_cmd += u'"%s"' % cmd.sanitize_path(po_dst_file.u_path)

    # Command line execution
    # -----------------------
    du_output = cmd.execute(u_cmd)

    if du_output['u_stderr']:
        print du_output['u_stderr']

    # Coordinates calculation after image manipulation
    # -------------------------------------------------
    o_img_transformation = ImgKeyCoords()
    o_img_transformation.ti_size = _img_get_size(po_dst_file.u_path)

    # Debug code to overlay image regions
    # _draw_coordinates(po_dst_file, o_img_transformation)

    return o_img_transformation


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
    o_img_light = files.FilePath(o_MEDIA_ROOT_FP.u_path, u'frame', u'brightness.png')
    o_img_light.absfile()

    # Variables preparation for imagemagick command
    #----------------------------------------------
    ti_img_size = geom.max_rect_in(ptf_rec_out=po_cfg.ti_size, ptf_asp_in=po_cfg.tf_aspect)
    i_light_size = 2 * max(ti_img_size[0], ti_img_size[1])
    f_aspect_ratio = po_cfg.tf_aspect[0] / po_cfg.tf_aspect[1]
    f_gb_aspect_ratio = 160.0 / 144.0

    # Real location (x,y) in pixels of the focus point of the image
    ti_focus = (int(po_cfg.tf_options[0] * ti_img_size[0]), int(po_cfg.tf_options[1] * ti_img_size[1]))

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
    u_cmd += u'"%s" ' % cmd.sanitize_path(po_src_file.u_path)                                # Source file

    if f_aspect_ratio == f_gb_aspect_ratio and i_colors <= 4 and b_grayscale:                # GameBoy (mono) color tint
        u_cmd += u'+level-colors "#0f380e,#9bbb0e" '
    #else:
    #    print po_src_file.u_path
    #    print 'aspect: %f (!= %f)' % (f_aspect_ratio, f_gb_aspect_ratio)
    #    print 'colors: %i' % i_colors
    #    print '   b/w: %s' % b_grayscale

    u_cmd += u'-resize %ix%i! ' % (ti_img_size[0], ti_img_size[1])                           # Resizing
    u_cmd += u'-background transparent '                                                     # Transparent background

    u_cmd += u'\( "%s" -resize %ix%i! -geometry %s \) -composite ' % (cmd.sanitize_path(o_img_light.u_path),
                                                                      i_light_size,
                                                                      i_light_size,
                                                                      u_foc_img_off)         # Light/shadow add

    u_cmd += u'-bordercolor "%s" -border %i ' % (u_frame_color, i_frame_thickness)         # Frame border
    u_cmd += u'-rotate %f ' % po_cfg.f_rotation                                              # Rotation
    u_cmd += u'\( -clone 0 -background black -shadow %ix%i+0+%i \) ' % (i_shadow_opac,
                                                                        i_shadow_blur,
                                                                        i_shadow_dist)       # Shadow creation
    u_cmd += u'-reverse -background none -layers merge +repage '                             # Shadow composition

    u_cmd += u'-background "#%s" -flatten ' % po_cfg.u_color                                 # Background color
    u_cmd += u'"%s"' % cmd.sanitize_path(po_dst_file.u_path)                                 # Output file

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
    # draw_coordinates(po_dst_file, o_img_transformation)

    return o_img_transformation


def _cnv_hbars(po_src_file, po_dst_file, po_cfg):
    """
    Image conversion that pixelates the image using horizontal bars.

    This function is a quick modification (only two lines modified from _cnv_mosaic:

        In _cnv_mosaic:

            [1] ti_pic_size_final = geom.max_rect_in(po_cfg.ti_size, po_cfg.tf_aspect)
            [2] u_cmd += u'-ordered-dither o2x2 -resize %ix%i! ' % (ti_pic_size_small[0], ti_pic_size_small[1])
            [3] ti_pic_size_small = geom.max_rect_in((i_pixels, i_pixels), po_cfg.tf_aspect)

        Here:

            [1] ti_pic_size_final = po_cfg.ti_size
            [2] u_cmd += u'-ordered-dither o2x2 -resize %ix%i! ' % (1, ti_pic_size_small[1])
            [3] ti_pic_size_small = (1, i_pixels)

    So, don't edit this function
    directly for any major change.

    :param po_src_file:
    :param po_dst_file:
    :param po_cfg:
    :return:
    """

    # Variables preparation
    #----------------------
    i_colors = int(po_cfg.tf_options[0])
    i_pixels = int(po_cfg.tf_options[1])

    ti_pic_size_final = po_cfg.ti_size
    ti_pic_size_small = (1, i_pixels)

    ti_pic_size_big = geom.min_rect_out(ptf_rec_in=ti_pic_size_final, pf_rot_out=po_cfg.f_rotation)

    # Command line build
    #-------------------
    u_cmd = u'convert '
    u_cmd += u'"%s" ' % cmd.sanitize_path(po_src_file.u_path)

    # Pixelation
    u_cmd += u'-colors %i ' % i_colors
    u_cmd += u'-ordered-dither o2x2 -resize %ix%i! ' % (ti_pic_size_small[0], ti_pic_size_small[1])
    u_cmd += u'-modulate 100,120,100 '

    # Color overlay
    u_cmd += u'-colorspace rgb '
    u_cmd += u'\( -clone 0 -fill "#%s" -colorize 100%% \) -compose Over -composite  ' % po_cfg.u_color

    # Resize (1 extra pixel added in each border to avoid border color seen because rounding error)
    u_cmd += u'-filter point -resize %ix%i! ' % (ti_pic_size_big[0] + 2, ti_pic_size_big[1] + 2)

    # Rotation
    u_cmd += u'-rotate %f +repage ' % po_cfg.f_rotation

    # Crop
    u_cmd += u'-gravity Center '
    u_cmd += u'-crop %ix%i+0+0 +repage ' % (ti_pic_size_final[0], ti_pic_size_final[1])

    # Final output
    u_cmd += u'"%s"' % cmd.sanitize_path(po_dst_file.u_path)

    # Command line execution
    #-----------------------
    du_output = cmd.execute(u_cmd)

    if du_output['u_stderr']:
        print du_output['u_stderr']

    # Coordinates calculation after image manipulation
    #-------------------------------------------------
    o_img_transformation = ImgKeyCoords()
    o_img_transformation.ti_size = _img_get_size(po_dst_file.u_path)

    # Debug code to overlay image regions
    #_draw_coordinates(po_dst_file, o_img_transformation)

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
    o_img_corner_fold = files.FilePath(o_MEDIA_ROOT_FP.u_path, u'magcover', u'corner_fold.png')
    o_img_corner_fold.absfile()
    u_img_corner_fold = o_img_corner_fold.u_path.decode('utf8')

    o_img_left_brightness = files.FilePath(o_MEDIA_ROOT_FP.u_path, u'magcover', u'left_brightness.png')
    o_img_left_brightness.absfile()
    u_img_left_brightness = o_img_left_brightness.u_path.decode('utf8')

    o_img_left_fold = files.FilePath(o_MEDIA_ROOT_FP.u_path, u'magcover', u'left_fold_dark.png')
    o_img_left_fold.absfile()
    u_img_left_fold = o_img_left_fold.u_path.decode('utf8')

    o_img_stp = files.FilePath(o_MEDIA_ROOT_FP.u_path, u'magcover', u'staple.png')
    o_img_stp.absfile()
    u_img_stp = o_img_stp.u_path.decode('utf8')

    # Trigonometric pre-calculations
    #-------------------------------
    f_sin = math.sin(math.radians(po_cfg.f_rotation))
    f_cos = math.cos(math.radians(po_cfg.f_rotation))

    # Variables preparation
    #----------------------
    ti_cvr_size_final = geom.max_rect_in(po_cfg.ti_size, po_cfg.tf_aspect)

    # Staples
    ti_stp_size_orig = _img_get_size(u_img_stp)
    f_stp_pos_ratio = 0.049 * ti_cvr_size_final[0] / ti_cvr_size_final[1] + 0.220  # based in my quick statistical study
    f_stp_paper_y_ratio = 0.043 * 2                                                # TODO: Use statistical study again

    _i_stp_height = int(f_stp_paper_y_ratio * ti_cvr_size_final[1])
    ti_stp_size_final = (int(1.0 * ti_stp_size_orig[0] * _i_stp_height / ti_stp_size_orig[1]),
                         _i_stp_height)
    i_stp_x = int(11.0 / 60.0 * ti_stp_size_final[0])

    # Landscape covers will have just one staple while portrait ones will have 2
    li_staples_y = []
    if float(ti_cvr_size_final[0]) / ti_cvr_size_final[1] > 1.0:
        li_staples_y.append(0.5 * ti_cvr_size_final[1] - 0.5 * _i_stp_height)
    else:
        li_staples_y.append(f_stp_pos_ratio * ti_cvr_size_final[1] - 0.5 * _i_stp_height)
        li_staples_y.append((1 - f_stp_pos_ratio) * ti_cvr_size_final[1] - 0.5 * _i_stp_height)

    # Left fold configuration
    i_fold_size = math.ceil(0.025 * ti_cvr_size_final[0])
    f_fold_mult = 0.5

    # Shadow configuration
    i_shadow1_dist = math.ceil(0.01 * min(po_cfg.ti_size))
    i_shadow1_opac = 70                                                                    # 0-100
    i_shadow1_blur = math.ceil(0.0025 * max(po_cfg.ti_size))

    i_shadow2_blur = 4 * i_shadow1_blur

    # Left Brightness configuration
    f_left_bright_mult = 0.5 * (1 + abs(f_sin))                                            # 0.5 at 90º, 1.0 at 0º

    # Corner fold configuration
    f_bottom_right_bright_mult = 0.1 * (1 + max(0, math.cos(math.radians(45 + po_cfg.f_rotation))))
    i_corner_fold_size_final = int(0.06 * ti_cvr_size_final[0])

    # Command line build
    #-------------------
    u_cmd = u'convert '
    u_cmd += u'"%s" ' % cmd.sanitize_path(po_src_file.u_path)                              # Source file
    u_cmd += u'-resize %ix%i! ' % (ti_cvr_size_final[0], ti_cvr_size_final[1])             # Resizing
    u_cmd += u'-background transparent '                                                   # Transparent background

    # Left fold
    # TODO: Make left fold shadow transitions to a left fold brightness for high rotation angles (>45º)
    u_cmd += u'\( "%s" ' % u_img_left_fold
    u_cmd += u'-fill Black -colorize 100%%,100%%,100%%,0%% '
    u_cmd += u'-resize %ix%i! ' % (i_fold_size, ti_cvr_size_final[1])
    u_cmd += u'-channel alpha -fx "%s * a" ' % f_fold_mult                                 # Alpha channel modification
    u_cmd += u'-gravity NorthWest -extent %ix0 ' % ti_cvr_size_final[0]
    u_cmd += u'-background "#808080" -flatten -background transparent '
    u_cmd += u'\) -compose hardlight -composite '

    # Left reflection
    # TODO: Make reflection intensity (and shape?) change with rotation angle.
    u_cmd += u'\( "%s" ' % cmd.sanitize_path(u_img_left_brightness)                                           # Left brightness
    u_cmd += u'-resize %ix%i! ' % (ti_cvr_size_final[0], ti_cvr_size_final[1])             # Light add
    u_cmd += u'-channel alpha -fx "%s * a" ' % f_left_bright_mult                          # Alpha channel modification
    u_cmd += u'\) -composite '

    # Bottom right corner fold reflection
    u_cmd += u'-gravity SouthEast '
    u_cmd += u'\( "%s" ' % cmd.sanitize_path(u_img_corner_fold)
    u_cmd += u'-resize %ix%i! ' % (i_corner_fold_size_final, i_corner_fold_size_final)
    u_cmd += u'-channel alpha -fx "%s * a" ' % f_bottom_right_bright_mult
    u_cmd += u'\) -composite '
    u_cmd += u'-gravity NorthWest '

    # Staples
    u_cmd += u'-gravity east -extent +%i+0 -gravity northwest ' % i_stp_x
    for i_staple_y in li_staples_y:
        u_cmd += u'\( "%s" ' % cmd.sanitize_path(u_img_stp)
        u_cmd += u'-resize x%i ' % _i_stp_height
        u_cmd += u'-geometry +0+%i ' % i_staple_y
        u_cmd += u'\) -compose over -composite '

    u_cmd += u'-rotate %f ' % po_cfg.f_rotation

    # Primary shadow
    u_cmd += u'\( '
    u_cmd += u'-clone 0 -background black '
    u_cmd += u'-resize 100%% '
    u_cmd += u'-shadow %ix%i+0+%i ' % (i_shadow1_opac, i_shadow1_blur, i_shadow1_dist)
    u_cmd += u'\) '

    # Secondary shadow
    u_cmd += u'\( '
    u_cmd += u'-clone 0 -background black '
    u_cmd += u'-shadow 40x%i+0+0 ' % i_shadow2_blur
    u_cmd += u'\) '

    u_cmd += u'-reverse -background none -layers merge +repage '                         # Shadow composition

    u_cmd += u'-background "#%s" -flatten ' % po_cfg.u_color                             # Background color
    u_cmd += u'"%s"' % cmd.sanitize_path(po_dst_file.u_path)                             # Output file

    # Command line execution
    #-----------------------
    du_output = cmd.execute(u_cmd)

    if du_output['u_stderr']:
        print du_output['u_stderr']

    # Transformation object result
    ti_final_size = _img_get_size(po_dst_file.u_path)
    i_extra_top = max(0, i_shadow1_blur - i_shadow1_dist, i_shadow2_blur)
    i_extra_bottom = max(0, i_shadow1_blur + i_shadow1_dist, i_shadow2_blur)

    # Delta distances in rotated image in screen coordinates
    tf_dx = (0.5 * f_cos * ti_cvr_size_final[0], -0.5 * f_sin * ti_cvr_size_final[0])
    tf_dy = (-0.5 * f_sin * ti_cvr_size_final[1], -0.5 * f_cos * ti_cvr_size_final[1])

    tf_center = (0.5 * ti_final_size[0] + i_stp_x * f_cos,
                 0.5 * (ti_final_size[1] - i_extra_top - i_extra_bottom) + i_extra_top)
    tf_left = (tf_center[0] - tf_dx[0], tf_center[1] - tf_dx[1])
    tf_right = (tf_center[0] + tf_dx[0], tf_center[1] + tf_dx[1])
    tf_top = (tf_center[0] + tf_dy[0], tf_center[1] + tf_dy[1])
    tf_top_left = (tf_top[0] - tf_dx[0], tf_top[1] - tf_dx[1])
    tf_top_right = (tf_top[0] + tf_dx[0], tf_top[1] + tf_dx[1])
    tf_bottom = (tf_center[0] - tf_dy[0], tf_center[1] - tf_dy[1])
    tf_bottom_left = (tf_bottom[0] - tf_dx[0], tf_bottom[1] - tf_dx[1])
    tf_bottom_right = (tf_bottom[0] + tf_dx[0], tf_bottom[1] + tf_dx[1])

    # Transformation object result
    o_img_transformation = ImgKeyCoords()
    o_img_transformation.ti_size = ti_final_size
    o_img_transformation.tf_top_left = (tf_top_left[0] / ti_final_size[0], tf_top_left[1] / ti_final_size[1])
    o_img_transformation.tf_top = (tf_top[0] / ti_final_size[0], tf_top[1] / ti_final_size[1])
    o_img_transformation.tf_top_right = (tf_top_right[0] / ti_final_size[0], tf_top_right[1] / ti_final_size[1])
    o_img_transformation.tf_left = (tf_left[0] / ti_final_size[0], tf_left[1] / ti_final_size[1])
    o_img_transformation.tf_center = (tf_center[0] / ti_final_size[0], tf_center[1] / ti_final_size[1])
    o_img_transformation.tf_right = (tf_right[0] / ti_final_size[0], tf_right[1] / ti_final_size[1])
    o_img_transformation.tf_bottom_left = (tf_bottom_left[0] / ti_final_size[0],
                                           tf_bottom_left[1] / ti_final_size[1])
    o_img_transformation.tf_bottom = (tf_bottom[0] / ti_final_size[0], tf_bottom[1] / ti_final_size[1])
    o_img_transformation.tf_bottom_right = (tf_bottom_right[0] / ti_final_size[0],
                                            tf_bottom_right[1] / ti_final_size[1])

    # Debug code to overlay image regions
    #_draw_coordinates(po_dst_file, o_img_transformation)

    return o_img_transformation


def _cnv_mosaic(po_src_file, po_dst_file, po_cfg):
    # Variables preparation
    #----------------------
    i_colors = int(po_cfg.tf_options[0])
    i_pixels = int(po_cfg.tf_options[1])

    ti_pic_size_final = po_cfg.ti_size

    # The shortest side of original picture will contain the desired number of pixels and the longest one the pixels
    # needed to keep the original aspect ratio.
    if po_cfg.tf_aspect[0] < po_cfg.tf_aspect[1]:
        i_width_small = i_pixels
        i_height_small = int(round(po_cfg.tf_aspect[1] / po_cfg.tf_aspect[0] * i_pixels))
    else:
        i_height_small = i_pixels
        i_width_small = int(round(po_cfg.tf_aspect[0] / po_cfg.tf_aspect[1] * i_pixels))

    ti_pic_size_small = (i_width_small, i_height_small)

    #print 'SRC ASPECT: %s' % str(po_cfg.tf_aspect)
    #print 'SMALL SIZE: %s' % str(ti_pic_size_small)

    ti_pic_size_big = geom.min_rect_out(ptf_rec_in=ti_pic_size_final,
                                        pf_rot_out=po_cfg.f_rotation,
                                        ptf_asp_out=po_cfg.tf_aspect)

    # Command line build
    #-------------------
    u_cmd = u'convert '
    u_cmd += u'"%s" ' % cmd.sanitize_path(po_src_file.u_path)

    # Pixelation
    u_cmd += u'-colors %i ' % i_colors
    u_cmd += u'-ordered-dither o2x2 -resize %ix%i! ' % (ti_pic_size_small[0], ti_pic_size_small[1])
    u_cmd += u'-modulate 100,120,100 '

    # Color overlay
    u_cmd += u'-colorspace rgb '
    u_cmd += u'\( -clone 0 -fill "#%s" -colorize 100%% \) -compose Over -composite  ' % po_cfg.u_color

    # Resize (1 extra pixel added in each border to avoid border color seen because rounding error)
    u_cmd += u'-filter point -resize %ix%i! ' % (ti_pic_size_big[0] + 2, ti_pic_size_big[1] + 2)

    #u_cmd += u'-background red '

    # Rotation
    u_cmd += u'-rotate %f +repage ' % po_cfg.f_rotation

    # Crop
    u_cmd += u'-gravity Center '
    u_cmd += u'-crop %ix%i+0+0 +repage ' % (ti_pic_size_final[0], ti_pic_size_final[1])

    # Final output
    u_cmd += u'"%s"' % cmd.sanitize_path(po_dst_file.u_path)

    # Command line execution
    #-----------------------
    du_output = cmd.execute(u_cmd)

    if du_output['u_stderr']:
        print du_output['u_stderr']

    # Coordinates calculation after image manipulation
    #-------------------------------------------------
    o_img_transformation = ImgKeyCoords()
    o_img_transformation.ti_size = _img_get_size(po_dst_file.u_path)

    # Debug code to overlay image regions
    #_draw_coordinates(po_dst_file, o_img_transformation)

    return o_img_transformation


def _cnv_reduce(po_src_file, po_dst_file, po_cfg):
    """
    Simple function to resize an image while respecting it's original aspect ratio.
    :param po_src_file:
    :param po_dst_file:
    :type po_cfg ImgConvertCfg:
    :return:
    """

    # TODO: Think about something interesting to do with the options -o float,float

    # Variables preparation for imagemagick command
    # ----------------------------------------------
    ti_img_src_size = _img_get_size(po_src_file.u_path)
    ti_img_dst_size = geom.max_rect_in(ptf_rec_out=po_cfg.ti_size, ptf_asp_in=po_cfg.tf_aspect)

    # Command line build
    #-------------------
    u_cmd = u'convert '
    u_cmd += u'"%s" ' % cmd.sanitize_path(po_src_file.u_path)

    # Background
    u_cmd += u'-background "#%s" ' % po_cfg.u_color

    # Resize
    if ti_img_src_size[0] > ti_img_dst_size[0] and ti_img_src_size[1] > ti_img_dst_size[1]:
        u_cmd += u'-resize %ix%i! ' % (ti_img_dst_size[0], ti_img_dst_size[1])

    # Rotation
    u_cmd += u'-rotate %f +repage ' % po_cfg.f_rotation

    # Final output
    u_cmd += u'"%s"' % cmd.sanitize_path(po_dst_file.u_path)

    # Command line execution
    #-----------------------
    du_output = cmd.execute(u_cmd)

    if du_output['u_stderr']:
        print du_output['u_stderr']

    # Coordinates calculation after image manipulation
    #-------------------------------------------------
    o_img_transformation = ImgKeyCoords()
    o_img_transformation.ti_size = _img_get_size(po_dst_file.u_path)

    # Debug code to overlay image regions
    #_draw_coordinates(po_dst_file, o_img_transformation)

    return o_img_transformation


def _cnv_vbars(po_src_file, po_dst_file, po_cfg):
    """
    Image conversion that pixelates the image using vertical bars.

    This function is a quick modification (only two lines modified from _cnv_mosaic:

        In _cnv_mosaic:

            [1] ti_pic_size_final = geom.max_rect_in(po_cfg.ti_size, po_cfg.tf_aspect)
            [2] u_cmd += u'-ordered-dither o2x2 -resize %ix%i! ' % (ti_pic_size_small[0], ti_pic_size_small[1])
            [3] ti_pic_size_small = geom.max_rect_in((i_pixels, i_pixels), po_cfg.tf_aspect)

        Here:

            [1] ti_pic_size_final = po_cfg.ti_size
            [2] u_cmd += u'-ordered-dither o2x2 -resize %ix%i! ' % (ti_pic_size_small[1], 1)
            [3] ti_pic_size_small = (i_pixels, 1)

    So, don't edit this function
    directly for any major change.

    :param po_src_file:
    :param po_dst_file:
    :param po_cfg:
    :return:
    """

    # Variables preparation
    #----------------------
    i_colors = int(po_cfg.tf_options[0])
    i_pixels = int(po_cfg.tf_options[1])

    ti_pic_size_final = po_cfg.ti_size
    ti_pic_size_small = (i_pixels, 1)

    ti_pic_size_big = geom.min_rect_out(ptf_rec_in=ti_pic_size_final, pf_rot_out=po_cfg.f_rotation)

    # Command line build
    #-------------------
    u_cmd = u'convert '
    u_cmd += u'"%s" ' % cmd.sanitize_path(po_src_file.u_path)

    # Pixelation
    u_cmd += u'-colors %i ' % i_colors
    u_cmd += u'-ordered-dither o2x2 -resize %ix%i! ' % (ti_pic_size_small[0], ti_pic_size_small[1])
    u_cmd += u'-modulate 100,120,100 '

    # Color overlay
    u_cmd += u'-colorspace rgb '
    u_cmd += u'\( -clone 0 -fill "#%s" -colorize 100%% \) -compose Over -composite  ' % po_cfg.u_color

    # Resize (1 extra pixel added in each border to avoid border color seen because rounding error)
    u_cmd += u'-filter point -resize %ix%i! ' % (ti_pic_size_big[0] + 2, ti_pic_size_big[1] + 2)

    #u_cmd += u'-background red '

    # Rotation
    u_cmd += u'-rotate %f +repage ' % po_cfg.f_rotation

    # Crop
    u_cmd += u'-gravity Center '
    u_cmd += u'-crop %ix%i+0+0 +repage ' % (ti_pic_size_final[0], ti_pic_size_final[1])

    # Final output
    u_cmd += u'"%s"' % cmd.sanitize_path(po_dst_file.u_path)

    # Command line execution
    #-----------------------
    du_output = cmd.execute(u_cmd)

    if du_output['u_stderr']:
        print du_output['u_stderr']

    # Coordinates calculation after image manipulation
    #-------------------------------------------------
    o_img_transformation = ImgKeyCoords()
    o_img_transformation.ti_size = _img_get_size(po_dst_file.u_path)

    # Debug code to overlay image regions
    #_draw_coordinates(po_dst_file, o_img_transformation)

    return o_img_transformation


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
    u_cmd += u'"%s" ' % cmd.sanitize_path(o_img_file.u_path)

    u_cmd += u'-stroke lime -fill "#ff000080" '
    u_cmd += u'-draw "polygon %s %s %s %s" ' % (u_tl, u_t, u_c, u_l)

    u_cmd += u'-stroke lime -fill "#00ff0080" '
    u_cmd += u'-draw "polygon %s %s %s %s" ' % (u_t, u_tr, u_r, u_c)

    u_cmd += u'-stroke lime -fill "#0000ff80" '
    u_cmd += u'-draw "polygon %s %s %s %s" ' % (u_l, u_c, u_b, u_bl)

    u_cmd += u'-stroke lime -fill "#ff00ff80" '
    u_cmd += u'-draw "polygon %s %s %s %s" ' % (u_c, u_r, u_br, u_b)

    u_cmd += u'"%s"' % cmd.sanitize_path(o_img_file.u_path)

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

    u_cmd = u'identify -format %%k "%s"' % cmd.sanitize_path(pu_image)
    du_output = cmd.execute(u_cmd)
    i_colors = int(du_output['u_stdout'])

    return i_colors


def _img_is_grayscale(pu_image):
    """
    Function to check if an image is a pure greyscale image using imagemagick.
    :param pu_image: File name
    :return: True if the image is greyscale.
    """

    # Reference for getting the amount of color in the image:
    #
    # http://www.imagemagick.org/discourse-server/viewtopic.php?t=19580#p133865
    #
    # The output will be one single float value 0.0-1.0 (as a string, of course) like "0.273162"

    u_cmd = u'convert "%s" -colorspace HSL -channel g -separate +channel -format "%%[fx:mean]" ' \
            u'info:' % cmd.sanitize_path(pu_image)
    du_output = cmd.execute(u_cmd)

    f_color_ratio = float(du_output['u_stdout'])

    if f_color_ratio == 0.0:
        b_grayscale = True
    else:
        b_grayscale = False

    return b_grayscale


def _img_get_size(pu_image):
    """
    Function to get the size of an image file.
    :param pu_image: Image file. i.e. '/home/john/my_face.jpg'
    :return: A tuple of integers with width and height. i.e. (640, 480)
    """

    u_cmd = u'identify -format %%G "%s"' % cmd.sanitize_path(pu_image)
    du_output = cmd.execute(u_cmd)

    # The standard output of the command above is widthxheight. i.e. 640x906. So, it's easy to parse.
    i_width = int(du_output['u_stdout'].partition(u'x')[0])
    i_height = int(du_output['u_stdout'].partition(u'x')[2])

    return i_width, i_height


def _clamp(i_value, i_min, i_max):
    """
    Function to force a value to be between certain range.
    :param i_value:
    :param i_min:
    :param i_max:
    :return:
    """
    return max(min(i_max, i_value), i_min)
