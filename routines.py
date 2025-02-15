# PYTHON IMPORTS
from configparser import ConfigParser
from datetime import datetime, timedelta, date, time
from icalendar import Calendar
from re import compile, match
from os.path import getsize
from time import timezone, localtime, altzone

# PLUGIN IMPORTS
from . import CONFIGPATH, CONFIGFILE, _  # for localized messages


def getTimeDiffUTC():
	offset = timezone if (localtime().tm_isdst == 0) else altzone
	return int(offset / -3600)


def Code_utf8(wert=""):
	wert = wert.replace('\xc2\x86', '').replace('\xc2\x87', '') or ""
	return wert


class Farben():
	def farb_re(self, farb):
		if farb:
			new_farb = int(str(farb).strip().lstrip('#'), 16)
			if new_farb == 0:
				new_farb = 0x000001
			return (new_farb)


class Feiertage():
	def ostern_greg(self, jahr):
		bewegl_feiertage = []
		a = jahr % 19
		b, c = divmod(jahr, 100)
		d, e = divmod(b, 4)
		f = int((b + 8) / 25)
		g = int((b - f + 1) / 3)
		h = (19 * a + b - d - g + 15) % 30
		i, k = divmod(c, 4)
		l = (32 + 2 * e + 2 * i - h - k) % 7
		m = int((a + 11 * h + 22 * l) / 451)
		mon, tag = divmod(h + l - 7 * m + 114, 31)
		startDate1 = datetime(int(jahr), int(mon), int(tag + 1))
		x = (_("Easter Sunday"), _("Holiday"), startDate1, startDate1, None, None, jahr, _("Easter Sunday"))
		bewegl_feiertage.append(x)
		startDate = startDate1 + timedelta(1)
		x = (_("Easter Monday"), _("Holiday"), startDate, startDate, None, None, jahr, _("Easter Monday"))
		bewegl_feiertage.append(x)
		startDate = startDate1 - timedelta(2)
		x = (_("Good Friday"), _("Holiday"), startDate, startDate, None, None, jahr, _("Good Friday"))
		bewegl_feiertage.append(x)
		startDate = startDate1 + timedelta(39)
		x = (_("Ascension"), _("Holiday"), startDate, startDate, None, None, jahr, _("Ascension"))
		bewegl_feiertage.append(x)
		startDate = startDate1 + timedelta(50)
		x = (_("Whit Monday"), _("Holiday"), startDate, startDate, None, None, jahr, _("Whit Monday"))
		bewegl_feiertage.append(x)
		startDate = startDate1 + timedelta(49)
		x = (_("Pentecost Sunday"), _("Holiday"), startDate, startDate, None, None, jahr, _("Pentecost Sunday"))
		bewegl_feiertage.append(x)
		startDate = startDate1 + timedelta(60)
		x = (_("Corpus Christi"), _("Holiday"), startDate, startDate, None, None, jahr, _("Corpus Christi"))
		bewegl_feiertage.append(x)
		return (bewegl_feiertage)

	def ostern_jul(self, jahr):
		bewegl_feiertage = []
		jahr = jahr
		a = jahr % 4
		b = jahr % 7
		c = jahr % 19
		d = (19 * c + 15) % 30
		e = (2 * a + 4 * b - d + 34) % 7
		mon, tag = divmod(d + e + 114, 31)
		startDate1 = datetime(jahr, mon, tag + 1)
		x = (_("Easter Sunday"), _("Holiday"), startDate1, startDate1, None, None, jahr, _("Easter Sunday"))
		bewegl_feiertage.append(x)
		startDate = startDate1 + timedelta(1)
		x = (_("Easter Monday"), _("Holiday"), startDate, startDate, None, None, jahr, _("Easter Monday"))
		bewegl_feiertage.append(x)
		startDate = startDate1 - timedelta(2)
		x = (_("Good Friday"), _("Holiday"), startDate, startDate, None, None, jahr, _("Good Friday"))
		bewegl_feiertage.append(x)
		startDate = startDate1 + timedelta(39)
		x = (_("Ascension"), _("Holiday"), startDate, startDate, None, None, jahr, _("Ascension"))
		bewegl_feiertage.append(x)
		startDate = startDate1 + timedelta(50)
		x = (_("Whit Monday"), _("Holiday"), startDate, startDate, None, None, jahr, _("Whit Monday"))
		bewegl_feiertage.append(x)
		startDate = startDate1 + timedelta(49)
		x = (_("Pentecost Sunday"), _("Holiday"), startDate, startDate, None, None, jahr, _("Pentecost Sunday"))
		bewegl_feiertage.append(x)
		startDate = startDate1 + timedelta(60)
		x = (_("Corpus Christi"), _("Holiday"), startDate, startDate, None, None, jahr, _("Corpus Christi"))
		bewegl_feiertage.append(x)
		return (bewegl_feiertage)


