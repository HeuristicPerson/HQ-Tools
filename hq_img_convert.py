#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Function and command line utility to convert "raw" game images
"""

import argparse
import sys

import libs


# CONSTANTS
#=======================================================================================================================
u_PROG_NAME = u'HQ IMAGE CONVERT'
u_PROG_VER = u'v2016.02.21'

tu_MODES = ('frame',)
tu_GRABS = ('top-left', 'top', 'top-right', 'left', 'center', 'right', 'bottom-left', 'bottom', 'bottom-right')

o_CWD = libs.files.get_cwd()
o_IMG_CONV_DEF_CFG = libs.imagemagick.ImgConvertRandomCfg()


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

    o_arg_parser = argparse.ArgumentParser(description='A command line utility to convert and "enrich" video-game '
                                                       'screenshots.')
    o_arg_parser.add_argument('mode',
                              action='store',
                              choices=tu_MODES,
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
                              help='Aspect ratio or platform alias. i.e. "16,9" or "nes". Valid platform alias are: %s.'
                                   % u_platforms)
    o_arg_parser.add_argument('-g',
                              action='store',
                              default='center',
                              choices=tu_GRABS,
                              help='Grab point. .i.e.')
    o_arg_parser.add_argument('-o',
                              action='store',
                              default='0,0',
                              help='Image offset . i.e. "20+5,10+3"')
    o_arg_parser.add_argument('-r',
                              action='store',
                              default='0+0',
                              help='Image rotation. i.e. "15+5" will be a rotation of 15 degrees anticlockwise plus a '
                                   'random rotation of +/- 5 degrees.')
    o_arg_parser.add_argument('-s',
                              action='store',
                              default='320,240',
                              help='Image size. i.e. "320,240". This is the maximum image size. Images will be '
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
    if u_mode in tu_MODES:
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

    # Aspect ratio
    #-------------
    u_aspect = o_args.a
    o_aspect = None

    if u_aspect is not None and libs.geom.is_valid_coord_string(u_aspect):
        o_aspect = libs.geom.Coord()
        o_aspect.from_str(u_aspect)
        if o_aspect.f_x and o_aspect.f_y != 0:
            u_msg = u'%s %i:%i' % (libs.cons.u_OK_TEXT, o_aspect.f_x, o_aspect.f_y)
        else:
            u_msg = u'%s %i:%i  (Any 0 => automatic)' % (libs.cons.u_OK_TEXT, o_aspect.f_x, o_aspect.f_y)
            #todo: Add code to get aspect ratio from shortcuts with console alias. i.e. "snes" -> 4:3
    elif u_aspect is None:
        u_msg = u'%s automatic (same as source image)' % libs.cons.u_OK_TEXT
    else:
        i_cmd_errors += 1
        u_msg = u'%s %s' % (libs.cons.u_ER_TEXT, u_aspect)

    u_output += u'\n  G_ASP: %s\n' % u_msg

    # Rotation
    #---------
    u_rotation = o_args.r
    o_rotation = None

    if libs.geom.is_valid_coord_string(u_rotation):
        o_rotation = libs.geom.Coord()
        o_rotation.from_str(u_rotation)
        u_msg = u'%s %s±%sº' % (libs.cons.u_OK_TEXT, o_rotation.f_x, o_rotation.f_dx)
    else:
        i_cmd_errors += 1
        u_msg = u'%s %s - Unknown format' % (libs.cons.u_ER_TEXT, u_rotation)

    u_output += u'  G_ROT: %s\n' % u_msg

    # Size
    #-----
    u_size = o_args.s
    o_size = None

    if libs.geom.is_valid_coord_string(u_size):
        o_size = libs.geom.Coord()
        o_size.from_str(u_size)
        if (o_size.f_x >= 1) and (o_size.f_y >= 1):
            u_msg = u'%s %i±%i x %i±%i px' % (libs.cons.u_OK_TEXT, o_size.f_x, o_size.f_dx, o_size.f_y, o_size.f_dy)
        else:
            i_cmd_errors += 1
            u_msg = u'%s %ix%i - Both sizes need to be bigger than 1' % (libs.cons.u_ER_TEXT, o_size.f_x, o_size.f_y)
    else:
        i_cmd_errors += 1
        u_msg = u'%s %s - '

    u_output += u'  G_SIZ: %s\n' % u_msg

    # Grab
    #-----
    u_grab = o_args.g
    u_output += u'  G_GRA: %s %s\n' % (libs.cons.u_OK_TEXT, u_grab)

    # Offset
    #-------
    u_offset = o_args.o
    o_offset = None
    if libs.geom.is_valid_coord_string(u_offset):
        o_offset = libs.geom.Coord()
        o_offset.from_str(u_offset)
        u_msg = u'%s %i±%i,%i±%i px\n' % (libs.cons.u_OK_TEXT, o_offset.f_x, o_offset.f_dx, o_offset.f_y, o_offset.f_dy)
    else:
        i_cmd_errors += 1
        u_msg = u'%s %s' % (libs.cons.u_ER_TEXT, u_offset)

    u_output += u'  G_OFF: %s' % u_msg

    # Preparing the graphical configuration object
    #---------------------------------------------
    o_graph_cfg = libs.imagemagick.ImgConvertRandomCfg()
    if o_aspect:
        o_graph_cfg.ti_aspect = (int(o_aspect.f_x), int(o_aspect.f_y))
    if o_offset:
        o_graph_cfg.ti_offset = (int(o_offset.f_x), int(o_offset.f_y), int(o_offset.f_dx), int(o_offset.f_dy))
    if o_rotation:
        o_graph_cfg.tf_rotation = (o_rotation.f_x, o_rotation.f_dx)
    if o_size:
        o_graph_cfg.ti_size = (int(o_size.f_x), int(o_size.f_y), int(o_size.f_dx), int(o_size.f_dy))
    if u_grab:
        o_graph_cfg.u_grab = u_grab

    print u_output

    if i_cmd_errors:
        print u'%i error(s) found. Solve them and try launching the program again.' % i_cmd_errors
        sys.exit()
    else:
        return {'u_mode': u_mode,
                'o_src': o_src,
                'o_dst': o_dst,
                'o_cfg': o_graph_cfg}


def img_convert(pu_mode=None, pu_src_file=None, pu_dst_file=None, po_cfg=o_IMG_CONV_DEF_CFG):

    # I think that for code organization it'd be a better idea to make this function just a wrapper of a function
    # located in imagemagick. That way, I could add the available transformations (frame, sphere, magcover...) list in
    # there. So, everytime I neede to define a new transformation, I'd just need to modify that file.
    o_output = libs.imagemagick.cnv_img(pu_mode, pu_src_file, pu_dst_file, po_cfg)
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

                o_dst_file = libs.files.FilePath(dx_cmd_args['o_dst'].u_path, o_src_file.u_file)
                lo_dst_files.append(o_dst_file)

    # Image processing
    for o_src_file, o_dst_file in zip(lo_src_files, lo_dst_files):

        print 'WRITTEN: %s' % o_dst_file.u_path

        img_convert(pu_mode=dx_cmd_args['u_mode'],
                    pu_src_file=o_src_file.u_path,
                    pu_dst_file=o_dst_file.u_path,
                    po_cfg=dx_cmd_args['o_cfg'])
