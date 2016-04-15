# -*- coding: utf-8 -*-

#############################################################################
#
# Copyright (C) 2016 Miraclebox Multimedia AB
# All Rights Reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#############################################################################

from enigma import getDesktop, eTimer, eListboxPythonMultiContent, gFont

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap, MultiPixmap
from Components.Sources.List import List
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend

from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists

from twisted.web.client import downloadPage

from boxbranding import getMachineBrand

# Own imports
from tools import GetSVTPlayerVersion
from update import update_notification
from Cover import Cover
from ExtPlayer import ExMoviePlayer
from settings import *
from update import UpdateNotification

import helper
import bestofsvt as bestof
import svt as svt
import CommonFunctions as common 

#System Imports
import re
import json
import sys
import time
import urllib

MODE_CHANNELS = "kanaler"
MODE_A_TO_O = "a-o"
MODE_PROGRAM = "pr"
MODE_CLIPS = "clips"
MODE_LIVE_PROGRAMS = "live"
MODE_LATEST = "latest"
MODE_LATEST_NEWS = 'news'
MODE_POPULAR = "popular"
MODE_LAST_CHANCE = "last_chance"
MODE_VIDEO = "video"
MODE_CATEGORIES = "categories"
MODE_CATEGORY = "ti"
MODE_LETTER = "letter"
MODE_SEARCH = "search"
MODE_BESTOF_CATEGORIES = "bestofcategories"
MODE_BESTOF_CATEGORY = "bestofcategory"
MODE_VIEW_TITLES = "view_titles"
MODE_VIEW_EPISODES = "view_episodes"
MODE_VIEW_CLIPS = "view_clips"
MODE_PLAYLIST_MANAGER = "playlist-manager"
MODE_FAVORITES = "favorites"


def SVTMenuEntryComponent(name, description, long_description = None, pngname="default", info = None, width=540):
	#print "SVTMenuEntryComponent :", name, description, long_description, pngname, width
	screenwidth = getDesktop(0).size().width()
	if screenwidth and screenwidth == 1920:
		width = 1280
		icons = "iconsHD"
	else:
		width = 640
		icons = "icons"
		
	png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/SVTPlay/" + icons + "/" + pngname + ".png") 
	if png is None: 
		png = LoadPixmap("/usr/lib/enigma2/python/Plugins/Extensions/SVTPlay/" + icons + "/CategoryItem.png")

	if screenwidth and screenwidth == 1920:
		return [
			(_(name), description, long_description, info),
			#MultiContentEntryText(pos=(100, 0), size=(width-60, 40), font=0, text = _(name)),
			#MultiContentEntryPixmapAlphaBlend(pos=(10, 5), size=(90, 90), png = png),
			MultiContentEntryText(pos=(20, 0), size=(width-60, 40), font=0, text = _(name)),
			MultiContentEntryPixmapAlphaBlend(pos=(10, 5), size=(0, 0), png = png),
		]
	else:
		return [
			(_(name), description, long_description, info),
			#MultiContentEntryText(pos=(60, 0), size=(width-60, 30), font=0, text = _(name)),
			#MultiContentEntryPixmapAlphaBlend(pos=(5, 0), size=(30, 30), png = png),
			MultiContentEntryText(pos=(10, 0), size=(width-60, 30), font=0, text = _(name)),
			MultiContentEntryPixmapAlphaBlend(pos=(5, 0), size=(0, 0), png = png),
		]
	
class SVTMenuList(MenuList):
	def __init__(self, list, enableWrapAround=True):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		screenwidth = getDesktop(0).size().width()
		if screenwidth and screenwidth == 1920:
			self.l.setFont(0, gFont("Regular", 32))
			self.l.setItemHeight(80)  
		else:
			self.l.setFont(0, gFont("Regular", 22))
			self.l.setItemHeight(30)
			