class Rules():
	def parseRule(self, rule):
		rule_list = []
		frequency = None
		interval = 1
		count = None
		untilDate = None
		byMonth = None
		byMonthday = None
		byDay = None
		byHoure = None
		byMinute = None
		byYearday = None
		byWeekno = None
		byWeekst = None
		a_rules = rule.split(";")
		for x in a_rules:
			if "FREQ=" in x:
				frequency = x.replace("FREQ=", "")
			elif "UNTIL=" in x:
				untilDate = self.parseDate(x.replace("UNTIL=", ""))
			elif "COUNT=" in x:
				count = x.replace("COUNT=", "")
			elif "INTERVAL=" in x:
				interval = int(x.replace("INTERVAL=", ""))
			elif "BYMINUTE=" in x:
				byMinute = x.replace("BYMINUTE=", "")
			elif "BYHOUR=" in x:
				byHoure = x.replace("BYHOUR=", "")
			elif "BYYEARDAY=" in x:
				byYearday = x.replace("BYYEARDAY=", "")
			elif "BYWEEKNO=" in x:
				byWeekno = x.replace("BYWEEKNO=", "")
			elif "BYWEEKST=" in x:
				byWeekst = x.replace("BYWEEKST=", "")
			elif "BYMONTHDAY=" in x:
				byMonthday = x.replace("BYMONTHDAY=", "")
				byMonthday = byMonthday.split(',')
			elif "BYMONTH=" in x:
				byMonth = x.replace("BYMONTH=", "")
				byMonth = byMonth.split(',')
			elif "BYDAY=" in x:
				byDay = x.replace("BYDAY=", "")
				byDay = byDay.split(',')
		rule_list = (frequency, interval, byMonth, byMonthday, untilDate, byMinute, byHoure, byDay, byYearday, byWeekno, byWeekst, count)
		rule = []
		for x in rule_list:
			if x is not None:
				rule = rule_list
				break
		return rule

	def parseEvent(self, lines, index=None, filename="", schicht=None):
		dname = filename.replace(CONFIGPATH, '')
		startTime = time(0)
		summary = ''
		mask = {}
		mask['Summary'] = compile(r"^SUMMARY:(.*)")
		mask['EXDATE'] = compile(r"^EXDATE(.*)")
		mask['Summary2'] = compile(r"^SUMMARY;(.*)")
		mask['DTStart'] = compile(r"^DTSTART;.*:(.*).*")
		mask['DTEnd'] = compile(r"^DTEND;.*:(.*).*")
		#mask['DTStartTZ']=compile(r"^DTSTART:(.*).*Z")
		#mask['DTEndTZ']=compile(r"^DTEND:(.*).*Z")
		mask['DTStart1'] = compile(r"^DTSTART:(.*).*")
		mask['DTEnd1'] = compile(r"^DTEND:(.*).*")
		mask['Categories'] = compile(r"^CATEGORIES:(.*)")
		mask['RRule'] = compile(r"^RRULE.*:(.*)")
		mask['LOCATION'] = compile(r"^LOCATION:*:(.*)")
		mask['Description'] = compile(r"^DESCRIPTION:(.*)")
		mask['Comment'] = compile(r"^COMMENT.*:(.*)")
		mask['TRIGGER'] = compile(r"^TRIGGER.*:(.*)")
		timed = 'time'
		count = list(range(1, len(lines)))
		for i in count:
			data = lines[i]
			if data.startswith(' '):
				lines[i - 1] = lines[i - 1].strip('\r\n') + lines[i].lstrip()
				del lines[i]
				count.insert(i, i)
				count.pop()
		DTstart = None
		r_date1 = 0
		rule = None
		DTend = None
		categories = None
		comment = None
		description = ""
		aktion = None
		alert = None
		location = ""
		schicht1 = None
		trigger1 = None
		self.date_fehler = 0
		valarm = 0
		exdate = []
		no_stsr = None
		aktion_des = None
		for line in lines:
			if mask['Summary'].match(line) and summary == '':
				summary = mask['Summary'].match(line).group(1)
				summary = str(summary.strip('\r\n'))
			elif mask['Summary2'].match(line):
				summary_a = mask['Summary2'].match(line).group(1)
				rs1 = (summary_a.find(":")) + 1
				summary = summary_a[rs1:]
				summary = str(summary.strip('\r\n'))
			elif mask['LOCATION'].match(line):
				location = mask['LOCATION'].match(line).group(1)
				location = str(location.strip('\r\n'))
			elif mask['Description'].match(line):
				if not len(description):
					description = mask['Description'].match(line).group(1)
					description = str(description.strip('\r\n'))
