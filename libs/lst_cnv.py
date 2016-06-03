import codecs

import files


def lconvert(pu_src_fmt=None, pu_dst_fmt=None, pu_src_file=None, pu_dst_file=None, pu_dat=None, pb_print=False):
    """
    Function to convert list files between different front-end formats.
    :param pu_src_fmt:
    :param pu_dst_fmt:
    :param pu_src_file:
    :param pu_dst_file:
    :param pb_print:
    :return:
    """

    # Parameter validation

    return 'foo'

# READ/WRITE FUNCTIONS FOR DIFFERENT FORMATS
#=======================================================================================================================
# There are two different functions for each favourites list format:
#
#     1. A "xxx_read" list that reads a favourite list in the format xxx (wahcade or MALA for example) and outputs a dat
#        container object from hqlib with the full game objects found. #TODO: I'd include the not-found games also.
#
#     2. A "xxx_write" list that receives a game container object from hqlib and generates a favourites list in the xxx
#        format.


def lst_read(pu_file='', pu_format=''):
    """
    Function to read the romsets present in a list.

    :param pu_file:
    :param pu_format:
    :return:
    """

    if pu_format == 'wahcade':
        lu_romsets_found = _wahcade_read(pu_file)

    else:
        raise Exception('Unknown format "%s"' % pu_format)

    return lu_romsets_found


# WAHCADE
#--------
def _wahcade_read(pu_file=u''):
    """
    Function to read a list of games from a WahCade list file and return a list of games found in a database.

    The full format of the wahcade list file is found at:

    https://github.com/sairuk/wahcade/blob/68798363289c057020f9fa690420a23daa798365/doc/file_formats/gamelist_format.txt

        line  desc
        ----  ----
        1     ROM NAME
        2     RomSet Name
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

    :param po_db: Database object to look games for. Defined at roms.py.

    :return:
    """

    lu_romsets_found = []

    # Getting the list of ROMs in the file
    #-------------------------------------
    o_file = codecs.open(pu_file, 'r', 'utf8')

    while True:
        lu_lines = files.read_nlines(o_file, 13)

        if not lu_lines:
            break
        else:
            u_romset_name = lu_lines[0]
            lu_romsets_found.append(u_romset_name)

    o_file.close()

    return lu_romsets_found


def wahcade_write(pu_file='', plo_game_container=None):
    pass