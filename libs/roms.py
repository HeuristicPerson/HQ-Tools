#!/usr/bin/env
# -*- coding: utf-8 -*-

import codecs
import xml.etree.cElementTree
import os                       # OS utils
import re

import csv


# Constants
#=======================================================================================================================
_u_VERSION = u'2015-04-18'                                          # Version of the library
lu_IGNORE_EXTS = [u'cue']
#-----------------------------------------------------------------------------------------------------------------------


class Filter:
    """
    Class to store information about a filter that will be applied later to RomSetContainer.
    """

    def __init__(self, u_attribute, u_method, *x_values):
        self.u_attribute = u_attribute
        self.u_method = u_method
        self.lx_values = x_values

        for x_value in x_values:
            if not isinstance(x_value, (unicode, str, int, float)):
                raise Exception('ERROR, type "%s" is not valid value for a filter' % type(x_value))

        # TODO: Create a check for x_values to avoid the case when you create a wrong filter with a tuple (123, 145)

    def __str__(self):
        u_output = u''
        u_output += u'[Filter]\n'
        u_output += u'u_attribute: %s\n' % self.u_attribute
        u_output += u'   u_method: %s\n' % self.u_method
        u_output += u'  lx_values: %s\n' % str(self.lx_values)

        return u_output.encode('utf8', 'strict')


class Field:
    """
    Class to store configuration data for CSV import method for RomSetContainer.
    """
    def __init__(self, pi_src_column, ps_dst_field):
        self.i_src_column = pi_src_column
        self.s_dst_field = ps_dst_field