#			elif action=="DISPLAY":
#				al_description = mask['Description'].match(line).group(1)
#				al_description = str(description.strip('\r\n'))
			elif mask['DTStart'].match(line):
				r_date1 = mask['DTStart'].match(line).group(1)
				DTstart = self.parseDate(r_date1)
			elif mask['DTStart1'].match(line):
				r_date1 = mask['DTStart1'].match(line).group(1)
				DTstart = self.parseDate(r_date1)
			elif mask['DTEnd'].match(line):
				r_date2 = mask['DTEnd'].match(line).group(1)
				DTend = self.parseDate(r_date2)
			elif mask['DTEnd1'].match(line):
				DTend = self.parseDate(mask['DTEnd1'].match(line).group(1))
			elif mask['RRule'].match(line):
				rule = mask['RRule'].match(line).group(1)
				rule = rule.strip()
				rule = rule.replace(' ', '')
				if len(rule):
					rule = self.parseRule(rule)
			elif mask['Categories'].match(line):
				categories = mask['Categories'].match(line).group(1)
				categories = categories.strip('\r\n')
			elif mask['Comment'].match(line):
				comment = mask['Comment'].match(line).group(1)
				comment = comment.strip('\r\n')
			elif '"VALARM"' in line:
				valarm = 1
			elif 'Action' in line:
				if valarm == 0:
					aktion = line.strip('\r\n').replace('ACTION:', "")
					if aktion and str(aktion) == "no_startscreen":
						no_stsr = 1
				else:
					aktion_des = line.strip('\r\n').replace('ACTION:', "")
			elif 'EXDATE' in line:
				ed = line.strip('\r\n').split(":")
				ed_a = self.parseDate(ed[1], 1)
				exdate.append(ed_a)
			elif 'TRIGGER' in line:
				erg = self.parseTrigger(line, DTstart)
				trigger1 = erg[0]
				if erg[1] and str(aktion).upper() == "DISPLAY":
