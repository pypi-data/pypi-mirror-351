#  -*- coding: utf-8 -*-
"""
Author: Rafael R. L. Benevides
"""

from .bulletins import BulletinA, BulletinC, update_bulletins, get_latest_update, update_if_needed

from .eop import EOP


# make sure the bulletins dir exists
BulletinA.path.parent.mkdir(exist_ok=True)

# update the bulletins if they're a week old or don't exist
update_if_needed()