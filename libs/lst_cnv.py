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


# WAHCADE
#--------
def wahcade_read():
    pass


def wahcade_write():
    pass