#					if aktion_des is None:
#						aktion_des = txt_s
					alert = (erg[1], str(aktion_des), erg[2], erg[3])
		if DTstart:
			if description is None:
				description = summary
			if schicht:
				if summary.strip() in schicht:
					schicht1 = 1
			if isinstance(DTstart, datetime):
				timed = 'time'
			else:
				DTstart = datetime.combine(DTstart, startTime)
				timed = 'ganztag'
			if DTend:
				if not isinstance(DTend, datetime):
					DTend = datetime.combine(DTend, startTime)
					if DTend.date() > DTstart.date():
						DTend = DTend - timedelta(days=1)
			else:
				DTend = DTstart
			if rule and DTend < DTstart:
				DTend = DTstart
			detail_list = (summary, categories, DTstart, DTend, aktion, rule, description, self.date_fehler, index, dname, comment, trigger1, timed, location, schicht1, alert, no_stsr, exdate)
			return detail_list
		else:
			return None

	def parseDate(self, dateStr, test=None):
		dateStr = dateStr.strip()
		self.date_ok = 1
		year = int(dateStr[:4])
		if year < 1900:
			year = 1900
		month = int(dateStr[4:6])
		day = int(dateStr[6:8])
		if self.date_ok:
			if len(dateStr) > 10:
				hour = int(dateStr[9:11])
				minute = int(dateStr[11:13])
				sek = int(dateStr[13:15])
				dt1 = datetime(year, month, day, hour, minute, sek)
				if dateStr[15:16] == 'Z':
					dt1 = dt1 + timedelta(hours=getTimeDiffUTC())
				return dt1
			else:
				return date(year, month, day)

	def parseTrigger(self, line=None, DTstart=timedelta(minutes=0)):
		trigger1 = None
		trigger = None
		t_t = None
		td = None
		if line:
			trigger1 = line.replace("TRIGGER", "")
			trigger1 = trigger1.strip('\r\n')
			if len(trigger1):
				if trigger1.startswith(";VALUE=DATE-TIME:"):
					trigger = trigger1.replace(";VALUE=DATE-TIME:", "")
					trigger = self.parseDate(trigger)
				elif trigger1.startswith(":-"):
					trigger1 = trigger1[1:]
					d = match(r'.*?(\d+)', trigger1)
					t_t = int(d.group(1)) if d else 0
					if trigger1[2] == "T":
						if trigger1.endswith("M"):
							td = "m"
							trigger = DTstart - timedelta(minutes=t_t)
						elif trigger1.endswith("H"):
							td = "h"
							trigger = DTstart - timedelta(hours=t_t)
					elif trigger1.endswith("D"):
						td = "d"
						trigger = DTstart - timedelta(days=t_t)
		return (trigger1, trigger, td, t_t)

	def parseEvent_b(self, datei, schicht=None):
		all_list = []
		aktion_des = None
		r = getsize(datei)
		if r > 180:
			with open(datei, "rb") as d:
				cal_datei = d.read()
			index = 0
			gcal = None
			schicht1 = None
			dname = datei.replace(CONFIGPATH, '')
			err = ""
			gcal = Calendar().from_ical(cal_datei)
			startTime = time(0)
			if gcal:
				self.oldtz = gcal.get('X-WR-TIMEZONE')
				mask = {}
				mask['TRIGGER'] = compile("^TRIGGER(.*)")
				for Icomp in gcal.walk():
					if Icomp.name == "VEVENT":
						timed = 'ganztag'
						rule = None
						trigger1 = None
						aktion = None
						alert = None
						schicht1 = 0
						exdate = []
						for Icomp2 in Icomp.walk("VALARM"):
							aktion = Icomp2.decoded('ACTION', None)
							aktion_des = Icomp2.decoded('description', None)
						Icomp_str = str(Icomp)
						txt_s = Code_utf8(Icomp.get('summary'))
						if schicht and txt_s.strip() in schicht:
							schicht1 = 1
						DTstart = Icomp.decoded("dtstart")
						if isinstance(DTstart, datetime):
							timed = 'time'
						else:
							DTstart = datetime.combine(DTstart, startTime)
						DTend = Icomp.decoded("dtend", None)
						if DTend:
							if not isinstance(DTend, datetime):
								DTend = datetime.combine(DTend, startTime)
								DTend = DTend - timedelta(days=1)
							elif DTend.tzinfo is not None:
