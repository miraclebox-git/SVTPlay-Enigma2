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
