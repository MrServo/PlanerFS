# PYTHON IMPORTS
from configparser import ConfigParser
from os import listdir, unlink
from os.path import exists, join, isfile

# ENIGMA IMPORTS
from Components.ActionMap import NumberActionMap
from Components.config import ConfigLocations
from Components.Sources.List import List
from Screens.Console import Console
from Screens.LocationBox import LocationBox
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.Directories import copyfile

# PLUGIN IMPORTS
from . import CONFIGPATH, CONFIGFILE, PLUGINPATH, ICSNAME, ICSFILE, VCFNAME, DWIDE, VERSION, _  # for localized messages
from .PFSimport import all_import, vcf_import

last_backup_path = "/"
internet_File = ""
dat_dir = CONFIGPATH
cals_dir = '/tmp/'
sec_file = None
download_name = "download"
if exists(CONFIGFILE):
	configparser = ConfigParser()
	configparser.read(CONFIGFILE)
	if configparser.has_section("settings"):
		if configparser.has_option("settings", "last_backup_path"):
			last_backup_path = configparser.get("settings", "last_backup_path")
		if configparser.has_option("settings", "internet_File"):
			internet_File = configparser.get("settings", "internet_File")
		if configparser.has_option("settings", "dat_dir"):
			dat_dir = configparser.get("settings", "dat_dir")
		if configparser.has_option("settings", "sec_file"):
			sec_file = configparser.get("settings", "sec_file")
		if configparser.has_option("settings", "cals_dir"):
			cals_dir = configparser.get("settings", "cals_dir")
backup_path = ConfigLocations(default=[last_backup_path])


class PFS_filemenu7(Screen):
	skindatei = join(PLUGINPATH, "skin/%s/PFSmenulist.xml" % ("fHD" if DWIDE > 1300 else "HD"))
	with open(skindatei) as tmpskin:
		skin = tmpskin.read()

	def __init__(self, session, startart=0):
		self.startart = startart
		Screen.__init__(self, session)
		self.skinName = "menulist7"
		self.session = session
		self.settigspath = ""
		lista = []
		self["menulist"] = List([])
		self.num = 1
#		if internet_File != "":
#                    list.append(self.PFS_ListEntry((_('download for data update'), 'syncro')))
		lista.append(("1", _('Show list of all iCal-Files'), 'all_list'))
		lista.append(("2", _('backup files and settings'), 'backup'))
		lista.append(("3", _('restore files and settings'), 'restore'))
		lista.append(("4", _('delete extern ics-File'), 'delete'))
		lista.append(("5", _('Copy ics-File to PlanerFS path'), 'copy_in'))
		lista.append(("6", _('Copy ics-File of PlanerFS path'), 'copy_out'))
		lista.append(("7", _('Import all events from an ics file'), 'import_all'))
		lista.append(("8", _('Import all cards from an vcf file'), 'import_vcf'))
		if not exists(ICSFILE):
			lista.append(("9", _('make second calendar'), 'make_sec'))
		self.setTitle("PlanerFS: " + _("Files Handling"))
		self["menulist"].setList(lista)
		self["actions"] = NumberActionMap(["OkCancelActions", "ColorActions", "InputActions", "DirectionActions"],
		{
				"ok": self.run,
				"cancel": self.close,
				"1": self.keyNumberGlobal,
				"2": self.keyNumberGlobal,
				"3": self.keyNumberGlobal,
				"4": self.keyNumberGlobal,
				"5": self.keyNumberGlobal,
				"6": self.keyNumberGlobal,
				"7": self.keyNumberGlobal,
				"8": self.keyNumberGlobal,
				"9": self.keyNumberGlobal,
				# "0": self.keyNumberGlobal,
				# "red": self.ftpload,
				# "green": self.setMainMenu,
				# "yellow": self.restore,
				# "blue": self.internet_import
		}, -1)

	def keyNumberGlobal(self, number):
		self["menulist"].setIndex(number - 1)
		self.run()

	def run(self):
		self.vcf = 0
		returnValue = self["menulist"].getCurrent()[2]
		if returnValue == 'backup':
			self.backup()
		elif returnValue == 'restore':
			self.restore()
		elif returnValue == 'delete':
			self.del_1()
		elif returnValue == 'syncro':
			self.internet_import()
		elif returnValue == 'copy_in':
			self.copy_in()
		elif returnValue == 'copy_out':
			self.copy_out()
		elif returnValue == 'import_all':
			self.import_path()
		elif returnValue == 'import_vcf':
			self.vcf = 1
			self.import_path()
		elif returnValue == 'make_sec':
			self.make_sec()
		elif returnValue == 'all_list':
			self.all_list()

	def all_list(self):
		self.session.open(PFS_allfilelist)

	def make_sec(self):
		with open(ICSFILE, "w") as f:
			f.write("BEGIN:VCALENDAR\nMETHOD:PUBLISH\nPRODID: -Enigma2-Plugin / PlanerFSsec %s\nVERSION:2.0\nEND:VCALENDAR" % VERSION)
		self.session.open(MessageBox, _("second calendar was created successfully, to see push-button Bouquet on the calendar"), MessageBox.TYPE_INFO)
		self.close()

	def copy_in(self):