#								if DTend.tzinfo.utcoffset(DTend) is not None and self.oldtz != "UTC":
								DTend = DTend + timedelta(hours=getTimeDiffUTC())
							DTend = DTend.replace(tzinfo=None)
						if DTstart.tzinfo is not None and DTstart.tzinfo.utcoffset(DTstart) is not None:   # and self.oldtz == "UTC"
							DTstart = DTstart + timedelta(hours=getTimeDiffUTC())
						DTstart = DTstart.replace(tzinfo=None)
						if DTend is None:
							DTend = DTstart
						if 'TRIGGER' in Icomp_str or 'EXDATE' in Icomp_str:
							lines = Icomp_str.split("\n")
							for line in lines:
								if 'TRIGGER' in line:
									erg = self.parseTrigger(line, DTstart)
									trigger1 = erg[0]
									if erg[1] and aktion and aktion.upper() == "DISPLAY":
										if aktion_des is None:
											aktion_des = txt_s
										alert = (erg[1], str(aktion_des), erg[2], erg[3])
								elif 'EXDATE' in line:
									ed = line.split(":")
									ed_a = self.parseDate(ed[1], 1)
									exdate.append(ed_a)
						rrule = Icomp.get("rrule", None)
						if rrule:
							rrule = str(rrule).strip()  # + ';'	# Leerzeichen sowie \r\n am Anfang sowie am Ende entfernen
							rrule = rrule.replace(' ', '')  # Leerzeichen entfernen
							rule = self.parseRule(rrule)
						descript = txt_s
						d_read = Icomp.get('description', None)
						if d_read:  # and len(d_read.strip()):
							descript = Code_utf8(str(d_read))
						comment = None
						c_read = Icomp.get('comment', None)
						if c_read:
							comment = Code_utf8(str(c_read))
						no_stsr = None
						a_read = Icomp.get('ACTION', None)
						if a_read and str(a_read) == "no_startscreen":
							no_stsr = 1  # =str(a_read)
						locali = ''
						l_read = Icomp.get('location', None)
						if l_read:
							locali = Code_utf8(str(l_read))
						ca_read = Icomp.get('categories', None)
						cate = ca_read.to_ical().decode() if ca_read else None
						detail_list = (txt_s, cate, DTstart, DTend, aktion, rule, descript, 0, index, dname, comment, trigger1, timed, locali, schicht1, alert, no_stsr, exdate)
						if detail_list not in all_list:
							all_list.append(detail_list)
							index += 1
				if len(err):
					fx = open("/tmp/PlanerFS-Errors.txt", "r+")
					old = fx.read()
					if str(datei) not in old:
						fx.write("plfs_err:\n%s\n" % datei)
						fx.write("%s\n" % err)
					fx.close()
				return all_list


