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

from Screens.MessageBox import MessageBox
from Tools.Directories import fileExists

from twisted.web.client import downloadPage
from tools import GetSVTPlayerVersion

from enigma import eTimer

import zipfile
from os import system

class UpdateNotification:
	def setSession(self, session):
		self.session = session
		
	def UpdateSVTPlayer(self):
		print "[SVTPlay] UpdateSVTPlayer"
		downloadPage("https://raw.githubusercontent.com/miraclebox-git/SVTPlay-Enigma2/master/usr/lib/enigma2/python/Plugins/Extensions/SVTPlay/version.py", '/tmp/svtversion.txt').addCallback(self.downloadVersionFileFinished).addErrback(self.errorUpdate)

	def downloadVersionFileFinished(self, html):
		print "[SVTPlay] downloadVersionFileFinished"
		is_update = False
		if fileExists("/tmp/svtversion.txt"):
			self.version_txt = open('/tmp/svtversion.txt', 'r').read()[11:16]
			if (int(self.version_txt.replace(".", "")) > int(GetSVTPlayerVersion().replace(".", ""))):
				is_update = True
		if is_update:
			message = _('There is new version of SVTPlay available.\nDo you want to install new version ?\n\nCurrent Version: %s\nNew Version: %s') % (GetSVTPlayerVersion(), self.version_txt)
			self.session.openWithCallback(self.downloadNewVersion, MessageBox, message, MessageBox.TYPE_YESNO)

	def UpdateTimerInit(self):
		print "[SVTPlay] UpdateTimerInit"
		self.update_timer = eTimer()
		self.update_timer.callback.append(self.UpdateSVTPlayer)
		self.update_timer.start(1000, True)

	def downloadNewVersion(self, yesno):
		if yesno:
			self.upgradeDownloadStart()

	def errorUpdate(self, html):
		print "[SVTPlay] errorUpdate : ",  html
		self.session.open(MessageBox, _("Can not download informations about new version!"), type = MessageBox.TYPE_ERROR, timeout=5 )

	def upgradeDownloadStart(self):
		self.session.open(MessageBox, _("Downloading new version..."), type = MessageBox.TYPE_INFO)
		downloadPage("https://github.com/miraclebox-git/SVTPlay-Enigma2/archive/master.zip", '/tmp/svtplay.zip').addCallback(self.upgradeDownloadFinished).addErrback(self.upgradeDownloadFailed)

	def upgradeDownloadFailed(self, result):
		print '[SVTPlay] upgrade download failed: %s ' % result
		self.session.open(MessageBox, _("Can not download new version!"), type = MessageBox.TYPE_ERROR, timeout=5 )

	def upgradeDownloadFinished(self, result):
		print '[SVTPlay] upgrade download finished'
		try:
			self.session.open(MessageBox, _("Installing new version..."), type = MessageBox.TYPE_INFO)
			zf = zipfile.ZipFile(r"/tmp/svtplay.zip")
			zf.extractall(r"/tmp/svtplay/")
			system('cp -a /tmp/svtplay/SVTPlay-Enigma2-master/* /')
			print '[SVTPlay] upgraded finished'
			self.session.openWithCallback(self.restartGUI, MessageBox, _("System restart after SVTPlay update to version[%s].\n\n") % self.version_txt, type = MessageBox.TYPE_INFO, timeout = 5 )
		except:
			self.session.open(MessageBox, _("Restart system failed. \nPlease restart STB manually."), type = MessageBox.TYPE_INFO, timeout = 5)

	def restartGUI(self, ret):
		if ret:
			from enigma import quitMainloop
			quitMainloop(3)
			
update_notification = UpdateNotification()
