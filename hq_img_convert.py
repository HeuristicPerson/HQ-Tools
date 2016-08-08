#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Function and command line utility to convert "raw" game images
"""

import argparse
import re
import sys

from libs import cons
from libs import files
from libs import geom
from libs import imagemagick
from libs import strings

from libs.imagemagick import ImgConvCfgGenerator

# CONSTANTS
#=======================================================================================================================
u_PROG_NAME = u'HQ IMAGE CONVERT'
u_PROG_VER = u'v2016.02.21'

o_CWD = files.get_cwd()
o_IMG_CONV_DEF_CFG = imagemagick.ImgConvCfgGenerator()


# HELPER FUNCTIONS
#=======================================================================================================================
def _get_cmd_options():
    """
    Function to process the command-line options.

    :return: TODO: A dictionary with different options.
    """

    # Variable preparation
    u_platforms = u''
    for o_platform in cons.do_platforms.itervalues():
        u_platforms += u'"%s" (%s), ' % (o_platform.u_ALIAS, o_platform.u_NAME)
    u_platforms = u_platforms.strip()
    u_platforms = u_platforms.strip(u',')

    # Fixing a problem in argparse when entering optional arguments with negative numbers (i.e. -a -1.0) which confuse
    # argparse since it thinks the -1.0 means: a) "-a" option doesn't have the following needed argument value, b) there
    # is an unknown extra argument "-1.0". The quick (and dirty) solution is to pre-process the arguments and add an
    # extra space at the beginning of the affected arguments.
    lu_new_args = []
    for u_arg in sys.argv:
        if u_arg[0] == '-' and u_arg[1].isdigit():
            lu_new_args.append(' %s' % u_arg)
        else:
            lu_new_args.append(u_arg)
    sys.argv = lu_new_args
    #for i, arg in enumerate(sys.argv):
    #    if (arg[0] == '-') and arg[1].isdigit(): sys.argv[i] = ' ' + arg

    o_arg_parser = argparse.ArgumentParser(description='A command line utility to convert and "enrich" video-game '
                                                       'screenshots.')
    o_arg_parser.add_argument('mode',
                              action='store',
                              choices=imagemagick.tu_CNV_MODES,
                              help='Image mode. i.e. "frame".')
    o_arg_parser.add_argument('src',
                              action='store',
                              help='Source image file. i.e. "/home/john/original-pic.jpg".')
    o_arg_parser.add_argument('dst',
                              action='store',
                              help='Destination image file. i.e. "/home/carl/pictures/final-pic.png".')
    o_arg_parser.add_argument('-a',
                              action='store',
                              default='0,0',
                              help='Aspect ratio or platform alias. i.e. "-a 16,9" or "-a nes". Valid platform alias '
                                   'are: %s.' % u_platforms)
    o_arg_parser.add_argument('-e',
                              action='store',
                              default=None,
                              choices=(None,) + imagemagick.tu_VALID_EXTS,
                              help='Change dst extension. i.e. "-e jpg" will create a jpg image. If you are converting '
                                   'a single file, you can simply define the extension by the output file name. For '
                                   'example "output.png" will produce a png file. When you are converting a whole '
                                   'directory of images, the output file name for each of the files will be the source'
                                   'file name; so the parameter "-e" allows you to change the extension.')
    o_arg_parser.add_argument('-o',
                              action='store',
                              default='0,0',
                              help='Options. i.e. "-o 1+0,2+1". They will mean something totally different depending '
                                   'on the mode chosen. For example, in "frame" mode, you can select the position of '
                                   'the brightness.')
    o_arg_parser.add_argument('-c',
                              action='store',
                              default='80808000',
                              help='Color in RGBA hex format. i.e. "-c ff000080".')
    o_arg_parser.add_argument('-r',
                              action='store',
                              default='0+0',
                              help='Image rotation. i.e. "-r 15+5" will be a rotation of 15 degrees anticlockwise plus a '
                                   'random rotation of +/- 5 degrees.')
    o_arg_parser.add_argument('-s',
                              action='store',
                              default='320,240',
                              help='Image size. i.e. "-s 320,240". This is the maximum image size. Images will be '
                                   'enlarged or reduced maintaining their aspect ratio until they occupy the maximum '
                                   'possible area of the area defined by this parameter. i.e. a square image which is '
                                   '30x30 pixels with a size parameter of "-s 100,200" will end being 100x100 pixels '
                                   'since that\'s the biggest square that can fit inside the rectangle of 100x200 '
                                   'pixels.')

    # Parsing and validation of the parameters
    i_cmd_errors = 0
    u_output = u''
    o_args = o_arg_parser.parse_args()

    # Mode
    #-----
    u_mode = o_args.mode
    if u_mode in imagemagick.tu_CNV_MODES:
        u_mode_found = cons.u_OK_TEXT
    else:
        i_cmd_errors += 1
        u_mode_found = cons.u_ER_TEXT
    u_output += u'   MODE: %s %s\n' % (u_mode_found, u_mode)

    # Source file or dir
    #-------------------
    u_src = o_args.src
    o_src = files.FilePath(u_src)
    o_src = o_src.absfile()

    if o_src.exists():
        if o_src.is_dir():
            u_type = u'D'
        else:
            u_type = u'F'

        u_msg = u'%s %s %s' % (cons.u_OK_TEXT, u_type, o_src.u_path)
    else:
        i_cmd_errors += 1
        u_msg = u'%s ? %s' % (cons.u_ER_TEXT, o_src.u_path)

    u_output += u'    SRC: %s\n' % u_msg

    # Destination file or dir
    #------------------------
    u_dst = o_args.dst
    o_dst = files.FilePath(u_dst)
    o_dst = o_dst.absfile()

    if o_src.is_file() and o_dst.root_exists() and (not o_dst.is_dir()):
        u_msg = u'%s F %s' % (cons.u_OK_TEXT, o_dst.u_path)
    elif o_src.is_dir() and o_dst.is_dir():
        u_msg = u'%s D %s' % (cons.u_OK_TEXT, o_dst.u_path)
    else:
        i_cmd_errors += 1
        # Error messages with advise about how to solve it
        if o_src.is_file() and o_dst.is_dir():
            u_msg = u'%s D %s - DST can\'t be a dir when SRC is a file' % (cons.u_ER_TEXT, o_dst.u_path)
        elif not o_dst.root_exists():
            u_msg = u'%s %s - can\'t find %s' % (cons.u_ER_TEXT, o_dst.u_path, o_dst.u_root)

        # Generic error message
        else:
            u_msg = u'%s ? %s' % (cons.u_ER_TEXT, o_dst.u_path)

    u_output += u'    DST: %s\n' % u_msg

    # Graphical configuration
    #========================
    o_graph_cfg = imagemagick.ImgConvCfgGenerator()

    # Aspect ratio
    #-------------
    u_aspect = o_args.a.strip()

    if u_aspect is not None:
        if u_aspect in cons.do_platforms:
            o_graph_cfg.tf_aspect = u_aspect
            o_platform = cons.do_platforms[u_aspect]
            u_msg = u'%s %s (%.2f, %.2f)' % (cons.u_OK_TEXT, u_aspect, o_platform.i_WIDTH, o_platform.i_HEIGHT)
        else:
            try:
                o_aspect = geom.Coord(pu_string=u_aspect)
                o_graph_cfg.tf_aspect = (o_aspect.f_x, o_aspect.f_y)
                if o_aspect.f_x and o_aspect.f_y != 0:
                    u_msg = u'%s %.2f:%.2f' % (cons.u_OK_TEXT, o_aspect.f_x, o_aspect.f_y)
                else:
                    u_msg = u'%s %.2f:%.2f  (Any 0 => automatic)' % (cons.u_OK_TEXT, o_aspect.f_x, o_aspect.f_y)
            except ValueError:
                    u_msg = u'%s %s - Unknown aspect format' % (cons.u_ER_TEXT, u_aspect)

    elif u_aspect is None:
        u_msg = u'%s automatic (same as source image)' % cons.u_OK_TEXT

    else:
        i_cmd_errors += 1
        u_msg = u'%s %s - Unknown aspect format' % (cons.u_ER_TEXT, u_aspect)

    u_output += u'\n  G_ASP: %s\n' % u_msg

    # Background color
    #-----------------
    u_bgcolor = o_args.c.strip()

    if u_bgcolor.lower() == _parse_color(u_bgcolor):
        o_graph_cfg.u_color = u_bgcolor
        u_msg = u'%s %s' % (cons.u_OK_TEXT, u_bgcolor)
    else:
        i_cmd_errors += 1
        u_msg = u'%s %s - Unknown color format' % (cons.u_ER_TEXT, u_bgcolor)

    u_output += u'  G_BGC: %s\n' % u_msg

    # Extension
    #----------
    u_ext = o_args.e
    if u_ext:
        o_graph_cfg.u_format = u_ext
        u_msg = u'%s %s' % (cons.u_OK_TEXT, u_ext)
    else:
        u_msg = u'%s automatic' % cons.u_OK_TEXT

    u_output += u'  G_EXT: %s\n' % u_msg

    # Options
    #--------
    u_options = o_args.o.strip()

    try:
        o_options = geom.Coord(pu_string=u_options)
        o_graph_cfg.tf_options = (o_options.f_x, o_options.f_y, o_options.f_dx, o_options.f_dy)
        u_msg = u'%s %.2f±%.2f, %.2f±%.2f' % (cons.u_OK_TEXT, o_options.f_x, o_options.f_dx,
                                              o_options.f_y, o_options.f_dy)
    except ValueError:
        i_cmd_errors += 1
        u_msg = u'%s %s - Unknown format' % (cons.u_ER_TEXT, u_options)

    u_output += u'  G_OPT: %s\n' % u_msg

    # Rotation
    #---------
    u_rotation = o_args.r.strip()

    try:
        o_rotation = geom.Coord(pu_string=u_rotation)
        o_graph_cfg.tf_rotation = (o_rotation.f_x, o_rotation.f_dx)
        u_msg = u'%s %.2f±%.2fº' % (cons.u_OK_TEXT, o_rotation.f_x, o_rotation.f_dx)
    except ValueError:
        i_cmd_errors += 1
        u_msg = u'%s %s - Unknown format' % (cons.u_ER_TEXT, u_rotation)

    u_output += u'  G_ROT: %s\n' % u_msg

    # Size
    #-----
    u_size = o_args.s.strip()

    try:
        o_size = geom.Coord(pu_string=u_size)
        o_graph_cfg.ti_size = (int(o_size.f_x), int(o_size.f_y), int(o_size.f_dx), int(o_size.f_dy))
        if (o_size.f_x >= 1) and (o_size.f_y >= 1):
            u_msg = u'%s %i±%i x %i±%i px' % (cons.u_OK_TEXT, o_size.f_x, o_size.f_dx, o_size.f_y, o_size.f_dy)
        else:
            i_cmd_errors += 1
            u_msg = u'%s %ix%i - Both sizes need to be bigger than 1' % (cons.u_ER_TEXT, o_size.f_x, o_size.f_y)
    except ValueError:
        i_cmd_errors += 1
        u_msg = u'%s %s - '

    u_output += u'  G_SIZ: %s\n' % u_msg

    print u_output

    if i_cmd_errors:
        print u'%i error(s) found. Solve them and try launching the program again.' % i_cmd_errors
        sys.exit()
    else:
        return {'u_mode': u_mode,
                'u_src': o_src.u_path,
                'u_dst': o_dst.u_path,
                'o_cfg': o_graph_cfg}


def _parse_color(pu_string):
    """
    Function to check if a string contains a valid RGB(A) hexadecimal color.
    :return: True/False
    """
    u_pattern = r'([0-9a-f]{8})|([0-9a-f]{6})'
    o_match = re.search(u_pattern, pu_string, flags=0)

    if o_match:
        return o_match.group()


def img_convert(pu_mode=None,
                pu_src_path=None,
                pu_dst_path=None,
                po_cfg=o_IMG_CONV_DEF_CFG,
                pb_del_src=False,
                pi_print_mode=1):

    o_input_src_fp = files.FilePath(pu_src_path)
    o_input_dst_fp = files.FilePath(pu_dst_path)

    # 1st we build the list of source and destination files
    #------------------------------------------------------
    lo_raw_sources_fp = []
    lo_raw_destinations_fp = []

    # Single file mode
    if o_input_src_fp.is_file():
        lo_raw_sources_fp.append(o_input_src_fp)
        # if output = dir => output file name the same as the input file name
        if o_input_dst_fp.is_dir():
            o_proc_dst_fp = files.FilePath(o_input_dst_fp.u_path, o_input_src_fp.u_file)
            lo_raw_destinations_fp.append(o_proc_dst_fp)
        # if output = file, the directory have to exist
        elif o_input_dst_fp.root_exists():
            lo_raw_destinations_fp.append(o_input_dst_fp)
        # error handling
        else:
            raise ValueError('Problem with pu_src_path and/or pu_dst_path in single file mode')

    # Directory mode
    elif o_input_src_fp.is_dir():
        lo_content_fp = o_input_src_fp.content(pu_mode='files')
        lo_raw_sources_fp += lo_content_fp
        # if output = dir => output file names will be the same as the input file name
        if o_input_dst_fp.is_dir():
            for o_element_fp in lo_content_fp:
                o_proc_dst_fp = files.FilePath(o_input_dst_fp.u_path, o_element_fp.u_file)
                lo_raw_destinations_fp.append(o_proc_dst_fp)
        elif o_input_dst_fp.is_file():
            raise ValueError('You can\'t convert a directory to a single file')
        else:
            raise ValueError('Unknown error')

    # Error handling
    else:
        raise ValueError('Problem with unknown mode: not "single file" or "directory" mode?')

    # 2nd, from the raw list of elements, we must consider just the ones with proper image extension
    #-----------------------------------------------------------------------------------------------
    lo_clean_sources_fp = []
    lo_clean_destinations_fp = []

    for o_raw_source_fp, o_raw_destination_fp in zip(lo_raw_sources_fp, lo_raw_destinations_fp):
        b_src_ext_ok = False
        b_dst_ext_ok = False

        if o_raw_source_fp.has_exts(*imagemagick.tu_VALID_EXTS):
            b_src_ext_ok = True
        if o_raw_destination_fp.has_exts(*imagemagick.tu_VALID_EXTS):
            b_dst_ext_ok = True

        if b_src_ext_ok and b_dst_ext_ok:
            lo_clean_sources_fp.append(o_raw_source_fp)
            lo_clean_destinations_fp.append(o_raw_destination_fp)

    # 3rd, we process the images
    #---------------------------
    i_image = 0
    for o_src_fp, o_dst_fp in zip(lo_clean_sources_fp, lo_clean_destinations_fp):
        i_image += 1
        o_output = imagemagick.cnv_img(pu_mode, o_src_fp.u_path, o_dst_fp.u_path, po_cfg)

        if pi_print_mode > 0:
            u_output = u'%s [%i/%i] %s  ->  %s' % (cons.u_OK_TEXT,
                                                   i_image,
                                                   len(lo_clean_sources_fp),
                                                   o_src_fp.u_path,
                                                   o_dst_fp.u_path)
            # One-line print mode
            if pi_print_mode == 1:
                if cons.i_TERM_COLS > 0 and cons.i_TERM_ROWS > 0:
                    u_output = u_output.ljust(cons.i_TERM_COLS)[0:cons.i_TERM_COLS]

                u_output = u'\r%s' % u_output
                sys.stdout.write(u_output)
                sys.stdout.flush()
            # One line per converted file mode
            elif pi_print_mode == 2:
                print u_output.encode('utf8')

    if pi_print_mode == 1:
        u_output = u'\r'
        sys.stdout.write(u_output)
        sys.stdout.flush()

    # It should be able to work with dirs and print a summary of what's doing (3 print modes, 0-1-2), etc...

    # TODO: Create a proper output with enough information to know what happened with the process
    #return o_output

# Main Code
#=======================================================================================================================
if __name__ == '__main__':
    print strings.hq_title(u_PROG_NAME, u_PROG_VER)

    dx_cmd_args = _get_cmd_options()

    # Image processing
    print 'Processing'
    print '-----------------------------------------'

    o_transformation_result = img_convert(pu_mode=dx_cmd_args['u_mode'],
                                          pu_src_path=dx_cmd_args['u_src'],
                                          pu_dst_path=dx_cmd_args['u_dst'],
                                          po_cfg=dx_cmd_args['o_cfg'])