class RomSetContainer:
    """
    Class to store a list of games, each game can contain different ROM files data. The information can be read/write to
    disk ROM file objects.
    """

    def __init__(self, u_file=None):

        # TODO: RomSetContainer should contain an internal registry with all the manipulations suffered by the object so
        #       when you export the file to disk you know the information is not coming directly from the RAW dat file.

        # I think that some "MODIFIED" flags would be enough like .db_flags{'added_sets': True, 'removed_sets': True...}

        # Variable definition
        self.i_games = 0          # number of games stored
        self.i_position = None    # _RomSet position for the iterator

        self.u_name = u''         # internal name of the dat file.
        self.u_description = u''  # description of the dat file.
        self.u_version = u''      # version of the dat file (usually a date).
        self.u_comment = u''      # extra comment for the dat file.
        self.u_type = u''         # type of DAT file the data comes from.
        self.u_author = u''       # Author of the dat.

        self.lo_games = []        # list of game objects inside the dat file

        self._db_flags = {'from_dat': False,
                          'sets_added': False,
                          'sets_deleted': False,
                          'data_imported': False}       # Modification flags

        self._tu_valid_search_fields = ('i_year',
                                        'u_ccrc32', 'u_dcrc32',
                                        'u_cmd5', 'u_dmd5',
                                        'u_csha1', 'u_dsha1',
                                        'u_desc', 'u_name', 'u_auth')

        if u_file:
            self.read_from_dat(u_file)

    def __str__(self):
        u_output = u''
        u_output += u'<RomSetContainer>\n'
        u_output += u'  ._db_flags: %s\n' % str(self._db_flags)
        u_output += u'  .u_name:    %s\n' % self.u_name
        u_output += u'  .u_desc:    %s\n' % self.u_description
        u_output += u'  .u_version: %s\n' % self.u_version
        u_output += u'  .u_comment: %s\n' % self.u_comment
        u_output += u'  .u_type:    %s\n' % self.u_type
        u_output += u'  .u_author:  %s\n' % self.u_author
        u_output += u'  .i_games:   %i\n' % self.i_games

        return u_output.encode('utf8', 'strict')

    def __iter__(self):
        if self.i_games > 0:
            self.i_position = 0

            # If the list is not sorted, it's sorted before iterating over it.
            self._sort()

        return self

    def __len__(self):
        return self.i_games

    def next(self):
        if (self.i_position is not None) and (self.i_position < self.i_games):
            self.i_position += 1
            return self.lo_games[self.i_position - 1]
        else:
            raise StopIteration()

    def _add_romset(self, o_romset):
        """
        Internal method to add games to the container WITHOUT any kind of duplicity or other kind of check.

        :param o_romset:
        """

        self.lo_games.append(o_romset)
        self.i_games += 1

    def add_romset(self, o_romset):
        """
        Method to add a new romset game to the container.

        :param o_romset: _RomSet to add.

        :return: True if the game was successfully added, false in other case.
        """

        b_added = False

        if (o_romset is not None) and (not self.id_exists(o_romset.u_id)):
            self._add_romset(o_romset)
            b_added = True

        return b_added

    def _duplicates_found(self):
        """
        Method to check the existence of duplicated ids which will break the whole idea of this project.

        :return: True if duplicates were found, False in other case.
        """

        lu_md5s = []

        for o_romset in self.lo_games:
            lu_md5s.append(o_romset.u_dmd5)

        su_unique_md5s = set(lu_md5s)

        # Since I want to be sure that I found the errors, by default I assume there are duplicated MD5s.
        b_duplicates = True

        if len(lu_md5s) == len(su_unique_md5s):
            b_duplicates = False

        return b_duplicates

    def _show_duplicates(self):
        """
        Method to quick show duplicates so you can fix the problems using other tools or manually.

        WARNING! This method can be really slow.

        :return: A list of lists.
        """

        dlu_duplicated_romsets = {}

        for o_romset in self:
            if o_romset.u_dmd5 not in dlu_duplicated_romsets:
                dlu_duplicated_romsets[o_romset.u_dmd5] = []

            dlu_duplicated_romsets[o_romset.u_dmd5].append(o_romset.u_name)

        # Since for an A-B duplicate we check the duplicity two times A vs B, B vs A, the lists of duplicates are
        # doubled and have to be made unique.
        dlu_clean_duplicated_romsets = {}
        for u_key, lu_values in dlu_duplicated_romsets.iteritems():
            if len(lu_values) > 1:
                dlu_clean_duplicated_romsets[u_key] = set(lu_values)

        return dlu_clean_duplicated_romsets

    def empty(self):
        """
        Method to clean all the games of the container but keeping the meta-data.

        :return: Nothing
        """

        self.lo_games = []
        self.i_games = 0

    def copy_metadata_from(self, o_game_container):
        """
        Method to copy meta-data information (everything but the list of games itself and the number of games) from
        other RomSetContainer object.

        :param o_game_container: External RomSetContainer object.
        """

        # Modification of data
        self.u_name = o_game_container.u_name
        self.u_description = o_game_container.u_description
        self.u_version = o_game_container.u_version
        self.u_comment = o_game_container.u_comment
        self.u_type = o_game_container.u_type
        self.u_author = o_game_container.u_author

        u_log_message = u''
        u_log_message += u'Metadata copied: '
        u_log_message += u'u_name="%s" ' % self.u_name
        u_log_message += u'u_desc="%s" ' % self.u_description
        u_log_message += u'u_version="%s" ' % self.u_version
        u_log_message += u'u_comment="%s" ' % self.u_comment
        u_log_message += u'u_type="%s" ' % self.u_type
        u_log_message += u'u_author="%s" ' % self.u_author

    def csv_export(self, ptu_fields=(), ptu_headings=()):
        """
        Method to export the RomSetContainer data to a csv file.

        :param ptu_fields: Tuple of the fields to export, i.e. ('_u_crc32', 'u_name', 'i_year'')

        :param ptu_headings: Tuple with the headings for each field. If the tuple is emtpy, the raw field names will be
                             used. i.e. ('CRC32', 'Game Name', 'Year')

        :return: Nothing
        """

        o_csv = csv.ParsedCsv()

        # Comments
        o_csv.lu_comments.append(u'   Dat Name: %s' % self.u_name)
        o_csv.lu_comments.append(u'    Version: %s' % self.u_version)
        o_csv.lu_comments.append(u'Description: %s' % self.u_description)
        o_csv.lu_comments.append(u'    Comment: %s' % self.u_comment)
        o_csv.lu_comments.append(u'     Author: %s' % self.u_author)
        o_csv.lu_comments.append(u'       Type: %s' % self.u_type)
        o_csv.lu_comments.append(u'      Games: %i' % self.i_games)

        lu_flags = []
        for u_key, b_value in self._db_flags.iteritems():
            lu_flags.append(u'%s=%s' % (u_key, b_value))
        lu_flags.sort()
        u_flags = u' '.join(lu_flags)

        o_csv.lu_comments.append(u'      Flags: %s' % u_flags)

        # Headings
        if ptu_headings:
            o_csv.lu_headings = ptu_headings
        else:
            o_csv.lu_headings = ptu_fields

        for o_game in self:
            lu_saved_fields = []

            for u_field in ptu_fields:
                u_field_to_save = str(getattr(o_game, u_field))
                lu_saved_fields.append(u_field_to_save)

            o_csv.append_row(lu_saved_fields)

        return o_csv

    def csv_import(self, po_csv=None, po_id_field=None, plo_fields=None, pb_overwrite=False):
        """
        Method to import data from a csv object.

        :param po_csv: Csv object from csv library.
        :param po_id_field: Field object indicating the csv column to use as identification field and the name of that
                            field. WARNING: Using a non-unique field as identification field can lead to import data to
                            the wrong SETs.
        :param plo_fields: List of Field objects indicating which columns to import.
        :param pb_overwrite: If True, imported data will overwrite the previous existing data. If False, previous data
                             will be kept.
        :return: Nothing.
        """

        if po_id_field and plo_fields:
            self._db_flags['data_imported'] = True

            for lu_row in po_csv.llu_rows:
                u_csv_id = lu_row[po_id_field.i_src_column]
                for o_romset in self:
                    if getattr(o_romset, po_id_field.s_dst_field) == u_csv_id:
                        for o_update_field in plo_fields:
                            if o_update_field.s_dst_field == 'i_year':
                                if pb_overwrite or o_romset.i_year == 0:
                                    o_romset.i_year = int(lu_row[o_update_field.i_src_column])

                            elif o_update_field.s_dst_field == 'u_desc':
                                # Description field always has content so no need to check for "empty".
                                if pb_overwrite:
                                    o_romset.u_desc = lu_row[o_update_field.i_src_column]

                            elif o_update_field.s_dst_field == 'u_auth':
                                if pb_overwrite or o_romset.u_mfr == u'':
                                    o_romset.u_mfr = lu_row[o_update_field.i_src_column]

                            # TODO: Add new fields to romset like genre, number of players, etc... that can be imported
                            else:
                                raise ValueError('Invalid value to update "%s"' % o_update_field.s_dst_field)
                        # Id field should be unique, so we stop searching for other romsets after the first match
                        break

    def filter(self, o_filter):
        """
        Method to filter in/out games depending on a field name and allowed/disallowed values for that field.

        :param u_attribute: Name of the field to filter by. i.e. 'i_year'.

        :param lu_field_values: List of values we're using to filter. i.e. (1989, 1990, 1993) to filter by years

        :param u_method: 'in', 'out' to return the games the games that match the values of lu_field_values or the games
                         that DON'T match the values of lu_field_values.

        :return: A list of games that match or don't match your filter criteria.
        """

        # Two RomSetContainer objects are created to store the games that matched the filter and the games that didn't
        # matched it.
        o_matched_container = RomSetContainer()
        o_matched_container.copy_metadata_from(self)
        o_matched_container.modify_metadata(u'FILTER(', u')')
        o_unmatched_container = RomSetContainer()
        o_unmatched_container.copy_metadata_from(self)

        for o_game in self:

            # The first thing to do is (to try) to obtain o_game.<u_attribute>
            try:
                x_value = getattr(o_game, o_filter.u_attribute)

            except AttributeError:
                raise Exception('ERROR: You are trying to access the unknown attribute "%s"' % o_filter.u_attribute)

            # Then we can filter. Since we are filtering already unique games present in our container, we don't need
            # to perform any uniqueness test while adding the games to the matched/unmatched containers. So, we use the
            # method _add_romset which doesn't perform that test and is much faster than the equivalent one with test
            # add_romset.
            if o_filter.u_method == 'equals':
                if x_value in o_filter.lx_values:
                    o_matched_container._add_romset(o_game)

                else:
                    o_unmatched_container._add_romset(o_game)

        return o_matched_container, o_unmatched_container

    def id_exists(self, u_id):
        """
        Method to check if a id already exists in the database
        :param u_id: id to check.
        :return: True if the id already exists, False in other case.
        """
        b_exists = False

        for o_game in self.lo_games:
            if o_game.u_id == u_id:
                b_exists = True
                break

        return b_exists

    # TODO: Probably this method can be deleted. It's also quite nasty since doesn't allow you to modify just one field.
    def modify_metadata(self, u_start=u'', u_end=u''):
        """
        Method to modify metadata information adding extra information at the beginning and end of each field.

        :param u_start: Extra text to add at the beginning
        :param u_end:  Extra text to add at the end.

        :return: Nothing
        """

        # Modification of data
        self.u_name = u'%s%s%s' % (u_start, self.u_name, u_end)
        self.u_description = u'%s%s%s' % (u_start, self.u_description, u_end)
        self.u_version = u'%s%s%s' % (u_start, self.u_version, u_end)
        self.u_comment = u'%s%s%s' % (u_start, self.u_comment, u_end)
        self.u_type = u'%s%s%s' % (u_start, self.u_type, u_end)
        self.u_author = u'%s%s%s' % (u_start, self.u_author, u_end)

    def set_id(self, s_mode):
        """
        Method to set the id field for each game as one between the different options given.

        :param s_mode: Which mode should be used to assign the games an id. Valid modes are defined in _RomSet object.

        :return Nothing.
        """

        for o_game in self.lo_games:
            o_game.set_id(s_mode)

    def get_romsets_by_field(self, pu_field, pb_first, *px_search_values):
        """
        Method to get a list of MULTIPLE GAMES with certain content in a field.

        :param pu_field: Name of the field. i.e. 'i_year'

        :param px_search_values: Content of the field to search for. i.e. 1985, 1986

        :return: A list with the found romsets.
        """

        lo_romsets = []

        if pu_field not in self._tu_valid_search_fields:
            raise ValueError('Error: pu_field must be one of %s' % str(self._tu_valid_search_fields))

        else:
            for o_romset in self:
                if getattr(o_romset, pu_field) in px_search_values:
                    lo_romsets.append(o_romset)
                    if pb_first:
                        break

        return lo_romsets

    def read_from_dat(self, pu_file):
        """
        Method to load Dat data from a file on disk.

        :param pu_file: File containing the data. i.e. '/home/john/mame.dat'

        :return: Nothing.
        """

        # If the file is not present, we raise an error
        if not os.path.isfile(pu_file):
            raise ValueError('Can\'t find dat file "%s"' % pu_file)

        o_file = codecs.open(pu_file, u'rb', u'utf8', u'ignore')

        # We try to automatically identify it reading the beginning of the file.
        u_first_line = o_file.readline()
        o_file.close()

        # Identifying ClrMamePro mode
        if (u_first_line.find(u'clrmamepro') != -1) or (u_first_line.find(u'emulator') != -1):
            u_format = 'cmp'

        # Identifying Xml mode
        elif u_first_line.find(u'<?xml') != -1:
            u_format = 'xml'

        # Unknown format error raise
        else:
            raise IOError('Unknown DAT format')

        # Loading the file using the different readers depending on the format parameter
        if u_format == 'cmp':
            self._read_from_cmp(pu_file)
        elif u_format == 'xml':
            self._read_from_xml(pu_file)

        # After loading the games from disk, the list is sorted
        self._sort()

        # We alter the proper flag
        self._db_flags['from_dat'] = True

        # Now that the game container has been populated from disk, is the time to check that we don't have duplicated
        # Ids
        if self._duplicates_found():
            print self._show_duplicates()
            raise Exception('Duplicated Id\'s found')

    def _read_from_cmp(self, u_file):
        """
        Method to process ClrMamePro DATs.
        """
        self.u_type = u'ClrMamePro'

        o_file = codecs.open(u_file, 'rb', 'utf8', 'ignore')

        b_head_mode = False
        b_game_mode = False

        ls_head_strings = []    # List that will contain the multiple lines with data from the heading.
        lu_game_strings = []    # List that will contain the multiple lines with data for a game.

        for u_line in o_file:

            # Detection of the start of the heading of the file
            if (u_line.find(u'clrmamepro (') == 0) or (u_line.find('emulator (') == 0):
                b_head_mode = True
                continue

            # If we are in "head-mode" and the first character of the line is ")", it means we have reached the end of
            # the heading (so we have all its lines) and we can parse them.
            if b_head_mode and u_line.find(')') == 0:
                self.u_name = _dat_vertical_parse(ls_head_strings, 'name')
                self.u_description = _dat_vertical_parse(ls_head_strings, 'description')
                self.u_version = _dat_vertical_parse(ls_head_strings, 'version')
                self.u_comment = _dat_vertical_parse(ls_head_strings, 'comment')

                ls_head_strings = []
                b_head_mode = False
                continue

            # If we are in "head-mode", we add the found lines to a list that will be parsed later" (look the code just
            # above).
            if b_head_mode:
                ls_head_strings.append(u_line)
                continue

            # _RomSet data
            if u_line.find('game (') == 0:
                b_game_mode = True
                continue

            if b_game_mode and u_line.find(')') == 0:
                u_romset_name = _dat_vertical_parse(lu_game_strings, 'name')
                u_romset_description = _dat_vertical_parse(lu_game_strings, 'description')
                u_romset_author = _dat_vertical_parse(lu_game_strings, 'manufacturer')
                u_game_year = _dat_vertical_parse(lu_game_strings, 'year')
                if u_game_year == u'':
                    u_game_year = u'0'

                lu_game_roms = _dat_vertical_parse(lu_game_strings, 'rom', 'multi')

                o_dat_romset = _RomSet(u_romset_name, u_romset_description)
                o_dat_romset.i_year = int(u_game_year)
                o_dat_romset.u_auth = u_romset_author

                for s_game_rom in lu_game_roms:
                    # sometimes name has quotes " around and sometimes not, so it's safer to use size as end.
                    u_rom_name = _dat_horizontal_parse(s_game_rom, 'name ', 'size')

                    u_rom_size = _dat_horizontal_parse(s_game_rom, 'size ', ' ')
                    u_rom_crc = _dat_horizontal_parse(s_game_rom, 'crc ', ' ')
                    u_rom_md5 = _dat_horizontal_parse(s_game_rom, 'md5 ', ' ')
                    u_rom_sha1 = _dat_horizontal_parse(s_game_rom, 'sha1 ', ' ')

                    # create a rom object
                    o_rom = _Rom()
                    o_rom.u_name = u_rom_name
                    o_rom.i_size = int(u_rom_size)
                    o_rom.u_crc32 = u_rom_crc.lower()
                    o_rom.u_md5 = u_rom_md5.lower()
                    o_rom.u_sha1 = u_rom_sha1.lower()

                    # add the rom object to the list
                    o_dat_romset.lo_roms.append(o_rom)

                # We add the game to the container without any kind of check, we will do it later.
                self._add_romset(o_dat_romset)

                lu_game_strings = []
                b_game_mode = False
                continue

            # _RomSet mode actions
            if b_game_mode:
                lu_game_strings.append(u_line)
                pass

    def _read_from_xml(self, u_file):
        self.u_type = u'XML'

        o_xml_tree = xml.etree.cElementTree.parse(u_file)
        o_xml_root = o_xml_tree.getroot()

        # Header information
        o_header = o_xml_root.find('header')
        self.u_name = o_header.find('name').text
        self.u_description = o_header.find('description').text
        self.u_version = o_header.find('version').text
        self.u_author = o_header.find('author').text

        # _RomSet information
        for o_game_elem in o_xml_root.findall('game'):
            u_game_name = o_game_elem.attrib['name']
            u_game_description = u_game_name

            o_dat_game = _RomSet(u_game_name, u_game_description)

            for o_rom_elem in o_game_elem.findall('rom'):
                # create a rom object
                o_rom = _Rom()
                o_rom.u_name = o_rom_elem.attrib['name']
                o_rom.i_size = int(o_rom_elem.attrib['size'])
                o_rom.u_crc32 = o_rom_elem.attrib['crc'].lower()
                o_rom.u_md5 = o_rom_elem.attrib['md5'].lower()
                o_rom.u_sha1 = o_rom_elem.attrib['sha1'].lower()

                # add the rom object to the list
                o_dat_game.lo_roms.append(o_rom)

            # We add the game to the container without any kind of check, we will do it later.
            self._add_romset(o_dat_game)

    def _sort(self):
        # Sorting of the list based on the game description (which is more reliable than the short name of the game)
        self.lo_games.sort(key=lambda o_game: o_game.u_desc.encode('utf8', 'strict'), reverse=False)