#		self.backup_path=ConfigLocations(default=["/tmp/"]
		self.session.openWithCallback(self.callCopy_in, BackupLocationBox, _("Please select source path..."), "", "/tmp/", ConfigLocations(default=["/tmp/"]))

	def copy_out(self):
		cal_files_path = CONFIGPATH
		cal_files = []
		if exists(cal_files_path):
			for cal_file in listdir(cal_files_path):
				if cal_file.endswith(".ics"):
					cal_files.append((cal_file, join(cal_files_path, cal_file)))
		if len(cal_files) > 0:
			self.session.open(del_files7, cal_files, "copy_out")
		else:
			self.session.open(MessageBox, _(_("No ics-File in this Path exist!")), MessageBox.TYPE_INFO)

	def import_path(self):
		self.session.openWithCallback(self.callImport, BackupLocationBox, _("Please select source path..."), "", CONFIGPATH, ConfigLocations(default=["/tmp/", CONFIGPATH]))

	def callImport(self, path):
		if self.vcf == 0:
			cal_files = []
			if path is not None:
				if exists(path):
					for cal_file in listdir(path):
						if cal_file.endswith(".ics") and join(path, ICSNAME) != ICSFILE:
							cal_files.append((cal_file, join(path, cal_file)))
				if len(cal_files) > 0:
					self.session.open(del_files7, cal_files, "importer")
					self.close()
				else:
					self.session.open(MessageBox, _("No ics-File in this Path exist!"), MessageBox.TYPE_INFO)
		elif self.vcf == 1:
			vcf_files = []
			if path is not None:
				if exists(path):
					for vcf_file in listdir(path):
						if vcf_file.endswith(".vcf") and join(path, vcf_file) != VCFNAME:
							vcf_files.append((vcf_file, join(path, vcf_file)))
				if len(vcf_files) > 0:
					self.session.open(del_files7, vcf_files, "importer_vcf")
					self.close()
				else:
					self.session.open(MessageBox, _("No vcf-File in this Path exist!"), MessageBox.TYPE_INFO)

	def del_1(self):
		cal_files_path = CONFIGPATH
		cal_files = []
		if exists(cal_files_path):
			for cal_file in listdir(cal_files_path):
				if cal_file.endswith(".ics") and cal_file != ICSNAME:
					cal_files.append((cal_file, join(cal_files_path, cal_file)))
		if len(cal_files) > 0:
			self.session.open(del_files7, cal_files, "delete")
		else:
			self.session.open(MessageBox, _("No extern ics-File exist!"), MessageBox.TYPE_INFO)

	def callCopy_in(self, path):
		cal_files = []
		if path is not None:
			if exists(path):
				for cal_file in listdir(path):
					if cal_file.endswith(".ics"):
						cal_files.append((cal_file, join(path, cal_file)))
			if len(cal_files) > 0:
				self.session.open(del_files7, cal_files, "copy_in")
			else:
				self.session.open(MessageBox, _("No ics-File in this Path exist!"), MessageBox.TYPE_INFO)

	def backup(self):
		self.session.openWithCallback(self.callBackup, BackupLocationBox, _("Please select the backup path..."), "", last_backup_path, ConfigLocations(default=[last_backup_path]))

	def callBackup(self, path):
		if path is not None:
			if isfile(path):
				last_backup_path = path
				conf_l = []
				with open(CONFIGFILE, 'r') as fp:
					conf_lines = fp.readlines()
				for x in conf_lines:
					split = x.strip().split(' = ', 1)
					if split[0] == "Backup Path":
						x = "Backup Path = %s" % last_backup_path
					conf_l.append(x)
				with open(CONFIGFILE, "w") as f:
					f.writelines(conf_l)
				self.settigspath = path + "ConfFS.tar.gz"
				if isfile(self.settigspath):
					self.session.openWithCallback(self.callOverwriteBackup, MessageBox, _("Overwrite existing Backup?"), type=MessageBox.TYPE_YESNO,)
				else:
					com = "tar czvf %s /etc/ConfFS/" % (self.settigspath)
					self.session.open(Console, _("Backup ConfFS..."), [com])
			else:
				self.session.open(MessageBox, _("Directory %s nonexistent.") % (path), type=MessageBox.TYPE_ERROR, timeout=5)
		else:
			print("[PlanerFS] backup cancel")

	def callOverwriteBackup(self, res):
		if res:
			com = "tar czvf %s /etc/ConfFS/" % (self.settigspath)
			self.session.open(Console, _("Backup Files and Settings..."), [com])

	def restore(self):
		self.session.openWithCallback(self.callRestore, BackupLocationBox, _("Please select the restore path..."), "", last_backup_path, ConfigLocations(default=[last_backup_path]))

	def callRestore(self, path):
		if path is not None:
			self.settigspath = "%sConfFS.tar.gz" % path
			if isfile(self.settigspath):
				self.session.openWithCallback(self.callOverwriteSettings, MessageBox, _("Overwrite existing Settings and Files?"), type=MessageBox.TYPE_YESNO,)
			else:
				self.session.open(MessageBox, _("File %s nonexistent.") % (path), type=MessageBox.TYPE_ERROR, timeout=5)
		else:
			print("[ConfFS] backup cancel")

	def callOverwriteSettings(self, res):
		if res:
			com = "cd /; tar xzvf %s" % (self.settigspath)
			self.session.open(Console, _("Restore Files and Settings..."), [com])


