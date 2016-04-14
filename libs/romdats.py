#!/usr/bin/env
# -*- coding: utf-8 -*-

import codecs
import copy
import datetime
import xml.etree.cElementTree
import os  # OS utils


# Constants
#=======================================================================================================================
_u_VERSION = u'2015-04-18'                                          # Version of the library
_tu_GAME_SEARCH_FIELDS = (u'crc32', u'description', u'md5', u'name', u'sha1')    # Valid fields to get games by
#-----------------------------------------------------------------------------------------------------------------------


class Filter:
    """
    Class to store information about a filter that will be applied later to GameContainer.
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


class GameContainer:
    """
    Class to store a list of games, each game can contain different ROM files data. The information can be read/write to
    disk ROM file objects.
    """

    def __init__(self, u_file=u'', u_log=''):

        # TODO: GameContainer should contain an internal registry with all the manipulations suffered by the object so
        #       when you export the file to disk you know the information is not comming directly from the RAW dat file.

        # Variable definition
        self.i_games = 0          # number of games stored
        self.i_position = None    # Game position for the iterator

        self.u_name = u''         # internal name of the dat file.
        self.u_description = u''  # description of the dat file.
        self.u_version = u''      # version of the dat file (usually a date).
        self.u_comment = u''      # extra comment for the dat file.
        self.u_type = u''         # type of DAT file the data comes from.
        self.u_author = u''       # Author of the dat.

        self.lo_games = []        # list of game objects inside the dat file

        self._lu_log = []          # Internal log

        if u_file != u'':
            self.read_from_dat(u_file)

    def __str__(self):
        u_output = u''
        u_output += u'[Game container]\n'
        u_output += u'       u_name: %s\n' % self.u_name
        u_output += u'u_desc: %s\n' % self.u_description
        u_output += u'    u_version: %s\n' % self.u_version
        u_output += u'    u_comment: %s\n' % self.u_comment
        u_output += u'       u_type: %s\n' % self.u_type
        u_output += u'     u_author: %s\n' % self.u_author
        u_output += u'      i_games: %i\n' % self.i_games

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

    def _add_game(self, o_game):
        """
        Internal method to add games to the container WITHOUT any kind of duplicity or other kind of check.

        :param o_game:
        """

        self.lo_games.append(o_game)
        self.i_games += 1

    def add_game(self, o_game):
        """
        Method to add a new game to the container.

        :param o_game: Game to add.

        :return: True if the game was successfully added, false in other case.
        """

        b_added = False

        if (o_game is not None) and (not self.id_exists(o_game.u_id)):
            self._add_game(o_game)
            b_added = True

        return b_added

    def _duplicates_found(self):
        """
        Method to check the existence of duplicated ids which will break the whole idea of this project.

        :return: True if duplicates were found, False in other case.
        """

        lu_ids = []

        for o_game in self.lo_games:
            lu_ids.append(o_game.u_id)

        su_unique_ids = set(lu_ids)

        # Since I want to be sure that I found the errors, by default I assume there are duplicated Ids.
        b_duplicates = True

        if len(lu_ids) == len(su_unique_ids):
            b_duplicates = False

        return b_duplicates

    def _permanent_rom_list_header(self):
        """
        Method to build the file header for permanent ROM lists.

        :return: A unicode string containing the header of the permanent rom list.
        """

        # File header generation
        u_header = u''
        u_header += u'# Permanent ROM list. Data comes from this dat file:\n'
        u_header += u'#\n'
        u_header += u'#        Name: %s\n' % self.u_name
        u_header += u'# Description: %s\n' % self.u_description
        u_header += u'#     Version: %s\n' % self.u_version
        u_header += u'#     Comment: %s\n' % self.u_comment
        u_header += u'#      Author: %s\n' % self.u_author
        u_header += u'#\n'
        u_header += u'# Id\tName\n'

        return u_header

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
        other GameContainer object.

        :param o_game_container: External GameContainer object.
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

        self._log(u_log_message)

    def filter(self, o_filter):
        """
        Method to filter in/out games depending on a field name and allowed/disallowed values for that field.

        :param u_attribute: Name of the field to filter by. i.e. 'i_year'.

        :param lu_field_values: List of values we're using to filter. i.e. (1989, 1990, 1993) to filter by years

        :param u_method: 'in', 'out' to return the games the games that match the values of lu_field_values or the games
                         that DON'T match the values of lu_field_values.

        :return: A list of games that match or don't match your filter criteria.
        """

        u_log_in_start = u'Filter IN:'
        u_log_out_start = u'Filter OUT:'

        u_log_message = u''
        u_log_message += u'Attribute="%s" ' % o_filter.u_attribute
        u_log_message += u'Method="%s" ' % o_filter.u_method
        u_log_message += u'Value(s)="%s"' % str(o_filter.lx_values)

        # Two GameContainer objects are created to store the games that matched the filter and the games that didn't
        # matched it.
        o_matched_container = GameContainer()
        o_matched_container.copy_metadata_from(self)
        o_matched_container.modify_metadata(u'FILTER(', u')')
        o_matched_container._log(u'%s %s' % (u_log_in_start, u_log_message))

        o_unmatched_container = GameContainer()
        o_unmatched_container.copy_metadata_from(self)
        o_unmatched_container._log(u'%s %s' % (u_log_out_start, u_log_message))

        for o_game in self:

            # The first thing to do is (to try) to obtain o_game.<u_attribute>
            try:
                 x_value = getattr(o_game, o_filter.u_attribute)

            except AttributeError:
                raise Exception('ERROR: You are trying to access the unknown attribute "%s"' % o_filter.u_attribute)

            # Then we can filter. Since we are filtering already unique games present in our container, we don't need
            # to perform any uniqueness test while adding the games to the matched/unmatched containers. So, we use the
            # method _add_game which doesn't perform that test and is much faster than the equivalent one with test
            # add_game.
            if o_filter.u_method == 'equals':
                if x_value in o_filter.lx_values:
                    o_matched_container._add_game(o_game)

                else:
                    o_unmatched_container._add_game(o_game)

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

        :param s_mode: Which mode should be used to assign the games an id. Valid modes are defined in Game object.

        :return Nothing.
        """

        for o_game in self.lo_games:
            o_game.set_id(s_mode)

    def get_by_id(self, u_id):
        """
        Method that returns the game object corresponding to certain id.

        :param u_id: Identification of the game it's going to be returned. i.e. '12345678'.

        :return A game object
        """

        # TODO: Avoid the usage of filter.
        # I think the performance of this function through filters is much slower than actually checking the games one
        # by one. On the other hand, using filters I can: a) obtain multiple results which actually is a way to check
        # for duplicates present in the DB. But I'm not sure if that's a good idea.

        o_filter = Filter('u_id', 'equals', u_id)
        o_games_matched, o_games_not_matched = self.filter(o_filter)

        # If no games matched, None is output
        if len(o_games_matched) == 0:
            o_found_game = None

        # If one game was found, it's output
        elif len(o_games_matched) == 1:

            # I don't like this cheesy way to obtain the first (and only) element matched, but it works
            for o_game_matched in o_games_matched:
                o_found_game = o_game_matched
                break
        else:
            raise Exception('ERROR: Filter returns more than one result for one id')

        return o_found_game

    def get_by_ids(self, lu_ids):
        """
        Method to obtain a container of games from a list of Ids. If an output file is specified, the obtained results
        are sorted alphabetically and written to that file including information about the DB that was used to try to
        match the Ids.

        :param lu_ids: List containing the Ids to search. i.e. ['12345678', 'aaaaaaaa', 'a0b1c2d3e4']

        :return: A game container (sub-container if you wish), containing just the games found with the required IDs.
        """

        o_filter = Filter('u_id', 'equals', *lu_ids)
        o_games_in, o_games_out = self.filter(o_filter)

        return o_games_in

    def get_by_description(self, u_description):
        """
        Method that returns the game object corresponding to certain name.

        :param u_description: Name of the game that is going to be returned. i.e. 'Super Mario World (USA)'

        :return: A game object
        """

        # TODO: Avoid the usage of filter.
        # I think the performance of this function through filters is much slower than actually checking the games one
        # by one. On the other hand, using filters I can: a) obtain multiple results which actually is a way to check
        # for duplicates present in the DB. But I'm not sure if that's a good idea.

        o_filter = Filter('u_desc', 'equals', u_description)
        o_games_matched, o_games_not_matched = self.filter(o_filter)

        # If no games are present in the "found games container
        if o_games_matched.i_games == 0:
            o_found_game = None

        elif o_games_matched.i_games == 1:

            # I don't like this method of obtaining the first game of the container, but it's simple and it works
            for o_game_matched in o_games_matched:
                o_found_game = o_game_matched
                break

        else:
            raise Exception('ERROR: Filter returns more than one result for one description')

        return o_found_game

    def get_by_descriptions(self, lu_descriptions):
        """
        Method to obtain a sub-container of from a list of names (actually descriptions since name is the name of the
        ROM, not the real name of the game. For most console material, they are the same but for the case of Mame, short
        name is just 8 characters long while description is the real name of the game).

        This method is analogue to get_by_ids method.

        :param lu_descriptions: List containing the Ids to search. i.e. ['12345678', 'aaaaaaaa', 'a0b1c2d3e4']

        :return: A dictionary containing the matched games. i.e. {'12345678}': <game 1327>, 'aaaaaaaa': <game 148>}
        """

        # First we create an empty container
        o_games_found = GameContainer()
        o_games_found.copy_metadata_from(self)

        for u_description in lu_descriptions:
            o_game = self.get_by_description(u_description)
            o_games_found.add_game(o_game)

        return o_games_found

    def get_game_by_field(self, u_field=None, u_search_string=None, b_discard_irrelevant=False):
        """
        Quick method to obtain the first game that matches the required valued in the required field.

        :param u_field: Name of the field of the game to search in. i.e. 'i_crc32'
        :param u_search_string: String that needs to match. i.e. '12345678'
        :param b_discard_irrelevant: When searching by hashes, do you want to discard irrelevant files? (i.e. .cue)
        :return:
        """
        # Parameters validation
        if u_field not in _tu_GAME_SEARCH_FIELDS:
            raise Exception('ERROR: Unknown field "%s". Valid options are "%s"' % (u_field, str(_tu_GAME_SEARCH_FIELDS)))

        # Initialization
        o_first_game = None

        if u_search_string:
            for o_game in self:
                b_game_matched = False

                # Hash searches are case insensitive
                if u_field in (u'crc32', u'md5', u'sha1'):
                    du_hashes = o_game.get_hashes(b_discard_irrelevant=b_discard_irrelevant)
                    u_hash = du_hashes[u_field]
                    if u_hash.lower() == u_search_string.lower():
                        b_game_matched = True

                # While name and description searches are case sensitive
                else:
                    if u_field == u'description' and o_game.u_description == u_search_string:
                        b_game_matched = True
                    elif u_field == u'name' and o_game.u_name == u_search_string:
                        b_game_matched = True

                if b_game_matched:
                    o_first_game = o_game
                    break

        return o_first_game

    def import_extra_data_from_csv(self, u_file):
        """
        Method to import EXTRA DATA (JUST EXTRA META-DATA), like year, manufacturer, genre... from a csv file IN MY OWN
        AND SPECIFIC FORMAT. Only csv files previously written with this library should be loaded

        :param u_file: CSV file name to import. i.e. '/home/john/my-megadrive-games.csv'

        :return: Nothing
        """

        o_file = codecs.open(u_file, 'rb', 'utf8', 'ignore')

        # First line is csv generator comment, second line is empty
        o_file.readline()
        o_file.readline()

        self.u_name = o_file.readline().partition(':')[2].strip()
        self.u_description = o_file.readline().partition(':')[2].strip()
        self.u_version = o_file.readline().partition(':')[2].strip()
        self.u_comment = o_file.readline().partition(':')[2].strip()
        self.u_author = o_file.readline().partition(':')[2].strip()

        # One extra empty line and another one with column names
        o_file.readline()
        o_file.readline()

        # Real data
        for u_line in o_file:

            lu_elements = u_line.split(u'\t')
            lu_clean_elements = []
            for u_element in lu_elements:
                u_clean_element = u_element.strip()
                u_clean_element = u_clean_element.strip('"')
                u_clean_element = u_clean_element.strip()
                lu_clean_elements.append(u_clean_element)

            # TODO: Check which fields could be interesting to store and add them to this parser
            u_id = lu_clean_elements[0]

            # The id is not needed, it's just present in the csv to help people to manually update its information.
            #u_desc = lu_clean_elements[1]

            i_year = int(lu_clean_elements[2])
            u_manufacturer = lu_clean_elements[3]

            # We get the right game from the database using the id stored in the CSV file.
            o_game = self.get_by_id(u_id)

            # Then, we simply need to update its information with the one coming from the CSV file
            if o_game is not None:
                if i_year != 0:
                    o_game.i_year = i_year

                if u_manufacturer != u'':
                    o_game.u_manufacturer = u_manufacturer

            # If the game wasn't found, we add the line to an error report
            else:
                # TODO: Add the "game not found" report code.
                pass

        # Including the operation into the internal log
        self._log('Meta-Data imported from CSV file "%s"' % u_file)

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

        # Loading the file using the different readers depending on the format parameter
        if u_format == 'cmp':
            self._read_from_cmp(pu_file)
        elif u_format == 'xml':
            self._read_from_xml(pu_file)
        else:
            raise Exception('Unknown dat format "%s"' % u_format)

        # After loading the games from disk, the list is sorted
        self._sort()

        # I think it makes sense to make the games get an id using an automatic method when loading the dat. Then,
        # later, the user could have change that method calling by himself --externally-- the get_id method.

        # Redump DBs --> sum_crc32
        if self.u_author == u'redump.org':
            self.set_id('sum_crc32')

        # No-intro DBs --> sum_crc32
        elif self.u_comment.find(u'no-intro') != -1:
            self.set_id('sum_crc32')

        # MAME DB --> short_name
        elif self.u_name == u'mame':
            self.set_id('short_name')

        else:
            s_output = 'Unknown dat format, not "redump.org", not "no-intro", not "mane"'
            raise Exception(s_output)

        self._log(u'Read from "%s" file "%s"' % (u_format, pu_file))

        # Now that the game container has been populated from disk, is the time to check that we don't have duplicated
        # Ids
        if self._duplicates_found():
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

            # Game data
            if u_line.find('game (') == 0:
                b_game_mode = True
                continue

            if b_game_mode and u_line.find(')') == 0:
                u_game_name = _dat_vertical_parse(lu_game_strings, 'name')
                u_game_description = _dat_vertical_parse(lu_game_strings, 'description')
                u_game_manufacturer = _dat_vertical_parse(lu_game_strings, 'manufacturer')
                u_game_year = _dat_vertical_parse(lu_game_strings, 'year')
                if u_game_year == u'':
                    u_game_year = u'0'

                lu_game_roms = _dat_vertical_parse(lu_game_strings, 'rom', 'multi')

                o_dat_game = Game(u_game_name, u_game_description)
                o_dat_game.i_year = int(u_game_year)
                o_dat_game.s_manufacturer = u_game_manufacturer

                for s_game_rom in lu_game_roms:
                    o_dat_game.i_roms += 1

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
                    o_dat_game.lo_roms.append(o_rom)

                # We add the game to the container without any kind of check, we will do it later.
                self._add_game(o_dat_game)

                lu_game_strings = []
                b_game_mode = False
                continue

            # Game mode actions
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

        # Game information
        for o_game_elem in o_xml_root.findall('game'):
            u_game_name = o_game_elem.attrib['name']
            u_game_description = u_game_name

            o_dat_game = Game(u_game_name, u_game_description)

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
            self._add_game(o_dat_game)

    def export_to_file(self, u_file, u_format, o_filter=None):
        """
        Method to export PART OF THE DATA contained in the Dat container to disk using different formats. I highlight
        PART OF THE DATA since not all of it is saved, just the basic information about games, BUT NOT about their
        ROMs.

        :param u_file: Name of the output file to write. i.e. "/home/john/my-dat.dat"

        :param u_format: Format to save the data in. Valid values, so far, are: 'mini-list',

        :return: Nothing.
        """

        if o_filter is not None:
            # todo: make this method work with filters
            pass

        o_file = open(u_file.encode('utf8', 'strict'), 'w')

        if u_format == u'mini':
            self._export_to_mini(o_file)
        elif u_format == u'csv':
            self._export_to_csv(o_file)
        else:
            raise Exception('Unknown format to save the GameContainer "%s"' % u_format)

        o_file.close()

    def _export_to_csv(self, o_file):

        """
        Method to save the dat file to plain csv. For compatibility reasons, it's much better to separate the values
        with commas (instead of semicolons) and that forces you to add extra double quote symbols around text fields;
        which in this case, are all of them.

        :param o_file: Name of the file to write. i.e. '/home/john/my-dat.csv'

        :return: Nothing.
        """

        # TODO: Create a read_from_csv method and use, obviously, the same column order.

        u_header = u''

        u_header += u'# CSV dat generated by romdats.py version %s\n' % _u_VERSION
        u_header += u'#\n'
        u_header += u'#        Name: %s\n' % self.u_name
        u_header += u'# Description: %s\n' % self.u_description
        u_header += u'#     Version: %s\n' % self.u_version
        u_header += u'#     Comment: %s\n' % self.u_comment
        u_header += u'#      Author: %s\n' % self.u_author
        u_header += u'#\n'

        u_header += u'# Id\t'
        u_header += u'Name\t'
        u_header += u'Description\t'
        u_header += u'Year\t'
        u_header += u'Manufacturer\n'

        o_file.write(u_header.encode('utf8', 'strict'))

        for o_game in self:
            u_line = u'%s\t%s\t%i\t%s\n' % (o_game.u_id,
                                            o_game.u_description,
                                            o_game.i_year,
                                            o_game.u_manufacturer)

            o_file.write(u_line.encode('utf8', 'strict'))

    def _export_to_mini(self, o_file):
        """
        Method to export the game container to a mini-format that will just contain a header indicating which dat file
        the data comes from and a list of games containg just: a) the id of the game, b) the description of the game.

        :param o_file: Name of the file to write. i.e. '/home/john/my_games.txt'

        :return: Nothing.
        """

        u_header = u''
        u_header += u'# File generated by romdats.py version %s\n' % _u_VERSION
        u_header += u'#\n'
        u_header += u'#        Name: %s\n' % self.u_name
        u_header += u'# Description: %s\n' % self.u_description
        u_header += u'#     Version: %s\n' % self.u_version
        u_header += u'#     Comment: %s\n' % self.u_comment
        u_header += u'#        Type: %s\n' % self.u_type
        u_header += u'#      Author: %s\n' % self.u_author
        u_header += u'#       Games: %i\n' % self.i_games
        u_header += u'#%s\n' % (u'=' * 79)

        for u_line in self._lu_log:
            u_header += u'# %s\n' % u_line

        u_header += u'#%s\n' % (u'=' * 79)
        u_header += u'# Id\tTitle\n'
        u_header += u'#%s\n' % (u'=' * 79)

        o_file.write(u_header.encode('utf8', 'strict'))

        for o_game in self:
            u_line = u'%s\t%s\n' % (o_game.u_id.ljust(8), o_game.u_description)

            o_file.write(u_line.encode('utf8', 'strict'))

    def _log(self, u_message):
        """
        Method to internally log information about the manipulations suffered by the GameContainer
        :param u_message:
        :return:
        """

        o_timestamp = datetime.datetime.now()
        u_new_line = u'%s\t%s' % (o_timestamp.strftime(u'%d-%m-%Y %H:%M:%S.%f'), u_message)

        self._lu_log.append(u_new_line)

    def _sort(self):
        # Sorting of the list based on the game description (which is more reliable than the short name of the game)
        self.lo_games.sort(key=lambda o_game: o_game.u_desc.encode('utf8', 'strict'), reverse=False)


