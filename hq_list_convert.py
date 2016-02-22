#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command line utility and python library to convert from and to different front-end favourites lists.
"""

import argparse
import codecs
import sys

import libs
from hqlib import romdats

# CONSTANTS
#=======================================================================================================================
u_PROG_NAME = u'HQ LIST CONVERT'
u_PROG_VER = u'v2015.10.11'

tu_FORMATS = (u'mala', u'mamewah', u'hqtools', u'wahcade')

lu_VALID_MODES = []
for u_format_1 in tu_FORMATS:
    for u_format_2 in tu_FORMATS:
        lu_VALID_MODES.append(u'%s,%s' % (u_format_1, u_format_2))


# HELPER FUNCTIONS
#=======================================================================================================================
def _get_cmd_options():
    """
    Function to process the command-line options.

    :return: TODO: A dictionary with different options.
    """

    o_arg_parser = argparse.ArgumentParser(description='A command line utility to copy and hq_copy files between '
                                                       'different formats using a ROM dat file.')
    o_arg_parser.add_argument('mode',
                              action='store',
                              choices=lu_VALID_MODES,
                              metavar='[src_format],[dst_format]',
                              help='Conversion format. "src_format" is the source format and "dst_format" the '
                                   'destination format. Notice they are joint using a comma WITHOUT any extra space.')
    o_arg_parser.add_argument('source',
                              action='store',
                              help='Source directory or file. i.e. "/home/carl/pictures" or "/home/ann/145879ab.png"')
    o_arg_parser.add_argument('destination',
                              action='store',
                              help='Destination directory. i.e. "/home/cecil/output_pics"')
    o_arg_parser.add_argument('-d',
                              action='store',
                              help='Source dat file. i.e. "/home/john/snes.dat"')

    # Parsing and validation of the parameters
    i_errors = 0
    u_text_output = u''

    o_args = o_arg_parser.parse_args()

    # Validating operation mode
    u_src_format = o_args.mode.partition(u',')[0]
    u_dst_format = o_args.mode.partition(u',')[2]

    u_extra_src_mode = u''
    u_extra_dst_mode = u''

    u_text_output += u'  MODE: %s %s -> %s\n' % (libs.cons.u_OK_TEXT,
                                                 u_src_format,
                                                 u_dst_format)

    # Validating dat file
    u_dat_path = o_args.d.decode('utf8')
    o_dat_path = libs.files.FilePath(u_dat_path)
    if o_dat_path.is_file():
        u_dat_found = libs.cons.u_OK_TEXT
    else:
        u_dat_found = libs.cons.u_ER_TEXT
        i_errors += 1

    u_text_output += u'   DAT: %s %s\n' % (u_dat_found, u_dat_path)

    # Validating source path
    u_src_lst_path = o_args.source.decode('utf8')
    o_src_lst_path = libs.files.FilePath(u_src_lst_path)
    if o_src_lst_path.is_file():
        u_src_found = libs.cons.u_OK_TEXT
    else:
        u_src_found = libs.cons.u_ER_TEXT
        i_errors += 1

    u_text_output += u'   SRC: %s %s\n' % (u_src_found, u_src_lst_path)

    # Validating destination path
    u_dst_lst = o_args.destination.decode('utf8')
    o_dst_lst = libs.files.FilePath(u_dst_lst)

    if o_dst_lst.root_exists():
        u_dst_root_found = libs.cons.u_OK_TEXT
    else:
        u_dst_root_found = libs.cons.u_ER_TEXT
        i_errors += 1

    u_text_output += u'   DST: %s %s\n' % (u_dst_root_found, u_dst_lst)

    if i_errors:
        u_text_output += u'\n%i errors found. Please, fix them and run the program again.' % i_errors

    print u_text_output.encode('utf8', 'strict')

    if i_errors:
        sys.exit()

    return {'o_dat_file': o_dat_path,
            'o_src_list': o_src_lst_path,
            'o_dst_list': o_dst_lst,
            'u_src_format': u_src_format,
            'u_dst_format': u_dst_format}


def _list_parse(u_list_file, u_format, o_dat):
    """
    Function to parse a list of favorites (file) and generate a list with the game objects of them.

    :param u_list_file:
    :param o_dat:
    :return:
    """

    o_list_file = codecs.open(u_list_file, 'r', 'utf8')

    if u_format == u'mala':
        lo_games = _list_parse_mala(o_list_file, o_dat)
    elif u_format == u'mamewah':
        lo_games = _list_parse_mamewah(o_list_file, o_dat)
    elif u_format == u'wahcade':
        lo_games = _list_parse_wahcade(o_list_file, o_dat)
    else:
        raise Exception('ERROR: Unknown list format "%s"' % u_format)

    o_list_file.close()

    return lo_games


def _list_parse_wahcade(o_list_file, o_dat):
    """
    Function to parse wahcade favorite lists

    :param o_list_file: Favorite list file object.
    :param o_dat: Dat file object already parsed using hqlib
    :return: A list of game objects
    """

    i_lines_per_game = 12

    while True:
        lu_lines = libs.files.read_nlines(o_list_file, i_lines_per_game)

        if len(lu_lines) < i_lines_per_game:
            break
        else:
            #print lu_lines
            u_rom_name = lu_lines[0]
            print u_rom_name.strip()


# MAIN FUNCTION
#=======================================================================================================================
def hq_lconvert(u_src_fmt=None, u_dst_fmt=None, u_src_file=None, u_dst_file=None, u_dat=None, b_print=False):
    """
    Function to convert list files between different front-end formats.
    :param u_src_fmt:
    :param u_dst_fmt:
    :param u_src_file:
    :param u_dst_file:
    :param b_print:
    :return:
    """

    # Parameter validation

    lu_games = _list_parse(u_src_file, u_src_fmt, o_dat)

    return 'foo'


# EXECUTION AS COMMAND LINE PROGRAM
#=======================================================================================================================
if __name__ == '__main__':
    print libs.strings.hq_title(u_PROG_NAME, u_PROG_VER)

    dx_cmd_params = _get_cmd_options()

    if dx_cmd_params['o_dat_file'].u_path:
        o_dat = romdats.GameContainer(dx_cmd_params['o_dat_file'].u_path)
    else:
        o_dat = None

    print o_dat

    dx_result = hq_lconvert(u_src_fmt=dx_cmd_params['u_src_format'],
                            u_dst_fmt=dx_cmd_params['u_dst_format'],
                            u_src_file=dx_cmd_params['o_src_list'].u_path)


