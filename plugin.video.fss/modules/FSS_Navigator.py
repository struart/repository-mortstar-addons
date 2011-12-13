import os
import sys

import urllib
import urllib2
import cookielib
import md5

import time
import datetime
from time import strftime
from time import strptime
from datetime import timedelta
from datetime import date

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon

import FSS_Scraper

__settings__ = xbmcaddon.Addon("plugin.video.fss");
__handle__   = int(sys.argv[1])
__artwork__  = os.path.join(__settings__.getAddonInfo('path'),'image')
__language__ = __settings__.getLocalizedString
__scraper__  = FSS_Scraper.FSS_Scraper()


class FSS_Navigator:

    def __init__(self):
        self.username  = __settings__.getSetting("username")
        self.password  = __settings__.getSetting("password")
        self.passhash  = md5.new(self.password).hexdigest()
        self.loginData = urllib.urlencode(
            {'do' : 'login',
             'url' : __scraper__.memberurl,
             'vb_login_md5password' : self.passhash,
             'vb_login_md5password_utf' : self.passhash,
             'vb_login_username' : self.username,
             'vb_login_password' : 0})
        
        # Channel Info Array
        self.channelinfo = [('Sky Sports 1','SkySports1.png','vip1', True),
                            ('Sky Sports 2','SkySports2.png','vip2', True),
                            ('Sky Sports 3','SkySports3.png','vip3', True),
                            ('Sky Sports 4','SkySports4.png','vip4', True),
                            ('Sky Sports News','SkySportsNews.png','vip5', True),
                            ('ESPN UK','espnuk.png','vip6', True),
                            ('ESPN US','espnus.png','vip7', True),
                            ('ESPN 2','espn2.png','vip8', True),
                            ('ESPNU College Sports','espnu.png','vip9', True),
                            ('Setanta Sports Canada','Setanta.png','vip10', True),
                            ('Setanta Sports Australia','Setanta.png','vip11', True),
                            ('Setanta Sports China','Setanta.png','vip12', True),
                            ('Setanta Sports India','Setanta.png','vip13', True),
                            ('WBC Boxing','WBC.png','vip14', False), # Weird channel - not supported
                            ('Fox Soccer Channel','FSC.png','vip15', True),
                            ('Fox Soccer Plus','FSP.png','vip16', True),
                            ('British Eurosport', 'BritishEurosport.png', 'vip17', True),
                            ('British Eurosport 2', 'BritishEurosport.png', 'vip18', True),
                            ('At the Races', 'BritishEurosport.png', 'vip19', True),
                            ('Racing UK', 'BritishEurosport.png', 'vip20', True),
                            ('Sky News HD','SkyNewsHD.png','vip21', False),  # Channel is Silverlight - not supported
                            ('BBC 1', 'BBC1.png', 'vip22', True),
                            ('ITV 1', 'ITV1.png', 'vip23', True),
                            ('Sky 1', 'SKY1.png', 'vip24', True),
                            ('Sky Atlantic', 'SKYATLANTIC.png', 'vip25', True),
                            ('Sky Arts', 'SKYARTS.png', 'vip26', True),
                            ('Sky Movies 1', 'SKYMOVIES.png', 'vip27', True),
                            ('Sky Movies 2', 'SKYMOVIES.png', 'vip28', True)]

    # Does the login and opens some link
    def login(self, openurl):
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.open(__scraper__.loginurl, self.loginData)
        link = opener.open(openurl).read()
        return link

    # Checks that username and password are correctly set
    def settings(self):
        if self.username != '' and self.password != '':
            link = self.login(__scraper__.memberurl)
            if (__scraper__.account_check(link) == False):
                self.check_settings(__language__(30031))
            else:
                self.menu()
        else:
            self.check_settings(__language__(30032))

    # Called when there is a failure to authenticate user
    def check_settings(self, error_string):
	u=''.join([sys.argv[0],"?url=Settings&mode=4"])
	listfolder = xbmcgui.ListItem(error_string)
	listfolder.setInfo('video', {'Title': __language__(30032)})
	xbmcplugin.addDirectoryItem(__handle__, u, listfolder, isFolder=1)
        xbmcplugin.endOfDirectory(__handle__)

    # Does the homepage listing
    def menu(self):
        menu_list = []
        for menu_item in range(1,5):
            u=''.join([sys.argv[0],"?url=",__language__(30010 + menu_item),"&mode=",str(menu_item)])
            listfolder = xbmcgui.ListItem(__language__(30010 + menu_item))
	    listfolder.setInfo('video', {'Title': __language__(30010 + menu_item)})
	    menu_list.append((u,listfolder,True))
	xbmcplugin.addDirectoryItems(__handle__, menu_list)
        xbmcplugin.endOfDirectory(__handle__)

    # Lists all the 22/7 channels in the Channels page
    def list_channels(self):
        for i in range (1,len(self.channelinfo) + 1):
            if self.channelinfo[i-1][3] == True:
                self.add_nav_item(self.channelinfo[i-1][0],
                                  'true',
                                  str(i),
                                  False,
                                  urllib.quote_plus(__scraper__.channelurl %i),
                                  '5',
                                  self.channelinfo[i-1][1])
        xbmcplugin.endOfDirectory(__handle__)

    # Adds navigation items
    def add_nav_item(self, slist, isPlayable, chanId, isfolder, playUrl, mode, image):
        label = ''.join(slist)
        ic_th_image = os.path.join(__artwork__, image)
        listitem = xbmcgui.ListItem(label=label)
        listitem.setInfo('video' , {'title': label})
        listitem.setProperty('IsPlayable', isPlayable)
        listitem.setIconImage(ic_th_image)
        listitem.setThumbnailImage(ic_th_image)
        u=''.join([sys.argv[0],"?url=",playUrl,"&mode=%s" %mode,"&name=",urllib.quote_plus(label)])
        xbmcplugin.addDirectoryItem(handle=__handle__, url=u, listitem=listitem, isFolder=isfolder)

    # Gets the rtmp address from given url and plays stream
    def play_stream(self, url):
        link = self.login(url)
        rtmpUrl = __scraper__.build_rtmp_url(link, url)
        item = xbmcgui.ListItem(path=rtmpUrl)
        return xbmcplugin.setResolvedUrl(__handle__, True, item)

    # List next 7 days links in the Schedule menu
    def list_schedule(self):
        today = date.today()
        for i in range (0, 7):
            td = timedelta(days=i)
            d1 = (today + td).timetuple()
            Day = strftime("%A", d1)
            Date = __scraper__.date_to_ordinal(d1.tm_mday)
            usedate = __scraper__.convert_2_fssurldate(today + td)
            Month = strftime("%B", d1)
            self.add_nav_item([Day,' ',Date,' ',Month],
                              'false',
                              '0',
                              True,
                              usedate,
                              '6',
                              '')
       	xbmcplugin.endOfDirectory(__handle__)

    # Lists day's schedule for a given date
    def list_daily_schedule(self, period, g_date):
        if period == 'Today':
            aday = date.today()
            g_date = __scraper__.convert_2_fssurldate(aday)
        day = datetime.datetime(*(time.strptime(g_date, "%Y-%m-%d"))[0:6])
        today = str(day)
        link = self.login(__scraper__.dailyscheduleurl %today)
        __scraper__.get_schedule_item(link, today)
        xbmcplugin.endOfDirectory(__handle__)
