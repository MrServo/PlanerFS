# PYTHON IMPORTS
from configparser import ConfigParser
from datetime import datetime, timedelta
from os.path import exists
from re import match
from time import localtime, mktime, strftime, strptime

# ENIGMA IMPORTS
from Components.ActionMap import ActionMap
from Components.config import getConfigListEntry, ConfigInteger, ConfigText, ConfigClock, ConfigSelection, ConfigNumber, ConfigSequence, NoSave
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.SystemInfo import SystemInfo
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.VirtualKeyBoard import VirtualKeyBoard

# PLUGIN IMPORTS
from . import CONFIGFILE, _  # for localized messages


class PFS_edit_Termin(ConfigListScreen, Screen):

	def __init__(self, session, altdat=None, eigen_num=0, newdat=None):
		self.hauptliste = eigen_num
		self.fname = "PlanerFS.ics"
		if eigen_num == 3:
			self.fname = "PlanerFS2.ics"
		categor = (_("None"))
		if exists(CONFIGFILE):
			configparser = ConfigParser()
			configparser.read(CONFIGFILE)
			if configparser.has_option("settings", "categories"):
				categor = configparser.get("settings", "categories")
		self.categor = categor.split(",")
		if "timer" not in self.categor:
			self.categor.append("timer")
		self.altdat = altdat
		self.ind_nr = None
		self.timer = 0
		if self.altdat:
			if self.altdat[2] == "TIMER":
				self.timer = 1
			elif self.altdat[5] == "DISPLAY":
				self.timer = 0
				self.terminaction = "Yes"
			else:
				self.timer = 0
				self.terminaction = "No"
		self.terminart_liste = [(0, _("Simple event")), (2, _("Event by Rules")), (1, _("Timer")), (3, _("Timer by Rules"))]
		self.termin_freq_liste = [("YEARLY", _("YEARLY")), ("MONTHLY", _("MONTHLY")), ("monthly backward", _("monthly backward")), ("WEEKLY", _("WEEKLY")), ("DAILY", _("DAILY"))]
		self.termin_wiederholung_liste = [(0, _("never")), (1, _("by date")), (2, _("after count"))]
		self.now = tuple(x for x in localtime())
		self.oldtime = [self.now[2], self.now[1], self.now[0]]
		if newdat:
			self.oldtime = [newdat[0], newdat[1], newdat[2]]
		lim_1 = [(1, 31), (1, 12), (1900, 2999)]
		self.termin_end = mktime(self.now)
		self.terminart = NoSave(ConfigSelection(choices=self.terminart_liste, default=self.timer))
		self.uebernahme = True
		self.termin_id = None
		self.termin_wiederholung = NoSave(ConfigSelection(choices=self.termin_wiederholung_liste, default=0))
		self.termintext = NoSave(ConfigText(default=_("Event-text"), fixed_size=False))
		self.location = NoSave(ConfigText(default="", fixed_size=False))
		self.terminDESCRIPTION = NoSave(ConfigText(default=_("Description"), fixed_size=False))
		self.termin_start_date = NoSave(ConfigSequence(seperator=".", limits=lim_1, default=self.oldtime))
		self.end_date = NoSave(ConfigSequence(seperator=".", limits=lim_1, default=self.oldtime))
		self.termin_cat = NoSave(ConfigText(default=(""), fixed_size=False))
		self.timer_cat = NoSave(ConfigSelection(choices=[("unique", _("unique")), ("repeat", _("repeat"))], default="repeat"))
		self.ganztag = NoSave(ConfigSelection(choices=[("Yes", _("Yes")), ("No", _("No"))], default="Yes"))
		self.rule_set = NoSave(ConfigSelection(choices=[(1, _("Yes")), (0, _("No"))], default=0))
		self.termin_freq = NoSave(ConfigSelection(choices=self.termin_freq_liste, default="YEARLY"))
		self.termin_interval = NoSave(ConfigNumber(default=1))
		self.termin_count = NoSave(ConfigInteger(default=0, limits=(0, 999)))
		self.termin_byMonth = NoSave(ConfigInteger(default=0, limits=(0, 12)))
		self.termin_byMonthday = NoSave(ConfigInteger(default=0, limits=(0, 31)))
		self.termin_untilDate = NoSave(ConfigSequence(seperator=".", limits=lim_1, default=self.oldtime))
		self.termin_byDay = NoSave(ConfigNumber(default=0))
		self.termin_byYearday = NoSave(ConfigInteger(default=0, limits=(0, 365)))
		self.terminbyWeekno = NoSave(ConfigInteger(default=0, limits=(0, 52)))
		self.terminbyWeekst = None  # ToDo NoSave(ConfigInteger(default=?, limits=(?, ??)))
		self.terminaction = NoSave(ConfigSelection(choices=[("Yes", _("Yes")), ("No", _("No"))], default="Yes"))
		if SystemInfo["DeepstandbySupport"]:
			self.terminaktiv = NoSave(ConfigSelection(choices=[("on", _("when on")), ("sb", _("on and standby(Idle)")), ("dsb", _("on, standby(Idle) and deepstandby")), ("no_activ", _("No"))], default="on"))
		else:
			self.terminaktiv = NoSave(ConfigSelection(choices=[("on", _("when on")), ("sb", _("on and standby(Idle)")), ("no_activ", _("No"))], default="on"))
		soundliste = [("File", _("File")), ("Off", _("Off")), ("radio", _("radio"))]
		self.startvol = NoSave(ConfigInteger(default=10, limits=(0, 95)))
		self.maxvol = NoSave(ConfigInteger(default=100, limits=(5, 100)))
		self.terminsound = NoSave(ConfigSelection(choices=soundliste, default="Off"))
		t1 = mktime((self.now[0], self.now[1], self.now[2], self.now[3], self.now[4], 0, 0, 0, -1))
		t2 = t1  # mktime((self.now[0], self.now[1], self.now[2], self.now[4], self.now[4], 0, 0, 0, -1))
		self.terminTime = NoSave(ConfigClock(default=t1))
		self.terminTimeEnd = NoSave(ConfigClock(default=t2))
		self.vaDisplay = NoSave(ConfigSelection(choices=[(1, _("Yes")), (0, _("No"))], default=0))
		self.vaRel = NoSave(ConfigSelection(choices=[(1, _("Yes")), (0, _("No"))], default=0))
		self.vaTxt = NoSave(ConfigText(default="", fixed_size=False))
		self.vaTriggerT = NoSave(ConfigSelection(choices=[("D", _("Days")), ("H", _("Hours")), ("M", _("Minutes"))], default="M"))
		self.vaRTrigger = NoSave(ConfigInteger(default=0, limits=(0, 365)))
		self.vaTTrigger1 = NoSave(ConfigSequence(seperator=".", limits=lim_1, default=self.oldtime))
		self.vaTTrigger2 = NoSave(ConfigClock(default=t1))
		Screen.__init__(self, session)
		self.skinName = "Setup"
		self.nt = None
		self["key_yellow"] = StaticText("")
		self.setTitle(_("Add new event or timer"))
		if self.uebernahme and self.altdat:
			self["key_yellow"].setText(_("delete"))
			self.nt = 1
			self.altdat_uebernehmen()
		self.refresh()
		ConfigListScreen.__init__(self, self.list, on_change=self.reloadList)
		self["key_green"] = StaticText(_("Save"))
		self["key_red"] = StaticText(_("Cancel"))
		self["key_blue"] = StaticText("")
		self["description"] = Label(_("select from the list: Event by Date, Event by Rules, Timer"))
		self["footnote"] = Label()
		self["footnote"].hide()
		self["setupActions"] = ActionMap(["SetupActions", "DirectionActions", "ColorActions"],
		{
				"green": self.save,
				"red": self.cancel,
				"yellow": self.loesch,
				"save": self.save,
				"cancel": self.cancel,
				"down": self.downPressed,
				"up": self.upPressed,
				"ok": self.ok,
		}, -2)

	def altdat_uebernehmen(self):
		if self.altdat is None:
			return
		s_d = self.altdat
		if str(s_d[12]).endswith("ics"):
			self.fname = str(s_d[12])
		if s_d[1]:
			self.termintext.value = s_d[1].replace('\\n', '<tr>')
		if s_d[23]:
			self.terminaction = "No"
		if s_d[17] == "ganztag":
			self.ganztag.value = "Yes"
		else:
			self.ganztag.value = "No"
			self.terminTime.setValue([s_d[3].hour, s_d[3].minute])
			self.terminTimeEnd.setValue([s_d[4].hour, s_d[4].minute])
		if s_d[19]:
			self.location.value = s_d[19]
		if s_d[8]:
			self.terminDESCRIPTION.value = s_d[8]
		if s_d[10] >= 0:
			self.ind_nr = s_d[10]
		if s_d[3]:
			self.termin_start_date.value = [s_d[3].day, s_d[3].month, s_d[3].year]
		if s_d[4]:
			self.end_date.value = [self.altdat[4].day, self.altdat[4].month, s_d[4].year]
		if s_d[6]:
			self.termin_freq.value = s_d[6][0]
			self.rule_set.value = 1
			self.terminart.value = 2
			if self.timer == 1:
				if s_d[6][3] or s_d[6][7] or s_d[6][2]:
					self.terminart.value = 3
				else:
					self.terminart.value = 1
			if s_d[6][1]:
				self.termin_interval.value = int(s_d[6][1])
			if s_d[6][2]:
				self.termin_byMonth.value = int(s_d[6][2][0])
			if s_d[6][3]:
				if int(s_d[6][3][0]) < 0:
					self.termin_byMonthday.value = int(s_d[6][3][0])
					self.termin_freq.value = "monthly backward"
					self.termin_byMonthday.value = self.termin_byMonthday.value * -1
				else:
					self.termin_byMonthday.value = int(s_d[6][3][0])
			if s_d[6][4]:
				self.termin_wiederholung.value = 1
				u_date = s_d[6][4]
				self.termin_untilDate.value = [u_date.day, u_date.month, u_date.year]
			if s_d[6][7]:
				wd_list = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
				bd = ""
				for wd in s_d[6][7]:
					bd = bd + str(wd_list.index(wd) + 1)
				self.termin_byDay.value = int(bd)
			if s_d[6][8]:
				self.termin_byYearday.value = s_d[6][8]
			if s_d[6][9]:
				self.terminbyWeekno.value = s_d[6][9]
			if s_d[6][10]:
				self.terminbyWeekst = s_d[6][10]
			if s_d[6][11]:
				self.termin_count.value = int(s_d[6][11])
				self.termin_wiederholung.value = 2
		else:
			self.termin_wiederholung.value = 0
			if self.timer == 1:
				self.terminart.value = 1
			self.terminart.value = 0
			if self.timer == 1:
				self.terminart.value = 1
		self.hauptliste = s_d[11]
		if str(s_d[5]) == "DISPLAY":
			self.vaDisplay.value = 1
		if s_d[21] and s_d[22]:
			self.vaTxt.value = s_d[22][1]
			if s_d[21].startswith("-"):
				self.vaRel.value = 0
				d = match(r'.*?(\d+)', s_d[21])
				self.vaRTrigger.value = int(d.group(1)) if d else 0
				self.vaTTrigger1.value = self.termin_start_date.value
				self.vaTTrigger2.value = self.terminTime.value
				if s_d[21][2] == "T":
					if s_d[21][2].endswith("M"):
						self.vaTriggerT.value = "M"
					elif s_d[21].endswith("H"):
						self.vaTriggerT.value = "H"
				elif s_d[21].endswith("D"):
					self.vaTriggerT.value = "D"
			else:
				self.vaRel.value = 1
				dr = s_d[22][0]
				self.vaTTrigger1.value = [dr.day, dr.month, dr.year]
				self.vaTTrigger2.value = [dr.hour, dr.minute]
		if self.timer == 0:
			if s_d[5] == "no_startscreen":
				self.terminaction = "No"
			if s_d[2] and s_d[2] != "":
				self.termin_cat.value = s_d[2].strip()
		self.setTitle(_("Edit Event"))
		self.uebernahme = False

	def refresh(self):
		liste = []
		liste.extend((getConfigListEntry(_("Text"), self.termintext),))
		if self.terminsound.value == "File" or self.terminsound.value == "radio" and (self.terminart.value == 1 or self.terminart.value == 3):
			if self.terminsound.value == "radio" and self.termintext.value == _("Event-text"):
				self.termintext.value = _("radio alarm Clock")
			liste.extend((getConfigListEntry(_("start volume"), self.startvol), getConfigListEntry(_("max volume"), self.maxvol),))
			if self.terminsound.value == "radio":
				liste.extend((getConfigListEntry(_("Stream-URL"), self.terminDESCRIPTION),))
		else:
			if self.termintext.value == (_("radio alarm Clock")):
				self.termintext.value = (_("Event-text"))
			if self.terminDESCRIPTION.value == "http://":
				self.terminDESCRIPTION.value = (_("Description-text"))
		liste.extend((getConfigListEntry(_("Description"), self.terminDESCRIPTION),))
		liste.extend((getConfigListEntry(_("Category"), self.termin_cat), getConfigListEntry(_("Location"), self.location),))
		liste.extend((getConfigListEntry(_("Start-Date"), self.termin_start_date),))
		liste.extend((getConfigListEntry(_("daylong"), self.ganztag),))
		if self.ganztag.value != "Yes":
			liste.extend((getConfigListEntry(" " * 5 + _("Start-Time"), self.terminTime),))
			liste.extend((getConfigListEntry(" " * 5 + _("End-Time"), self.terminTimeEnd),))
		if not self.rule_set.value:
			liste.extend((getConfigListEntry(_("End-Date"), self.end_date),))
		liste.extend((getConfigListEntry(_("Use rules"), self.rule_set),))
		if self.rule_set.value:  # self.terminart.value==2 or self.terminart.value==3:
			liste.extend((
					getConfigListEntry(" " * 5 + _("Frequency"), self.termin_freq),
					getConfigListEntry(" " * 5 + _("Interval"), self.termin_interval),
					getConfigListEntry(" " * 5 + _("Month"), self.termin_byMonth),
					getConfigListEntry(" " * 5 + _("Monthday"), self.termin_byMonthday),
					getConfigListEntry(" " * 5 + _("WeekDays"), self.termin_byDay),
					))
			liste.extend((getConfigListEntry(" " * 5 + _("Event end"), self.termin_wiederholung),))
			if self.termin_wiederholung.value == 1:
				liste.extend((getConfigListEntry(" " * 10 + _("End-Date"), self.termin_untilDate),))
			else:
				if self.termin_wiederholung.value == 2:
					liste.extend((getConfigListEntry(" " * 10 + _("Count"), self.termin_count),))
				self.end_date.value = self.termin_start_date.value
		if self.termin_cat.value != "timer":
			liste.extend((getConfigListEntry(_("Display on Start"), self.terminaction),))
		else:
			self.terminaction = "No"
		liste.extend((getConfigListEntry(_("Alert on Display"), self.vaDisplay),))
		if self.vaDisplay.value:
			if self.vaTxt.value == "":
				self.vaTxt.value = self.termintext.value
			liste.extend((getConfigListEntry(" " * 5 + _("Alert-description"), self.vaTxt),))
			liste.extend((getConfigListEntry(" " * 5 + _("Alert by date-time"), self.vaRel),))
			if self.vaRel.value and self.vaTTrigger1:
				liste.extend((getConfigListEntry(" " * 5 + _("Alert date"), self.vaTTrigger1),))
				liste.extend((getConfigListEntry(" " * 5 + _("Alert time"), self.vaTTrigger2),))
			else:
				liste.extend((getConfigListEntry(" " * 5 + _("Alert reminder beforehand"), self.vaRTrigger),))
				liste.extend((getConfigListEntry(" " * 10 + _("Unit of time"), self.vaTriggerT),))
		self.list = liste

	def reloadList(self):
		self.refresh()
		self["config"].setList(self.list)

	def downPressed(self):
		l = len(self.list)
		idx = self["config"].getCurrentIndex()
		idx = idx + 1
		if idx < l:
			self["config"].setCurrentIndex(idx)
			self.help()

	def upPressed(self):
		idx = self["config"].getCurrentIndex()
		idx = idx - 1
		self["config"].setCurrentIndex(idx)
		self.help()

	def help(self):
		cur = self["config"].getCurrent()
		cur = cur and cur[1]
		if cur == self.terminart:    #("Event by Date")),(2, _("Event by Rules")),(1, _("Timer")
			helptext = _("select from the list: Event by Date, Event by Rules, Timer") + ", " + _("Press 'OK' for list")
		elif cur == self.termin_wiederholung:
			helptext = _("select from the list: repeat, repeat until, none") + ", " + _("Press 'OK' for list")
		elif cur == self.termin_cat:
			helptext = _("Press 'OK' for list")
		elif cur == self.termin_freq:
			helptext = _("monthly backward = for Day of Month backward (last Day...)") + ", " + _("Press 'OK' for list")
		elif cur == self.termin_byDay:
			helptext = _("sample: you will MO,TH,SA,SU then type: 1467")
		elif cur == self.terminTime:
			helptext = _("Next timer earliest in 5 minutes or 5 minutes after standby")
		elif cur == self.termintext:
			helptext = _("text for List, press ok for edit")
		elif cur == self.terminDESCRIPTION:
			if self.terminsound.value == "radio":
				helptext = _("set mp3-URL for radio-Stream: http:\\....\n (mp3,ogg, aac - not pls,m3u,wmp,flash....)")
			else:
				helptext = _("Long-Text, press ok for edit")
		else:
			helptext = ""
		self["description"].setText(helptext)

	def cat_wahl(self, kategorie):
		if kategorie is not None:
			self.termin_cat.value = kategorie[1].strip()
			self.refresh()

	def terminart_wahl(self, termin_art):
		if termin_art is not None:
			self.terminart.value = termin_art[1]
			self.refresh()

	def termin_freq_wahl(self, termin_freq):
		if termin_freq is not None:
			self.termin_freq.value = termin_freq[1]
			self.refresh()

	def termin_wiederholung_wahl(self, termin_wiederholung):
		if termin_wiederholung is not None:
			self.termin_wiederholung.value = termin_wiederholung[1]
			self.refresh()

	def ok(self):
		self.cur = self["config"].getCurrent()
		self.cur = self.cur and self.cur[1]
		titletext = _("Set/edit Text:")
		if self.cur == self.termintext:
			self.session.openWithCallback(self.description_back, VirtualKeyBoard, title=titletext, text=self.termintext.value)
		elif self.cur == self.terminDESCRIPTION:
			self.session.openWithCallback(self.description_back, VirtualKeyBoard, title=titletext, text=self.terminDESCRIPTION.value)
		elif self.cur == self.vaTxt:
			self.session.openWithCallback(self.description_back, VirtualKeyBoard, title=titletext, text=self.vaTxt.value)
		elif self.cur == self.location:
			self.session.openWithCallback(self.description_back, VirtualKeyBoard, title=titletext, text=self.location.value)