class SVTPlayMainMenu(Screen):
	skin = """
	<screen position="center,110" size="1100,550" title="SVTPlay" flags="wfNoBorder" >
		<!--<widget source="list" render="Listbox" position="10,10" size="720,475" scrollbarMode="showOnDemand" transparent="1" alphatest="blend">
			<convert type="TemplatedMultiContent">
                		{"template": [
                		MultiContentEntryText(pos = (60, 1), size = (640, 36), flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),
                		MultiContentEntryPixmapAlphaTest(pos = (4, 2), size = (36, 36), png = 3),
                		],
                		"fonts": [gFont("Regular", 24)],
                		"itemHeight": 36
                		}
            		</convert>
		</widget>-->
		<widget name="list" position="10,10" size="720,475" scrollbarMode="showOnDemand" transparent="1" alphatest="blend"/>
		<widget name="coverArt" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/SVTPlay/icons/fanart.png" position="740,10" size="355,226" transparent="1" alphatest="blend"/>
		<widget name="aired" position="740,250" size="170,35" font="Regular;20" transparent="1"/>
		<widget name="duration" position="930,250" size="170,35" font="Regular;20" transparent="1"/>
		<widget name="plot" position="740,280" size="355,226" font="Regular;20" transparent="1"/>
		
		<widget name="loadingPixmap" position="840,480" size="70,70" zPosition="10" pixmaps="/usr/lib/enigma2/python/Plugins/Extensions/SVTPlay/icons/buffering/buffering_1.png,/usr/lib/enigma2/python/Plugins/Extensions/SVTPlay/icons/buffering/buffering_2.png,/usr/lib/enigma2/python/Plugins/Extensions/SVTPlay/icons/buffering/buffering_3.png,/usr/lib/enigma2/python/Plugins/Extensions/SVTPlay/icons/buffering/buffering_4.png,/usr/lib/enigma2/python/Plugins/Extensions/SVTPlay/icons/buffering/buffering_5.png,/usr/lib/enigma2/python/Plugins/Extensions/SVTPlay/icons/buffering/buffering_6.png,/usr/lib/enigma2/python/Plugins/Extensions/SVTPlay/icons/buffering/buffering_7.png,/usr/lib/enigma2/python/Plugins/Extensions/SVTPlay/icons/buffering/buffering_8.png" transparent="1" alphatest="blend" />
		<widget name="loadingText" position="910,490" size="260,35" zPosition="10" font="Regular;30" transparent="1" />
		    
		<ePixmap position="40,504" size="200,40" zPosition="0" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="blend"/>
		<ePixmap position="320,504" size="200,40" zPosition="0" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="blend"/>
		<ePixmap position="600,504" size="200,40" zPosition="0" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="blend"/>
		<!--<ePixmap position="880,504" size="200,40" zPosition="0" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="blend"/>-->
		<widget name="key_red" position="80,504" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="red" transparent="1" />
		<widget name="key_green" position="360,504" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="green" transparent="1" />
		<widget name="key_yellow" position="660,504" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="yellow" transparent="1" />
		<!--<widget name="key_blue" position="940,504" zPosition="1" size="270,35" font="Regular;32" valign="top" halign="left" backgroundColor="blue" transparent="1" />-->
	</screen>"""
	
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, "SVTPlay")
		
		if config.svtplay.checkUpdateOnStartUp.value:
			update_notification = UpdateNotification()
			update_notification.setSession(self.session)
			update_notification.UpdateSVTPlayer()
	
		if config.svtplay.stopTv.value:
			self.session.nav.stopService()

		self.oldref = self.session.nav.getCurrentlyPlayingServiceReference()

		self.oldUrl = ""
		self.oldUrl2 = ""
		self.categoriesUrl = []
		
		self.can_exit = 0
		
		self["coverArt"] = Cover(self.coverLoaded)
		self["duration"] = Label()
		self["aired"] = Label()
		self["plot"] = Label()
		
		self["categoryTitle"] = Label()
		self["categoryTitle"].setText(_("Main Menu"))

		msg = ((_('Loading')) + '...')
		self['loadingText'] = Label(msg)
		self['loadingPixmap'] = MultiPixmap()
		
		self['loadingPixmap'].hide()
		self['loadingText'].hide()
		
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.updateLoadingPixmap)
		
		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_(" "))
		self["key_yellow"] = Label(_("Settings"))
		self["key_blue"] = Label(_("About"))
		
		self.list = []
		self["list"] = SVTMenuList(self.list)
		self.selectedList = []
		self.onChangedEntry = []
		
		self["list"].onSelectionChanged.append(self.selectionChanged)
		
		self.mainList()

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "WizardActions"],
		{
			"ok": self.KeyOk,
			"cancel": self.KeyExit,
			"red": self.KeyRed,
			"yellow": self.KeyYellow,
			"blue": self.KeyBlue,
			"up": self.KeyUp,
			"down": self.KeyDown,
			"back": self.KeyExit
		})

		self.onLayoutFinish.append(self.layoutFinished)

	def KeyUp(self):
		print "[SVTPlay] KeyUp"
		
	def KeyDown(self):
		print "[SVTPlay] KeyDown"
	      
	def layoutFinished(self):
		print "[SVTPlay] layoutFinished"

	def startShowLoading(self):
		self.curpix = 0
		self.count = 0
		self['loadingPixmap'].setPixmapNum(0)
		self.activityTimer.start(10)

	def updateLoadingPixmap(self):
		self.activityTimer.stop()
		if self.curpix > 7:
			self.curpix = 0
			self.count += 0
		if self.count > 1000:
			self.curpix = 7
		self['loadingPixmap'].setPixmapNum(self.curpix)
		#if self.count == 35:
			
			#self.hide()
			#self.close()
		self.activityTimer.start(140)
		self.curpix += 1
		self.count += 1

	def delTimer(self):
		del self.activityTimer

	def coverDownloadFailed(self, result):
		print '[SVTPlay] cover download failed: %s ' % result

	def selectionChanged(self):
		print "[SVTPlay] selectionChanged()"
		
		info = self["list"].getCurrent()[0][3]
		#print "[SVTPlay] selectionChanged : ", info
		
		try:
			duration = info["duration"]
		except:
			duration = "N/A"
		
		try:
			aired = info["aired"][:10]
		except:
			aired = "N/A"
		
		try:
			plot = info["plot"]
		except:
			plot = "N/A"
			
		if info:
			self["duration"].setText(_("Duration: ") + str(duration) + _(" min"))
			self["plot"].setText(str(plot))
			self["aired"].setText(_("Aired: ") + str(aired))
		else:
			self["duration"].setText("")
			self["plot"].setText("")
			self["aired"].setText("")

		self.downloadCover()
		
	def downloadCover(self):
		#self['coverArt'].updateIcon('/usr/lib/enigma2/python/Plugins/Extensions/SVTPlay/icons/fanart.png')
		downloadPage(str(self["list"].getCurrent()[0][2]), '/tmp/.cover').addCallback(self.coverDownloadFinished).addErrback(self.coverDownloadFailed)
		
	def hideCover(self):
		print '[SVTPlay] hide cover'
		self['coverArt'].hide()
		self['coverArt'].setPicloaded(False)

	def coverDownloadFinished(self, result):
		print '[SVTPlay] cover download finished'
		self['coverArt'].updateIcon('/tmp/.cover')
        
	def coverLoaded(self):
		print '[SVTPlay] cover loaded'
		self['coverArt'].show()
        
        def KeyRed(self):
		print '[SVTPlay] KeyRed'
		self.close()

        def KeyYellow(self):
		print '[SVTPlay] KeyYellow'
		self.session.open(SVTPlaySetup)

        def KeyBlue(self):
		print '[SVTPlay] KeyBlue'
		about_text = _('SVT Play - Version: %s\n\nPlugin for Enigma2 based on KODI addon.\n\nSupport on:\nhttp://miracleforum.net\n\nGIT:\nhttps://github.com/miraclebox-git/SVTPlay-Enigma2') % (GetSVTPlayerVersion())
		self.session.open(MessageBox, about_text, MessageBox.TYPE_INFO)

        def KeyExit(self):
		print '[SVTPlay] KeyExit, last menu : ', self.oldUrl, self.oldUrl2

		if self.can_exit == 0:
			if config.svtplay.stopTv.value:
				self.session.nav.playService(self.oldref)
				self.close()
		else:
			self.can_exit = self.can_exit - 1
			
		if self.oldUrl == "":
			self.close()
		elif self.oldUrl == MODE_CATEGORIES:
			self.mainList()
		elif self.oldUrl == MODE_CATEGORY:
			if self.oldUrl2 not in self.categoriesUrl:
				self.viewCategories()
			else:
				self.mainList()
		elif self.oldUrl == MODE_PROGRAM:
			try:
				self.viewProgramsForCategories(self.oldUrl2)
				self.oldUrl = MODE_CATEGORY
			except:
					self.mainList()
		elif self.oldUrl == MODE_CLIPS:
			self.viewClips(self.oldUrl2)
		elif self.oldUrl == MODE_A_TO_O:
			self.mainList()
		elif self.oldUrl in (MODE_POPULAR, MODE_LATEST, MODE_LAST_CHANCE, MODE_LIVE_PROGRAMS):
			self.mainList()
		elif self.oldUrl == MODE_LATEST_NEWS:
			self.mainList()
		elif self.oldUrl == MODE_CHANNELS:
			self.mainList()
		elif self.oldUrl == MODE_LETTER:
			self.mainList()
		elif self.oldUrl == MODE_SEARCH:
			self.mainList()
		elif self.oldUrl == MODE_BESTOF_CATEGORIES:
			self.mainList()
		elif self.oldUrl == MODE_BESTOF_CATEGORY:
			self.viewBestOfCategories()
			self.oldUrl = MODE_BESTOF_CATEGORIES
		else:
			if config.svtplay.stopTv.value:
				self.session.nav.playService(self.oldref)
				self.close()
		    

	def KeyOk(self):
		self.can_exit = self.can_exit + 1
		
		self.sel = self["list"].getCurrent()
		self["categoryTitle"].setText(self.sel[0][0])

		#print "[SVTPlay] KeyOK : ", self.sel
		#print "[SVTPlay] KeyOK : ", self.sel[0]
		#print "[SVTPlay] KeyOK : ", self.sel[0][0]
		#print "[SVTPlay] KeyOK : ", self.sel[0][1]
		
		try:
			ARG_URL = self.sel[0][1]["url"]
		except:
			ARG_URL = "none"
		
		try:
			ARG_PAGE = self.sel[0][1]["page"]
		except:
			ARG_PAGE = "1"
			
		try:
			ARG_TITLE = str(self.sel[0][0])
		except:
			ARG_TITLE = "N/A"
				
		ARG_MODE = self.sel[0][1]["mode"]
		
		if ARG_MODE not in ("pr", "bestofcategory", "video"):
			self.oldUrl2 = ARG_URL
		if ARG_MODE not in ("video"):
			self.oldUrl = ARG_MODE
		
		print "[SVTPlay] ARG_MODE = " + ARG_MODE + " ARG_URL = " + ARG_URL
		if ARG_MODE == MODE_CATEGORIES:
			print "[SVTPlay] ARG_MODE == MODE_CATEGORIES"
			self.viewCategories()
		elif ARG_MODE == MODE_CATEGORY:
			print "[SVTPlay] ARG_MODE == MODE_CATEGORY ARG_URL = " + ARG_URL
			self.viewProgramsForCategories(ARG_URL)
		elif ARG_MODE == MODE_PROGRAM:
			print "[SVTPlay] ARG_MODE == MODE_PROGRAM"
			self.viewEpisodes(ARG_URL)
			self.addClipDirItem(ARG_URL)
		elif ARG_MODE == MODE_CLIPS:
			print "[SVTPlay] ARG_MODE == CLIPS"
			self.viewClips(ARG_URL)
		elif ARG_MODE == MODE_A_TO_O:
			self.viewAtoO()
		elif ARG_MODE == MODE_VIDEO:
			self.playVideo(ARG_URL, ARG_TITLE)
		elif ARG_MODE in (MODE_POPULAR, MODE_LATEST, MODE_LAST_CHANCE, MODE_LIVE_PROGRAMS):
			self.viewSection(ARG_MODE, int(ARG_PAGE))
		elif ARG_MODE == MODE_LATEST_NEWS:
			self.viewLatestNews()
		elif ARG_MODE == MODE_CHANNELS:
			self.viewChannels()
		elif ARG_MODE == MODE_LETTER:
			self.viewProgramsByLetter(ARG_PARAMS.get("letter"))
		elif ARG_MODE == MODE_SEARCH:
			self.viewSearch()
		elif ARG_MODE == MODE_BESTOF_CATEGORIES:
			self.viewBestOfCategories()
		elif ARG_MODE == MODE_BESTOF_CATEGORY:
			self.viewBestOfCategory(ARG_URL)
  
	def noYet(self):
		nobox = self.session.open(MessageBox, _("Function Not Yet Available"), MessageBox.TYPE_INFO)
		nobox.setTitle(_("Info"))
	
	def viewCategories(self):
		categories = svt.getCategories()
		if not categories:
			return
      
		self.categoriesUrl = []
		self.clearList()
		for category in categories:
			self.categoriesUrl.append(str(category["url"]))
			self.addDirectoryItem(str(category["title"]), { "mode": MODE_CATEGORY, "url": category["url"] }, thumbnail = str(category["thumbnail"]))
		# Hack for SelectionChanged
		self.updateList()

	def viewProgramsForCategories(self, url):
		programs = svt.getProgramsForCategory(url)
		if not programs:
			return
		
		self.clearList()
		for program in programs:
			self.addDirectoryItem(str(program["title"]), { "mode" : MODE_PROGRAM, "url" : program["url"] }, thumbnail = str(program["thumbnail"]))
		# Hack for SelectionChanged
		self.updateList()

	def viewEpisodes(self, url):
		"""
		Displays the episodes for a program with URL 'url'.
		"""
		episodes = svt.getEpisodes(url)
		if not episodes:
			print ("No episodes found!")
			return

		self.clearList()
		for episode in episodes:
			self.createDirItem(episode, MODE_VIDEO)
			
		# Hack for SelectionChanged
		self.updateList()

	def viewLatestNews(self):
		items = svt.getLatestNews()
		if not items:
			return

		self.clearList()    
		for item in items:
			self.createDirItem(item, MODE_VIDEO)
			
		# Hack for SelectionChanged
		self.updateList()

	def viewChannels(self):
		channels = svt.getChannels()
		if not channels:
			return
		      
		self.clearList()
		for channel in channels:
			self.createDirItem(channel, MODE_VIDEO)
		
		# Hack for SelectionChanged
		self.updateList()

	def viewProgramsByLetter(self, letter):
		programs = svt.getProgramsByLetter(letter)
		if not programs:
			return
      
		self.clearList()
		for program in programs:
			self.addDirectoryItem(str(program["title"]), { "mode": MODE_PROGRAM, "url": program["url"] })
		# Hack for SelectionChanged
		self.updateList()

	def viewBestOfCategories(self):
		"""
		Creates a directory displaying each of the
		categories from the bestofsvt page
		"""
		categories = bestof.getCategories()
		if not categories:
			return
      
		params = {}
		params["mode"] = MODE_BESTOF_CATEGORY

		self.clearList()
		for category in categories:
			params["url"] = category["url"]
			self.addDirectoryItem(str(category["title"]), params)
		# Hack for SelectionChanged
		self.updateList()


	def viewBestOfCategory(self, url):
		"""
		Creates a directory containing all shows displayed
		for a category
		"""
		shows = bestof.getShows(url)
		if not shows:
			return

		params = {}
		params["mode"] = MODE_VIDEO

		self.clearList()
		for show in shows:
			params["url"] = show["url"]
			self.addDirectoryItem(str(show["title"]), params, show["thumbnail"], False, False, show["info"])
		# Hack for SelectionChanged
		self.updateList()

	def viewAtoO(self):
		programs = svt.getAtoO()
		if not programs:
			return

		self.clearList()
		for program in programs:
			self.addDirectoryItem(str(program["title"]), { "mode": MODE_PROGRAM, "url": program["url"] })
		# Hack for SelectionChanged
		self.updateList()

	def viewClips(self, url):
		"""
		Displays the latest clips for a program
		"""
		clips = svt.getClips(url)
		if not clips:
			print("No clips found!")
			return

		self.clearList()
		for clip in clips:
			self.createDirItem(clip, MODE_VIDEO)
			
		# Hack for SelectionChanged
		self.updateList()

	def viewSection(self, section, page):
		(items, moreItems) = svt.getItems(section, page)
		if not items:
			return
      
		self.clearList()
		for item in items:
			self.createDirItem(item, MODE_VIDEO)
		if moreItems:
			self.addNextPageItem(page+1, section)
			if page > 1:
				self.addPrevPageItem(page-1, section)
				
		# Hack for SelectionChanged
		self.updateList()

	def viewSearch(self):
		from Screens.VirtualKeyBoard import VirtualKeyBoard
		self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title = _("Search for:"), text = "")
	
	def VirtualKeyBoardCallback(self, callback = None):
		    if callback is not None and len(callback):
			    self.viewSearchCallBack(callback)
			    
	def viewSearchCallBack(self, keyword):
		if keyword == "" or not keyword:
			self.mainList()
			return
		
		self.clearList()
		keyword = urllib.quote(keyword)
		helper.infoMsg("Search string: " + keyword)

		keyword = re.sub(r" ", "+", keyword)

		results = svt.getSearchResults(keyword)
		for result in results:
			mode = MODE_VIDEO
			if result["type"] == "program":
				mode = MODE_PROGRAM
			self.createDirItem(result["item"], mode)
			
		#Hack for SelectionChanged
		self.updateList()
    
	def playVideo(self, url, title):
		if not url.startswith("/"):
			url = "/" + url

		url = svt.BASE_URL + url + svt.JSON_SUFFIX

		try:
			show_obj = helper.resolveShowURL(url)

			if show_obj["videoUrl"]:
				print "[SVTPlay] videoUrl : ", show_obj["videoUrl"].replace(":", "%3a")

				from enigma import eServiceReference
				
				url = "4097:1:0:1:0:0:0:0:0:0:http%3a//127.0.0.1%3a88/hlsvariant%3a//" +  str(show_obj["videoUrl"].replace(":", "%3a")) + ":" + title
				print "[SVTPlay] videoUrl: ", url
				fileRef = eServiceReference(url)
				self.session.open(ExMoviePlayer, fileRef)
			else:
				self.session.open(MessageBox, _('Sorry, NO VIDEO url found !'), MessageBox.TYPE_ERROR)
		except:
			self.session.open(MessageBox, _('Sorry, VIDEO url found !'), MessageBox.TYPE_ERROR)

	def clearList(self):
		self.list = []

	def updateList(self):
		self["list"].l.setList(self.list)

	def mainList(self):
		self["categoryTitle"].setText(_("Main Menu"))
		
		self.list = []
		self.addDirectoryItem("Popular", { "mode": MODE_POPULAR })
		self.addDirectoryItem("Latest programs", { "mode": MODE_LATEST })
		self.addDirectoryItem("Latest news broadcast", { "mode": MODE_LATEST_NEWS })
		self.addDirectoryItem("Last chance", { "mode": MODE_LAST_CHANCE })
		self.addDirectoryItem("Live broadcasts", { "mode": MODE_LIVE_PROGRAMS })
		self.addDirectoryItem("Channels", { "mode": MODE_CHANNELS })
		self.addDirectoryItem("Programs A-Ö", { "mode": MODE_A_TO_O })
		self.addDirectoryItem("Categories", { "mode": MODE_CATEGORIES })
		self.addDirectoryItem("BestOfSVT.se", { "mode": MODE_BESTOF_CATEGORIES })
		self.addDirectoryItem("Search", { "mode": MODE_SEARCH })
		#self.addDirectoryItem("Favorites", { "mode": MODE_FAVORITES })
		#self.addDirectoryItem("Playlist", { "mode": MODE_PLAYLIST_MANAGER }, folder=False)
		
		# Hack for SelectionChanged
		self.updateList()
		
	def addNextPageItem(self, nextPage, section):
		self.addDirectoryItem("Next page", {  "page": nextPage, "mode": section})
		# Hack for SelectionChanged
		self.updateList()

	def addPrevPageItem(self, prevPage, section):
		self.addDirectoryItem("Previous page", {  "page": prevPage, "mode": section})
		# Hack for SelectionChanged
		self.updateList()

	def createDirItem(self, article, mode):
		"""
		Given an article and a mode; create directory item
		for the article.
		"""
		params = {}
		params["mode"] = mode
		params["url"] = article["url"]
		folder = False
		#if (article["title"].lower().endswith("teckentolkad") == False and article["title"].lower().find("teckenspråk".decode("utf-8")) == -1):
			#params = {}
			#params["mode"] = mode
			#params["url"] = article["url"]
			#folder = False

		if mode == MODE_PROGRAM:
			folder = True
		info = None
		if "info" in article.keys():
			info = article["info"]
		self.addDirectoryItem(str(article["title"]), params, str(article["thumbnail"]), folder, False, info)
		# Hack for SelectionChanged
		self.updateList()
    
	def addDirectoryItem(self, title, params, thumbnail = None, folder = True, live = False, info = None):
		'''print "[SVTPlay] Title : ", title
		print "[SVTPlay] Params : ", params
		print "[SVTPlay] Thumbnail : ", thumbnail
		print "[SVTPlay] Folder : ", folder
		print "[SVTPlay] Live : ", live
		print "[SVTPlay] Info : ", info'''
		
		if params["mode"] == "video":
			mypixmap = "VideoItem"
		else:
			mypixmap = "CategoryItem"
		png = mypixmap
		name = _(title)
		data = params

		self.list.append(SVTMenuEntryComponent(title, data, thumbnail, png, info))
		
	def addClipDirItem(self, url):
		"""
		Adds the "Clips" directory item to a program listing.
		"""
		params = {}
		params["mode"] = MODE_CLIPS
		params["url"] = url
		self.addDirectoryItem(_("Clips"), params)
		
		# Hack for SelectionChanged
		self.updateList()

