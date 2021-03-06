###
# Copyright (c) 2015, butterscotchstallion
# All rights reserved.
#
#
###

"""
SpiffyRPG: An IRC RPG
"""
import sys
import os
import supybot
import supybot.world as world

# Use this for the version of this plugin.  You may wish to put a CVS keyword
# in here if you're keeping the plugin in CVS or some similar system.
__version__ = ""

# XXX Replace this with an appropriate author or supybot.Author instance.
__author__ = supybot.authors.unknown

# This is a dictionary mapping supybot.Author instances to lists of
# contributions.
__contributors__ = {}

# This is a url where the most recent plugin package can be downloaded.
__url__ = ''

"""
Adds SpiffyWorld path so the Limnoria plugin
knows about it
"""
test_path = os.path.realpath("../../../code/SpiffyRPG/SpiffyRPG/")
sys.path.append(test_path)

prod_path = os.path.realpath("../code/SpiffyRPG/SpiffyRPG/")
sys.path.append(prod_path)

from . import config
from . import plugin
from imp import reload
# In case we're being reloaded.
reload(config)
reload(plugin)
# Add more reloads here if you add third-party modules and want them to be
# reloaded when this plugin is reloaded.  Don't forget to import them as well!

if world.testing:
    from . import test

Class = plugin.Class
configure = config.configure
