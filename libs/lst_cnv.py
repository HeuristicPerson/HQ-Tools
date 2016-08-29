# -*- coding: utf-8 -*-

import codecs
import datetime
import re

import cons
import csv
import files
import lists
import roms


# CLASSES
#=======================================================================================================================
class RomSetMatch:
    """
    Class to store the minimum information found in the front-end lists required to find matches in the database.
    """
    def __init__(self, pu_crc32=u'', pu_name=u''):
        self.u_name = pu_name                      # RomSet name found in the list

        # TODO: Find a cleaner way of assigning _u_crc32 with sanity checks on creation.
        self._u_crc32 = None
        self._set_crc32(pu_crc32)                  # RomSet CRC32 found in the list

    def __str__(self):
        u_output = u''
        u_output += u'[RomSetMatch]\n'
        u_output += u'  ._u_crc32: %s\n' % self._u_crc32
        u_output += u'  .u_name:   %s\n' % self.u_name
        return u_output.encode('utf8')

    def _set_crc32(self, pu_crc32):
        """
        Method to set the crc32 with some sanity checks.
        :param pu_crc32:
        :return: Nothing.
        """
        b_crc32_ok = True

        pu_crc32 = pu_crc32.lower()

        # length check
        if len(pu_crc32) != 8:
            b_crc32_ok = False

        # characters check
        o_matches = re.match(r'[^0-9a-f]', pu_crc32)
        if o_matches:
            b_crc32_ok = False

        # Setting the CRC32 if everything is fine or empty in other case.
        if b_crc32_ok:
            self._u_crc32 = pu_crc32
        else:
            self._u_crc32 = u''

    def _get_crc32(self):
        return self._u_crc32

    u_crc32 = property(fget=_get_crc32, fset=_set_crc32)


class ListConvertOutput(object):
    def __init__(self):
        self.lu_cnv_romsets = []
        self.lu_unk_romsets = []

    def _get_num_converted_games(self):
        return len(self.lu_cnv_romsets)

    def _get_num_unknown_games(self):
        return len(self.lu_unk_romsets)

    i_cnv_romsets = property(fget=_get_num_converted_games)
    i_unk_romsets = property(fget=_get_num_unknown_games)