class Game:

    _i_id = 0

    def __init__(self, u_name, u_description):

        Game._i_id += 1

        # Variable definition
        self._i_id = Game._i_id  # Position number. It will be 0, 1, 2, 3... for the consecutive games in the dat.
        self.i_roms = 0              # Number of ROMs that make the full game.
        self.i_year = 0              # Year the game was published in (MAME dat support only, AFAIK).
        self.lo_roms = []            # List containing all the ROM information objects.
        self.u_desc = u''            # Usually, the full and long name of the game i.e. 'Super Mario World (Europe)'.
        self.u_id = u''              # Unique id string of the game used to identify the game.
        self.u_mfr = u''             # Manufacturer, company that programmed the game (MAME dat support only, AFAIK).
        self.u_name = u''            # Usually, the file name for the game. MAME uses a short 8 char or less name here.

        # Unused properties by now
        self.lu_languages = []    # List of iso codes (3 letters) for languages included
        self.lu_countries = []    # List of iso codes (3 letters) for countries where the game was published

        # Variable population (just the very basic information is needed).
        self.u_name = u_name
        self.u_desc = u_description

    def __str__(self):
        u_output = u''
        u_output += u'[Game]\n'
        u_output += u'  u_name: %s\n' % self.u_name
        u_output += u'  u_desc: %s\n' % self.u_desc
        u_output += u'  i_year: %i\n' % self.i_year
        u_output += u'   u_mfr: %s\n' % self.u_mfr
        u_output += u'    u_id: %s\n' % self.u_id
        u_output += u'  i_roms: %i\n' % self.i_roms
        u_output += u' lo_roms:\n'

        i_roms = 0

        for o_rom in self.lo_roms:
            i_roms += 1
            i_line = 0

            u_rom_text = str(o_rom).decode('utf8')

            # Modification of u_rom_text to show the rom number
            u_rom_text = u_rom_text.replace(u'[_Rom]', u'[_Rom] #%i' % (i_roms - 1))

            lu_rom_raw_lines = u_rom_text.splitlines()
            lu_rom_clean_lines = []

            for u_line in lu_rom_raw_lines:
                i_line += 1

                if i_line == 1:
                    u_extra_spaces = u' ' * 10
                else:
                    u_extra_spaces = u' ' * 10

                lu_rom_clean_lines.append('%s%s' % (u_extra_spaces, u_line))

            u_output += u'%s\n\n' % (u'\n'.join(lu_rom_clean_lines))

        return u_output.encode('utf8')

    def export(self, u_format):
        """
        Method to export the data of a game to a particular format.

        :param u_format:

        :return:
        """

        if u_format == u'simple':
            u_output = self._export_simple()
        else:
            raise Exception('Unknown export format for Game object "%s"' % u_format)

        return u_output

    def get_hashes(self, b_discard_irrelevant=False):
        """
        Method to obtain the COMPOUND hash of the game. It means the hash of *all* the ROMs included in the game will be
        summed. For example, if the game contains two ROMs:

            - Game A
                - ROM a1: CRC32 = 01020304
                - ROM a2: CRC32 = 0a0b0c0d

        The output of this function will be 01020304 + 0a0b0c0d (remember that hash values are hex representations of
        numbers).

        Two comments about the behavior of the function:

            1. Different hashing methods are used: crc32, md5, sha1

            #TODO: Explain b_discard_irrelevant parameter

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
        i_crc32_base10_value = 0
        i_md5_base10_value = 0
        i_sha1_base10_value = 0

        # The first step is to create a list with the real ROMs, avoiding meta-data ones like .cue files
        lo_relevant_roms = []

        for o_rom in self.lo_roms:

            # If discard is not activated, every ROM will be considered
            if not b_discard_irrelevant:
                lo_relevant_roms.append(o_rom)

            # In other case, ROMs are filtered based on the file extension
            else:
                if u'.' in o_rom.u_name:
                    u_ext = o_rom.u_name.rpartition('.')[2].lower()

                    if u_ext not in ['cue']:
                        lo_relevant_roms.append(o_rom)

        for o_rom in lo_relevant_roms:

            #print o_rom

            # Rom hash addition
            i_crc32_base10_value += int(o_rom.u_crc32, 16)
            i_md5_base10_value += int(o_rom.u_md5, 16)
            i_sha1_base10_value += int(o_rom.u_sha1, 16)

        # Converting base10 values to hex-string format
        u_crc32 = '%x' % i_crc32_base10_value
        u_md5 = '%x' % i_md5_base10_value
        u_sha1 = '%x' % i_sha1_base10_value

        # Resizing hashes to proper length (crc32 = 8 chars, md5 = 32 chars, sha1 = 40 chars)
        u_crc32 = u_crc32[-8:]
        u_crc32 = u_crc32.ljust(8, '0')

        u_md5 = u_md5[-32:]
        u_md5 = u_md5.ljust(32, '0')

        u_sha1 = u_sha1[-40:]
        u_sha1 = u_sha1.ljust(40, '0')

        #print 'crc32: %s' % u_crc32
        #print '  md5: %s' % u_md5
        #print ' sha1: %s' % u_sha1

        return {'u_crc32': u_crc32, 'u_md5': u_md5, 'u_sha1': u_sha1}

    def _export_simple(self):
        """
        Method to export the games in the most simple way possible, just the identification and the name separated by a
        tabulator.

        :return: The above data in unicode encoding, almost ready to be printed or saved to disk.
        """

        u_output = '%s\t%s' % (self.u_id, self.u_name)

        return u_output

    def set_id(self, s_mode):
        """
        Method to set the unique identifier string of the game.

        It should be basically the crc of the first ROM of the game but in certain cases (disc based games dat from
        redump.org or MAME emulator games) it's better to choose a different string like the crc of the first ROM that
        actually contains information (the second one for redump games because the first one correspond to a .cue file
        with just the structure of the disc) or simply the short name of the game (for example in MAME where games
        has an 8 character identifier string that doesn't change through the time even some of the ROM data could do).
        """

        # TODO: Make use of internal get_hash method

        # Mode to obtain the CRC32 from the first ROM with real DATA. I need to check if ROM order change from DAT
        # version to DAT version, that would make this method useless.
        if s_mode == 'first_crc32':
            try:
                o_first_rom = self.lo_roms[0]
                u_rom_extension = o_first_rom.u_name.rpartition('.')[2]

                # 
                if u_rom_extension.lower() != u'cue':
                    self.u_id = o_first_rom.s_crc
                else:
                    try:
                        self.u_id = self.lo_roms[1].u_crc
                    except IndexError:
                        self.u_id = ''

            except IndexError:
                self.u_id = ''

        # Mode to obtain the id directly from the short name of the game
        elif s_mode == 'short_name':
            self.u_id = self.u_name

        # Mode to sum all the crc32 of each ROM with dat (.cue files are discarded, maybe other file extensions in the
        # future) and assign that number as the identification for the game.
        #
        # EXTRA INFO ABOUT .cue EXCLUSION:
        # If the file name of the ROMs with real data change, the content of the cue is going to change, hence its
        # CRC32. That leads to the unwanted situation where, just by changing the file names of the ROMs, the
        # identification code of the game changes. To solve that, .cue files MUST NOT be considered in global CRC32
        # calculation.
        elif s_mode == 'sum_crc32':
            s_accumulated_cbc32 = '00000000'

            for o_rom in self.lo_roms:
                u_rom_extension = o_rom.u_name.rpartition('.')[2]

                if u_rom_extension.lower() != u'cue':
                    s_accumulated_cbc32 = _sum_crc32(s_accumulated_cbc32, o_rom.u_crc32)

            self.u_id = s_accumulated_cbc32

        # Finally, the error handling code.
        else:
            s_output = 'Unknown identification method for a game object "%s".' % s_mode
            raise Exception(s_output)


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
        u_output += u'  u_crc32: %s\n' % self.u_crc32
        u_output += u'    u_md5: %s\n' % self.u_md5
        u_output += u'   u_name: %s\n' % self.u_name
        u_output += u'   u_sha1: %s\n' % self.u_sha1

        return u_output.encode('utf8')


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


def _sum_crc32(u_crc32_a, u_crc32_b):
    """
    Function to create the sum of two crc32 strings. Since the crc32 have to contain just 8 characters, when you sum two
    crc32s big enough to generate a 9 character *crc32*, only the right 8 characters are returned. i.e. If you add
    'ffffffff' + '00000001' = '100000000' So the output of this function would be '00000000'.

    :param u_crc32_a: First crc32 to sum. i.e. '12345678'.

    :param u_crc32_b: Second crc32 to sum. i.e. '1a2b3c4d'.

    :return: A string with the truncated sum of the two crc32s. i.e. '2c5f92c5'.
    """

    #print '   %s + %s' % (s_crc32_a, s_crc32_b)

    u_crc32_a = '0x%s' % u_crc32_a
    u_crc32_b = '0x%s' % u_crc32_b

    i_int_a = int(u_crc32_a, 16)
    i_int_b = int(u_crc32_b, 16)

    i_sum = i_int_a + i_int_b

    h_crc32_sum = hex(i_sum)
    u_crc32_sum = str(h_crc32_sum)[2:].rjust(8, '0')[-8:]

    return u_crc32_sum