class Next_Termin():
	def next_termin(self, rule_list=None, start_datetime=None, ende=None, jetzt=(0, 0), monate=1, art="nix", exdate=[]):
		self.monat = int(jetzt[1])
		self.jahr = jetzt[0]
		monate = int(monate)  # +1
		if start_datetime:
			monat_anfang = datetime(self.jahr, self.monat, 1, start_datetime.hour, start_datetime.minute, 0)
		monat = self.monat + monate  # +1
		jahr = self.jahr
		if monat > 12:
			monat = self.monat - 12 + monate
			jahr = self.jahr + 1
		monat_ende = datetime(jahr, monat, 1, 23, 59, 59) - timedelta(days=1)
		if self.monat == 12:
			sdt1 = date(self.jahr + 1, 1, 1) - timedelta(1)
		else:
			sdt1 = date(self.jahr, self.monat + 1, 1) - timedelta(1)
		self.monatstage = int(sdt1.day)
		next_date = None
		next_date1 = None
		rl = rule_list
		if start_datetime and ende:
			st_date = datetime(start_datetime.year, start_datetime.month, start_datetime.day, start_datetime.hour, start_datetime.minute)
			zeit = (start_datetime.hour, start_datetime.minute)
			st_date2 = datetime(start_datetime.year, start_datetime.month, start_datetime.day)
			st_end = datetime(ende.year, ende.month, ende.day, start_datetime.hour, start_datetime.minute)
			if art == "terminlist2":
				st_end = st_end + timedelta(3)
		next_dats = []
		interval = 1
		until = monat_ende
		rcount = 0
		if rl and start_datetime:  #wenn rule
			st_end = datetime(start_datetime.year, start_datetime.month, start_datetime.day, start_datetime.hour, start_datetime.minute)
			if rl[11] is not None:
				rcount = int(rl[11])
			if rl[4] is None:  # or art=="schicht":
				until = monat_ende
			else:
				until2 = rl[4]
				if isinstance(rl[4], datetime):
					until2 = datetime.date(rl[4])
				until = datetime(until2.year, until2.month, until2.day, 23, 59)
			if rl[1] is not None:
				interval = int(rl[1])
			if until >= monat_anfang:
				if rl[0] == 'YEARLY':
					nj = self.jahr
					if rcount:
						nj = st_date2.year
					zcount = 0
					while nj <= int(until.year):
						if (self.jahr - st_date.year) % interval == 0:
							if rl[2] is not None and rl[3] is not None:
								for monat in rl[2]:
									for x in rl[3]:
										rl_x = int(x)
										if rl_x < 1:
											subtra = (rl_x * -1) - 1
											rl_x = int(self.monatstage) - subtra
										next_dats.append(datetime(nj, int(rl[2][0]), rl_x, zeit[0], zeit[1]))
							else:
								next_dats.append(datetime(nj, st_date.month, st_date.day, zeit[0], zeit[1]))
								if rcount:
									zcount += 1
						nj += interval
						if zcount > 0 and zcount >= rcount:
							break
				elif rl[0] == 'MONTHLY':
					sjahr = monat_anfang.year
					nj = monat_anfang.date()
					if rcount:
						sjahr = st_date2.year
						nj = st_date2.date()
					zcount = 0
					while nj <= until.date():
						if nj >= st_date2.date():
							xm = nj.month
							if rl[3]:
								for x in rl[3]:
									rl_x = int(x)
									if rl_x < 1:
										subtra = (rl_x * -1)  # -1
										if xm == 12:
											xm = 0
											sjahr = sjahr + 1
										next_dats.append(datetime(sjahr, int(xm + 1), 1, zeit[0], zeit[1]) - timedelta(subtra))
										if rcount:
											zcount += 1
									else:
										next_dats.append(datetime(sjahr, int(xm), rl_x, zeit[0], zeit[1]))
										if rcount:
											zcount += 1
							else:
								next_dats.append(datetime(sjahr, int(xm), st_date.day, zeit[0], zeit[1]))
								if rcount:
									zcount += 1
						xm2 = nj.month + interval
						if xm2 > 12:
							gr = int(xm2 / 12)
							xm2 = xm2 % 12
							sjahr = self.jahr + gr
						nj = date(int(sjahr), int(xm2), 1)
						if zcount > 0 and zcount >= rcount:
							break
				elif rl[0] == 'DAILY':
					wd_list = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
					delta = monat_anfang - st_date
					delta = delta.days
					diff = interval - ((delta - interval) % interval)
					start = monat_anfang
					if rcount:
						start = st_date
					zcount = 0
					while until >= start + timedelta(diff - interval):
						if rl[7]:
							for wd in rl[7]:
								wd2 = start + timedelta(diff)
								if wd == wd_list[wd2.weekday()]:
									if until >= st_date + timedelta(diff - interval):
										next_dats.append(st_date + timedelta(diff - interval))
										if rcount:
											zcount += 1
						else:
							if st_date <= start + timedelta(diff - interval) <= until:
								next_dats.append(start + timedelta(diff - interval))
								if rcount:
									zcount += 1
						diff = diff + interval
						if zcount > 0 and zcount >= rcount:
							break
				elif rl[0] == 'WEEKLY':
					d4 = interval * 7
					wd_list = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
					wo = (monat_anfang - st_date).days
					diff = d4 - ((wo + d4) % d4)
					diff = diff - d4
					count1 = 0
					st_date1 = st_date - timedelta(d4)
					start = monat_anfang
					if rcount:
						start = st_date
					zcount = 0
					while monat_ende >= start + timedelta(diff):
						count1 += 1
						if count1 > 60:
							break
						if st_date1 <= start + timedelta(diff) <= until:
							if rl[7]:
								for wd in rl[7]:
									wd2 = start + timedelta(diff)
									if wd == wd_list[wd2.weekday()]:
										next_dats.append(start + timedelta(diff))
										if rcount:
											zcount += 1
