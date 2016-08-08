#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command line utility and python library to convert from and to different front-end favourites lists.
"""

import argparse
import codecs
import sys

from libs import cons
from libs import files
from libs import lst_cnv
from libs import roms
from libs import strings

# CONSTANTS
#=======================================================================================================================
u_PROG_NAME = u'HQ LIST CONVERT'
u_PROG_VER = u'v2015.10.11'

tu_SRC_FORMATS = (u'dat', u'mala', u'mamewah', u'hqtools', u'wahcade')
tu_DST_FORMATS = (u'mala', u'mamewah', u'hqtools', u'wahcade')

lu_VALID_MODES = []
for u_format_1 in tu_SRC_FORMATS:
    for u_format_2 in tu_DST_FORMATS:
        lu_VALID_MODES.append(u'%s,%s' % (u_format_1, u_format_2))


# HELPER FUNCTIONS
#=======================================================================================================================
def _get_cmd_options():
    """
    Function to process the command-line options.

    :return: TODO: A dictionary with different options.
    """

    # TODO: handle files as relative paths if needed

    o_arg_parser = argparse.ArgumentParser(description='A command line utility to copy and hq_copy files between '
                                                       'different formats using a ROM dat file.')
    o_arg_parser.add_argument('mode',
                              action='store',
                              choices=lu_VALID_MODES,
                              metavar='[src_format],[dst_format]',
                              help='Conversion format. "src_format" is the source format and "dst_format" the '
                                   'destination format. Notice they are joint using a comma WITHOUT any extra space.')
    o_arg_parser.add_argument('files',
                              action='store',
                              nargs='+',
                              help='Source/destination lists to convert i.e. "/home/carl/list_1.lst" or "/home/ann/favourites.txt"')

    o_arg_parser.add_argument('-d',
                              action='store',
                              help='Source dat file. i.e. "/home/john/snes.dat"')

    o_arg_parser.add_argument('-l',
                              action='store',
                              default=None,
                              help='Log file (short)')

    o_arg_parser.add_argument('-L',
                              action='store',
                              default=None,
                              help='Log file (long)')

    # Parsing and validation of the parameters
    i_errors = 0
    u_text_output = u''

    o_args = o_arg_parser.parse_args()

    # Validating operation mode
    #--------------------------
    u_src_format = o_args.mode.partition(u',')[0].decode('utf8')
    u_dst_format = o_args.mode.partition(u',')[2].decode('utf8')

    u_text_output += u'  MODE: %s %s -> %s\n' % (cons.u_OK_TEXT,
                                                 u_src_format,
                                                 u_dst_format)

    # Validating dat file
    #--------------------
    u_dat_path = o_args.d.decode('utf8')
    o_dat_path = files.FilePath(u_dat_path)
    if o_dat_path.is_file():
        u_dat_found = cons.u_OK_TEXT
    else:
        u_dat_found = cons.u_ER_TEXT
        i_errors += 1

    u_text_output += u'   DAT: %s %s\n' % (u_dat_found, u_dat_path)

    # [1/4] Source/Destination files pre-validation
    #-----------------------------------------------
    u_src_lst_path = o_args.files[0].decode('utf8')
    try:
        u_dst_lst_path = o_args.files[1].decode('utf8')
    except IndexError:
        u_dst_lst_path = None

    if u_src_lst_path:
        o_src_lst_fp = files.FilePath(u_src_lst_path)
    else:
        o_src_lst_fp = None

    if u_dst_lst_path:
        o_dst_lst_fp = files.FilePath(u_dst_lst_path)
    else:
        o_dst_lst_fp = None

    # in dat mode, the user directly specifies the destination and the source file is the same dat file.
    if u_src_format == u'dat':
        o_dst_lst_fp = o_src_lst_fp
        u_dst_lst_path = u_src_lst_path

        o_src_lst_fp = o_dat_path

    # [2/4] Source file validation
    #-----------------------------
    if o_src_lst_fp.is_file():
        u_src_found = cons.u_OK_TEXT
    else:
        u_src_found = cons.u_ER_TEXT
        i_errors += 1

    if u_src_format == 'dat':
        u_extra = u' <-- automatically selected'
    else:
        u_extra = u''

    u_text_output += u'   SRC: %s %s %s\n' % (u_src_found, o_src_lst_fp.u_path, u_extra)

    # [3/4] Destination file validation
    #----------------------------------
    if o_dst_lst_fp and o_dst_lst_fp.root_exists():
        u_dst_root_found = cons.u_OK_TEXT
    else:
        u_dst_root_found = cons.u_ER_TEXT
        i_errors += 1

    u_text_output += u'   DST: %s %s\n' % (u_dst_root_found, u_dst_lst_path)

    # [4/4] Log file
    #---------------
    i_log = 0
    u_log_short = o_args.l
    u_log_full = o_args.L
    o_log_fp = None

    if u_log_short and u_log_full:
        i_errors += 1
        u_log_file = u'%s / %s' % (u_log_short, u_log_full)
        u_msg = u'<-- Select just ONE: long or short log file'
        u_log_file_success = cons.u_ER_TEXT
    elif not u_log_short and not u_log_full:
        o_log_fp = None
        i_log = 0
        u_msg = u''
        u_log_file_success = cons.u_ER_TEXT
        u_log_file = u''
    else:
        if u_log_short:
            u_log_file = u_log_short
            i_log = 1
            u_msg = u'(short log)'
        else:
            u_log_file = u_log_full
            i_log = 2
            u_msg = u'(full log)'

        o_log_fp = files.FilePath(u_log_file)

        if o_log_fp.root_exists():
            u_log_file_success = cons.u_OK_TEXT
        else:
            i_errors += 1
            u_log_file_success = cons.u_ER_TEXT

    u_text_output += u'   LOG: %s %s %s\n' % (u_log_file_success, u_log_file, u_msg)

    if i_errors:
        u_text_output += u'\n%i errors found. Please, fix them and run the program again.' % i_errors

    print u_text_output.encode('utf8', 'strict')

    if i_errors:
        sys.exit()

    return {'o_dat_file': o_dat_path,
            'o_src_list': o_src_lst_fp,
            'o_dst_list': o_dst_lst_fp,
            'u_src_format': u_src_format,
            'u_dst_format': u_dst_format,
            'o_log_fp': o_log_fp,
            'i_log': i_log,
            'o_log': o_log_fp}


# MAIN FUNCTION
#=======================================================================================================================
def lconvert(pu_src_fmt=None, pu_dst_fmt=None, pu_src_file=None, pu_dst_file=None, po_dat=None, pb_print=False,
             pi_log=0, pu_log=None):
    """
    This function is just a wrapper for the real function lst_cnv.lconvert
    """
    return lst_cnv.lconvert(pu_src_fmt=pu_src_fmt,
                            pu_dst_fmt=pu_dst_fmt,
                            pu_src_file=pu_src_file,
                            pu_dst_file=pu_dst_file,
                            po_dat=po_dat,
                            pb_print=pb_print,
                            pi_log=pi_log,
                            pu_log=pu_log)


# EXECUTION AS COMMAND LINE PROGRAM
#=======================================================================================================================
if __name__ == '__main__':
    print strings.hq_title(u_PROG_NAME, u_PROG_VER)

    dx_cmd_params = _get_cmd_options()

    if dx_cmd_params['o_dat_file'].u_path:
        o_dat = roms.RomSetContainer(dx_cmd_params['o_dat_file'].u_path)

    else:
        # TODO: Why allowing not to use DAT? Not sure about it now.
        o_dat = None

    if dx_cmd_params['o_log']:
        u_log = dx_cmd_params['o_log'].u_path
    else:
        u_log = None

    dx_result = lconvert(pu_src_fmt=dx_cmd_params['u_src_format'],
                         pu_dst_fmt=dx_cmd_params['u_dst_format'],
                         pu_src_file=dx_cmd_params['o_src_list'].u_path,
                         pu_dst_file=dx_cmd_params['o_dst_list'].u_path,
                         po_dat=o_dat,
                         pb_print=True,
                         pi_log=dx_cmd_params['i_log'],
                         pu_log=u_log)


