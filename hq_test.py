#!/usr/bin/env python
# -*- coding: utf-8 -*-

import libs

# CONSTANTS
#=======================================================================================================================
u_PROG_NAME = u'HQ TEST'
u_PROG_VERSION = u'v2015.09.27'
tu_MODULES = ('argparse', 'hqlib')


# HELPER FUNCTIONS
#=======================================================================================================================
def _check_module(u_module):
    """
    Function to check if a particular module is installed in the system or not.

    :param u_module: Name of the module. i.e. 'image', 'argparse'

    :return: True if the module is correctly installed in the system, False in other case.
    """
    u_code = u'import %s' % u_module

    try:
        exec u_code
        b_module_imported = True

    except ImportError:
        b_module_imported = False

    return b_module_imported

# MAIN CODE
#=======================================================================================================================
if __name__ == '__main__':
    print libs.strings.hq_title(u_PROG_NAME, u_PROG_VERSION)

    i_ok_mods = 0
    i_er_mods = 0
    i_tot_mods = len(tu_MODULES)

    for u_module in tu_MODULES:
        if _check_module(u_module):
            i_ok_mods += 1
            u_output = u'%s %s found' % (libs.cons.u_OK_TEXT, u_module)
        else:
            i_er_mods += 1
            u_output = u'%s %s not found' % (libs.cons.u_ER_TEXT, u_module)

        print u_output

    if i_er_mods:
        u_output = u'\n%i missing module(s). Please, install them before running %s' % (i_er_mods, libs.cons.u_SET_NAME)
    else:
        u_output = u'\nGreat! all required modules installed. %s should work fine!' % libs.cons.u_SET_NAME

    print u_output