#								if interval >1 and wd2.weekday()==6:
#									diff=diff+((7*interval)-6)
#								else:
								diff += interval  # 1
							else:
								d1 = (start + timedelta(diff)) - st_date
								d2 = (d4 - d1.days) % d4
								if d2 == 0:
									next_dats.append(start + timedelta(diff))
									if rcount:
										zcount += 1
									diff = diff + (7 * interval)
								else:
									diff += interval
						else:
							diff = diff + self.monatstage + 1
						if zcount > 0 and zcount >= rcount:
							break
		else:  #kein rule
			if st_end >= monat_anfang:
				if st_end.date() == st_date.date():
					next_dats.append(st_end)
				elif st_end.date() > st_date.date():
					max_dat = st_end + timedelta(1)
					next = st_date
					while max_dat.date() > next.date():
						next_dats.append(next)
						next = next + timedelta(1)
				elif monat_anfang <= st_date <= monat_ende:
					next_dats.append(st_date)
		next_date = []
		for next_date1 in next_dats:
			if next_date1.date() not in exdate and until and until >= next_date1:
				if next_date1 and monat_anfang <= next_date1 <= monat_ende:
					next_date.append(next_date1)
		next = (next_date)
		return next


class schicht():
	def parseSchicht(self, datei=None, sel=None, art="s2"):
		if datei is None:
			return
		all_list = []
		configparser = ConfigParser()
		configparser.read(CONFIGFILE)
		schicht = ("0", "0", "0")
		schicht_colors = {}
		if configparser.has_section("settings"):
			if configparser.has_option("settings", "schicht_art"):
				schicht = str(configparser.get("settings", "schicht_art")).split(",")
				if len(schicht) < 3:
					schicht.extend(("0", "0", "0")[len(schicht):])
			if configparser.has_option("settings", "schicht_col"):
				schicht_colors = eval(configparser.get("settings", "schicht_col"))
			else:
				schicht_colors = {"F": "#008B45", "S": "#FFD700", "N": "#3A5FCD", "fr": "#858585"}