class BackupLocationBox(LocationBox):
	def __init__(self, session, text, filename, dir, backup_path, minFree=None):
		inhibitDirs = ["/bin", "/boot", "/dev", "/lib", "/proc", "/sbin", "/sys", "/usr", "/var"]
		LocationBox.__init__(self, session, text=text, filename=filename, currDir=dir, bookmarks=backup_path, autoAdd=True, editDir=True, inhibitDirs=inhibitDirs, minFree=minFree)
		self.skinName = "LocationBox"


class del_files7(Screen):
	skindatei = join(PLUGINPATH, "skin/%s/PFSmenulist.xml" % ("fHD" if DWIDE > 1300 else "HD"))
	with open(skindatei) as tmpskin:
		skin = tmpskin.read()

	def __init__(self, session, cal_files, act):
		Screen.__init__(self, session)
		self.skinName = "menulist7"
		self.session = session
		self.ext_file_list(cal_files)
		self["menulist"] = List([])
		self["menulist"].style = "files"
		lista = self.cal_files
		self.act = act
		if self.act == "delete":
			self.setTitle("PlanerFS: " + _("delete extern ics-File"))
		elif self.act == "copy_in":
			self.setTitle("PlanerFS: " + _("Copy ics-File to PlanerFS path"))
		elif self.act == "copy_out":
			self.setTitle("PlanerFS: " + _("Copy ics-File of PlanerFS path"))
		elif self.act == "importer":
			self.setTitle("PlanerFS: " + _("Import all Data of ics-File"))
		elif self.act == "importer_vcf":
			self.setTitle("PlanerFS: " + _("Import all Data of vcf-File"))
		#self["list"] = PFS_List(list=lista, selection = 0)
		self["menulist"].setList(lista)
		self["actions"] = NumberActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],
		{
				"ok": self.call_ok,
				"cancel": self.exit,
				#"red": self.autostart,
				#"green": self.setMainMenu,
				#"yellow": self.restore,
				#"blue": self.backup
		}, -1)

	def call_ok(self):
		if self.act == "delete":
			self.del_file()
		elif self.act == "copy_in":
			self.cop_in()
		elif self.act == "copy_out":
			self.cop_out()
		elif self.act == "importer":
			self.import_all()
		elif self.act == "importer_vcf":
			self.import_vcf()
		else:
			pass

	def ext_file_list(self, cal_files):
		self.cal_files = []
		for x in cal_files:
			self.cal_files.append((x[0], x[1]))
		return self.cal_files

	def import_all(self):
