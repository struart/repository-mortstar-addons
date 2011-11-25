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
        channelEntryRegex = '<a id.+?href=\"(.+?)\" class=\"channel\".+?>(.+?)</a>'
        for eachChannel in re.finditer(channelEntryRegex, channelPage, re.M|re.DOTALL):
            self.channelList.append((eachChannel.group(1), eachChannel.group(2)))
