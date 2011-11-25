import re
import time

class Schedule:
    def __init__(self):
        self.scheduleList = []
        self.chanList  = [] # Channel Name & Channel URL
        self.match = re.compile('<h3>(.+?)</h3>')
        self.matchInfo = re.compile('<span.+?>(.+?) - (.+?)</span>(.+?)<span.+?>(.+?)</span>')
        self.__date__ = LOFDate()

    def ListSchedule(self, schedulePage):
        print "ListSchedule"
        self.ParseAndAppendSchedule(schedulePage)
        return self.scheduleList

    def ParseAndAppendSchedule(self, schedulePage):
        print "ParseAndAppendSchedule"
        for eachMatch in self.match.finditer(schedulePage):
            match = self.matchInfo.search(eachMatch.group(1))
            matchTime  = self.__date__.FixDate(match.group(1), match.group(2))
            matchTitleAndComp = match.group(3).strip(' - ')
            matchTitleAndComp = re.split(' - ', matchTitleAndComp)
            matchTitle = matchTitleAndComp[0]
            matchComp = matchTitleAndComp[1]
            for eachChannel in re.finditer('Channel (.+?)', match.group(4)):
                chanURL = ''.join(['channel', eachChannel.group(1), '.php'])
                chanName = eachChannel.group(0)
                self.chanList.append((chanURL, chanName))
            self.scheduleList.append((matchTime, matchTitle, matchComp, self.chanList))
            self.chanList = []

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
        currTime = time.localtime()
        ttDay = self.DateAddYear(ttDay, dateStr)
        # Make the event a timeStamp
        eventTimeStamp = time.mktime(ttDay)
        # Modify the event timeStamp to local time
        newTimeStamp = eventTimeStamp - time.timezone
        # Make it a timetuple
        newTimeTuple = time.localtime(newTimeStamp)
        # Finally make it a string
        dateStrPart1 = time.strftime("%H:%M | %A ", newTimeTuple)
        dateStrPart2 = self.DateToOrdinal(newTimeTuple.tm_mday)
        dateStrPart3 = time.strftime("%b", newTimeTuple)
        dateStr = ''.join([dateStrPart1, dateStrPart2, ' ', dateStrPart3])
        return dateStr
    
    def DateFromOrdinal(self, mDate):
        print "DateFromOrdinal"
        x = mDate.split(' ')
        removedOrdinal = ''.join([x[0], ' ', re.sub(r'[a-zA-Z]', '', x[1]), ' ', x[2]])
        return removedOrdinal

    def DateToOrdinal(self, mDate):
        print "DateToOrdinal"
        if 10 <= mDate % 100 < 20:
            return str(mDate) + 'th'
        else:
            return  str(mDate) + {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(mDate % 10, "th")

    def DateAddYear(self, ttDay, dateStr):
        print "DateAddYear"
        currTime = time.localtime()
        # if not December set year as this year
        if currTime.tm_mon != 12:
            ttDay = time.strptime(''.join([dateStr, ' ', str(currTime.tm_year)]), "%H:%M %a %d %b %Y")
        else:
            # If event month is January (and currTime is December) set year as next year
            if ttDay.tm_mon == 1:
                    ttDay = time.strptime(''.join([dateStr, ' ', str(currTime.tm_year + 1)]), "%H:%M %a %d %b %Y")
        return ttDay