#		elif self.cur == self.terminart:
#			liste = []
#			for x in self.terminart_liste:
#				r = (x[1], x[1])
#				liste.append(r)
#			self.session.openWithCallback(self.terminart_wahl, ChoiceBox, title=_("Select terminart"), list=liste)
#		elif self.cur == self.termin_freq:
#			liste = []
#			for x in self.termin_freq_liste:
#				r = (x[1], x[0])
#				liste.append(r)
#			self.session.openWithCallback(self.termin_freq_wahl, ChoiceBox, title=_("Select frequenz"), list=liste)
#		elif self.cur == self.termin_wiederholung:
#			liste = []
#			for x in self.termin_wiederholung_liste:
#				r = (x[1], x[0])
#				liste.append(r)
#			self.session.openWithCallback(self.termin_wiederholung_wahl, ChoiceBox, title=_("Select end art"), list=liste)
		elif self.cur == self.termin_cat:
			liste = [(_("no category"), ""), (_("Birthday"), _("Birthday")), (_("Holiday"), _("Holiday")), (_("Anniversary"), _("Anniversary")), (_("Wedding day"), _("Wedding day"))]
			for x in self.categor:
				if x != "None" and x != _("None") and x != "":
					r = (x, x)
					if r not in liste:
						liste.append(r)
			self.session.openWithCallback(self.cat_wahl, ChoiceBox, title=_("Select categorie"), list=liste)
		else:
			ConfigListScreen.keySelect(self)

	def description_back(self, text):
		if text:
			self.cur.value = text

	def save(self):
		freq = None
		interval = None
		byMonth = None
		byMonthday = None
		byDay = None
		untilDate = None
		byMinute = None
		byHoure = None
		byYearday = None
		byWeekno = None
		byWeekst = None
		cat = None
		action = None
		comment = None
		count = None
		rule = None
		trigger = None
		melde_text = self.termintext.value.replace('<tr>', '\\n')
		desc = self.terminDESCRIPTION.value.replace('<tr>', '\\n')
		if self.termin_cat.value and self.termin_cat.value != "":
			cat = self.termin_cat.value.strip()
		start_date = []
		start_date = self.termin_start_date.value
		end_date = self.end_date.value
		setTimeA = self.terminTime.value
		setTimeE = self.terminTimeEnd.value
		if self.ganztag.value == "Yes":
			setTimeA = (0, 0)
			setTimeE = (0, 0)
		begin = datetime(start_date[2], start_date[1], start_date[0], setTimeA[0], setTimeA[1])
		end = datetime(end_date[2], end_date[1], end_date[0], setTimeE[0], setTimeE[1])
		if self.ganztag.value == "Yes":
			end = end + timedelta(1)
		if self.terminaction == "No":
			action = "no_startscreen"
		if self.rule_set.value:
			if self.termin_wiederholung.value == 1:
				until = self.termin_untilDate.value
				untilDate = datetime(until[2], until[1], until[0], setTimeE[0], setTimeE[1])
			elif self.termin_wiederholung.value == 2:
				count = self.termin_count.value
			if self.termin_freq.value:
				freq = self.termin_freq.value
			if self.termin_interval.value:
				interval = str(self.termin_interval.value)
			if self.termin_byMonth.value and self.termin_byMonth.value != 0:
				byMonth = []
				byMonth.append(str(self.termin_byMonth.value))
			if self.termin_byMonthday.value and self.termin_byMonthday.value != 0:
				byMonthday = []
				if self.termin_freq.value == "monthly backward":
					byMonthday.append(str(int(self.termin_byMonthday.value) * -1))
					freq = "MONTHLY"
				else:
					byMonthday.append(str(self.termin_byMonthday.value))
			byMinute = None
			byHoure = None
			if self.termin_byDay.value and self.termin_byDay.value > 0:
				byDay = []
				wd_list = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
				for b in str(self.termin_byDay.value):
					if int(b) > 0:
						byDay.append(wd_list[int(b) - 1])
			if self.termin_byYearday.value:
				byYearday = self.termin_byYearday.value
			if self.terminbyWeekno.value:
				byWeekno = self.terminbyWeekno.value
			if self.terminbyWeekst:
				byWeekst = self.terminbyWeekst.value
			rule = (freq, interval, byMonth, byMonthday, untilDate, byMinute, byHoure, byDay, byYearday, byWeekno, byWeekst, count)
		if self.vaDisplay.value:
			if self.vaRel.value and self.vaTTrigger1:
				tr_date = self.vaTTrigger1.value
				tr_time = self.vaTTrigger2.value
				at = "%04i%02i%02iT%02i%02i00" % (tr_date[2], tr_date[1], tr_date[0], tr_time[0], tr_time[1])
				trigger = "TRIGGER;VALUE=DATE-TIME:" + at
			else:
				if self.vaRTrigger.value == 0:
					at = strftime("%Y%m%dT%H%M%S", strptime(str(begin), "%Y-%m-%d %H:%M:%S"))
					trigger = "TRIGGER;VALUE=DATE-TIME:" + at
				else:
					vor = "PT"
					if self.vaTriggerT.value == "D":
						vor = "P"
					trigger = "TRIGGER:-" + vor + str(self.vaRTrigger.value) + self.vaTriggerT.value
			if len(self.vaTxt.value):
				trigger += "\n%s:%s" % (_("Description-text"), self.vaTxt.value)
		detail_liste = (melde_text, cat, begin, end, action, rule, desc, self.ind_nr, self.terminart.value, self.fname, comment, None, self.ganztag.value, self.location.value, trigger)
		self.close(detail_liste)

	def loesch(self):
		if self.nt:
			self.close(None, "aktloesch")

	def cancel(self):
		self.close(None)
