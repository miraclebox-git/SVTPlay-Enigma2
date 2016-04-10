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

from Screens.InfoBar import MoviePlayer

class ExMoviePlayer(MoviePlayer):
	def __init__(self, session, service):
		self.session = session
		MoviePlayer.__init__(self, session, service)
		self.skinName = "MoviePlayer"
		MoviePlayer.WithoutStopClose = True

	def doEofInternal(self, playing):
		self.close()
		#self.leavePlayer()
			
	def leavePlayer(self):
		self.close()
		#list = ((_("Yes"), "y"), (_("No"), "n"),)
		#self.session.openWithCallback(self.cbDoExit, ChoiceBox, title=_("Stop playing this movie?"), list = list)

	def cbDoExit(self, answer):
		answer = answer and answer[1]
		if answer == "y":
			self.close()
			
	def up(self):
		print "Up"
	
	def down(self):
		print "Down"