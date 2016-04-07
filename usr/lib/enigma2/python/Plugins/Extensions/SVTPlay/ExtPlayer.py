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