#		try:
		if 1 == 1:
			with open("/tmp/PlanerFS-Errors.txt", "a") as f:
				f.write(str(self["menulist"].getCurrent()) + "\n")
			if self["menulist"].getCurrent()[0]:
				source = (self["menulist"].getCurrent()[1])
				importdatei = source  # "/etc/ConfFS/test.ics"
				imp = all_import().run(importdatei)
				if imp == 1:
					self.session.open(MessageBox, _("Import completed successfully"), MessageBox.TYPE_INFO)
					self.exit()
				else:
					self.session.open(MessageBox, _("unknown error"), MessageBox.TYPE_ERROR)
#		except Exception as e:
#			self.writing(str(e))

	def import_vcf(self):
		if self["menulist"].getCurrent()[0]:
			source = (self["menulist"].getCurrent()[1])
			importdatei = source  # "/etc/ConfFS/test.ics"
			imp = vcf_import().run(importdatei)
			if imp == 1:
				self.session.open(MessageBox, _("Import completed successfully"), MessageBox.TYPE_INFO)
				self.exit()
			else:
				self.session.open(MessageBox, _("unknown error"), MessageBox.TYPE_ERROR)

	def cop_in(self):
#		try:
		if 1 == 1:
			if self["menulist"].getCurrent()[0]:
				source = (self["menulist"].getCurrent()[1])
				target = join(CONFIGPATH, self["menulist"].getCurrent()[0])
				copyfile(source, target)
				self.exit()
#		except Exception as e:
#			self.writing(str(e))

	def cop_out(self):
		self.session.openWithCallback(self.callCopy_out, BackupLocationBox, _("Please select the target path..."), "", "/tmp/", ConfigLocations(default=["/tmp/"]))

	def callCopy_out(self, path):
#		try:
		if 1 == 1:
			if path is not None:
				if self["menulist"].getCurrent()[0]:
					source = (self["menulist"].getCurrent()[1])
					target = join(path, self["menulist"].getCurrent()[0])
					ret = copyfile(source, target)
					self.exit()
#		except Exception as e:
#			self.writing(str(e))

	def del_file(self):
		if self["menulist"].getCurrent()[0]:
			self.t = self["menulist"].getCurrent()
			text1 = _("selceted File is:") + "\n" + self.t[0] + "\n\n"
			self.session.openWithCallback(self.del_file_ok, MessageBox, _(text1 + _("Do you really want to delete this file?")), MessageBox.TYPE_YESNO)

	def del_file_ok(self, answer):
#		try:
		if 1 == 1:
			unlink(self["menulist"].getCurrent()[1])
			self.session.openWithCallback(self.exit, MessageBox, (self.t[0] + "\n" + _("file is deleted")), MessageBox.TYPE_INFO)