# FUNCTIONS
#=======================================================================================================================
def lconvert(pu_src_fmt=None, pu_dst_fmt=None, pu_src_file=None, pu_dst_file=None, po_dat=None, pb_print=False,
             pu_log=None, pi_log=0):
    """
    Function to convert between list formats for different front-ends.

    :param pu_src_fmt:

    :param pu_dst_fmt:

    :param pu_src_file:

    :param pu_dst_file:

    :type po_dat: roms.RomSetContainer

    :param pb_print:

    :type pu_log: Unicode Path of the log file to write.

    :param pi_log: 0, no log; 1, short log (list of missing sets in conversion); 2, full log (lists of missing and found
                   sets in the conversion).

    :return: None.
    """

    # Parameter validation
    o_src_fp = files.FilePath(pu_src_file)
    o_dst_fp = files.FilePath(pu_dst_file)

    # 1st we getting the name of the romsets present in the list.
    lo_src_romsets = lst_read(po_file_fp=o_src_fp, pu_format=pu_src_fmt)

    if pb_print:
        u_output = u'%i romsets found in source list "%s"' % (len(lo_src_romsets), pu_src_file)
        print u_output.encode('utf8')

    # 2nd we import extra data (year, manufacturer, genre...) from extra-dats
    # TODO: Set right order for if elif conditions to avoid matching Game Boy in Game Boy Color, for example.
    u_meta_file_root = u''
    if u'Game Boy' in po_dat.u_name:
        u_meta_file_root = u'gb'
    elif u'Genesis' in po_dat.u_name:
        u_meta_file_root = u'megadrive'
    elif u'32X' in po_dat.u_name:
        u_meta_file_root = u'32x'
    else:
        if pb_print:
            print 'UNKNOWN META-DATA FILE'

    o_meta_file_fp = files.FilePath(cons.o_METADATA_DIR_FP.u_path, u'%s_metadata.csv' % u_meta_file_root)

    if not o_meta_file_fp.is_file():
        if pb_print:
            print 'META-DATA FILE NOT FOUND "%s"' % o_meta_file_fp.u_path
    else:
        if pb_print:
            print 'IMPORTING META-DATA FROM "%s"' % o_meta_file_fp.u_path
        o_meta_file_csv = csv.ParsedCsv()
        o_meta_file_csv.load_from_disk(pu_file=o_meta_file_fp.u_path,
                                       pu_sep=u'\t',
                                       pu_com=u'#',
                                       pb_headings=True)

        o_id_field = roms.Field(0, 'u_ccrc32')
        lo_import_fields = [roms.Field(1, 'i_year'),
                            roms.Field(2, 'u_auth')]
        po_dat.csv_import(po_csv=o_meta_file_csv,
                          po_id_field=o_id_field,
                          plo_fields=lo_import_fields,
                          pb_overwrite=True)
        if pb_print:
            print 'META-DATA IMPORTED'

    # 3rd we try to find those romsets in the RomSetContainer
    do_dst_romsets = {}
    for o_src_romset in lo_src_romsets:
        try:
            # If the romset found in the FE list contains CRC32, we search the DB by CRC32
            if o_src_romset.u_crc32:
                o_db_romset = po_dat.get_romsets_by_field('u_ccrc32', True, o_src_romset.u_crc32)[0]
            # In other case, we search the DB by RomSet name.
            else:
                o_db_romset = po_dat.get_romsets_by_field('u_name', True, o_src_romset.u_name)[0]
        except IndexError:
            o_db_romset = None

        # IMPORTANT NOTE HERE: Even though we search in the DB by CRC32 (if we have it) and then by RomSet name (if we
        # don't have the CRC32). We create a dictionary with the results were the name is ALWAYS the key. It's not an
        # issue at all and the only minor problem could be that converting a list to hqtools using a different dat file
        # than the dat used to rename the roms, you could have one name A in the dictionary key, and one name B in the
        # o_db_romset. As I said, this is not an issue at all because the important value is the one stored in
        # o_db_romset. The o_src_romset.u_name is used only to sort the output list.
        do_dst_romsets[o_src_romset.u_name] = o_db_romset

    # 4th we export the above romsets to the desired format
    lst_write(po_dat=po_dat,
              pdo_romsets=do_dst_romsets,
              pu_file=pu_dst_file,
              pu_format=pu_dst_fmt)

    # ROMSets from source file are split into two groups, found/not-found. Those groups will be return by the function
    # and also, if desired, will be written to a log file.
    lo_romsets_found_in_db = []
    lo_romsets_missed_in_db = []

    for o_src_romset in lo_src_romsets:
        if do_dst_romsets[o_src_romset.u_name]:
            lo_romsets_found_in_db.append(o_src_romset)
        else:
            lo_romsets_missed_in_db.append(o_src_romset)

    # Log file creation:
    if pi_log > 0 and pu_log:
        o_log_fp = files.FilePath(pu_log)
        if pi_log == 1:
            b_full_log = False
        elif pi_log == 2:
            b_full_log = True
        else:
            raise ValueError

        _log_write(po_dat=po_dat,
                   plo_miss_romsets=lo_romsets_missed_in_db,
                   plo_have_romsets=lo_romsets_found_in_db,
                   pu_src_fmt=pu_src_fmt,
                   pu_dst_fmt=pu_dst_fmt,
                   po_log_fp=o_log_fp,
                   po_src_fp=o_src_fp,
                   po_dst_fp=o_dst_fp,
                   pb_full=b_full_log)

    # OUTPUT
    #-------
    o_output = ListConvertOutput()
    for o_romset in lo_romsets_found_in_db:
        o_output.lu_cnv_romsets.append(o_romset.u_name)
    for o_romset in lo_romsets_missed_in_db:
        o_output.lu_unk_romsets.append(o_romset.u_name)

    return o_output


#======================================================================================================================#
# READ/WRITE FUNCTIONS FOR DIFFERENT FORMATS                                                                           #
#======================================================================================================================#
#                                                                                                                      #
# There are two different functions for each favourites list format:                                                   #
#                                                                                                                      #
#     1. A "xxx_read" list that reads a favourite list in the format xxx (wahcade or MALA for example) and outputs a   #
#        dat container object from hqlib with the full game objects found.                                             #
#                                                                                                                      #
#     2. A "xxx_write" list that receives a game container object from hqlib and generates a favourites list in the    #
#        xxx format.                                                                                                   #
#                                                                                                                      #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def lst_read(po_file_fp=None, pu_format=None):
    """
    Function to get the name of the romsets present in a list.

    :param po_file_fp: Name of the file to read. i.e. '/home/john/my_favourites.lst'
    :param pu_format: Format of the list. i.e. 'wahcade' (only valid value by now).
    :return: A list with the name of the found romsets.
    """

    if pu_format == 'dat':
        lo_romsets_found = _dat_read(po_file_fp)
    elif pu_format == 'wahcade':
        lo_romsets_found = _wahcade_read(po_file_fp)
    elif pu_format == 'hqtools':
        lo_romsets_found = _hqtools_read(po_file_fp)

    else:
        raise Exception('Unknown format "%s"' % pu_format)

    return lo_romsets_found


