"""
Library with file tools.
"""

import os


class FilePath:
    """
    Class to handle file information: FilePath name, root, extension, etc...
    """
    def __init__(self, *u_path):
        self.u_path = os.path.join(*u_path)

        self.u_root = os.path.dirname(self.u_path)
        self.u_file = os.path.basename(self.u_path)
        self.u_name = self.u_file.rpartition('.')[0]
        self.u_ext = self.u_file.rpartition('.')[2]

    def __str__(self):
        u_output = u'[FilePath]\n'
        u_output += u'  Path: %s\n' % self.u_path
        u_output += u'  Root: %s\n' % self.u_root
        u_output += u'  FilePath: %s\n' % self.u_file
        u_output += u'  Name: %s\n' % self.u_name
        u_output += u'   Ext: %s\n' % self.u_ext

        return u_output.encode('utf8')

    def absfile(self):
        """
        Method that returns a new FilePath object with the path normalized.
        :return: a FilePath object.
        """
        u_abs_path = os.path.abspath(self.u_path).decode('utf8')
        o_abs_file = FilePath(u_abs_path)
        return o_abs_file

    def content(self, b_recursive=False):
        """
        Method that returns a list with the contents of the file object. If the file object is a file, the content will
        be always empty since a file doesn't contain other files or directories.

        :param b_recursive: If True, the content search will be recursive.

        :return: A list of FilePath objects
        """

        lo_file_objects = []

        if self.is_dir():
            if not b_recursive:
                for u_element in os.listdir(self.u_path):
                    u_full_path = os.path.join(self.u_path, u_element)
                    o_file_object = FilePath(u_full_path)
                    lo_file_objects.append(o_file_object)

            else:
                #TODO: Add recursive mode
                pass

        return lo_file_objects

    def exists(self):
        """
        Method that checks if the path exists or not.
        :return: True/False
        """
        if os.path.exists(self.u_path):
            b_exists = True
        else:
            b_exists = False

        return b_exists

    def root_exists(self):
        """
        Method to check if the root path exists or not.
        :return: True/False
        """
        if os.path.isdir(self.u_root):
            b_exists = True
        else:
            b_exists = False

        return b_exists

    def root_prepend(self, *pu_path):
        """
        Method to add extra elements at the beginning of the root. i.e. cc/dd.jpg -> aa/bb/cc/dd.jpg
        :param pu_path: Elements to prepend. i.e. "aa", "bb"
        :return: Nothing
        """
        print '0: %s' % pu_path
        print '1: %s' % self.u_root
        print os.path.join(pu_path, self.u_root)
        import sys
        sys.exit()

    def has_ext(self, u_ext):
        """
        Method to check if the FilePath object has certain extension no matter the casing.

        :param u_ext: Extension to test. i.e. 'jpg'

        :return: True/False, if the file extension matches or not (casi insensitive, jpg and JPG will output the same
                 result).
        """

        if self.u_ext.lower() == u_ext.lower():
            b_has_ext = True
        else:
            b_has_ext = False

        return b_has_ext

    def is_dir(self):
        """
        Method to check if the file object is a directory.

        :return: True/False
        """

        if self.exists() and os.path.isdir(self.u_path):
            b_is_dir = True

        else:
            b_is_dir = False

        return b_is_dir

    def is_file(self):
        """
        Method to check if the file object is a file.

        :return: True/False
        """

        if self.exists() and os.path.isfile(self.u_path):
            b_is_file = True

        else:
            b_is_file = False

        return b_is_file


def get_cwd():
    """
    Function to get the current working directory.

    :return: A FilePath object.
    """
    u_cwd = os.getcwd().decode('utf8')
    o_cwd = FilePath(u_cwd)
    return o_cwd


def read_nlines(o_file, i_lines):
    """
    Function to read n lines from a file
    :param o_file:
    :param i_lines:
    :return:
    """
    i_line = 0

    lu_lines = []

    try:
        for u_line in o_file:
            i_line += 1

            if i_line > i_lines:
                break
            else:
                lu_lines.append(u_line)
    except IOError:
        pass

    return lu_lines