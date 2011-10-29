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
        self.channelinfo = [('Sky Sports 1','SkySports1.png','vip1'),
                            ('Sky Sports 2','SkySports2.png','vip2'),
                            ('Sky Sports 3','SkySports3.png','vip3'),
                            ('Sky Sports 4','SkySports4.png','vip4'),
                            ('Sky Sports News','SkySportsNews.png','vip5'),
                            ('ESPN UK','espnuk.png','vip6'),
                            ('ESPN US','espnus.png','vip7'),
                            ('ESPN 2','espn2.png','vip8'), # Uses alternative streaming mechanism - not supported
                            ('Setanta Sports Canada','Setanta.png','vip9'),
                            ('Setanta Sports Australia','Setanta.png','vip10'),
                            ('ESPNU College Sports','espnu.png','vip11'),
                            ('Sky News HD','SkyNewsHD.png','vip12'), # Channel is Silverlight - not supported
                            ('WBC Boxing','WBC.png','vip13'), # Weird channel - not supported
                            ('Fox Soccer Channel','FSC.png','vip14'),
                            ('Fox Soccer Plus','FSP.png','vip15'),
                            ('British Eurosport', 'BritishEurosport.png', 'vip16')]

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
            if i != 12:
                if i != 13:
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
