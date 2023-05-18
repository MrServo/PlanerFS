# PYTHON IMPORTS
from configparser import ConfigParser
from datetime import date
from os import remove, system
from os.path import join
from PIL import Image, ImageFont, ImageDraw

# ENIGMA IMPORTS
from Tools.Directories import fileExists, resolveFilename, SCOPE_FONTS

# PLUGIN IMPORTS
from . import CONFIGPATH, CONFIGFILE, PLUGINPATH
from .routines import schicht

configparser = ConfigParser()
try:
	from Plugins.Extensions.LCD4linux.module import L4Lelement
	configparser = ConfigParser()
	configparser.read(CONFIGFILE)
	if configparser.has_option("settings", "l4l_sets"):
		l4l_sets = configparser.get("settings", "l4l_sets").split(":")
	else:
		l4l_sets = ("On", "1", "1", "0", "60", "100", "500", "10", "On", "0")
	L4Lmspfs = L4Lelement()
	l4l = True
	schicht_send = None
	if configparser.has_option("settings", "schicht_send"):
		schicht_send = True
	if configparser.has_option("settings", "schicht_send_url"):
		schicht_send_url = configparser.get("settings", "schicht_send_url")
except Exception:
	l4l = None
heute = date.today()

class mspFS_paint:
	def __init__(self, liste=None):
		if l4l and liste:
			try:
				remove("/tmp/mspFS.png")
				remove("/tmp/mspFS1.png")
				remove("/tmp/mspFS2.png")
			except Exception:
				pass
			if fileExists(join(PLUGINPATH, "schichtpicons/err.png")):
				schicht1 = schicht().parseSchicht(liste, (None, None))
				if schicht1:
					picon_path = join(PLUGINPATH, "schichtpicons")
					#for i in xrange(1,3):
					for i in range(3):
						txt = str(schicht1[i - 1][1])
						path1 = picon_path
						if not len(txt.strip()):
							txt = "notext"
						file1 = txt + ".png"
						schichtpicons = join(CONFIGPATH, "Schichtpicons")
						if fileExists(join(schichtpicons, file1)):
							path1 = schichtpicons
						elif not fileExists(join(picon_path, file1)):
							path1 = picon_path
							file1 = 'err.png'
						pt = join(path1, file1)
						dt = "/tmp/mspFS%s.png" % i
						system("cp %s %s" % (pt, dt))
					self.paint_l4l(schicht1)

	def paint_l4l(self, mySchicht):
		size = int(l4l_sets[4])  # 60
		breit = int(l4l_sets[5])  # 100  #from config
		hoch = int(l4l_sets[6])  # 600   #from config
		abstand = int(l4l_sets[7])  # 10  #from config
		top = str(l4l_sets[3])  # +"%"#10
		if len(l4l_sets) == 9:
			left = "0%"
		else:
			left = str(l4l_sets[9]) + "%"
		if breit > hoch:
			quer = 1
			anz = int(breit / (size + abstand))
			if anz > len(mySchicht) - 1:
				anz = len(mySchicht)
				size = int(breit - (len(mySchicht) - 1) * abstand / (len(mySchicht) - 1))
			hoch = size + abstand * 2
		else:
			quer = 0
			anz = int(hoch / (size + abstand))
			if anz > len(mySchicht) - 1:
				anz = len(mySchicht)
				size = int(hoch - (len(mySchicht) - 1) * abstand / (len(mySchicht) - 1))
			breit = size + abstand * 2
		im = Image.new('RGBA', (breit, hoch), (0, 0, 0, 0))
		draw = ImageDraw.Draw(im)
		px = abstand
		py = abstand
		for i2 in range(anz):
			col = mySchicht[i2][2].lstrip('#')
			lv = len(col)
			txt = mySchicht[i2][1]
			if len(txt) > 3:
				txt = txt[:3]
			textsize = int(size * 0.8)
			fontfile = resolveFilename(SCOPE_FONTS, "nmsbd.ttf")
			font = ImageFont.truetype(fontfile, textsize, encoding='unic')
			w, h = draw.textsize(txt, font=font)
			while w > int(size * 0.95):  # max 90% solange verkleinern
				textsize -= 1
				font = ImageFont.truetype(fontfile, textsize, encoding='unic')
				w, h = draw.textsize(txt, font=font)
			colx = tuple(int(col[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))  # col from hex
			col2 = (colx[0], colx[1], colx[2], 0)
			draw.ellipse((px, py, px + size, py + size), outline="black", fill=col2)
			draw.text((px + 1 + int((size - w) / 2), py + 1 + int((size - h) / 2)), txt, font=font, fill="black")
			if quer:
				px = px + size + abstand
			else:
				py = py + size + abstand
		im.save("/tmp/mspFS.png", "PNG")
		if l4l:
			L4Lmspfs.add("mspFS.png", {"Typ": "pic", "Align": left, "Pos": top, "File": "/tmp/mspFS.png", "Size": str(breit), "Screen": l4l_sets[2], "Lcd": l4l_sets[1], "Mode": l4l_sets[8].replace(",", ""), "Transp": "True"})
			L4Lmspfs.setRefresh()
