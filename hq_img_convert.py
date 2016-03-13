#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Function and command line utility to convert "raw" game images
"""

import argparse
import re
import sys

import libs


# CONSTANTS
#=======================================================================================================================
u_PROG_NAME = u'HQ IMAGE CONVERT'
u_PROG_VER = u'v2016.02.21'

o_CWD = libs.files.get_cwd()
o_IMG_CONV_DEF_CFG = libs.imagemagick.ImgConvCfgGenerator()


# HELPER FUNCTIONS
#=======================================================================================================================
def _get_cmd_options():
    """
    Function to process the command-line options.

    :return: TODO: A dictionary with different options.
    """

    # Variable preparation
    u_platforms = u''
    for o_platform in libs.cons.do_platforms.itervalues():
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
                              choices=libs.imagemagick.tu_CNV_MODES,
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
                              choices=(None,) + libs.imagemagick.tu_VALID_EXTS,
                              help='Change dst extension. i.e. "-e jpg" will create a jpg image. If you are converting '
                                   'a single file, you can simply define the extension by the output file name. For '
                                   'example "output.png" will produce a png file. When you are converting a whole '
                                   'directory of images, the output file name for each of the files will be the source'
                                   'file name; so the parameter "-e" allows you to change the extension.')
    o_arg_parser.add_argument('-f',
                              action='store',
                              default='0,0',
                              help='Focus point relative coordinates x,y. i.e. "-f 0.0,1.0" would be bottom-left '
                                   'corner.')
    o_arg_parser.add_argument('-b',
                              action='store',
                              default='#808080ff',
                              help='Background hex color in RGBA format. i.e. "-b ff000080".')
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
    if u_mode in libs.imagemagick.tu_CNV_MODES:
        u_mode_found = libs.cons.u_OK_TEXT
    else:
        i_cmd_errors += 1
        u_mode_found = libs.cons.u_ER_TEXT
    u_output += u'   MODE: %s %s\n' % (u_mode_found, u_mode)

    # Source file or dir
    #-------------------
    u_src = o_args.src
    o_src = libs.files.FilePath(u_src)
    o_src = o_src.absfile()

    if o_src.exists():
        if o_src.is_dir():
            u_type = u'D'
        else:
            u_type = u'F'

        u_msg = u'%s %s %s' % (libs.cons.u_OK_TEXT, u_type, o_src.u_path)
    else:
        i_cmd_errors += 1
        u_msg = u'%s ? %s' % (libs.cons.u_ER_TEXT, o_src.u_path)

    u_output += u'    SRC: %s\n' % u_msg

    # Destination file or dir
    #------------------------
    u_dst = o_args.dst
    o_dst = libs.files.FilePath(u_dst)
    o_dst = o_dst.absfile()

    if o_src.is_file() and o_dst.root_exists() and (not o_dst.is_dir()):
        u_msg = u'%s F %s' % (libs.cons.u_OK_TEXT, o_dst.u_path)
    elif o_src.is_dir() and o_dst.is_dir():
        u_msg = u'%s D %s' % (libs.cons.u_OK_TEXT, o_dst.u_path)
    else:
        i_cmd_errors += 1
        # Error messages with advise about how to solve it
        if o_src.is_file() and o_dst.is_dir():
            u_msg = u'%s D %s - DST can\'t be a dir when SRC is a file' % (libs.cons.u_ER_TEXT, o_dst.u_path)
        elif not o_dst.root_exists():
            u_msg = u'%s %s - can\'t find %s' % (libs.cons.u_ER_TEXT, o_dst.u_path, o_dst.u_root)

        # Generic error message
        else:
            u_msg = u'%s ? %s' % (libs.cons.u_ER_TEXT, o_dst.u_path)

    u_output += u'    DST: %s\n' % u_msg

    # Graphical configuration
    #========================
    o_graph_cfg = libs.imagemagick.ImgConvCfgGenerator()

    # Aspect ratio
    #-------------
    u_aspect = o_args.a.strip()

    if u_aspect is not None:
        if u_aspect in libs.cons.do_platforms:
            o_graph_cfg.tf_aspect = u_aspect
            o_platform = libs.cons.do_platforms[u_aspect]
            u_msg = u'%s %s (%.2f, %.2f)' % (libs.cons.u_OK_TEXT, u_aspect, o_platform.i_WIDTH, o_platform.i_HEIGHT)
        else:
            try:
                o_aspect = libs.geom.Coord(pu_string=u_aspect)
                o_graph_cfg.tf_aspect = (o_aspect.f_x, o_aspect.f_y)
                if o_aspect.f_x and o_aspect.f_y != 0:
                    u_msg = u'%s %.2f:%.2f' % (libs.cons.u_OK_TEXT, o_aspect.f_x, o_aspect.f_y)
                else:
                    u_msg = u'%s %.2f:%.2f  (Any 0 => automatic)' % (libs.cons.u_OK_TEXT, o_aspect.f_x, o_aspect.f_y)
            except ValueError:
                    u_msg = u'%s %s - Unknown aspect format' % (libs.cons.u_ER_TEXT, u_aspect)

    elif u_aspect is None:
        u_msg = u'%s automatic (same as source image)' % libs.cons.u_OK_TEXT

    else:
        i_cmd_errors += 1
        u_msg = u'%s %s - Unknown aspect format' % (libs.cons.u_ER_TEXT, u_aspect)

    u_output += u'\n  G_ASP: %s\n' % u_msg

    # Background color
    #-----------------
    u_bgcolor = o_args.b.strip()

    if u_bgcolor.lower() == _parse_color(u_bgcolor):
        o_graph_cfg.u_bgcolor = u_bgcolor
        u_msg = u'%s %s' % (libs.cons.u_OK_TEXT, u_bgcolor)
    else:
        i_cmd_errors += 1
        u_msg = u'%s %s - Unknown color format' % (libs.cons.u_ER_TEXT, u_bgcolor)

    u_output += u'  G_BGC: %s\n' % u_msg

    # Extension
    #----------
    u_ext = o_args.e
    if u_ext:
        o_graph_cfg.u_format = u_ext
        u_msg = u'%s %s' % (libs.cons.u_OK_TEXT, u_ext)
    else:
        u_msg = u'%s automatic' % libs.cons.u_OK_TEXT

    u_output += u'  G_EXT: %s\n' % u_msg

    # Focus
    #------
    u_focus = o_args.f.strip()

    try:
        o_focus = libs.geom.Coord(pu_string=u_focus)
        o_graph_cfg.tf_focus = (o_focus.f_x, o_focus.f_y, o_focus.f_dx, o_focus.f_dy)
        u_msg = u'%s %.2f±%.2f, %.2f±%.2f' % (libs.cons.u_OK_TEXT, o_focus.f_x, o_focus.f_dx, o_focus.f_y, o_focus.f_dy)
    except ValueError:
        i_cmd_errors += 1
        u_msg = u'%s %s - Unknown format' % (libs.cons.u_ER_TEXT, u_focus)

    u_output += u'  G_FOC: %s\n' % u_msg

    # Rotation
    #---------
    u_rotation = o_args.r.strip()

    try:
        o_rotation = libs.geom.Coord(pu_string=u_rotation)
        o_graph_cfg.tf_rotation = (o_rotation.f_x, o_rotation.f_dx)
        u_msg = u'%s %.2f±%.2fº' % (libs.cons.u_OK_TEXT, o_rotation.f_x, o_rotation.f_dx)
    except ValueError:
        i_cmd_errors += 1
        u_msg = u'%s %s - Unknown format' % (libs.cons.u_ER_TEXT, u_rotation)

    u_output += u'  G_ROT: %s\n' % u_msg

    # Size
    #-----
    u_size = o_args.s.strip()

    try:
        o_size = libs.geom.Coord(pu_string=u_size)
        o_graph_cfg.ti_size = (int(o_size.f_x), int(o_size.f_y), int(o_size.f_dx), int(o_size.f_dy))
        if (o_size.f_x >= 1) and (o_size.f_y >= 1):
            u_msg = u'%s %i±%i x %i±%i px' % (libs.cons.u_OK_TEXT, o_size.f_x, o_size.f_dx, o_size.f_y, o_size.f_dy)
        else:
            i_cmd_errors += 1
            u_msg = u'%s %ix%i - Both sizes need to be bigger than 1' % (libs.cons.u_ER_TEXT, o_size.f_x, o_size.f_y)
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
                'o_src': o_src,
                'o_dst': o_dst,
                'o_cfg': o_graph_cfg}


def _parse_color(pu_string):
    """
    Function to check if a string contains a valid RGB(A) hexadecimal color.
    :return: True/False
    """
    u_pattern = r'([0-9a-f]{8})|([0-9a-f]{6})'
    o_match = re.search(u_pattern, pu_string, flags=0)
    return o_match.group()


def img_convert(pu_mode=None, po_src_file=None, po_dst_file=None, po_cfg=o_IMG_CONV_DEF_CFG):

    # I think that for code organization it'd be a better idea to make this function just a wrapper of a function
    # located in imagemagick. That way, I could add the available transformations (frame, sphere, magcover...) list in
    # there. So, every time I need to define a new transformation, I'd just need to modify that file.

    o_output = libs.imagemagick.cnv_img(pu_mode, po_src_file, po_dst_file, po_cfg)

    return o_output

# Main Code
#=======================================================================================================================
if __name__ == '__main__':
    print libs.strings.hq_title(u_PROG_NAME, u_PROG_VER)

    dx_cmd_args = _get_cmd_options()

    # If src/dst and directories, the list of files inside src dir will be obtained and processed.
    lo_src_files = []
    lo_dst_files = []

    if dx_cmd_args['o_src'].is_file():
        lo_src_files.append(dx_cmd_args['o_src'])
        lo_dst_files.append(dx_cmd_args['o_dst'])
    else:
        for o_src_file in dx_cmd_args['o_src'].content():
            if o_src_file.is_file():
                lo_src_files.append(o_src_file)

                # If src and dst are directories, the final dst files will be called like the source files but they will
                # have a different root directory
                o_dst_file = libs.files.FilePath(dx_cmd_args['o_dst'].u_path, o_src_file.u_file)
                lo_dst_files.append(o_dst_file)

    # Image processing
    print 'Processing'
    print '-----------------------------------------'

    i_image = 0

    for o_src_file, o_dst_file in zip(lo_src_files, lo_dst_files):

        i_image += 1

        u_output = u'WORKING: %s [%i/%i] %s' % (libs.cons.u_PR_TEXT, i_image, len(lo_src_files), o_src_file.u_path)
        print u_output.encode('utf8'),

        o_transformation_result = img_convert(pu_mode=dx_cmd_args['u_mode'],
                                              po_src_file=o_src_file,
                                              po_dst_file=o_dst_file,
                                              po_cfg=dx_cmd_args['o_cfg'])

        if o_transformation_result:
            u_result_text = libs.cons.u_OK_TEXT
        else:
            u_result_text = libs.cons.u_ER_TEXT

        u_output = u'\rCREATED: %s [%i/%i] %s' % (u_result_text, i_image,
                                                  len(lo_src_files), o_transformation_result.o_path.u_path)
        print u_output.encode('utf8')