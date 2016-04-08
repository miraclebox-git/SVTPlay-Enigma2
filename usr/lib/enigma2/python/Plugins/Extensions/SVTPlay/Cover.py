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

from enigma import ePicLoad
from Components.Pixmap import Pixmap

class Cover(Pixmap):
	def __init__(self, callback = None):
		Pixmap.__init__(self)
		self.picload = ePicLoad()
		self.picload.PictureData.get().append(self.paintIconPixmapCB)
		self.callback = callback
		self.picloaded = False
		self.showPic = False

	def onShow(self):
		Pixmap.onShow(self)
		if self.instance.size().width() > 0:
			self.picload.setPara((self.instance.size().width(), self.instance.size().height(), 1, 1, False, 1, '#00000000'))
			self.showPic = True

	def paintIconPixmapCB(self, picInfo = None):
		ptr = self.picload.getData()
		if self.showPic and ptr != None:
			self.instance.setPixmap(ptr)
			self.picloaded = True
		if self.callback is not None:
			self.callback()
		return

	def updateIcon(self, filename):
		self.picloaded = False
		if self.showPic:
			self.picload.startDecode(filename)

	def setPicloaded(self, value):
		self.picloaded = value

	def getPicloaded(self):
		return self.picloaded
