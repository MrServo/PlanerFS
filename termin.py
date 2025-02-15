# PYTHON IMPORTS
from configparser import ConfigParser
from datetime import datetime, timedelta, date
from os.path import exists, isfile
from re import compile
from time import localtime, mktime

# PLUGIN IMPORTS
from . import CONFIGFILE, _  # for localized messages
from .routines import Feiertage, Rules, Next_Termin

schicht_start = 0
conf = {"kalender_art": "Gregorian", "vorschaum": 1, "altloesch": 365, "erinn_ext": "1", "m_sound": "No", "m_vol_min": 10, "m_vol_max": 100, "m_sound_art": "file", "m_dauer": 0, "m_sound_volume": (10, 100), "categories": "", "schicht_art": "0,0,0", "schicht_col": {}}
categories1 = (_('Birthday'), _('Anniversary'), _('Wedding day'), 'Birthday', 'Anniversary', 'Wedding day')
if exists(CONFIGFILE):
	configparser = ConfigParser()
	configparser.read(CONFIGFILE)
	if configparser.has_section("settings"):
		l1 = configparser.items("settings")
		for k, v in l1:
			if k in conf and v.strip() != "":
				if v.strip() in ("False", "false", "None", "none"):
					conf[k] = False
				elif v.strip() in ("True", "true"):
					conf[k] = True
				elif k == "categories":
					categories1 = v
					categories1 = list(categories1.split(","))
				else:
					conf[k] = int(v.strip()) if v.isdigit() else v.strip()
schicht = str(conf["schicht_art"]).split(",")
if len(schicht) < 3:
	schicht.extend(("0", "0", "0")[len(schicht):])
schicht_start = int(schicht[1])
m_sound_volume = (int(conf["m_vol_min"]), int(conf["m_vol_max"]))


class TerminList():
	def __init__(self):
		lt = localtime()
		self.monat = lt[1]
		self.jahr = lt[0]
		self.today = date.today()
		self.terminlist = []
		self.timer_liste = []
		self.events = []
		self.fehler_list = []
		self.schichtlist = []

	def getlists(self, term_datei=None, modul=0):
		dataLines = []
		lt = localtime()
		if not isinstance(conf["schicht_col"], dict):
			conf["schicht_col"] = eval(conf["schicht_col"])
		self.schichtnamen = []
		if isinstance(conf["schicht_col"], dict):
			for key in conf["schicht_col"].keys():
				self.schichtnamen.append(key)
		if term_datei == "kalender":
			monat = self.monat + conf["vorschaum"]
			jahr = self.jahr
			if monat > 12:
				monat = self.monat - 12 + conf["vorschaum"]
				jahr = self.jahr + 1
			end = date(jahr, monat, 1) - timedelta(1)
			if conf["kalender_art"] == "Gregorian":
				self.bewegl_feiertage = Feiertage().ostern_greg(self.jahr)
				if int(end.year) > self.jahr:
					self.bewegl_feiertage.extend(Feiertage().ostern_greg(self.jahr + 1))
			elif conf["kalender_art"] == "Julian":
				self.bewegl_feiertage = Feiertage().ostern_jul(self.jahr)
				if int(end.year) > self.jahr:
					self.bewegl_feiertage.extend(Feiertage().ostern_jul(self.jahr + 1))
			else:
				self.bewegl_feiertage = []
			for x2 in self.bewegl_feiertage:
				if x2[3].date() >= self.today:
					day_heute = 0
					if self.today == x2[3]:
						day_heute = 1
					next_date = (x2[3].year, x2[3].month, x2[3].day)
					y = (next_date, x2[0], x2[1], x2[2], day_heute, x2[6], (0, 0), 0, 0, x2[3])
					self.terminlist.append(y)
			self.listen7 = (self.terminlist, self.timer_liste)
		elif term_datei:
			self.termindatei = term_datei
			self.alerts = []
			self.listen = []
			eigen = 0
			if "PlanerFS.ics" in str(term_datei) or "PlanerFS2.ics" in str(term_datei):
				eigen = 1
			self.altdat = self.today - timedelta(int(conf["altloesch"]))
			altjahr = self.altdat.year
			altmonat = self.altdat.month
			self.altdatum = date(altjahr, altmonat, 1)
			if self.monat == 12:
				sdt1 = date(self.jahr + 1, 1, 1) - timedelta(1)
			else:
				sdt1 = date(self.jahr, self.monat + 1, 1) - timedelta(1)
			self.monatstage = int(sdt1.day)
			if isfile(self.termindatei):
				if modul:
					parse1 = Rules().parseEvent_b(self.termindatei, self.schichtnamen)
					if parse1:
						for x in parse1:
							if x not in self.events and x[5] or (x[3].date() >= self.today - timedelta(days=1)):
								self.events.append(x)
				if len(self.events) == 0:
					tempFile = open(self.termindatei, 'r')
					dataLines.extend(tempFile.readlines())
					tempFile.close()
					mask = {}
					mask['BEGIN'] = compile(r"^BEGIN:VEVENT")
					mask['END'] = compile(r"^END:VEVENT")
					inEvent = False
					index = 0
					fname = self.termindatei
					eventLines = []
					for line in dataLines:
						line = line.replace("\r", "")
						if mask['BEGIN'].match(line):
							eventLines = []
							inEvent = True
						elif mask['END'].match(line) and inEvent:
							parse1 = Rules().parseEvent(eventLines, index, fname, self.schichtnamen)
							if parse1[5] or (parse1[3].date() >= self.today):
								self.events.append(parse1)
							inEvent = False
							index += 1
						elif inEvent:
							eventLines.append(line)
				nowyear = self.today.year
				if self.altdatum <= date(self.jahr, self.monat, 1):
					for x in self.events:
						sr = 1
						no_stscr = None
						if len(x) > 16:
							no_stscr = x[16]
							if x[14]:
								sr = 0
								self.schichtlist.append((x[0], x[2], x[3], x[5], x[6], None, x[17]))
								if schicht_start:
									sr = 1
						if sr:
							zeit1 = (0, 0, "")
							y1 = None
							y2 = None
							ld = None
