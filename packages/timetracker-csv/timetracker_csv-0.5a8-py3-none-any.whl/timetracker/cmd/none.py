"""Do command, `none`"""

__copyright__ = 'Copyright (C) 2025-present, DV Klopfenstein, PhD. All rights reserved.'
__author__ = "DV Klopfenstein, PhD"

from logging import debug
from timetracker.msgs import str_tostart
from timetracker.utils import yellow
from timetracker.cmd.common import get_cfg
from timetracker.cmd.common import prtmsg_started01


def cli_run_none(fnamecfg, args):
    """Do command, `none`"""
    # pylint: disable=unused-argument
    cfg = get_cfg(fnamecfg)
    run_none(cfg.cfg_loc, args.name)

def run_none(cfg_proj, username=None):
    """If no Timetracker command is run, print informative messages"""
    debug(yellow('RUNNING COMMAND NONE'))
    # Check for start time
    if (startobj := cfg_proj.get_starttime_obj(username)) is not None:
        prtmsg_started01(startobj)
        return startobj
    print(str_tostart())
    return None


# Copyright (C) 2025-present, DV Klopfenstein, PhD. All rights reserved.