class _RomSet(object):

    def __init__(self, pu_name, pu_description):

        # Properties: Basic ones
        self.u_name = pu_name        # Usually, the file name for the game. MAME uses a short 8 char or less name here.
        self.u_desc = pu_description # Usually, the full and long name of the game i.e. 'Super Mario World (Europe)'.

        # Properties: The rest
        self.i_year = 0              # Year the game was published in (MAME dat support only, AFAIK).
        self.lo_roms = []            # List containing all the ROM information objects.
        self.u_auth = u''            # Author, company that programmed the game (MAME dat support only, AFAIK).

        # Properties: Unused ones, by now...
        self._lu_languages = []      # List of iso codes (3 letters) for languages included
        self._lu_countries = []      # List of iso codes (3 letters) for countries where the game was published
        self._lu_genres = []         # List of genres

    def __str__(self):
        u_output = u''
        u_output += u'[_RomSet]\n'
        u_output += u'  .u_ccrc32: %s\n' % self.u_ccrc32
        u_output += u'  .u_cmd5:   %s\n' % self.u_cmd5
        u_output += u'  .u_csha1:  %s\n' % self.u_csha1
        u_output += u'  .i_csize:  %s\n' % self.i_csize
        u_output += u'  .u_dcrc32: %s\n' % self.u_dcrc32
        u_output += u'  .u_desc:   %s\n' % self.u_desc
        u_output += u'  .u_dmd5:   %s\n' % self.u_dmd5
        u_output += u'  .u_dsha1:  %s\n' % self.u_dsha1
        u_output += u'  .u_dsize:  %s\n' % self.i_dsize
        u_output += u'  .u_auth:   %s\n' % self.u_auth
        u_output += u'  .u_name:   %s\n' % self.u_name
        u_output += u'  .i_year:   %i\n' % self.i_year
        u_output += u'  .lo_roms:\n'

        i_roms = 0

        for o_rom in self.lo_roms:
            i_roms += 1
            u_rom_text = str(o_rom).decode('utf8')

            # Modification of u_rom_text to show the rom number
            u_rom_text = u_rom_text.replace(u'[_Rom]', u'[_Rom] #%i' % (i_roms - 1))

            lu_rom_raw_lines = u_rom_text.splitlines()
            lu_rom_clean_lines = []

            for u_line in lu_rom_raw_lines:
                u_extra_spaces = u' ' * 13
                lu_rom_clean_lines.append('%s%s' % (u_extra_spaces, u_line))

            u_output += u'%s\n\n' % (u'\n'.join(lu_rom_clean_lines))

        return u_output.encode('utf8')

    def _get_hash(self, pu_type='crc32', pb_clean=False):
        """
        Method to obtain the COMPOUND hash of the game. It means the hash of *all* the ROMs included in the game will be
        summed. For example, if the game contains two ROMs:

            - _RomSet A
                - ROM a1: CRC32 = 01020304
                - ROM a2: CRC32 = 0a0b0c0d

        The output of this function will be 01020304 + 0a0b0c0d (remember that hash values are hex representations of
        numbers).

        Two comments about the behavior of the function:

            1. Different hashing methods are used: crc32, md5, sha1

            #TODO: Explain pb_clean parameter

            2. Only *relevant* ROMs are considered. For example, meta-data information is typically included in the form
               of .cue files for optical disc images. That information is not really included in the original media and
               its content would modify the hash result of the real data. Imagine two .cue files containing:

                   Track 1: Street Fighter.bin

                   Track 1: Street fighter.bin

               Although the content of the .bin file is the same, the .cue files are different (notice the
               capital-lowercase initial of "fighter"). In consequence, the hash of the .cue file is different and the
               global hash of the whole game will be different. SO, TO AVOID THIS ISSUE, .CUE FILES AND OTHER META-DATA
               FILES ARE NOT CONSIDERED WHEN CALCULATING THE HASH OF THE GAME.

        :return: A keyed dictionary with 'crc32', 'md5', and 'sha1' hashes in hex-string format
        """

        # Initialization
        i_base10_value = 0

        # The first step is to create a list with the real ROMs, avoiding meta-data ones like .cue files
        lo_relevant_roms = []

        for o_rom in self.lo_roms:
            # If discard is not activated, every ROM will be considered
            if not pb_clean:
                lo_relevant_roms.append(o_rom)

            # In other case, ROMs are filtered based on the file extension
            else:
                if u'.' in o_rom.u_name:
                    u_ext = o_rom.u_name.rpartition('.')[2].lower()

                    # TODO: Move ignored extensions to a more global constant
                    if u_ext not in lu_IGNORE_EXTS:
                        lo_relevant_roms.append(o_rom)

        for o_rom in lo_relevant_roms:

            # Rom hash addition
            if pu_type == 'crc32':
                try:
                    i_base10_value += int(o_rom.u_crc32, 16)
                except ValueError:
                    i_base10_value += 0
            elif pu_type == 'md5':
                try:
                    i_base10_value += int(o_rom.u_md5, 16)
                except ValueError:
                    i_base10_value += 0
            elif pu_type == 'sha1':
                try:
                    i_base10_value += int(o_rom.u_sha1, 16)
                except ValueError:
                    i_base10_value += 0
            else:
                raise Exception('Invalid pu_type "%s"' % pu_type)

        # Converting base10 values to hex-string format
        u_hash = '%x' % i_base10_value

        # Resizing hashes to proper length (crc32 = 8 chars, md5 = 32 chars, sha1 = 40 chars)
        if pu_type == 'crc32':
            i_hash_length = 8
        elif pu_type == 'md5':
            i_hash_length = 32
        elif pu_type == 'sha1':
            i_hash_length = 40
        else:
            raise Exception('Invalid pu_type "%s"' % pu_type)

        u_hash = u_hash[-i_hash_length:]
        u_hash = u_hash.rjust(i_hash_length, '0')

        return u_hash

    def _get_size(self, pb_clean=False):
        """
        Method to get the size of a romset taking into account all the files (dirty mode) or just relevant files (clean
        mode).

        :param pb_clean: True for clean mode, False for dirty mode
        """
        lo_relevant_roms = []
        i_global_size = 0

        for o_rom in self.lo_roms:
            # If discard is not activated, every ROM will be considered
            if not pb_clean:
                lo_relevant_roms.append(o_rom)

            # In other case, ROMs are filtered based on the file extension
            else:
                if u'.' in o_rom.u_name:
                    u_ext = o_rom.u_name.rpartition('.')[2].lower()

                    if u_ext not in lu_IGNORE_EXTS:
                        lo_relevant_roms.append(o_rom)

        for o_rom in lo_relevant_roms:
            i_global_size += o_rom.i_size

        return i_global_size

    # Properties with a bit of code behind
    def _get_ccrc32(self):
        return self._get_hash(pu_type='crc32', pb_clean=True)

    def _get_dcrc32(self):
        return self._get_hash(pu_type='crc32', pb_clean=False)

    def _get_cmd5(self):
        return self._get_hash(pu_type='md5', pb_clean=True)

    def _get_dmd5(self):
        return self._get_hash(pu_type='md5', pb_clean=False)

    def _get_csha1(self):
        return self._get_hash(pu_type='sha1', pb_clean=True)

    def _get_dsha1(self):
        return self._get_hash(pu_type='sha1', pb_clean=False)

    def _get_csize(self):
        return self._get_size(pb_clean=True)

    def _get_dsize(self):
        return self._get_size(pb_clean=False)

    u_ccrc32 = property(fget=_get_ccrc32, fset=None)
    u_dcrc32 = property(fget=_get_dcrc32, fset=None)
    u_cmd5 = property(fget=_get_cmd5, fset=None)
    u_dmd5 = property(fget=_get_dmd5, fset=None)
    u_csha1 = property(fget=_get_csha1, fset=None)
    u_dsha1 = property(fget=_get_dsha1, fset=None)
    i_csize = property(fget=_get_csize, fset=None)
    i_dsize = property(fget=_get_dsize, fset=None)


