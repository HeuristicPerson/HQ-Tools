"""
Library to define the platform object for storing information about systems (SNES, Megadrive, NES...)
"""


class Platform:
    def __init__(self, pu_alias=u'', pu_name=u'', pi_width=0, pi_height=0):
        # Arguments check
        if u'' in (pu_alias.strip(), pu_name.strip()):
            raise Exception('ERROR: Name and alias must contain printable characters (pu_alias, pu_name) = (%s, %s)'
                            % (pu_alias.encode('utf8'), pu_name.encode('utf8')))

        if 0 in (pi_width, pi_height):
            raise Exception('ERROR: None of the proportions can be zero (pi_width, pi_height) = (%i, %i)'
                            % (pi_width, pi_height))

        for i_dimension in (pi_width, pi_height):
            if i_dimension < 0:
                raise Exception('ERROR: None of the proportions can be negative (pi_width, pi_height) = (%i, %i)'
                                % (pi_width, pi_height))

        self.u_ALIAS = pu_alias
        self.u_NAME = pu_name
        self.i_WIDTH = pi_width
        self.i_HEIGHT = pi_height
