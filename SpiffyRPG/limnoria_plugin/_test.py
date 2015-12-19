###
# Copyright (c) 2015, butterscotchstallion
# All rights reserved.
#
#
###

from supybot.test import *
import supybot.log as log
import supybot.ircdb as ircdb

class ChannelStatsTestCase(ChannelPluginTestCase):
    plugins = ("SpiffyRPG")

    def setUp(self):
        ChannelPluginTestCase.setUp(self)
        self.prefix = 'foo!bar@baz'
        self.nick = 'foo'
        self.irc.feedMsg(ircmsgs.privmsg(self.irc.nick,
                                         'register foo bar',
                                         prefix=self.prefix))
        _ = self.irc.takeMsg()
        chanop = ircdb.makeChannelCapability(self.channel, 'op')
        ircdb.users.getUser(self.nick).addCapability(chanop)

    def test(self):
        self.irc.feedMsg(ircmsgs.join(self.channel, prefix=self.prefix))
        self.assertNotError('channelstats')
        self.assertNotError('channelstats')
        self.assertNotError('channelstats')



# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