#							try:
							if 1 == 1:
								next_datet = None
								if x[1] is None or x[1].lower() != "timer":
									zeit1 = (x[2].hour, x[2].minute, "")
									if x[5] is None and x[3].date() > x[2].date():
										ld = x[3]
										if x[2].date() == self.today:
											ld = None
										elif x[3].date() == self.today:
											ld = None
											zeit1 = (x[3].hour, x[3].minute, "- ")
									next_datet = Next_Termin().next_termin(x[5], x[2], x[3], (lt[0], lt[1]), conf["vorschaum"] + 1, "terminlist", x[17])
									if next_datet and len(next_datet):
										for z in next_datet:
											day_heute = 0
											nd = z.date()
											if self.today <= nd:
												next_date = (z.year, z.month, z.day)
												date1 = datetime(z.year, z.month, z.day, zeit1[0], zeit1[1])
												if self.today == nd:
													day_heute = 1
												jubi = 0
												for tmp in categories1:
													cat = tmp.strip().lower()
													if (x[1] and cat in x[1].lower()) or (x[6] and cat in x[6].lower()):
														jubi = int(nowyear) - int(x[3].year)
														if nowyear < z.year:
															jubi += 1
												y1 = (next_date, x[0], x[1], x[2], day_heute, x[6], zeit1, x[11], jubi, date1, x[4], no_stscr, ld)
												self.terminlist.append(y1)
												if (x[15] or "DISPLAY" in str(x[4])) and (eigen or conf["erinn_ext"] == "1"):
													sound = conf["m_sound"]
													if x[15]:
														dr = x[15][0]
														date1 = datetime(z.year, z.month, z.day, dr.hour, dr.minute)
														if x[15][2] and x[15][3]:
															if x[15][2] == "m":
																date1 = date1 - timedelta(minutes=x[15][3])
															elif x[15][2] == "h":
																date1 = date1 - timedelta(hours=x[15][3])
															elif x[15][2] == "d":
																date1 = date1 - timedelta(days=x[15][3])
													t2b = mktime(date1.timetuple())
													now = datetime.now()
													u = mktime(now.timetuple())
													if t2b - u > 0 and t2b - u < 86401:
														zeit1 = (date1.hour, date1.minute)
														y2 = ((date1.year, date1.month, date1.day), x[0], x[1], date1, conf["m_sound"], x[10], m_sound_volume, x[6], zeit1, x[11], t2b, conf["m_dauer"], jubi)
														self.timer_liste.append(y2)
								else:
									if not x[10] or x[10] != "no_activ":
										next_datet2 = None
										now = datetime.now()
										next_datet2 = Next_Termin().next_termin(x[5], x[2], x[2], (lt[0], lt[1]), conf["vorschaum"] + 1, "terminlist2", x[17])
										zeit1 = (x[2].hour, x[2].minute)
										sound = conf["m_sound"]
										if next_datet2 and len(next_datet2):
											for z in next_datet2:
												next_date = (z.year, z.month, z.day)
												date1 = datetime(z.year, z.month, z.day, x[2].hour, x[2].minute)
												if (x[15] or "DISPLAY" in str(x[4])) and (eigen or conf["erinn_ext"] == "1"):
													sound = conf["m_sound"]
													if x[15]:
														dr = x[15][0]
														date1 = datetime(z.year, z.month, z.day, dr.hour, dr.minute)
														if x[15][2] and x[15][3]:
															if x[15][2] == "m":
																date1 = date1 - timedelta(minutes=x[15][3])
															elif x[15][2] == "h":
																date1 = date1 - timedelta(hours=x[15][3])
															elif x[15][2] == "d":
																date1 = date1 - timedelta(days=x[15][3])
												t2b = mktime(date1.timetuple())
												u = mktime(now.timetuple())
												vol = (conf["m_vol_min"], conf["m_vol_max"])  # m_sound_volume
												url = None
												if t2b - u > 0 and t2b - u < 86401:
													zeit1 = (date1.hour, date1.minute)
													if x[4] == "radio" or x[4] == "AUDIO":
														vol = x[6].split(",")
														vol = (int(vol[0]), int(vol[1]))
														if x[4] == "radio":
															urla = x[6].split(",")
															url = urla[2]
													y2 = ((date1.year, date1.month, date1.day), x[0], x[1], date1, x[4], x[10], vol, url, zeit1, x[11], t2b, conf["m_dauer"], 0)
													self.timer_liste.append(y2)
#							except Exception as e:
#								f2 = open("/tmp/PlanerFS-Errors.txt", "a")
#								f2.write("schwerer Fehler:\n")
#								f2.write(">> " + str(self.termindatei) + "\n")
#								f2.write(str(x[0]) + "\n")
#								f2.write(str(e) + "\n")
#								f2.close()
#								continue
		return (self.terminlist, self.timer_liste, self.fehler_list, self.schichtlist)
