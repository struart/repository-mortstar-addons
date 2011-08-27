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

        # Regex Patterns
        self.unapwd_regex = '<strong>Welcome, (.+?).</strong><br />'
        self.embedstring_regex = '<embed(.+?)</span></span></p>'
        self.rtmpaddress_regex = 'streamer=(.+?)&amp;type=video'
        self.appurl_regex = 'rtmp://(.+?)/(.+?)&amp;type=video'
        self.playurl_regex = 'flashvars="file=(.+?)&amp;streamer'
        self.stripchannels_regex = '\(VIP.+?\)|\d{1,2}[A|P]M|\d{1,2}[:|.]\d{1,2}[A|P]M'
        self.category_regex = '(.+?) - (.+?)'
        self.channel_regex = 'CLICK HERE FOR VIP(.*?)<'
        self.reoccuring_event_regex = 'occurs'
        self.multiday_event_regex = 'to'
        self.event_dst_regex = 'This event ignores DST'
        self.event_regex = '<form action="calendar.php\?do=manage&amp;e=(.+?)</form>'
        self.eventcat_regex = '<td class="tcat">(.+?) -'
        self.eventtitle_regex = '<td class="tcat".+? - (.+?)</td>'
#        self.eventdate_regex = '</div>(.*?)<span class="time">| <br />'
        self.eventdate_regex = '<div class="smallfont">(.+?)<.+?</div>'
        self.eventtime_regex = '><span class="time">(.+?)</span> to <span class="time">(.+?)</span>'

        # Regex Statements
        self.unapwd = re.compile(self.unapwd_regex, re.DOTALL|re.M)
        self.embedstring = re.compile(self.embedstring_regex, re.DOTALL|re.M)
        self.rtmpaddress = re.compile(self.rtmpaddress_regex, re.DOTALL|re.M)
        self.appurl = re.compile(self.appurl_regex, re.DOTALL|re.M)
        self.playurl = re.compile(self.playurl_regex, re.DOTALL|re.M)
        self.stripchannel = re.compile(self.stripchannels_regex, re.DOTALL|re.M|re.IGNORECASE)
        self.category = re.compile(self.category_regex, re.DOTALL|re.M)
        self.channel = re.compile(self.channel_regex, re.DOTALL|re.M)
        self.reoccuring_event = re.compile(self.reoccuring_event_regex, re.M|re.DOTALL)
        self.multiday_event = re.compile(self.multiday_event_regex, re.M|re.DOTALL)
        self.event_dst = re.compile(self.event_dst_regex, re.M|re.DOTALL)
        self.event = re.compile(self.event_regex, re.M|re.DOTALL)
        self.eventcat = re.compile(self.eventcat_regex, re.M|re.DOTALL)
        self.eventtitle = re.compile(self.eventtitle_regex, re.M|re.DOTALL)
        self.eventdate = re.compile(self.eventdate_regex, re.M|re.DOTALL)
        self.eventtime = re.compile(self.eventtime_regex, re.M|re.DOTALL)        

    def account_check(self, link):
        if self.unapwd.search(link)  == None:
            return False
        else:
            return True

    def build_rtmp_url(self, link, channelurl):
        embedstring = self.embedstring.search(link).group(0)
        rtmpaddress = self.rtmpaddress.search(embedstring).group(1)
        appurl = self.appurl.search(embedstring).group(2)
        playurl = self.playurl.search(embedstring).group(1)
        playurl = re.sub('.flv', '', playurl)
        rtmpurl = ''.join([rtmpaddress,
                          ' playpath=', playurl,
                          ' app=', appurl,
                          ' pageURL=', channelurl,
                          ' swfVfy=true live=true'])
        return rtmpurl

    def schedules(self, schedulePage):
        __navigator__ = FSS_Navigator.FSS_Navigator()
        for each_event in self.schedule.finditer(schedulePage):
            eventinfo, matchtitle = self.get_event_info(each_event.group(0))
            slist = [each_event.group(0)]
            isPlayable = 'false'
            chanId = '0'
            isFolder=True
            playUrl = 'Whatever'
            mode = '4'
            __navigator__.add_nav_item(slist,
                                       isPlayable,
                                       chanId,
                                       isFolder,
                                       playUrl,
                                       mode)

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
    
    def get_schedule_item(self, schedulepage, date):
        __navigator__ = FSS_Navigator.FSS_Navigator()
        str_searchdate = date
        tt_searchdate = time.strptime(str_searchdate, "%Y-%m-%d %H:%M:%S")
        str_searchdate = time.strftime("%m-%d-%Y", tt_searchdate)
        
        for each_event in self.event.finditer(schedulepage):
            cat = self.eventcat.search(each_event.group(1)).group(1)
            title = self.eventtitle.search(each_event.group(1)).group(1)
            title = self.stripchannel.sub('', title).strip()
            date = self.eventdate.search(each_event.group(1))
            dates = date.group(1).strip()
            dst = self.event_dst.search(each_event.group(1))
            if dst == None:
                isdst = True
            else:
                isdst = False
            if self.reoccuring_event.search(dates) != None:
                dates = str_searchdate
            if self.multiday_event.search(dates) != None:
                datesplit = re.split(' to ', dates)
                startdate = datesplit[0]
            else:
                startdate = str_searchdate
            etime = self.eventtime.search(each_event.group(1))
            starthour = etime.group(1)
            event_start = ''.join([startdate, ' ', starthour])
            tt_event_start = time.strptime(event_start, "%m-%d-%Y %I:%M %p")
            if isdst == False:
                dt_event_start = datetime.datetime(*tt_event_start[0:6]) + datetime.timedelta(hours=1)
                tt_event_start= dt_event_start.timetuple()
            
            for every_channel in self.channel.finditer(each_event.group(0)):
#                slist = [cat, ' | ', title, '| ', starthour, ' - Live on VIP', every_channel.group(1)]
                slist = [cat, ' | ', title, ' | ', starthour]
                isPlayable = 'true'
                chanId = every_channel.group(1)
                isFolder=False
                playUrl = urllib.quote_plus(self.channelurl %chanId)
                mode = '5'
                __navigator__.add_nav_item(slist,
                                           isPlayable,
                                           chanId,
                                           isFolder,
                                           playUrl,
                                           mode)

    def convert_2_fssurldate(self, date):
        day = (date + timedelta(days=0)).timetuple()
        day = ''.join([str(day.tm_year),'-',str(day.tm_mon),'-',str(day.tm_mday)])
        return day