class _Rom:
    """
    Class to store all the information for a ROM file contained in a DAT file. Typically that information is the name
    of the ROM, the description, CRC-MD5-SHA1 check-sums...
    """

    def __init__(self):
        # Variable definition
        self.u_name = ''   # name of the ROM. i.e. 'Super Mario World.sfc'
        self.u_crc32 = ''  # crc32 checksum of the file data i.e. 'a209fe80'
        self.u_md5 = ''    # md5 checksum of the file data
        self.u_sha1 = ''   # sha1 checksum of the file data
        self.i_size = 0    # file size in bytes

        # Variable population

    def __str__(self):
        u_output = u''
        u_output += u'[_Rom]\n'
        u_output += u'   i_size: %i\n' % self.i_size
        u_output += u'  _u_crc32: %s\n' % self.u_crc32
        u_output += u'    u_md5: %s\n' % self.u_md5
        u_output += u'   u_name: %s\n' % self.u_name
        u_output += u'   u_sha1: %s\n' % self.u_sha1

        return u_output.encode('utf8')


# Functions
#=======================================================================================================================
def get_rom_header(pu_rom_file):
    """
    Function to return the year(s) found in a rom file.

    Only the first bytes of the ROM are scanned and only years 19xx and 20xx are searched for.

    :param pu_rom_file: Name of the file to search in.

    :return: A list with the found years as integers.
    """

    i_bytes = 2048
    i_min_year = 1970
    i_max_year = 2020

    li_years = []
    li_years_clean = []

    o_file = open(pu_rom_file, mode='rb')
    s_data_chunk = o_file.read(i_bytes)
    o_file.close()

    o_match = re.search(r'(\d{4})', s_data_chunk)

    if o_match:
        for s_year in o_match.groups():
            li_years.append(int(s_year))

    for i_year in li_years:
        if i_min_year <= i_year <= i_max_year:
            li_years_clean.append(i_year)

    return li_years_clean


