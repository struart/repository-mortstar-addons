import os
import sys

import urllib
import urllib2
from urllib2 import URLError
import cookielib

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
SCHED_URL = ''.join([BASE_URL, 'today.php'])
WATCH_URL = ''.join([BASE_URL, 'watchlive/'])

class LOFNavigator:

    def __init__(self):
        self.__conn__ = LOFConnect()
        # ListContainer
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
        channelPage = self.__conn__.QueryLOF(WATCH_URL, "ListChannels")
        if channelPage != False:
            channelList = __chan__.ListChannels(channelPage)
            for channel in channelList:
                self.label = channel[1]
                self.playUrl = ''.join([WATCH_URL, channel[0]])
                self.mode = '5'
                self.isPlayable = 'true'
                self.isFolder = False
                self.AddDir()
        else:
            print "Channel listing not returned"
            self.MainMenu()
        xbmcplugin.endOfDirectory(__handle__)
        
    def ListSchedule(self):
        print "NavigatorListSchedule"
        schedulePage = self.__conn__.QueryLOF(SCHED_URL, "ListSchedule")
        if schedulePage != False:
            scheduleList = __sched__.ListSchedule(schedulePage)
            for event in range(len(scheduleList)):
                if len(scheduleList[event][3]) == 0:
                    self.label = ''.join([scheduleList[event][0], ' | ', scheduleList[event][1], ' | Coming Soon'])
                    self.playUrl = ''
                    self.mode = ''
                    self.isPlayable = 'false'
                    self.isFolder = False
                elif len(scheduleList[event][3]) == 1:
                    self.label = ''.join([scheduleList[event][0], ' | ', scheduleList[event][1]])
                    self.playUrl = ''.join([WATCH_URL, scheduleList[event][3][0][0]])
                    self.mode = '5'
                    self.isPlayable = 'true'
                    self.isFolder = False
                else:
                    self.label = ''.join([scheduleList[event][0], ' | ', scheduleList[event][1]])
                    tempEventList = []
                    for channel in range(len(scheduleList[event][3])):
                        tempEventList.append(''.join([WATCH_URL, scheduleList[event][3][channel][0], ',', scheduleList[event][3][channel][1], '#']))
                    strEventList = ''.join(tempEventList)
                    self.playUrl = strEventList
                    self.mode = '6'
                    self.isPlayable = 'false'
                    self.isFolder = True
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
            self.mode = '5'
            self.isPlayable = 'true'
            self.isFolder = False
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
            xbmc.Player( xbmc.PLAYER_CORE_DVDPLAYER ).play(rtmpUrl, item )
        else:
            print "Couldn't open playback stream"
            self.MainMenu()
        
    def AddDir(self):
        print "AddDir"
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
