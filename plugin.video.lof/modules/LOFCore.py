import os
import sys

import urllib
import urllib2
from urllib2 import URLError

import re

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from LOFChannels import Channels
from LOFSchedule import Schedule

__settings__ = xbmcaddon.Addon("plugin.video.lof");
__handle__   = int(sys.argv[1])
__artwork__  = os.path.join(__settings__.getAddonInfo('path'),'image')
__chan__     = Channels()
__sched__    = Schedule()

BASE_URL = 'http://www.liveonlinefooty.com/'
LOGIN_URL = ''.join([BASE_URL, 'amember/member.php'])
SCHED_URL = ''.join([BASE_URL, 'liveschedule.php'])
WATCH_URL = ''.join([BASE_URL, 'watchlive/'])

class LOFNavigator:

    def __init__(self):
        self.__conn__ = LOFConnect()
        # ListContainer
        self.addDirAction = ''
        self.label = ''
        self.playUrl = ''
        self.mode = ''
        self.isPlayable = ''
        self.isFolder = ''
    
    def MainMenu(self):
        print "MainMenu"
	u=sys.argv[0]+"?url=Channels&mode=1"
	listfolder = xbmcgui.ListItem('Channels')
	listfolder.setInfo('video', {'Title': 'Channels'})
	xbmcplugin.addDirectoryItem(__handle__, u, listfolder, isFolder=1)

	u=sys.argv[0]+"?url=Schedule&mode=2"
	listfolder = xbmcgui.ListItem('Schedule')
	listfolder.setInfo('video', {'Title': 'Schedule'})
	listfolder.setIconImage(os.path.join(__artwork__, 'calendar.png'))
	xbmcplugin.addDirectoryItem(__handle__, u, listfolder, isFolder=1)
  
	xbmcplugin.endOfDirectory(__handle__)

    def ListChannels(self):
        print "NavigatorListChannels"
        channelPage = ''
        channelList = __chan__.ListChannels(channelPage)
        for channel in channelList:
            self.label = channel[1]
            self.playUrl = ''.join([WATCH_URL, channel[0]])
            self.addDirAction = 'ListChannels'
            self.AddDir()
