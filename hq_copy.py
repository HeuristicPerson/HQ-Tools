#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command line utility and python library to copy files from folder A to B translating the names between crc32, md5, sha1,
and title schemes. For hashing names (crc32, md5, sha1), dirty or clean hashes can be used. Dirty means all the files
included in the full game are used to obtain the global hash (i.e. for a CD game it would be .cue and .bin files). In
Clean mode, meta-data files not actually present in the real disc (.cue files) wouldn't be taken into account.
"""

import argparse
import os         # I use os only to remove files so maybe it's a waste of memory
import re
import shutil
import sys

from libs import cons
from libs import files
from libs import strings
from libs import time

from libs.roms import RomSetContainer


# CLASSES
#=======================================================================================================================
class SingleMode:
    def __init__(self, pu_desc=u'', ps_field=''):
        self.u_desc = pu_desc
        self.u_field = ps_field


# CONSTANTS
#=======================================================================================================================
du_HASH_MODE = {'': u'', 'c': u'clean ', 'd': u'dirty'}
du_HASH = {'C': u'crc32', 'M': u'md5', 'S': u'sha1', 'T': u'description'}
u_PROG_NAME = u'HQ COPY'
u_PROG_VER = u'v2015.10.11'

lu_VALID_MODES = []
do_valid_single_modes = {'cC': SingleMode(pu_desc=u'clean CRC32', ps_field='u_ccrc32'),
                         'cM': SingleMode(pu_desc=u'clean MD5', ps_field='u_cmd5'),
                         'cS': SingleMode(pu_desc=u'clean SHA1', ps_field='u_csha1'),
                         'dC': SingleMode(pu_desc=u'dirty CRC32', ps_field='u_dcrc32'),
                         'dM': SingleMode(pu_desc=u'dirty MD5', ps_field='u_dmd5'),
                         'dS': SingleMode(pu_desc=u'dirty SHA1', ps_field='u_dsha1'),
                         'T': SingleMode(pu_desc=u'Title', ps_field='u_desc')}
lu_valid_single_modes = sorted(do_valid_single_modes.keys(), key=lambda u_element: u_element.lower())
#lu_valid_single_modes.sort()

for u_head in do_valid_single_modes.keys():
    for u_tail in do_valid_single_modes.keys():
        if u_head != u_tail:
            lu_VALID_MODES.append('%s%s' % (u_head, u_tail))


# HELPER FUNCTIONS
#=======================================================================================================================
def _get_cmd_options():
    """
    Function to process the command-line options.

    :return: TODO: A dictionary with different options.
    """

    o_arg_parser = argparse.ArgumentParser(description='A command line utility to copy and rename files between '
                                                       'different formats using a ROM dat file.')
    o_arg_parser.add_argument('-s',
                              action='store_true',
                              help='Simulation mode; files won\'t be copied.')
    o_arg_parser.add_argument('mode',
                              action='store',
                              choices=lu_VALID_MODES,
                              metavar='2x[%s]' % u','.join(lu_valid_single_modes),
                              help='Renaming mode, source and destination. First two letters (or one for title) '
                                   'specify the source format: clean CRC32 (cC), clean MD5 (cM), clean SHA1 (cS), dirty'
                                   'CRC32 (dC), dirty MD5 (dM), dirty SHA1 (dS), or title (T). Second two letters '
                                   'indicate the destination format in the same format i.e. "dCT" will use dirty '
                                   'hashes to copy files from dirty CRC32 naming scheme to real Title.')
    o_arg_parser.add_argument('dat',
                              action='store',
                              help='Source dat file. i.e. "/home/john/snes.dat"')
    o_arg_parser.add_argument('source',
                              action='store',
                              help='Source directory or file. i.e. "/home/carl/pictures" or "/home/ann/145879ab.png"')
    o_arg_parser.add_argument('destination',
                              action='store',
                              help='Destination directory. i.e. "/home/cecil/output_pics"')
    o_arg_parser.add_argument('-r',
                              action='store',
                              help='Regex pattern and group. i.e. "(.*),0". Everything BEFORE the comma is the '
                                   'pattern and everything AFTER the comma is the group to capture.')

    # Parsing and validation of the parameters
    i_errors = 0
    u_text_output = u''

    o_args = o_arg_parser.parse_args()

    # Validating simulation mode
    b_simulation = o_args.s
    if b_simulation:
        u_text_output += '   SIM: %s simulation is ON, files won\'t be copied\n' % cons.u_OK_TEXT

    # Validating rename mode
    o_matches = re.match(r'([dc]?[CMST])([dc]?[CMST])', o_args.mode)

    u_src_format = o_matches.group(1)
    u_dst_format = o_matches.group(2)

    u_text_output += u'  MODE: %s %s (%s) -> %s (%s)\n' % (cons.u_OK_TEXT,
                                                           u_src_format,
                                                           do_valid_single_modes[u_src_format].u_desc,
                                                           u_dst_format,
                                                           do_valid_single_modes[u_dst_format].u_desc)

    # Validating dat file
    u_dat_file = o_args.dat.decode('utf8')
    o_dat_file_fp = files.FilePath(u_dat_file)
    if o_dat_file_fp.is_file():
        u_dat_found = cons.u_OK_TEXT
    else:
        u_dat_found = cons.u_ER_TEXT
        i_errors += 1

    u_text_output += u'   DAT: %s %s\n' % (u_dat_found, u_dat_file)

    # Validating source path
    u_src_path = o_args.source.decode('utf8')
    o_src_fp = files.FilePath(u_src_path)
    if o_src_fp.exists():
        u_src_found = cons.u_OK_TEXT
    else:
        u_src_found = cons.u_ER_TEXT
        i_errors += 1

    u_text_output += u'   SRC: %s %s\n' % (u_src_found, u_src_path)

    # Validating destination path
    u_dst_path = o_args.destination.decode('utf8')
    o_dst_fp = files.FilePath(u_dst_path)
    if o_dst_fp.is_dir():
        u_dst_found = cons.u_OK_TEXT
    else:
        u_dst_found = cons.u_ER_TEXT
        i_errors += 1

    u_text_output += u'   DST: %s %s\n' % (u_dst_found, u_dst_path)

    # Validating regex mode
    u_regex_data = o_args.r

    u_regex = None
    i_regex_group = None
    if u_regex_data:
        u_regex_data = u_regex_data.decode('utf8')

        try:
            u_regex = u_regex_data.rpartition(u',')[0]
            i_regex_group = int(u_regex_data.rpartition(u',')[2])
            u_text_output += u'  REXP: %s #%i in "%s"\n' % (cons.u_OK_TEXT, i_regex_group, u_regex)

        except (ValueError, IndexError):
            u_text_output += u'  REXP: %s Wrong regular expression data "%s"\n' % (cons.u_ER_TEXT, u_regex_data)
            i_errors += 1

    if i_errors:
        u_text_output += u'\n%i errors found. Please, fix them and run the program again.' % i_errors

    print u_text_output.encode('utf8', 'strict')

    if i_errors:
        sys.exit()

    return {'b_simulation': b_simulation,
            'u_dat_file': u_dat_file,
            'u_src_path': u_src_path,
            'u_dst_path': u_dst_path,
            'u_src_format': u_src_format,
            'u_dst_format': u_dst_format,
            'u_regex_pattern': u_regex,
            'i_regex_group': i_regex_group}


def _regex_catcher(u_text, u_pattern=None, i_group=None):
    """
    Function to capture a text inside a longer string using regex pattern.

    :param u_text: Text where we are looking for patterns. i.e. 'I have a dog and a cat'
    :param u_pattern: Regex pattern to search. i.e. '(d.g) (and)'
    :param i_group: Group to catch. i.e. 1

    :return: The captured text. In the above example it would be 1st group, so the output would be 'dog'
    """

    o_pattern = re.compile(u_pattern)
    o_match = o_pattern.match(u_text)

    if o_match is None:
        u_output = None
    else:
        u_output = o_match.group(i_group)

    return u_output


# MAIN FUNCTION
#=======================================================================================================================
def hq_copy(po_dat=None, pu_src_path='', pu_dst_dir='', pu_src_fmt='', pu_dst_fmt='', pb_sim=False,
            pi_print_mode=0, u_regex_pattern=None, i_regex_group=None, pb_del_src=False):
    """
    Renaming function for files and directories. Valid formats are crc32, md5, sha1 and real hq_title.

    Function to hq_copy a file (or the files contained in a directory) from a naming scheme to another one. In HQ_TOOLS,
    the valid naming schemes for files are:

        - 'title': The file has the same name than the ROM it belongs to. i.e. 'Super Mario World (Eur).jpg'.

        - 'crc32': The file is named like the CRC32 hash of the ROM it belongs to. i.e. 'ab46b0f1.png'.

        - 'md5':

        - 'sha1':

    The output of the function is... # TODO

    :param pu_dat: Dat file to use for renaming. i.e. '/home/charles/dat_files/snes.dat'

    :param pu_src_path: Source file (or directory) to be renamed. i.e. '/home/ann/my_files/' or '/home/metroid (eur).jpg'

    :param pu_dst_dir: Directory where to write the renamed file. i.e. '/home/jonh/renamed_files'

    :param pb_clean_hash: Indicates if clean hashes (omitting .cue files, for example) should be obtained from dat file
                         when comparing file names or, instead, full dirty hashes should be used instead (default).

    :param pb_sim: Simulation mode. If True, files won't be actually copied.

    :param u_regex_pattern: Regex pattern to allow the renaming of files that contain the expected name (crc32, md5...)
                            PLUS extra information. i.e. "012345687 - foo.gif".

    :param i_regex_group: Number of the group to catch

    :type i_print_mode int: 0-> No print at all, 1-> Print in single line mode, 2-> Print in persistent mode.

    :return: Statistics about the renaming process.
    """

    o_start = time.now()

    # Extra parameters check is needed in case the hq_copy function is called from another program because argument
    # check is valid just when you directly call this program from command line.
    # TODO: Add a check that po_dat is a RomSetContainer instance.

    o_src_fp = files.FilePath(pu_src_path)
    if not o_src_fp.exists():
        raise Exception('Source path "%s" not found' % pu_src_path)

    o_dst_fp = files.FilePath(pu_dst_dir)
    if not o_dst_fp.is_dir():
        raise Exception('Destination dir "%s" not found' % pu_dst_dir)

    if pu_dst_fmt not in do_valid_single_modes.keys():
        raise Exception('Unknown destination format "%s"' % pu_dst_fmt)

    if pu_src_fmt not in do_valid_single_modes.keys():
        raise Exception('Unknown source format "%s"' % pu_src_fmt)

    # Mode alias to search field relationship
    du_mode_to_field = {''}

    # Getting the list of files to process
    lo_files_to_process = []

    o_src_path = files.FilePath(pu_src_path)
    o_dst_dir = files.FilePath(pu_dst_dir)

    if o_src_path.is_file():
        lo_files_to_process.append(o_src_path)
    elif o_src_path.is_dir():
        for o_src_fp in o_src_path.content():
            if o_src_fp.is_file():
                lo_files_to_process.append(o_src_fp)

    # Stats initialization
    i_files_total = len(lo_files_to_process)
    i_files_recognized = 0
    i_files_renamed = 0

    lu_ren_files = []
    lu_unk_files = []

    # Processing of the files
    i_file = 0
    for o_src_fp in lo_files_to_process:
        i_file += 1

        # If the regex mode is not active, the full name of the file is used to find a game in the database. But with
        # regex matching, just part of the filename is used.
        if None in (u_regex_pattern, i_regex_group):
            u_caught_name = o_src_fp.u_name
        else:
            u_caught_name = _regex_catcher(o_src_fp.u_name, u_regex_pattern, i_regex_group)

        try:
            o_romset = po_dat.get_romsets_by_field(do_valid_single_modes[pu_src_fmt].u_field, True, u_caught_name)[0]
        except IndexError:
            o_romset = None

        if o_romset:
            i_files_recognized += 1
            lu_ren_files.append(o_src_fp.u_file)

            u_output_name = getattr(o_romset, do_valid_single_modes[pu_dst_fmt].u_field)

            o_dst_file_object = files.FilePath(o_dst_dir.u_path, u'%s.%s' % (u_output_name, o_src_fp.u_ext))
            u_dst_file_name = o_dst_file_object.u_file

            if pb_sim:
                u_copy_text = u's'
            else:
                i_files_renamed += 1
                shutil.copy(o_src_fp.u_path, o_dst_file_object.u_path)

                # TODO: Fix this nasty hack since doesn't show any success/fail result for delete.
                if pb_del_src:
                    os.remove(o_src_fp.u_path)

                u_copy_text = cons.u_OK_TEXT

        else:
            lu_unk_files.append(o_src_fp.u_file)
            u_dst_file_name = u'-- UNKNOWN --'
            u_copy_text = cons.u_ER_TEXT

        if pi_print_mode > 0:
            u_output = u'%s [%i/%i] %s: %s  ->  %s: %s' % (u_copy_text,
                                                           i_file,
                                                           len(lo_files_to_process),
                                                           pu_src_fmt, o_src_fp.u_file,
                                                           pu_dst_fmt, u_dst_file_name)
            if pi_print_mode == 1:
                sys.stdout.write(u'\r%s' % u_output.ljust(cons.i_TERM_COLS)[0:cons.i_TERM_COLS])
                sys.stdout.flush()

            elif pi_print_mode == 2:
                print u_output.encode('utf8')

            else:
                raise ValueError

    if pi_print_mode == 1:
        # Cleaning the last line and returning the cursor to the beginning
        sys.stdout.write(u'\r%s\r' % u''.ljust(cons.i_TERM_COLS))
    elif pi_print_mode == 2:
        # This is just an empty line at the end of the converted files
        print

    o_end = time.now()

    return {'i_total_files': i_files_total,
            'i_recog_files': i_files_recognized,
            'i_unk_files': i_files_total - i_files_recognized,
            'i_copied_files': i_files_renamed,
            'o_time': o_end - o_start,
            'lu_ren_files': lu_ren_files,
            'lu_unk_files': lu_unk_files}


# EXECUTION AS COMMAND LINE PROGRAM
#=======================================================================================================================
if __name__ == '__main__':
    print strings.hq_title(u_PROG_NAME, u_PROG_VER)

    dx_args = _get_cmd_options()
    dx_rename_output = hq_copy(po_dat=dx_args['u_dat_file'],
                               pu_src_path=dx_args['u_src_path'], pu_dst_dir=dx_args['u_dst_path'],
                               pu_src_fmt=dx_args['u_src_format'], pu_dst_fmt=dx_args['u_dst_format'],
                               pb_sim=dx_args['b_simulation'],
                               u_regex_pattern=dx_args['u_regex_pattern'],
                               i_regex_group=dx_args['i_regex_group'],
                               i_print_mode=2)

    # Some basic stats are printed to screen
    f_renamed_percent = 100.0 * dx_rename_output['i_recog_files'] / dx_rename_output['i_total_files']
    f_unknown_percent = 100.0 * dx_rename_output['i_unk_files'] / dx_rename_output['i_total_files']

    i_length = len(str(dx_rename_output['i_total_files']))
    u_ren_files = str(dx_rename_output['i_recog_files']).rjust(i_length)
    u_unk_files = str(dx_rename_output['i_unk_files']).rjust(i_length)

    u_output = u''
    u_output += u' STATS: %s\n' % dx_rename_output['o_time']
    u_output += u'        %i files found\n' % dx_rename_output['i_total_files']
    u_output += u'        %s files renamed (%.2f%%)\n' % (u_ren_files, f_renamed_percent)
    u_output += u'        %s files ignored (%.2f%%)\n' % (u_unk_files, f_unknown_percent)

    print u_output