#		except OSError as e:
#			txt = 'error: \n%s' % e
#			self.session.openWithCallback(self.exit, MessageBox, txt, MessageBox.TYPE_INFO)

	def writing(self, err=None):
		if err:
			with open("/tmp/PlanerFS-Errors.txt", "a") as f:
				f.write("pfsfiles:\n" + err + "\n")
			self.session.open(MessageBox, _("unknown error"), MessageBox.TYPE_ERROR)

	def exit(self, answer=None):
		self.close()


class PFS_allfilelist(Screen):
	skindatei = join(PLUGINPATH, "skin/%s/PFSmenulist.xml" % ("fHD" if DWIDE > 1300 else "HD"))
	with open(skindatei) as tmpskin:
		skin = tmpskin.read()

	def __init__(self, session):
		liste = []
		self.sliste = liste
		self["menulist"] = List([])
		self["menulist"].style = "files"
		Screen.__init__(self, session)
		self.skinName = "menulist7"
		self.setTitle("PlanerFS: " + _("Show list of all iCal-Files"))
		self["actions"] = NumberActionMap(["OkCancelActions", "ColorActions", "InputActions", "DirectionActions"],
		{
				"ok": self.nix,
				"cancel": self.close,
		}, -1)
		self.onLayoutFinish.append(self.read)

	def nix(self):
		pass

	def read(self):
		files = []
		onlines = None
		sec_file = ""
		files.append(("", 'in dir: >> /etc/ConfFS/', 1, ""))
		if exists('/etc/ConfFS/PlanerFS.ics'):
			files.append(("", " " * 5 + '/etc/ConfFS/PlanerFS.ics', 1, ""))
		if sec_file != "" and sec_file != _("none") and exists(sec_file):
			files.append(("", " " * 5 + sec_file, 1, ""))
		if dat_dir != '/etc/ConfFS/':
			files.append(("", 'in dir: >> /' + dat_dir, 1, ""))
			if exists(dat_dir):
				for cal_file in listdir(dat_dir):
					if cal_file == 'PlanerFS_online.txt':
						onlines = dat_dir + cal_file
					if cal_file.endswith(".ics"):
						files.append(("", " " * 5 + dat_dir + cal_file, 1, ""))
		for cal_file in listdir(cals_dir):
			if cal_file.endswith(".ics"):
				files.append(("", join(cals_dir, cal_file), 1, ""))
		if onlines:
			files.append(("", "in online-file: " + str(onlines), None, "", ""))
			fp = open(onlines, 'r')
			onl_lines = fp.readlines()
			fp.close()
			for x in onl_lines:
				x = x.strip()
				if len(x) and ("://" in x or ".ics" in x):
					splits = x.split('=')
					#url=splits[2].strip()
					if x.startswith("#"):
						files.append(("", " " * 8 + splits[0].replace("#", "") + "(inctive) "))
						files.append(("", " " * 5 + "url:" + splits[1], 0, "", x))
					else:
						files.append(("", " " * 8 + splits[0]))
						files.append(("", " " * 5 + "url:" + splits[1], 1, "", x))
		if exists('/etc/ConfFS/PlanerFS_online.txt'):
			files.append(("", "in online-file: " + '/etc/ConfFS/PlanerFS_online.txt', None, "", ""))
			fp = open('/etc/ConfFS/PlanerFS_online.txt', 'r')
			onl_lines = fp.readlines()
			fp.close()
			for x in onl_lines:
				x = x.strip()
				if len(x) and ("://" in x or ".ics" in x):
					splits = x.split('=')
					#url=splits[2].strip()
					if x.startswith("#"):
						files.append(("", " " * 8 + splits[0].replace("#", "") + "(inctive) "))
						files.append(("", " " * 5 + "url:" + splits[1], 0, "", x))
					else:
						files.append(("", " " * 8 + splits[0]))
						files.append(("", " " * 5 + "url:" + splits[1], 1, "", x))
		self["menulist"].setList(files)