#				schicht_colors={"F":"#32CD32","S":"#FFD700","N":"#3A5FCD","fr":"#858585","Urlaub":"#FF0000"}
		sch_beschr = int(schicht[2])
		if _("without text") not in schicht_colors:
			schicht_colors[_("without text")] = "#858585"
		if sch_beschr and _("If description") not in schicht_colors:
			schicht_colors[_("If description")] = "#858585"
		d = datetime.today()
		jetzt = (d.year, d.month)
		if sel and str(sel) == "export1":
			vor = 2
			now1 = datetime(d.year, d.month, d.day, 0, 0, 0)
			now1 = now1 - timedelta(days=1)
		elif sel and sel[0]:
			jetzt = sel
			vor = 1
			now1 = datetime(jetzt[0], jetzt[1], 1, 0, 0, 0)
		else:
			vor = 2
			now1 = datetime(d.year, d.month, d.day, 0, 0, 0)
		datlist = []
		rullist = []
		datei.sort(key=lambda x: x[1])
		datei.reverse()
		for dats in datei:
			rule = None
			color = schicht_colors[_("without text")]  # "97FFFF"
			txt = dats[0]
			gesamt = dats[5]
			all = str(dats)
			if dats[4] and dats[4].strip() != dats[0].strip():
				if sch_beschr:
					color = schicht_colors[_("If description")]
				elif txt.strip() in schicht_colors:
					color = schicht_colors[txt.strip()]
				if len(dats[4].strip()):
					txt = txt + " (" + dats[4] + ")"
			elif txt.strip() in schicht_colors:
				color = schicht_colors[txt.strip()]
			DTstart = dats[1]
			DTend = dats[2]
			rule = dats[3]
			if rule:
				exd = []
				if len(dats) > 6:
					exd = dats[6]
				DTend = now1 + timedelta(days=32)
				if rule[4]:
					DTend = rule[4]
					if not isinstance(DTend, datetime):
						DTend = datetime.combine(DTstart, time(0))
				if DTstart < now1 + timedelta(days=31) and DTend >= now1:
					next_datet = Next_Termin().next_termin(rule, DTstart, DTend, jetzt, vor, "schicht", exd)
					for x in next_datet:
						detail_list = (x.day, txt, color, x, gesamt, all)
						if vor == 1:
							if x.month == jetzt[1] and detail_list not in rullist:
								rullist.append(detail_list)
						else:
							if x >= now1 and x < now1 + timedelta(days=20):
								rullist.append(detail_list)
			else:
				if sel and sel[0] and str(sel) != "export1":
					if DTend >= now1 and DTstart < now1 + timedelta(days=31):
						if DTend >= DTstart:
							dx = DTstart
							while dx <= DTend:
								detail_list = (dx.day, txt, color, dx, gesamt, all)

								if dx >= now1 and detail_list not in all_list and dx.month == jetzt[1]:
									datlist.append(dx.date())
									all_list.append(detail_list)
								dx = dx + timedelta(days=1)
						else:
							if DTstart.month == jetzt[1]:
								detail_list = (DTstart.day, txt, color, DTstart, gesamt, all)
								if detail_list not in all_list:
									all_list.append(detail_list)
				else:
					now2 = now1 + timedelta(days=21)
					if DTstart < now2 and DTend >= now1:
						if DTend > DTstart:
							dx = DTstart
							while dx <= DTend and dx <= now2:
								detail_list = (dx.day, txt, color, dx, gesamt, all)
								if detail_list not in all_list and dx < now2 and dx >= now1:
									if dx.date() not in datlist:
										datlist.append(dx.date())
										all_list.append(detail_list)
								dx = dx + timedelta(days=1)
						else:
							detail_list = (DTstart.day, txt, color, DTstart, gesamt, all)
							if detail_list not in all_list:
								if DTstart.date() not in datlist:
									datlist.append(DTstart.date())
									all_list.append(detail_list)
		if len(rullist):
			for x in rullist:
				if x[3].date() not in datlist:
					datlist.append(x[3].date())
					all_list.append(x)
		max1 = date(jetzt[0], jetzt[1], 1)
		max2 = max1 + timedelta(days=31)
		if sel and sel[0] and str(sel) != "export1":  # and str(sel)!="export"
			while now1.date() < max2:
				if now1.date() not in datlist:
					all_list.append((now1.day, "", schicht_colors[_("without text")], now1))
					datlist.append(now1.date())
					now1 = now1 + timedelta(days=1)
		else:
			now2 = now1 + timedelta(days=20)
			now3 = now1
			while now3 < now2:
				if now3.date() not in datlist:
					all_list.append((now3.day, "", schicht_colors[_("without text")], now3))
					datlist.append(now3.date())
					now3 = now3 + timedelta(days=1)
		all_list.sort(key=lambda x: x[3] or str(sel) == "export1")
		if sel is None or sel[0] is None:
			n_l = all_list
			all_list = []
			for x in n_l:
				if x[3] >= now1:
					all_list.append(x)
		return all_list
