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
                            ('Setanta Sports Ireland','Setanta.png','vip13', True),
                            ('Sky Sports F1','SkySportsF1.png','vip14', True),
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

        # VIP Channel Info Array
        self.vipchannelinfo = [('Sky Sports 1','SkySports1.png','vip1', True),
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
                               ('Setanta Sports Ireland','Setanta.png','vip13', True),
                               ('Sky Sports F1','SkySportsF1.png','vip14', True),
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
                               ('Sky Movies 2', 'SKYMOVIES.png', 'vip28', True),
                               ('VIP 29', 'none.png', 'vip29', True),
                               ('VIP 30', 'none.png', 'vip30', True),
					 ('VIP 31', 'none.png', 'vip31', True),
                               ('VIP 32', 'none.png', 'vip32', True),
                               ('VIP 33', 'none.png', 'vip33', True),
                               ('VIP 34', 'none.png', 'vip34', True),
                               ('VIP 35', 'none.png', 'vip35', True),
                               ('VIP 36', 'none.png', 'vip36', True),
                               ('VIP 37', 'none.png', 'vip37', True),
                               ('VIP 38', 'none.png', 'vip38', True),
                               ('VIP 39', 'none.png', 'vip39', True),
                               ('VIP 40', 'none.png', 'vip40', True),
					 ('VIP 41', 'none.png', 'vip41', True),
                               ('VIP 42', 'none.png', 'vip42', True),
                               ('VIP 43', 'none.png', 'vip43', True),
                               ('VIP 44', 'none.png', 'vip44', True),
                               ('VIP 45', 'none.png', 'vip45', True),
                               ('VIP 46', 'none.png', 'vip46', True),
                               ('VIP 47', 'none.png', 'vip47', True),
                               ('VIP 48', 'none.png', 'vip48', True),
                               ('VIP 49', 'none.png', 'vip49', True),
                               ('VIP 50', 'none.png', 'vip50', True),
					 ('VIP 51', 'none.png', 'vip51', True),
                               ('VIP 52', 'none.png', 'vip52', True),
                               ('VIP 53', 'none.png', 'vip53', True),
                               ('VIP 54', 'none.png', 'vip54', True),
                               ('VIP 55', 'none.png', 'vip55', True),
                               ('VIP 56', 'none.png', 'vip56', True),
                               ('VIP 57', 'none.png', 'vip57', True),
                               ('VIP 58', 'none.png', 'vip58', True),
                               ('VIP 59', 'none.png', 'vip59', True),
                               ('VIP 60', 'none.png', 'vip60', True),
                               ('VIP 61', 'none.png', 'vip61', True),
                               ('VIP 62', 'none.png', 'vip62', True),
                               ('VIP 63', 'none.png', 'vip63', True),
                               ('VIP 64', 'none.png', 'vip64', True),
                               ('VIP 65', 'none.png', 'vip65', True),
                               ('VIP 66', 'none.png', 'vip66', True),
                               ('VIP 67', 'none.png', 'vip67', True),
                               ('VIP 68', 'none.png', 'vip68', True),
                               ('VIP 69', 'none.png', 'vip69', True),
                               ('VIP 70', 'none.png', 'vip70', True),
                               ('VIP 71', 'none.png', 'vip71', True),
                               ('VIP 72', 'none.png', 'vip72', True),
                               ('VIP 73', 'none.png', 'vip73', True),
                               ('VIP 74', 'none.png', 'vip74', True),
                               ('VIP 75', 'none.png', 'vip75', True),
                               ('VIP 76', 'none.png', 'vip76', True),
                               ('VIP 77', 'none.png', 'vip77', True),
                               ('VIP 78', 'none.png', 'vip78', True),
                               ('VIP 79', 'none.png', 'vip79', True),
                               ('VIP 80', 'none.png', 'vip80', True),
                               ('VIP 81', 'none.png', 'vip81', True),
                               ('VIP 82', 'none.png', 'vip82', True),
                               ('VIP 83', 'none.png', 'vip83', True),
                               ('VIP 84', 'none.png', 'vip84', True),
                               ('VIP 85', 'none.png', 'vip85', True),
                               ('VIP 86', 'none.png', 'vip86', True),
                               ('VIP 87', 'none.png', 'vip87', True),
                               ('VIP 88', 'none.png', 'vip88', True),
                               ('VIP 89', 'none.png', 'vip89', True),
                               ('VIP 90', 'none.png', 'vip90', True),
                               ('VIP 91', 'none.png', 'vip91', True),
                               ('VIP 92', 'none.png', 'vip92', True),
                               ('VIP 93', 'none.png', 'vip93', True),
                               ('VIP 94', 'none.png', 'vip94', True),
                               ('VIP 95', 'none.png', 'vip95', True),
                               ('VIP 96', 'none.png', 'vip96', True),
                               ('VIP 97', 'none.png', 'vip97', True),
                               ('VIP 98', 'none.png', 'vip98', True),
                               ('VIP 99', 'none.png', 'vip99', True),
                               ('VIP 100', 'none.png', 'vip100', True)]


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
        for menu_item in range(1,6):
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
                                  '6',
                                  self.channelinfo[i-1][1])
        xbmcplugin.endOfDirectory(__handle__)

    # Lists all the VIP channels in the VIP Channels page
    def list_vipchannels(self):
        for i in range (1,len(self.vipchannelinfo) + 1):
            if self.vipchannelinfo[i-1][3] == True:
                self.add_nav_item(self.vipchannelinfo[i-1][0],
                                  'true',
                                  str(i),
                                  False,
                                  urllib.quote_plus(__scraper__.channelurl %i),
                                  '6',
                                  self.vipchannelinfo[i-1][1])
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
