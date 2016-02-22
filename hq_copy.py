#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Command line utility and python library to copy files from folder A to B translating the names between crc32, md5, sha1,
and title schemes. For hashing names (crc32, md5, sha1), dirty or clean hashes can be used. Dirty means all the files
included in the full game are used to obtain the global hash (i.e. for a CD game it would be .cue and .bin files). In
Clean mode, meta-data files not actually present in the real disc (.cue files) wouldn't be taken into account.
"""

import argparse
import imp
# TODO: Remove os dependency and use files.py from libs instead
import os
import re
import shutil
import sys


u_CWD = os.path.dirname(os.path.realpath(__file__))

from hqlib import romdats
#romdats = imp.load_source(u'romdats', os.path.join(u_CWD, 'hqlib', 'romdats.py'))

import libs


# CONSTANTS
#=======================================================================================================================
du_FORMATS = {'c': 'crc32', 'm': 'md5', 's': 'sha1', 't': 'description'}
u_PROG_NAME = u'HQ COPY'
u_PROG_VER = u'v2015.10.11'

lu_valid_modes = []
for u_1st_char in ('C', 'D'):
    for u_2nd_char in du_FORMATS.keys():
        for u_3rd_char in du_FORMATS.keys():
            lu_valid_modes.append('%s%s%s' % (u_1st_char, u_2nd_char, u_3rd_char))

tu_valid_modes = tuple(lu_valid_modes)


# HELPER FUNCTIONS
#=======================================================================================================================
def _get_cmd_options():
    """
    Function to process the command-line options.

    :return: TODO: A dictionary with different options.
    """

    o_arg_parser = argparse.ArgumentParser(description='A command line utility to copy and hq_copy files between '
                                                       'different formats using a ROM dat file.')
    o_arg_parser.add_argument('-s',
                              action='store_true',
                              help='Simulation mode; files won\'t be copied.')
    o_arg_parser.add_argument('mode',
                              action='store',
                              choices=tu_valid_modes,
                              metavar='[DC][cmst][cmst]',
                              help='Renaming mode. 1st letter specifies the usage of clean (C) or dirty (D) hashes. '
                                   '2nd and 3rd letter specify the source and destination format: crc32 (c), md5 (m), '
                                   'sha1 (s), and hq_title (t). i.e. "Dct" will use dirty hashes to copy files from '
                                   'crc32 naming scheme to real hq_title scheme.')
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
        u_text_output += '   SIM: %s simulation is ON, files won\'t be copied\n' % libs.cons.u_OK_TEXT

    # Validating hq_copy mode
    if o_args.mode[0] == 'C':
        b_clean_hash = True
    else:
        b_clean_hash = False

    u_src_format = o_args.mode[1]
    u_dst_format = o_args.mode[2]

    u_extra_src_mode = u''
    u_extra_dst_mode = u''

    if u_src_format != 't':
        if b_clean_hash:
            u_extra_src_mode = u'clean '
        else:
            u_extra_src_mode = u'dirty '

    if u_dst_format != 't':
        if b_clean_hash:
            u_extra_dst_mode = u'clean '
        else:
            u_extra_dst_mode = u'dirty '

    u_text_output += u'  MODE: %s %s%s -> %s%s\n' % (libs.cons.u_OK_TEXT,
                                                     u_extra_src_mode,
                                                     du_FORMATS[u_src_format],
                                                     u_extra_dst_mode,
                                                     du_FORMATS[u_dst_format])

    # Validating dat file
    u_dat_file = o_args.dat.decode('utf8')
    if os.path.isfile(u_dat_file):
        u_dat_found = libs.cons.u_OK_TEXT
    else:
        u_dat_found = libs.cons.u_ER_TEXT
        i_errors += 1

    u_text_output += u'   DAT: %s %s\n' % (u_dat_found, u_dat_file)

    # Validating source path
    u_src_path = o_args.source.decode('utf8')
    if os.path.exists(u_src_path):
        u_src_found = libs.cons.u_OK_TEXT
    else:
        u_src_found = libs.cons.u_ER_TEXT
        i_errors += 1

    u_text_output += u'   SRC: %s %s\n' % (u_src_found, u_src_path)

    # Validating destination path
    u_dst_path = o_args.destination.decode('utf8')
    if os.path.isdir(u_dst_path):
        u_dst_found = libs.cons.u_OK_TEXT
    else:
        u_dst_found = libs.cons.u_ER_TEXT
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
            u_text_output += u'  REXP: %s #%i in "%s"\n' % (libs.cons.u_OK_TEXT, i_regex_group, u_regex)

        except (ValueError, IndexError) as o_exception:
            u_text_output += u'  REXP: %s Wrong regular expression data "%s"\n' % (libs.cons.u_ER_TEXT, u_regex_data)
            i_errors += 1

    if i_errors:
        u_text_output += u'\n%i errors found. Please, fix them and run the program again.' % i_errors

    print u_text_output.encode('utf8', 'strict')

    if i_errors:
        sys.exit()

    return {'b_clean_hash': b_clean_hash,
            'b_simulation': b_simulation,
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
def hq_copy(u_dat='', u_src_path='', u_dst_dir='', u_src_fmt='', u_dst_fmt='', b_clean_hash=False, b_sim=False,
            b_print=False, u_regex_pattern=None, i_regex_group=None):
    """
    Renaming function for files and directories. Valid formats are crc32, md5, sha1 and real hq_title.

    Function to hq_copy a file (or the files contained in a directory) from a naming scheme to another one. In HQ_TOOLS,
    the valid naming schemes for files are:

        - 'title': The file has the same name than the ROM it belongs to. i.e. 'Super Mario World (Eur).jpg'.

        - 'crc32': The file is named like the CRC32 hash of the ROM it belongs to. i.e. 'ab46b0f1.png'.

        - 'md5':

        - 'sha1':

    The output of the function is... # TODO

    :param u_dat: Dat file to use for renaming. i.e. '/home/charles/dat_files/snes.dat'

    :param u_src_path: Source file (or directory) to be renamed. i.e. '/home/ann/my_files/' or '/home/metroid (eur).jpg'

    :param u_dst_dir: Directory where to write the renamed file. i.e. '/home/jonh/renamed_files'

    :param b_clean_hash: Indicates if clean hashes (omitting .cue files, for example) should be obtained from dat file
                         when comparing file names or, instead, full dirty hashes should be used instead (default).

    :param b_sim: Simulation mode. If True, files won't be actually copied.

    :param u_regex_pattern: Regex pattern to allow the renaming of files that contain the expected name (crc32, md5...)
                            PLUS extra information. i.e. "012345687 - foo.gif".

    :param i_regex_group: Number of the group to catch

    :return: Statistics about the renaming process.
    """

    o_start = libs.time.now()

    # Extra parameters check is needed in case the hq_copy function is called from another program because argument
    # check is valid just when you directly call this program from command line.
    if not os.path.isfile(u_dat):
        raise Exception('Dat file "%s" not found' % u_dat)

    if not os.path.exists(u_src_path):
        raise Exception('Source path "%s" not found' % u_src_path)

    if not os.path.isdir(u_dst_dir):
        raise Exception('Destination dir "%s" not found' % u_dst_dir)

    u_dst_fmt = u_dst_fmt.lower()
    u_src_fmt = u_src_fmt.lower()

    if u_dst_fmt not in du_FORMATS.keys():
        raise Exception('Unknown destination format "%s"' % u_dst_fmt)

    if u_src_fmt not in du_FORMATS.keys():
        raise Exception('Unknown source format "%s"' % u_src_fmt)

    # Loading of the dat file
    o_dat = romdats.GameContainer(u_dat)

    # Getting the list of files to process
    lo_files_to_process = []

    o_src_path = libs.files.FilePath(u_src_path)
    o_dst_dir = libs.files.FilePath(u_dst_dir)

    if o_src_path.is_file():
        lo_files_to_process.append(o_src_path)
    elif o_src_path.is_dir():
        for o_src_file_object in o_src_path.content():
            if o_src_file_object.is_file():
                lo_files_to_process.append(o_src_file_object)

    # Stats initialization
    i_files_total = len(lo_files_to_process)
    i_files_recognized = 0
    i_files_renamed = 0

    lu_ren_files = []
    lu_unk_files = []

    # Processing of the files
    for o_src_file_object in lo_files_to_process:

        # If the regex mode is not active, the full name of the file is used to find a game in the database. But with
        # regex matching, just part of the filename is used.
        if None in (u_regex_pattern, i_regex_group):
            u_caught_name = o_src_file_object.u_name
        else:
            u_caught_name = _regex_catcher(o_src_file_object.u_name, u_regex_pattern, i_regex_group)

        o_game = o_dat.get_game_by_field(du_FORMATS[u_src_fmt], u_caught_name, b_clean_hash)

        if o_game:
            i_files_recognized += 1
            lu_ren_files.append(o_src_file_object.u_file)

            if u_dst_fmt in ('c', 'm', 's'):
                du_hashes = o_game.get_hashes(b_discard_irrelevant=b_clean_hash)
                u_output_name = du_hashes[du_FORMATS[u_dst_fmt]]
            else:
                u_output_name = o_game.u_description

            o_dst_file_object = libs.files.FilePath(o_dst_dir.u_path, '%s.%s' % (u_output_name,
                                                                                 o_src_file_object.u_ext))
            u_dst_file_name = o_dst_file_object.u_file

            if b_sim:
                u_copy_text = 's'
            else:
                shutil.copy(o_src_file_object.u_path, o_dst_file_object.u_path)
                u_copy_text = libs.cons.u_OK_TEXT

        else:
            lu_unk_files.append(o_src_file_object.u_file)
            u_dst_file_name = '-- UNKNOWN --'
            u_copy_text = libs.cons.u_ER_TEXT

        # Add extra indication of clean or dirty hash
        u_extra_src = ''
        u_extra_dst = ''

        if u_src_fmt in ('c', 'm', 's'):
            if b_clean_hash:
                u_extra_src = 'C '
            else:
                u_extra_src = 'D '

        if u_dst_fmt in ('c', 'm', 's'):
            if b_clean_hash:
                u_extra_dst = 'C '
            else:
                u_extra_dst = 'D '

        if b_print:
            print '%s %s%s: %s -> %s%s: %s' % (u_copy_text,
                                               u_extra_src,
                                               du_FORMATS[u_src_fmt],
                                               o_src_file_object.u_file,
                                               u_extra_dst,
                                               du_FORMATS[u_dst_fmt],
                                               u_dst_file_name)

    if b_print:
        # This is just an empty line at the end of the converted files
        print

    o_end = libs.time.now()

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
    print libs.strings.hq_title(u_PROG_NAME, u_PROG_VER)

    dx_args = _get_cmd_options()
    dx_rename_output = hq_copy(u_dat=dx_args['u_dat_file'],
                               u_src_path=dx_args['u_src_path'], u_dst_dir=dx_args['u_dst_path'],
                               u_src_fmt=dx_args['u_src_format'], u_dst_fmt=dx_args['u_dst_format'],
                               b_clean_hash=dx_args['b_clean_hash'],
                               b_sim=dx_args['b_simulation'],
                               u_regex_pattern=dx_args['u_regex_pattern'],
                               i_regex_group=dx_args['i_regex_group'],
                               b_print=True)

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