def lst_write(po_dat=None, pdo_romsets=None, pu_file=u'', pu_format=u''):
    """
    Function to write a list file with the romset objects contained in a dictionary.

    :param pdo_romsets: Dictionary of romsets to include in the list. Key = Name of the RomSet, Value = RomSet object.

    :param pu_file: File to write the RomSets in. i.e. '/home/john/my_favs.lst'.

    :param pu_format: Format of the list. i.e. 'wahcade'.

    :param po_dat: Dat used to search for the ROMs (it will be used in the internal hql format by now)

    :return: Nothing?
    """

    po_file_fp = files.FilePath(pu_file)

    if pu_format == 'wahcade':
        _wahcade_write(pdo_romsets=pdo_romsets, po_file_fp=po_file_fp)

    elif pu_format == 'hqtools':
        _hqtools_write(po_dat=po_dat, pdo_romsets=pdo_romsets, po_file_fp=po_file_fp)

    else:
        raise Exception('Unknown format "%s"' % pu_format)

    return None


# DAT LISTS: Yes, dat files are an (kind of hacky) input list format
#=======================================================================================================================
# To avoid any hack or workaround, I'm actually reading and parsing again the same dat file I already had. Slow...
def _dat_read(po_file_fp=None):
    lo_romsets_found = []
    o_romset_container = roms.RomSetContainer(po_file_fp.u_path)
    for o_romset in o_romset_container:
        o_match = RomSetMatch(pu_name=o_romset.u_name)
        lo_romsets_found.append(o_match)

    return lo_romsets_found


# HQ TOOLS LISTS: Internal format of this program
#=======================================================================================================================
def _hqtools_read(po_file_fp):
    """
    Function to read a list of RomSets in hqtools format.
    :param po_file_fp: File to read the data from
    :return: A list of romsets found in the list
    """
    lo_romsets_found = []

    o_csv = csv.ParsedCsv()
    o_csv.load_from_disk(po_file_fp.u_path, pu_sep=u'\t', pu_com=u'#', pb_headings=True)

    for lu_row in o_csv.llu_rows:
        o_romset_match = RomSetMatch(pu_crc32=lu_row[0], pu_name=lu_row[1])
        lo_romsets_found.append(o_romset_match)

    return lo_romsets_found


def _hqtools_write(po_dat=None, pdo_romsets=None, po_file_fp=None):
    """
    Function to write a list of RomSets in hqtools format (HQ list, the internal format of this program).

    :param po_dat: RomSetContainer object (see roms.py). It's used because in the hql format, data about the dat where
                   the roms were found is also stored.

    :param dict pdo_romsets:

    :param unicode pu_file: Name of the file. i.e. '/home/john/my_favs.lst'

    :return: Nothing
    """

    o_csv = csv.ParsedCsv()
    o_csv.lu_headings = [u'CRC32 (c)', u'NAME']

    # Comments
    lu_comments = []
    lu_comments.append(u'%s - List File v1.0' % cons.u_SET_NAME)
    lu_comments.append(u'Dat Name: %s' % po_dat.u_name)
    lu_comments.append(u'Dat Desc: %s' % po_dat.u_description)
    lu_comments.append(u'Dat Ver:  %s' % po_dat.u_version)
    lu_comments.append(u'Dat Com:  %s' % po_dat.u_comment)
    o_csv.lu_comments = lu_comments

    # TODO: Check out the best way to alphabetically sort unicode texts containing spaces
    for u_romset_name in lists.title_sort(pdo_romsets.keys()):
        o_romset = pdo_romsets[u_romset_name]
        if o_romset:
            lu_data_line = [o_romset.u_ccrc32, o_romset.u_name]
        else:
            lu_data_line = [u'········', u_romset_name]

        o_csv.append_row(lu_data_line)

    o_csv.save_to_disk(pu_file=po_file_fp.u_path, pu_sep=u'\t', pu_com=u'#')


