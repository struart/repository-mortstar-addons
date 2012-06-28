import re

class Channels:
    def __init__(self):
        self.channelList = []

    def ListChannels(self, channelPage):            
        print "ListChannels"
        self.ParseAndAppendChannels(channelPage)
        # Make sure that there are channels in the list
        if len(self.channelList) > 0:
            print ''.join([str(len(self.channelList)), ' channels added to list'])
            print self.channelList
        else:
            print "No channels added to channel list"
        return self.channelList

    def ParseAndAppendChannels(self, channelPage):
        print "ParseAndAppendChannels"
        self.channelList = []
        for i in range(1,13):
            if i == 5:
                self.channelList.append(('channel4hd.php', 'Channel 4 HD'))
            self.channelList.append((''.join(['channel', str(i), '.php']), ''.join(['Channel ', str(i)])))
##        channelEntryRegex = 'a href=\"(.+?).php\" class=.+?>(.+?)</a>'
##        for eachChannel in re.finditer(channelEntryRegex, channelPage, re.M|re.DOTALL):
##            self.channelList.append((''.join([eachChannel.group(1), '.php']), eachChannel.group(2)))
