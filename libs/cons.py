# Constants File
# -*- coding: utf-8 -*-

import platform


u_OK_TEXT = u'✔'
u_ER_TEXT = u'x'
u_PR_TEXT = u'⌛'
u_SET_NAME = u'HQ UTILS'

# Screen proportions
do_platforms = {'gb': platform.Platform(pu_alias=u'gb', pu_name=u'GameBoy', pi_width=160, pi_height=144),
                'gba': platform.Platform(pu_alias=u'gba', pu_name=u'GameBoy Advance', pi_width=240, pi_height=160),
                'gbc': platform.Platform(pu_alias=u'gbc', pu_name=u'GameBoy', pi_width=160, pi_height=144),
                'lynx': platform.Platform(pu_alias=u'lynx', pu_name=u'Lynx', pi_width=160, pi_height=102),
                'megadrive': platform.Platform(pu_alias=u'megadrive', pu_name=u'Megadrive', pi_width=4, pi_height=3),
                'nes': platform.Platform(pu_alias=u'nes', pu_name=u'N.E.S.', pi_width=4, pi_height=3),
                'snes': platform.Platform(pu_alias=u'snes', pu_name=u'Super Nintendo', pi_width=4, pi_height=3)}
