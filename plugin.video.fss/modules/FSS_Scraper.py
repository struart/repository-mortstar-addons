import os
import sys

import urllib
import re
import time
import datetime
from datetime import date
from datetime import timedelta
from datetime import tzinfo
from time import strptime

import FSS_Navigator

class FSS_Scraper:

    def __init__(self):
        # URL's
        self.baseurl = 'http://www.flashsportstreams.tv/'
        self.loginurl = ''.join([self.baseurl, 'forum/login.php?do=login'])
        self.memberurl = ''.join([self.baseurl, 'forum/view.php?pg=home&styleid=1'])
        self.channelurl = ''.join([self.baseurl, 'forum/view.php?pg=vip%s'])
        self.scheduleurl = ''.join([self.baseurl, 'forum/calendar.php'])
        self.dailyscheduleurl = ''.join([self.baseurl, 'forum/calendar.php?do=getinfo&day=%s&c=1'])
        # Regex Statements
        self.unapwd = re.compile('<strong>Welcome, (.+?).</strong><br />', re.DOTALL|re.M)
        # Regex for getting rtmpurl
        self.embedstring = re.compile('<embed(.+?)</p>', re.DOTALL|re.M)
        self.swfurl = re.compile('src=\"(.+?)\"', re.DOTALL|re.M)
        self.playpath = re.compile('file=(.+?)&', re.DOTALL|re.M)
        self.tcurl = re.compile('streamer=(.+?)&', re.DOTALL|re.M)
        self.flashstring = re.compile('file=(.+?)&.+?streamer=(.+?)&amp.+?src=\"(.+?)\"', re.DOTALL|re.M)
        self.app = re.compile('rtmp://.+?/(.+?)&amp', re.DOTALL|re.M)
        self.stripchannel = re.compile('\(VIP.+?\)|\d{1,2}[A|P]M|\d{1,2}[:|.]\d{1,2}[A|P]M', re.DOTALL|re.M|re.IGNORECASE)
        # Regex for schedule parsing
        self.category = re.compile('(.+?) - (.+?)', re.DOTALL|re.M)
        self.channel = re.compile('CLICK HERE FOR VIP(.*?)<', re.DOTALL|re.M)
        self.event_dst = re.compile('This event ignores DST', re.M|re.DOTALL)
        self.event = re.compile('<form action="calendar.php\?do=manage&amp;e=(.+?)</form>', re.M|re.DOTALL)
        self.eventcat = re.compile('<td class="tcat">(.+?)[-|:]', re.M|re.DOTALL)
        self.eventtitle = re.compile('<td class="tcat">.+?[-|:](.+?)</td>', re.M|re.DOTALL)
        self.eventdate = re.compile('<div class="smallfont">(.+?)<.+?</div>', re.M|re.DOTALL)
        self.eventtime = re.compile('><span class="time">(.+?)</span> to <span class="time">(.+?)</span>', re.M|re.DOTALL)        

    def account_check(self, link):
        if self.unapwd.search(link)  == None:
            return False
        else:
            return True

    def build_rtmp_url(self, link, pageurl):
        embedstring = self.embedstring.search(link).group(0)
        swfurl = self.swfurl.search(embedstring).group(1)
        playpath = self.playpath.search(embedstring).group(1)
        tcurl = self.tcurl.search(embedstring).group(1)
        app = self.app.search(embedstring).group(1)
        rtmpaddress = ''.join([tcurl, '/', app])
        rtmpurl = ''.join([rtmpaddress,
                          ' playpath=', playpath,
                          ' app=', app,
                          ' pageURL=', pageurl,
                          ' tcURL=', tcurl,
                          ' swfUrl=', swfurl, 
                          ' swfVfy=true live=true'])
        return rtmpurl

    def get_schedule_item(self, schedulepage, date):
        __navigator__ = FSS_Navigator.FSS_Navigator()
        for each_event in self.event.finditer(schedulepage):
            event_info = each_event.group(1)
            cat, title, starthour = self.get_event_info(event_info)
            for every_channel in self.channel.finditer(each_event.group(0)):
                __navigator__.add_nav_item([cat, ' | ', title, ' | ', starthour, ' | VIP', every_channel.group(1)],
                                           'true',
                                           every_channel.group(1),
                                           False,
                                           urllib.quote_plus(self.channelurl %every_channel.group(1)),
                                           '5',
                                           '')

    def get_event_info(self, event_info):
        cat = self.eventcat.search(event_info).group(1)
        title = self.eventtitle.search(event_info).group(1)
        title = self.stripchannel.sub('', title).strip()
        starthour = self.eventtime.search(event_info).group(1)
        return cat, title, starthour
    
    def convert_to_dst(self, event_info, event_start):
        if self.event_dst.search(event_info) != None:
            dt_event_start = datetime.datetime(*event_start[0:6]) + datetime.timedelta(hours=1)
            event_start= dt_event_start.timetuple()
        return event_start
            
    def date_to_ordinal(self, date):
        if 10 <= date % 100 < 20:
            return str(date) + 'th'
        else:
            return  str(date) + {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(date % 10, "th")

    def convert_to_24h_clock(self, intime, meridian, date):
        returndate = date
        if meridian == 'PM':
            returntime = ''.join([str(int(intime.split(':')[0]) + 12), ':', intime.split(':')[1]])
            if returntime == '24:00':
                returntime = '00:00'
                time_tuple = time.strptime(date, "%m-%d-%Y")
                dt_obj = datetime.datetime(*time_tuple[0:6])
                date =  dt_obj + timedelta(days=1)
                returndate = dt_obj.strftime("%m-%d-%Y")
        else:
            if intime == '12:00':
                returntime = '00:00'
            else:
                returntime = intime
        return returntime, returndate
    
    def convert_2_fssurldate(self, date):
        day = (date + timedelta(days=0)).timetuple()
        day = ''.join([str(day.tm_year),'-',str(day.tm_mon),'-',str(day.tm_mday)])
        return day
