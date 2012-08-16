import re
import time

class Schedule:
    def __init__(self):
        self.scheduleList = []
        self.chanList  = [] # Channel Name & Channel URL
        self.match = re.compile('<span.+?>(.+?) - (.+?)</span>(.+?)<span.+?>(.+?)</span>')
        self.channel = re.compile('<a href="http://www.dhmediahosting.com/watchlive/(.+?)"(.+?)</a>') #<font color="">(.+?)</font>(.+?)</a>')
        self.matchInfo = re.compile('<span.+?>(.+?) - (.+?)</span>(.+?)<span.+?>(.+?)</span>')
        self.previousPage = re.compile('<h3><a href=\"/(.+?)\">(.+?)</a> \| (.+?)</h3>')
        self.nextPage = re.compile('<h3>(.+?) \| <a href=\"/(.+?)\">(.+?)</a></h3>')
        self.__date__ = LOFDate()

    def ListSchedule(self, schedulePage):
        print "ListSchedule"
        self.ParseAndAppendSchedule(schedulePage)
        self.MoreScheduleListings(schedulePage)
        return self.scheduleList

    def ParseAndAppendSchedule(self, schedulePage):
        print "ParseAndAppendSchedule"
        for eachMatch in self.match.finditer(schedulePage):
            matchTime = self.__date__.FixDate(eachMatch.group(1), eachMatch.group(2))
            matchTitleAndComp = re.sub('<[^<]+?>', '', eachMatch.group(3)).strip(' - ')
            matchTitleAndComp = re.split(' - ', matchTitleAndComp)
            matchTitle = matchTitleAndComp[0]
            if len(matchTitleAndComp) > 1:
                matchComp = matchTitleAndComp[1]
            else:
                matchComp = ''
            # Add list of channels event is being broadcast on
            for eachChannel in self.channel.finditer(eachMatch.group(0)):
                chanURL = eachChannel.group(1)
                chanName = re.sub(r'target="player"><[^>]*?>', '', eachChannel.group(2))
                chanName = re.sub(r'</font>','',chanName)
                self.chanList.append((chanURL, chanName))
            self.scheduleList.append((matchTime, matchTitle + " (" + matchComp + ")", matchComp, self.chanList))
            self.chanList = []

    def MoreScheduleListings(self, schedulePage):
        print "MoreScheduleListings"
        if self.previousPage.search(schedulePage) == None:
            prevPage = False
        else:
            self.chanList.append((self.previousPage.search(schedulePage).group(1), ''))
            self.scheduleList.insert(0,(True, 'Previous Page', '', self.chanList))
        if self.nextPage.search(schedulePage) == None:
            nxtPage = False
        else:
            self.chanList.append((self.nextPage.search(schedulePage).group(2), ''))
            self.scheduleList.append((True, 'Next Page', '', self.chanList))
    
    def ListChannelSchedule(self):
        print "ListChannelSchedule"
        pass

class LOFDate:
    
    def __init__(self):
        return None

    def FixDate(self, mDate, mHour):
        print "FixDate"
        dateStr = ''.join([mHour, ' ', self.DateFromOrdinal(mDate)])
        ttDay = time.strptime(dateStr, "%H:%M %a %d %b")
        ttDay = self.DateAddYear(ttDay, dateStr)
        # Make the event a timeStamp
        eventTimeStamp = time.mktime(ttDay)
        # Modify the event timeStamp to local time
        newTimeStamp = eventTimeStamp - time.timezone
        # Make it a timetuple
        newTimeTuple = time.localtime(newTimeStamp)
        # Finally make it a string
        dateStrPart1 = time.strftime("%H:%M | %a ", newTimeTuple)
        dateStrPart2 = self.DateToOrdinal(newTimeTuple.tm_mday)
        dateStrPart3 = time.strftime("%b", newTimeTuple)
        dateStr = ''.join([dateStrPart1, dateStrPart2, ' ', dateStrPart3])
        return dateStr
    
    def DateFromOrdinal(self, mDate):
        x = mDate.split(' ')
        removedOrdinal = ''.join([x[0], ' ', re.sub(r'[a-zA-Z]', '', x[1]), ' ', x[2]])
        print "  removedOrdinal=" + removedOrdinal 
        return removedOrdinal

    def DateToOrdinal(self, mDate):
        print "DateToOrdinal"
        if 10 <= mDate % 100 < 20:
            return str(mDate) + 'th'
        else:
            return  str(mDate) + {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(mDate % 10, "th")

    def DateAddYear(self, ttDay, dateStr):
        currTime = time.localtime()
        # if not December set year as this year
        if currTime.tm_mon != 12:
            ttDay = time.strptime(''.join([dateStr, ' ', str(currTime.tm_year)]), "%H:%M %a %d %b %Y")
        else:
            # If event month is January (and currTime is December) set year as next year
            if ttDay.tm_mon == 1 and currTime.tm_mon == 12:
                ttDay = time.strptime(''.join([dateStr, ' ', str(currTime.tm_year + 1)]), "%H:%M %a %d %b %Y")
            # If event month is December and currTime is December set year as this year
            else:
                ttDay = time.strptime(''.join([dateStr, ' ', str(currTime.tm_year)]), "%H:%M %a %d %b %Y")
        return ttDay