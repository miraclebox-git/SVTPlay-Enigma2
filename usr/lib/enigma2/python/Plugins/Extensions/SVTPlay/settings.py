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

from Components.ActionMap import ActionMap
from Components.Label import Label

from Components.config import *
from Components.UsageConfig import *
from Components.ConfigList import *

from Screens.Screen import Screen

from Tools.Directories import fileExists

config.svtplay = ConfigSubsection()
config.svtplay.showOnMainMenu = ConfigYesNo(default=True)
config.svtplay.showOnExtensions = ConfigYesNo(default=False)
config.svtplay.showOnPluginList = ConfigYesNo(default=False)
config.svtplay.stopTv = ConfigYesNo(default=False)

class SVTPlaySetup(Screen, ConfigListScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["Setup"]
		Screen.setTitle(self, _("SVTPlay Setup"))
		
		self.list = []
		
		ConfigListScreen.__init__(self, self.list)
			
		self["key_red"] = Label(_("Exit"))
		self["key_green"] = Label(_("Save"))

		self["actions"] = ActionMap(["WizardActions", "ColorActions"],
		{
			"green": self.keySave,
			"back": self.keyCancel,
			"red": self.keyCancel,
		}, -2)
		
		self.list.append(getConfigListEntry(_("Show plugin on main menu"), config.svtplay.showOnMainMenu))
		self.list.append(getConfigListEntry(_("Show plugin on extensions list"), config.svtplay.showOnExtensions))
		self.list.append(getConfigListEntry(_("Show plugin on plugin list"), config.svtplay.showOnPluginList))
		self.list.append(getConfigListEntry(_("Stop TV when enter to plugin"), config.svtplay.stopTv))

		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)

	def keyRight(self):
		ConfigListScreen.keyRight(self)

	def keySave(self):
		for x in self["config"].list:
			x[1].save()

		self.close()

	def keyCancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()