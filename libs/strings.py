import cons

"""
Library with string functions
"""

def hq_title(u_prog_name=u'', u_prog_version=u''):
    """
    Function to decorate a string as a hq_title.

    :param u_string: Text to include in the hq_title. i.e. 'This is the main hq_title'

    :return: Decorated string. i.e. 'THIS IS THE MAIN TITLE'
                                    '======================'
    """

    u_title_text = '%s - %s (%s)' % (cons.u_SET_NAME, u_prog_name, u_prog_version)

    u_output = '%s\n%s\n' % (u_title_text, '=' * len(u_title_text))

    return u_output