##        channelPage = self.__conn__.QueryLOF(WATCH_URL, "ListChannels")
##        if channelPage != False:
##            channelList = __chan__.ListChannels(channelPage)
##            for channel in channelList:
##                self.label = channel[1]
##                self.playUrl = ''.join([WATCH_URL, channel[0]])
##                self.addDirAction = 'ListChannels'
##                self.AddDir()
##        else:
##            print "Channel listing not returned"
##            self.MainMenu()
        xbmcplugin.endOfDirectory(__handle__)
        
    def ListSchedule(self, url):
        print "NavigatorListSchedule"
        if url == 'Schedule':
            schedulePage = self.__conn__.QueryLOF(SCHED_URL, "ListSchedule")
        else:
            schedulePage = self.__conn__.QueryLOF(''.join([BASE_URL, url]), "ListSchedule")
        if schedulePage != False:
            # SL = scheduleList
            __SL__ = __sched__.ListSchedule(schedulePage)
            for event in range(len(__SL__)):
                # Event has no channels listed in schedule
                if len(__SL__[event][3]) == 0:
                    self.label = ''.join([__SL__[event][0], ' | ', __SL__[event][1], ' | Coming Soon'])
                    self.addDirAction = 'EventNoChannels'
                # Event has a single channel item listed
                elif len(__SL__[event][3]) == 1:
                    # Channel item is next or previous schedule page url
                    if __SL__[event][0] == True:
                        self.label = __SL__[event][1]
                        self.playUrl = urllib.quote_plus(__SL__[event][3][0][0])
                        self.addDirAction = 'AnotherSchedulePage'
                    # Event has a single channel url
                    else:
                        self.label = ''.join([__SL__[event][0], ' | ', __SL__[event][1]])
                        self.playUrl = ''.join([WATCH_URL, __SL__[event][3][0][0]])
                        self.addDirAction = 'EventItem'
                # Event has multiple channel listings
                else:
                    tempEventList = []
                    for channel in range(len(__SL__[event][3])):
                        tempEventList.append(''.join([WATCH_URL, __SL__[event][3][channel][0], ',', __SL__[event][3][channel][1], '#']))
                    self.label = ''.join([__SL__[event][0], ' | ', __SL__[event][1]])
                    strEventList = ''.join(tempEventList)
                    self.playUrl = strEventList
                    self.addDirAction = 'MultipleChannels'
                self.AddDir()
        else:
            print "Schedule not returned"
            self.MainMenu()
        xbmcplugin.endOfDirectory(__handle__)

    def ListChannelSchedule(self, channelList):
        print "CoreListChannelSchedule"
        chanReg = re.compile('(.+?),(.+?)#', re.M | re.DOTALL)
        for eachChan in chanReg.finditer(channelList):
            self.label = str.capitalize(eachChan.group(2))
            self.playUrl = eachChan.group(1)
            self.addDirAction = 'ListChannelSchedule'
            self.AddDir()
        xbmcplugin.endOfDirectory(__handle__)
        
    def PlayStream(self, url):
        print ''.join(["PlayStream - ", url])
        watchPage = self.__conn__.QueryLOF(url, "PlayStream")
        if watchPage != False:
            print "Building the rtmp address"
            swfPlayer = re.search('SWFObject\(\'(.+?)\'', watchPage).group(1)
            playPath = re.search('\'file\',\'(.+?)\'', watchPage).group(1)
            streamer = re.search('\'streamer\',\'(.+?)\'', watchPage).group(1)
            appUrl = re.search('rtmp://.+?/(.+?)\'\)', watchPage).group(1)
            rtmpUrl = ''.join([streamer,
                   ' playpath=', playPath,
                   ' app=', appUrl,
                   ' pageURL=', url,
                   ' swfUrl=', swfPlayer,
                   ' live=true'])
            print rtmpUrl
	    item = xbmcgui.ListItem(path=rtmpUrl)
            return xbmcplugin.setResolvedUrl(__handle__, True, item)
        else:
            print "Couldn't open playback stream"
            self.MainMenu()
        
    def AddDir(self):
        print "AddDir"
        if self.addDirAction == 'ListChannels':
            self.mode = '5'
            self.isPlayable = 'true'
            self.isFolder = False
        elif self.addDirAction == 'EventNoChannels':
            self.playUrl = ''
            self.mode = ''
            self.isPlayable = 'false'
            self.isFolder = False
        elif self.addDirAction == 'AnotherSchedulePage':
            self.mode = '2'
            self.isPlayable = 'false'
            self.isFolder = True
        elif self.addDirAction == 'EventItem':
            self.mode = '5'
            self.isPlayable = 'true'
            self.isFolder = False
        elif self.addDirAction == 'MultipleChannels':
            self.mode = '6'
            self.isPlayable = 'false'
            self.isFolder = True
        elif self.addDirAction == 'ListChannelSchedule':
            self.mode = '5'
            self.isPlayable = 'true'
            self.isFolder = False
            
        ic_th_image = os.path.join(__artwork__, 'chan_icon.png')
        liz = xbmcgui.ListItem(label = self.label)
        liz.setInfo('video' , {'title': self.label})
        liz.setIconImage(ic_th_image)
        liz.setProperty('IsPlayable', self.isPlayable)
        liz.setThumbnailImage(ic_th_image)
        u=''.join([sys.argv[0], "?url=", self.playUrl, "&mode=", self.mode, "&name=",urllib.quote_plus(self.label)])
        xbmcplugin.addDirectoryItem(handle=__handle__, url=u, listitem=liz, isFolder=self.isFolder)
        
class LOFConnect:
    def __init__(self):
        self.username  = __settings__.getSetting("username")
        self.password  = __settings__.getSetting("password")
        self.loginData = urllib.urlencode({'amember_login' : self.username,
                                           'amember_pass' : self.password,
                                           'submit' : 'Login'})

    def QueryLOF(self, openurl, action):
        print ''.join(["QueryLOF - ", action])
        opener = urllib2.build_opener()
        # Login and View Page
        try:
            response = opener.open(openurl, self.loginData).read()
            opener.close()
        except URLError, e:
            if hasattr(e, 'reason'):
                print 'Failed to login: ' + str(e.reason)
                xbmc.executebuiltin("XBMC.Notification('Failed to login'," + str(e.reason) + ", 5000)")
                return False
            elif hasattr(e, 'code'):
                print 'Failed to login: ' + str(e.code)
                xbmc.executebuiltin("XBMC.Notification('Failed to login'," + str(e.code) + ", 5000)")
                return False
        return response