def main(session, **kwargs):
	if getMachineBrand() in ("Miraclebox"):
		session.open(SVTPlayMainMenu)
	else:
		session.open(MessageBox, _('Sorry, this plugin is dedicated for Miraclebox only !'), MessageBox.TYPE_ERROR)

def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(_("SVT Play"), main, "svt_play", 1)]
	return []

from Plugins.Plugin import PluginDescriptor
def Plugins(**kwargs):
	screenwidth = getDesktop(0).size().width()
	desc_mainmenu = PluginDescriptor(name = "SVT Play", description = _('www.svtplay.se'), where = PluginDescriptor.WHERE_MENU, fnc = menu)
	desc_plugin = PluginDescriptor(name = "SVT Play", description=_('www.svtplay.se'), icon='plugin_iconhd.png', where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main)
	desc_pluginhd = PluginDescriptor(name = "SVT Play", description=_('www.svtplay.se'), icon='plugin_icon.png', where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main)
	desc_extensions = PluginDescriptor(name = "SVT Play", description=_('www.svtplay.se'), icon='plugin_icon.png', where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)

	list = []
	if config.svtplay.showOnMainMenu.value:
		list.append(desc_mainmenu)
	if config.svtplay.showOnExtensions.value:
		list.append(desc_extensions)
	if config.svtplay.showOnPluginList.value:
		if screenwidth and screenwidth == 1920:  
			list.append(desc_pluginhd)
		else:
			list.append(desc_plugin)
	return list
      