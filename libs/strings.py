"""
Library with string functions
"""


def title(u_string):
    """
    Function to decorate a string as a title.

    :param u_string: Text to include in the title. i.e. 'This is the main title'

    :return: Decorated string. i.e. 'THIS IS THE MAIN TITLE'
                                    '======================'
    """

    u_output = '%s\n%s\n' % (u_string, '=' * len(u_string))

    return u_output