# WAHCADE
#=======================================================================================================================
def _wahcade_read(po_file_fp=None):
    """
    Function to read a list of games from a WahCade list file and return a list of games found in a database.

    The full format of the wahcade list file is found at:

    https://github.com/sairuk/wahcade/blob/68798363289c057020f9fa690420a23daa798365/doc/file_formats/gamelist_format.txt

        line  desc
        ----  ----
        1     ROM NAME
        2     Game Name
        3     Year
        4     Manufacturer
        5     Clone Of <rom name>
        6     Rom Of <rom name>
        7     Display Type (Raster / Vector)
        8     Screen Type (Vertical / Horizontal)
        9     Controller Type
        10    Driver Status
        11    Colour Status
        12    Sound Status
        13    CatVer
        (repeat for each game)

    :param pu_file: path of the file to read. i.e. '/home/john/wahcade_john.lst'

    :return: A list of RomSetMatch objects.
    """

    lo_romsets_found = []

    # Getting the list of ROMs in the file
    #-------------------------------------
    o_file = codecs.open(po_file_fp.u_path, 'r', 'utf8')

    while True:
        lu_lines = files.read_nlines(o_file, 13)

        if not lu_lines:
            break
        else:
            u_romset_name = lu_lines[0]
            o_romset_match = RomSetMatch(pu_crc32=u'', pu_name=u_romset_name)
            lo_romsets_found.append(o_romset_match)

    o_file.close()

    return lo_romsets_found


def _wahcade_write(pdo_romsets=None, po_file_fp=None):
    """
    Function to write a list of romsets to wahcade list format. See _wahcade_read function for details about wahcade
    file format.

    :param pu_file:


    :type pdo_romsets: dict[unicode, roms._RomSet]

    :return:
    """

    o_file = codecs.open(po_file_fp.u_path, 'w', 'utf8')

    for u_romset_name in lists.title_sort(pdo_romsets.keys()):
        # First we get the romset object
        o_romset = pdo_romsets[u_romset_name]

        # Only "full" romsets (the ones found in the database) are written to the wahcade list
        if o_romset:
            # Data preparation
            if o_romset.i_year != 0:
                u_year = unicode(o_romset.i_year)
            else:
                u_year = u''

            if o_romset:
                #print o_romset
                u_output = u''
                u_output += u'%s\n' % o_romset.u_name
                u_output += u'%s\n' % o_romset.u_desc
                u_output += u'%s\n' % u_year
                u_output += u'%s\n' % o_romset.u_auth
                u_output += u'\n'
                u_output += u'\n'
                u_output += u'\n'
                u_output += u'\n'
                u_output += u'\n'
                u_output += u'\n'
                u_output += u'\n'
                u_output += u'\n'
                u_output += u'\n'  # CatVer. In origional Wahcade lists it appears as Unknown. I'll leave it empty but
                                   # maybe I have to force "unknown" to avoid problems.

                o_file.write(u_output)

    o_file.close()


#=======================================================================================================================
# LOG WRITING FUNCTIONS (SHORT AND FULL LOGS) (write only)
#=======================================================================================================================
# TODO: Make this single function write both short/full logs with a parameter.
def _log_write(po_dat=None, plo_miss_romsets=None, plo_have_romsets=None, po_log_fp=None, pu_src_fmt=u'', po_src_fp=None,
               po_dst_fp=None, pu_dst_fmt=u'', pb_full=False):
    """
    Function to write a short log of the list conversion performed.
    :param po_dat:
    :param pl_romsets:
    :param po_log_fp:
    :return:
    """

    o_now = datetime.datetime.now()

    if pb_full:
        i_max_length = max(len(str(len(plo_have_romsets))), len(str(len(plo_miss_romsets))))
    else:
        i_max_length = len(str(len(plo_have_romsets)))

    u_output = u''
    u_output += u'HQ LIST CONVERTER SHORT LOG\n'
    u_output += u'===========================\n'
    u_output += u'DATE: %s\n' % o_now.strftime(u'%d-%m-%Y %H:%M:%S')
    u_output += u'PROC: %s -> %s\n' % (pu_src_fmt, pu_dst_fmt)
    u_output += u' SRC: %s\n' % po_src_fp.u_path
    u_output += u' DST: %s\n' % po_dst_fp.u_path
    u_output += u' DAT: %s (%s)\n' % (po_dat.u_name, po_dat.u_version)
    u_output += u'MISS:\n'

    i_romset = 0
    for o_romset in plo_miss_romsets:
        i_romset += 1
        u_number = unicode(i_romset).rjust(i_max_length)
        u_output += u'      %s - %s\n' % (u_number, o_romset.u_name)

    if pb_full:
        u_output += u'HAVE:\n'
        i_romset = 0
        for o_romset in plo_have_romsets:
            i_romset += 1
            u_number = unicode(i_romset).rjust(i_max_length)
            u_output += u'      %s + %s\n' % (u_number, o_romset.u_name)

    # Writing to file
    o_file = codecs.open(po_log_fp.u_path, 'w', 'utf8')
    o_file.write(u_output)
    o_file.close()
