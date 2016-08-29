# Constants File
# -*- coding: utf-8 -*-

import cmd
import files
import platform


u_OK_TEXT = u'✔'
u_ER_TEXT = u'x'
u_PR_TEXT = u'⌛'
u_SET_NAME = u'HQ UTILS'

# Screen proportions
do_platforms = {'32x': platform.Platform(pu_alias=u'32x', pu_name=u'Megadrive 32X', pi_width=4, pi_height=3),
                'gb': platform.Platform(pu_alias=u'gb', pu_name=u'GameBoy', pi_width=160, pi_height=144),
                'gba': platform.Platform(pu_alias=u'gba', pu_name=u'GameBoy Advance', pi_width=240, pi_height=160),
                'gbc': platform.Platform(pu_alias=u'gbc', pu_name=u'GameBoy', pi_width=160, pi_height=144),
                'ggear': platform.Platform(pu_alias=u'ggear', pu_name=u'Game Gear', pi_width=4, pi_height=3),
                'jaguar': platform.Platform(pu_alias=u'jaguar', pu_name=u'Jaguar', pi_width=4, pi_height=3),
                'lynx': platform.Platform(pu_alias=u'lynx', pu_name=u'Lynx', pi_width=160, pi_height=102),
                'msystem': platform.Platform(pu_alias=u'msystem', pu_name=u'Master Sytem', pi_width=4, pi_height=3),
                'megadrive': platform.Platform(pu_alias=u'megadrive', pu_name=u'Megadrive', pi_width=4, pi_height=3),
                'n64': platform.Platform(pu_alias=u'n64', pu_name=u'Nintendo 64', pi_width=4, pi_height=3),
                'nes': platform.Platform(pu_alias=u'nes', pu_name=u'N.E.S.', pi_width=4, pi_height=3),
                'snes': platform.Platform(pu_alias=u'snes', pu_name=u'Super Nintendo', pi_width=4, pi_height=3)}

# Folders
o_CF_FP = files.FilePath(__file__.decode('utf8'))
o_CD_FP = files.FilePath(o_CF_FP.u_root)

o_METADATA_DIR_FP = files.FilePath(o_CD_FP.u_path, u'..', u'roms_metadata')

# Console width and height
du_output = cmd.execute(u'stty size')
if not du_output['u_stderr']:
    u_rows, u_cols = du_output['u_stdout'].split()
else:
    u_rows = u'0'
    u_cols = u'0'

i_TERM_COLS = int(u_cols)
i_TERM_ROWS = int(u_rows)