# Helper Functions
#=======================================================================================================================
def _dat_vertical_parse(ls_lines, s_section, s_mode='single'):
    """Function to parse a group of lines which contains different information about the same item.

    So, the information follows a pattern similar to:

        field_1 data_a
        field_1 data_b
        field_2 data_c
        ...

        ls_lines: a list containing the individual lines as strings.

        s_section: name of the section (in the above example s_section = field_1, for example).

        s_mode: 'single', each field exists once and the function returns its data as a string.
                'multi', each field exists several times and the function returns its data as a list of strings.

        @rtype : string or list of strings
    """

    ls_data = []
    s_data = ''

    # Adding a space to the section because it has to exist a space between the section and the data.
    s_section += ' '

    for s_line in ls_lines:
        s_line = s_line.strip()

        if s_line.find(s_section) == 0:
            i_start_pos = len(s_section)
            s_data = s_line[i_start_pos:]
            s_data = s_data.strip()
            s_data = s_data.strip('"')
            ls_data.append(s_data)

    if s_mode == 'single':
        x_output = s_data
    elif s_mode == 'multi':
        x_output = ls_data
    else:
        raise Exception('Error: %s mode for _dat_vertical_parse() NOT known.' % s_mode)

    return x_output


def _dat_horizontal_parse(s_line, s_start, s_end):
    """
    Function to parse a SINGLE line containing information about a particular item.

    So, the information follows a pattern similar to:

        a_start DATA_A a_end b_start DATA_B b_end...

    :param s_line: string containing the line to be parsed.

    :param s_start: leading string for data. In the above example: "a_start", "b_start"...

    :param s_end: ending string for data. In the above example: "a_end", "b_end"...

    Comment: Typically, all the items inside the line are unique, so there is no need to 'multi' parameter like in
    _dat_vertical_parse() function.

        @rtype: string

    """

    s_output = ''

    if s_line.find(s_start) != -1:
        i_start_pos = s_line.find(s_start) + len(s_start)
        i_end_pos = s_line.find(s_end, i_start_pos)

        if i_end_pos != -1:
            s_output = s_line[i_start_pos:i_end_pos]

    # It shouldn't appear extra spaces around the real data but just in case...
    s_output = s_output.strip()
    s_output = s_output.strip('"')
    s_output = s_output.strip()

    return s_output


#def _sum_crc32(u_crc32_a, u_crc32_b):
#    """
#    Function to create the sum of two crc32 strings. Since the crc32 have to contain just 8 characters, when you sum two
#    crc32s big enough to generate a 9 character *crc32*, only the right 8 characters are returned. i.e. If you add
#    'ffffffff' + '00000001' = '100000000' So the output of this function would be '00000000'.
#
#    :param u_crc32_a: First crc32 to sum. i.e. '12345678'.
#
#    :param u_crc32_b: Second crc32 to sum. i.e. '1a2b3c4d'.
#
#    :return: A string with the truncated sum of the two crc32s. i.e. '2c5f92c5'.
#    """
#
#    #print '   %s + %s' % (s_crc32_a, s_crc32_b)
#
#    u_crc32_a = '0x%s' % u_crc32_a
#    u_crc32_b = '0x%s' % u_crc32_b
#
#    i_int_a = int(u_crc32_a, 16)
#    i_int_b = int(u_crc32_b, 16)
#
#    i_sum = i_int_a + i_int_b
#
#    h_crc32_sum = hex(i_sum)
#    u_crc32_sum = str(h_crc32_sum)[2:].rjust(8, '0')[-8:]
#
#    return u_crc32_sum