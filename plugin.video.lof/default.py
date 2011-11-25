#XBMC liveonlinefooty.com Plugin
#
#Copyright (C) 2011  mclog and myksterx
#Official Development Thread - http://forum.xbmc.org/showthread.php?t=97494
#Official Release Thread - http://forum.xbmc.org/showthread.php?p=776481#post776481
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import sys

import urllib
import xbmcaddon

from modules import LOFCore

__settings__ = xbmcaddon.Addon("plugin.video.lof");
__nav__      = LOFCore.LOFNavigator()

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring)>=2:
        params = sys.argv[2]
        cleanedparams = params.replace('?','')
        if (params[len(params)-1] == '/'):
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

params = get_params()

url = None
mode = None
try:
    url = urllib.unquote_plus(params["url"])
    title = urllib.unquote_plus(params["title"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass

if mode == None or url==None or len(url)<1:
    print "Mode None - MainMenu"
    __nav__.MainMenu()
elif mode == 1:
    print "Mode 1 - ListChannels"
    __nav__.ListChannels()
elif mode == 2:
    print "Mode 2 - ListSchedule"
    __nav__.ListSchedule()
elif mode == 5:
    print "Mode 5 - PlayStream"
    __nav__.PlayStream(url)
elif mode == 6:
    print "Mode 6 - ListChannelSchedule"
    __nav__.ListChannelSchedule(url)
