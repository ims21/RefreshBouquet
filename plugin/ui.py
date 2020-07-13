# -*- coding: utf-8 -*-
# for localized messages
from . import _, ngettext

#
#  Refresh Bouquet - Plugin E2 for OpenPLi
VERSION = "2.05"
#  by ims (c) 2016-2020 ims21@users.sourceforge.net
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#

from ServiceReference import ServiceReference
from enigma import eServiceCenter, iServiceInformation, eServiceReference, eListboxPythonMultiContent, eListbox, gFont, RT_HALIGN_LEFT, getDesktop, eDVBDB
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.config import config, ConfigYesNo, getConfigListEntry, ConfigSelection, NoSave
from Components.Label import Label
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from Screens.ChoiceBox import ChoiceBox
from Components.ScrollLabel import ScrollLabel
from Components.MenuList import MenuList
from Components.ConfigList import ConfigListScreen
from Screens.MessageBox import MessageBox
from Components.Sources.ServiceEvent import ServiceEvent
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from Tools.LoadPixmap import LoadPixmap
from Tools.BoundFunction import boundFunction
from Tools.Transponder import ConvertToHumanReadable
import os, unicodedata
import skin
from plugin import plugin_path
from Screens.VirtualKeyBoard import VirtualKeyBoard
from ServiceReference import ServiceReference
from Components.Sources.Boolean import Boolean
from Components.Pixmap import Pixmap
from Components.About import GetIPsFromNetworkInterfaces
import socket

config.plugins.refreshbouquet.case_sensitive = ConfigYesNo(default = False)
config.plugins.refreshbouquet.omit_first = ConfigYesNo(default = True)
config.plugins.refreshbouquet.debug = ConfigYesNo(default = False)
config.plugins.refreshbouquet.log = ConfigYesNo(default = False)
config.plugins.refreshbouquet.mr_sortsource = ConfigSelection(default = "0", choices = [("0", _("Original")),("1", _("A-z sort")),("2", _("Z-a sort"))])
config.plugins.refreshbouquet.used_services = ConfigSelection(default = "all", choices = [("all",_("no")),("HD",_("HD")),("4K",_("4K/UHD")),("HD4K",_("HD or 4K/UHD"))])
config.plugins.refreshbouquet.diff = ConfigYesNo(default = False)
config.plugins.refreshbouquet.preview = ConfigYesNo(default = False)
config.plugins.refreshbouquet.autotoggle = ConfigYesNo(default = True)
config.plugins.refreshbouquet.on_end = ConfigYesNo(default = True)
config.plugins.refreshbouquet.orbital = ConfigSelection(default = "x", choices = [("x",_("no")),])
config.plugins.refreshbouquet.stype = ConfigYesNo(default = False)
config.plugins.refreshbouquet.current_bouquet = ConfigSelection(default = "0", choices = [("0",_("no")),("source",_("source bouquet")),("target",_("target bouquet"))])
config.plugins.refreshbouquet.selector2bouquet = ConfigYesNo(default = False)
config.plugins.refreshbouquet.bouquet_name = ConfigYesNo(default = True)
config.plugins.refreshbouquet.confirm_move = ConfigYesNo(default = True)
config.plugins.refreshbouquet.ignore_last_char = ConfigSelection(default = None, choices = [(None,_("no")),(".",".")])
choicelist = []
for i in range(1, 11, 1):
	choicelist.append(("%d" % i))
choicelist.append(("15","15"))
choicelist.append(("20","20"))
config.plugins.refreshbouquet.vk_length = ConfigSelection(default = "3", choices = [("0", _("No"))] + choicelist + [("255", _("All"))])
config.plugins.refreshbouquet.vk_sensitive = ConfigYesNo(default=False)
config.plugins.refreshbouquet.sortmenu = ConfigSelection(default = "0", choices = [("0", _("Original")),("1", _("A-z sort")),("2", _("Z-a sort")),("3", _("Selected top")),("4", _("Original - reverted"))])
config.plugins.refreshbouquet.rbb_dotted = ConfigYesNo(default=False)
config.plugins.refreshbouquet.deleted_bq_fullname = ConfigYesNo(default=False)

cfg = config.plugins.refreshbouquet

TV = (1, 17, 22, 25, 31, 134, 195)
RADIO = (2, 10)

E2 = "/etc/enigma2"

sel_position = None

class refreshBouquet(Screen, HelpableScreen):
	skin = """
	<screen name="refreshBouquet" position="center,center" size="560,375" title="Refresh Bouquet">
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on"/>
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on"/>
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on"/>
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on"/>
		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="source_text" position="10,40" zPosition="2" size="200,25" valign="center" halign="left" font="Regular;22" foregroundColor="yellow"/>
		<widget name="target_text" position="10,65" zPosition="2" size="200,25" valign="center" halign="left" font="Regular;22" foregroundColor="blue"/>
		<widget name="source_name" position="220,40" zPosition="2" size="330,25" valign="center" halign="left" font="Regular;22" foregroundColor="white"/>
		<widget name="target_name" position="220,65" zPosition="2" size="330,25" valign="center" halign="left" font="Regular;22" foregroundColor="white"/>
		<ePixmap pixmap="skin_default/div-h.png" position="5,92" zPosition="2" size="550,2"/>
		<widget source="config" render="Listbox" position="5,97" size="550,250" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
				{"template": [
						MultiContentEntryText(pos = (0, 0), size = (550, 25), font=0, flags = RT_HALIGN_LEFT, text = 0),
						],
					"fonts": [gFont("Regular", 22)],
					"itemHeight": 25
				}
			</convert>
		</widget>
		<ePixmap pixmap="skin_default/div-h.png" position="5,350" zPosition="2" size="550,2"/>
		<widget name="info" position="5,353" zPosition="2" size="550,23" valign="center" halign="left" font="Regular;20" foregroundColor="white"/>
	</screen>"""

	def __init__(self, session, Servicelist=None, currentBouquet=None):
		self.skin = refreshBouquet.skin
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)

		self.Servicelist = Servicelist
		currentBouquet = ( ServiceReference(currentBouquet).getServiceName(), currentBouquet)
		self.setTitle(_("RefreshBouquet v. %s" % VERSION))

		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
			{
			"cancel": (self.exit, _("exit plugin")),
			"ok": (self.showMenu, _("select action")),
			})
		self["RefreshBouquetActions"] = HelpableActionMap(self, "RefreshBouquetActions",
			{
			"red": (self.exit, _("exit plugin")),
			"green": (self.showMenu, _("select action")),
			"yellow": (self.getSource, _("select source bouquet")),
			"blue": (self.getTarget, _("select target bouquet")),
			"menu": (self.showMenu, _("select action")),
			"clearInputs": (self.clearInputs, _("clear selection")),
			"moving": (self.startMoving, _("enable/disable moving bouquet")),
			"next": (self.moveDown, _("move item down")),
			"prev": (self.moveUp, _("move item up")),
			}, -2)

		self.edit = 0
		self.idx = 0
		self.changes = False
		self["h_prev"] = Pixmap()
		self["h_next"] = Pixmap()
		self.showPrevNext()

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Run"))
		self["key_yellow"] = Button(_("Set source"))
		self["key_blue"] = Button(_("Set target"))

		self.list = List([])
		self["config"] = self.list

		self["source_text"] = Label(_("Source bouquet:"))
		self["target_text"] = Label(_("Target bouquet:"))
		self["source_name"] = Label()
		self["target_name"] = Label()

		self.infotext = _("Select or source or target or source and target bouquets!") + " "
		self.infotext += _("Source select with 'yellow' button, target with 'blue' button. Selection can be cleared with '0'.") + " "
		self.infotext += _("For some operations, a selector on the bouquet is sufficient.") + " "
		self.infotext += _("Use the context 'menu' or 'green' buttons to select operation.") + " "
		self.infotext += _("Button '6' enable/disable moving bouquet with 'preview' and 'next' buttons.")
		self["info"] = Label(self.infotext)

		self.sourceItem = None
		self.targetItem = None

		self.playingRef = self.session.nav.getCurrentlyPlayingServiceOrGroup()

		if cfg.current_bouquet.value == "source":
			self.getSource(currentBouquet)
		elif cfg.current_bouquet.value == "target":
			self.getTarget(currentBouquet)
		else:
			self.currentBouquet = currentBouquet
		self.onLayoutFinish.append(self.getBouquetList)
		if cfg.selector2bouquet.value:
			self.onLayoutFinish.append(self.setSelector)

	def startMoving(self):
		self.edit = not self.edit
		self.idx = self["config"].getIndex()
		self.showPrevNext()
	def showPrevNext(self):
		if self.edit:
			self["h_prev"].show()
			self["h_next"].show()
		else:
			self["h_prev"].hide()
			self["h_next"].hide()
			if self.changes:
				self.updateMovedBouquet()
				self.changes=False
	def moveUp(self):
		if self.edit and self.idx -1 >= 0:
			self.moveDirection(-1)
	def moveDown(self):
		if self.edit and self.idx +1 < self["config"].count():
			self.moveDirection(1)
	def moveDirection(self, direction):
			self["config"].setIndex(self.idx)
			tmp = self["config"].getCurrent()
			self["config"].setIndex(self.idx+direction)
			tmp2 = self["config"].getCurrent()
			self["config"].modifyEntry(self.idx, tmp2)
			self["config"].modifyEntry(self.idx+direction, tmp)
			self.idx+=direction
			self.changes=True

	def exit(self):
		self.Servicelist.servicelist.resetRoot()
		if cfg.on_end.value:
			self.session.nav.playService(self.playingRef)
		self.setDefaultCfg()
		self.close()

	def setDefaultCfg(self):
		config.plugins.refreshbouquet.orbital.value = config.plugins.refreshbouquet.orbital.default
		config.plugins.refreshbouquet.ignore_last_char.value = config.plugins.refreshbouquet.ignore_last_char.default
		config.plugins.refreshbouquet.used_services.value = config.plugins.refreshbouquet.used_services.default

	def showMenu(self):
		buttons = []
		menu = []
		bName =self.getSelectedBouquetName()
		if self.sourceItem or self.targetItem:			# at least one is selected
			if self.sourceItem and self.targetItem:		# both are selected
				if self.sourceItem != self.targetItem:	# source != target
					menu.append((_("Manually replace services"),0))
					menu.append((_("Add selected services to target bouquet"),1))
					menu.append((_("Add selected missing services to target bouquet"),2))
					menu.append((_("Refresh services in target bouquet"),4))
					buttons = ["1","2","3","green"]
				menu.append((_("Move selected services in source bouquet"),5))
				menu.append((_("Remove selected services in source bouquet"),3))
				buttons += ["6","8"]
			else:						# or source or target only
				menu.append((_("Move selected services in bouquet"),5))
				menu.append((_("Remove selected services in bouquet"),3))
				buttons = ["6","8"]
			if self.sourceItem: # rbb for sources only
				menu.append((_("Create '%s.rbb' file") % bName,20))
				buttons += [""]
				#if self.isRbbFile():
				menu.append((_("Create bouquet from rbb file"),21))
				buttons += [""]
				menu.append((_("Create TE file '%s-%s.ini' to '/tmp'") % (socket.gethostname().upper(), bName.replace(' ','_')),30))
				buttons += [""]
		menu.append((_("Create new bouquet"),13))
		buttons += [""]
		if self["config"].getCurrent():
			name = self["config"].getCurrent()[0]
			menu.append((_("Rename bouquet '%s'") % name,14))
			buttons += [""]
		if self["config"].getCurrent():
			name = self["config"].getCurrent()[0]
			menu.append((_("Remove bouquet '%s'") % name,15))
			buttons += ["red"]
		if self.isDeletedBouquet():
			menu.append((_("Manage deleted bouquets"),18))
			buttons += [""]
		menu.append((_("Settings..."),10))
		buttons.append("menu")
		self.session.openWithCallback(self.menuCallback, ChoiceBox, title=_("Select action for bouquet:"), list=menu, keys=["dummy" if key=="" else key for key in buttons])
		self["info"].setText(self.infotext)

	def menuCallback(self, choice):
		if choice is None:
			return
		if choice[1] == 0:
			self.replaceSelectedServicesManually()
		elif choice[1] == 1:
			self.addServices()
		elif choice[1] == 2:
			self.addMissingServices()
		elif choice[1] == 3:
			self.removeServices()
		elif choice[1] == 4:
			self.refreshServices()
		elif choice[1] == 5:
			self.moveServices()
		elif choice[1] == 10:
			self.options()
		elif choice[1] == 13:
			self.newBouquet()
		elif choice[1] == 14:
			self.renameBouquet()
		elif choice[1] == 15:
			self.removeBouquetFromList()
		elif choice[1] == 18:
			self.ManageDeletedBouquets()
		elif choice[1] == 20:
			self.saveRbbBouquet()
		elif choice[1] == 21:
			self.createRbbBouquet()
		elif choice[1] == 30:
			self.saveTEIniFile()
		else:
			self["info"].setText(_("Wrong selection!"))
			return

# set selector to selected bouquet
	def setSelector(self):
		item = self.sourceItem if self.sourceItem else self.targetItem if self.targetItem else self.currentBouquet
		if item:
			index = 0
			for i in self["config"].list:
				if i[0] == item[0]:
					self["config"].setIndex(index)
				index += 1

# clear input
	def clearInput(self, name):
		if name == self["source_name"].getText():
			self.sourceItem = None
			self["source_name"].setText("")
		if name == self["target_name"].getText():
			self.targetItem = None
			self["target_name"].setText("")
		self["info"].setText(self.infotext)

# clear selected inputs
	def clearInputs(self):
		self.sourceItem = None
		self.targetItem = None
		self["source_name"].setText("")
		self["target_name"].setText("")
		self["info"].setText(self.infotext)

# get name for source bouquet
	def getSource(self, currentBouquet=None):
		if currentBouquet is not None: # set current bouquet
			current = currentBouquet
		else:
			current = self["config"].getCurrent()
		self["source_name"].setText(current[0])
		self.sourceItem = current
		self.setBouquetsOrbitalPositionsConfigFilter(self.sourceItem)
# get name for target bouquet
	def getTarget(self, currentBouquet=None):
		if currentBouquet is not None: # set current bouquet
			current = currentBouquet
		else:
			current = self["config"].getCurrent()
		self["target_name"].setText(current[0])
		self.targetItem = current
# get all orbital positions in source bouquet to config for filtering
	def setBouquetsOrbitalPositionsConfigFilter(self, sourceItem):
		def op2human(orb_pos):
			if orb_pos == 0xeeee:
				return _("Terrestrial")
			elif orb_pos == 0xffff:
				return _("Cable")
			if orb_pos > 1800:
				return str((float(3600 - orb_pos)) / 10.0) + _("° W")
			elif orb_pos > 0:
				return str((float(orb_pos)) / 10.0) + _("° E")
			return "unknown"
		positions = []
		new_choices = [("x",_("no"))]
		source = self.getServices(sourceItem[0])
		if not source:
			return
		for service in source:
			if self.isNotService(service[1]):
				continue
			op_hex_str = service[1].split(':')[6][0:-4]
			positions.append(op_hex_str)
		unique_choices = set(positions)
		for op in unique_choices:
			op_txt = op2human(int(op,16)) if op else op
			new_choices.append(("%s" % op ,"%s" % op_txt))
		config.plugins.refreshbouquet.orbital = NoSave(ConfigSelection(default = "x", choices = new_choices))

# call refreshService as replace		
	def refreshServices(self):
		self.actualizeServices()

#
# Replace service-reference for services in target with same name as in source
#
	def actualizeServices(self):
		data = MySelectionList([])
		if self.sourceItem and self.targetItem:
			target = self.getServices(self.targetItem[0])
			source = self.getServices(self.sourceItem[0])
			if not len(target):
				self["info"].setText(_("Target bouquet is empty !"))
				return
			if not len(source):
				self["info"].setText(_("Source bouquet is empty !"))
				return
			setIcon() # icons for selecting must be set before adding to list in compareServices
			(data, length) = self.compareServices(source, target)
			if length:
				self.session.open(refreshBouquetRefreshServices, data, self.targetItem)
			else:
				self.session.open(MessageBox, _("No differences found"), type = MessageBox.TYPE_INFO, timeout = 5)

# looking new service reference for target service - returns service name, old service reference, new service reference and position in target bouquet

	def compareServices(self, source_services, target_services):
		differences = MySelectionList([])
		potencialy_duplicity = []
		i = 0 # index
		length = 0 # found items
		for t in target_services: # bouquet for refresh
			if self.isNotService(t[1]):
				i += 1
				continue
			t_name = self.prepareStr(t[0]).replace(cfg.ignore_last_char.value,'') if cfg.ignore_last_char.value else self.prepareStr(t[0])
			t_splited = t[1].split(':') # split target service_reference
			t_core = ":".join((t_splited[3],t_splited[4],t_splited[5],t_splited[6]))
			if cfg.stype.value: # differences in service type too
				t_core = ":".join((t_splited[2],t_core))
			t_op = t_splited[6][:-4]
			for s in source_services: # source bouquet - with fresh scan - f.eg. created by Fastscan or Last Scanned
				if self.isNotService(s[1]): # skip all non playable
					continue
				s_splited = s[1].split(':') # split service_reference
				s_core = ":".join((s_splited[3],s_splited[4],s_splited[5],s_splited[6]))
				if cfg.stype.value: # differences in service type too
					s_core = ":".join((s_splited[2],s_core))
				if cfg.orbital.value != "x": # only on selected op
					if s_splited[6][:-4] != cfg.orbital.value:
						continue
				if t_name == self.prepareStr(s[0]): # found services with equal name
					s_splited = s[1].split(':') # split ref
					if t_op == s_splited[6][:-4]: # same orbital position only
						if t_core != s_core and not t_splited[10] and not s_splited[10]: # is different ref ([3]-[6])and is not stream
							length += 1
							select = True
							try:
								tmp = potencialy_duplicity.index(self.charsOnly(s[0])) # same services_name in source = could be duplicity ... set in list as unselected
								if cfg.debug.value:
									debug("Founded: %s" % self.charsOnly(s[0]))
								select = False
							except:
								if cfg.debug.value:
									debug("Unique: %s" % self.charsOnly(s[0]))
							# name, [new ref, old ref], index, selected
							differences.list.append(MySelectionEntryComponent(s[0], [s[1], t[1]], i, select))
							if cfg.debug.value:
								debug("Added: %s" % self.charsOnly(s[0]))
						potencialy_duplicity.append(self.charsOnly(s[0])) # add to list for next check duplicity
			i += 1
			self.l = MySelectionList(differences)
			self.l.setList(differences)
		return differences, length
###
# Add missing services to source bouquet or all services to empty bouquet
###
	def addMissingServices(self):
		data = MySelectionList([])
		if self.sourceItem and self.targetItem:
			target = self.getServices(self.targetItem[0])
			source = self.getServices(self.sourceItem[0])
			if not len(source):
				self["info"].setText(_("Source bouquet is empty !"))
				return
			new = []
			if len(target):
				# fill target bouquet with missing services from source
				new = self.getMissingSourceServices(source, target)
			else:
				# fill empty target with or TV or Radio source services
				new = self.addToBouquetFiltered(source)
			if not len(new):
				self["info"].setText(_("No services in source bouquet or no differences in bouquets!"))
				return
			nr = 0
			if cfg.debug.value:
				debug(">>> New <<<")
			for i in new:
				nr +=1
				if cfg.debug.value:
					debug("nr:\t%s %s\t\t%s" % (nr, i[0],i[1]))
				# service name, service reference, index, selected
				data.list.append(MySelectionEntryComponent(i[0], i[1], nr, False))
			self.l = MySelectionList(data)
			self.l.setList(data)
			self.session.open(refreshBouquetCopyServices, data, self.targetItem, missing=True, parent=self.session.current_dialog)

# returns source services not existing in target service (filtered)

	def getMissingSourceServices(self, source, target):
		mode = config.servicelist.lastmode.value
		differences = []
		for s in source: # services in source bouquet
			if self.isNotService(s[1]):
				if cfg.debug.value:
					debug("Drop: %s %s" % (s[0], s[1]))
				continue
			if cfg.used_services.value != "all":
				if cfg.used_services.value is "HD4K":
					if not self.isHDinName(s[0]) and not self.isUHDinName(s[0]):
						if cfg.debug.value:
							debug("Drop (SD): %s %s" % (s[0], s[1]))
						continue
				elif cfg.used_services.value == "HD":
					if not self.isHDinName(s[0]):
						if cfg.debug.value:
							debug("Drop (not HD): %s %s" % (s[0], s[1]))
						continue
				elif cfg.used_services.value == "4K":
					if not self.isUHDinName(s[0]):
						if cfg.debug.value:
							debug("Drop (not UHD): %s %s" % (s[0], s[1]))
						continue
			if cfg.orbital.value != "x":
				if s[1].split(':')[6][:-4] != cfg.orbital.value:
					continue
			add = 1
			for t in target: # services in target bouquet
				if self.isNotService(t[1]):
					if cfg.debug.value:
						debug("Drop: %s %s" % (t[0], t[1]))
					continue
				if self.prepareStr(s[0]) == self.prepareStr(t[0]): # service exist in target (test by service name)
					if cfg.debug.value:
						debug("Drop: %s %s" % (s[0], t[0]))
					add = 0
					break
			if add:
				s_splited = s[1].split(':') # split ref
				t_splited = t[1].split(':') # split ref
				if t_splited[10] == '' and s_splited[10] == '': # it is not stream
					if mode == "tv":
						if int(s_splited[2],16) in TV:
							differences.append((s[0], s[1]))
					else:
						if int(s_splited[2],16) in RADIO:
							differences.append((s[0], s[1]))
				else:
					if cfg.debug.value:
						debug("Dropped stream: %s %s" % (s[0], s[1]))
		return differences

###
# close moveServices or call again moveServices
###
	def moveServicesCallback(self, close, answer):
		if not close or not answer:
			self.moveServices()

# get transponder parameter
	def getTransponderInfo(self, service_reference, parameter):
		ref = ServiceReference(service_reference).ref
		transponder_info = eServiceCenter.getInstance().info(ref).getInfoObject(ref, iServiceInformation.sTransponderData)
		return transponder_info[parameter]

# get transponder freq
	def getTransponderFreq(self, ref):
		ref = eServiceReference(ref)
		info = eServiceCenter.getInstance().info(ref)
		transponderraw = info.getInfoObject(ref, iServiceInformation.sTransponderData)
		transponderdata = ConvertToHumanReadable(transponderraw)
		return transponderdata["frequency"]/1000

#
# Test for deleted userbouquet
#
	def isDeletedBouquet(self):
		for x in os.listdir(E2):
			if x.startswith("userbouquet") and x.endswith(".del"):
				return True
		return False

# call refreshBouquetRemoveBouquets screen

	def ManageDeletedBouquets(self):
		from managebq import refreshBouquetManageDeletedBouquets
		self.session.openWithCallback(self.getBouquetList, refreshBouquetManageDeletedBouquets)

#
# Save BOX_BOUQUET TransEdit ini file to /tmp/BOX-BOUQUET.ini file
#
	def saveTEIniFile(self):
		boxIP = "http://%s:%s" % (GetIPsFromNetworkInterfaces()[0][1], "8001")
		boxName = socket.gethostname().upper()
		bouquet, t1, t2 = self.prepareSingleBouquetOperation()
		if bouquet:
			item = self.getServices(bouquet[0])
			if not len(item):
				self["info"].setText("%s" % t1)
				return
			new = []
			new = self.addToBouquetFiltered(item)
			if not len(new):
				self["info"].setText("s" % t2)
				return
			# fill tmp with services
			num = 1
			tmp = []
			for t in new: # bouquet for save
				if self.isNotService(t[1]):
					continue
				name = self.prepareStr(t[0])
				if name.upper() == '<N/A>':
					continue
				tmp.append(("%s=%s/%s|%s\n" % (num, boxIP, t[1], name.replace('|', '-'))))
				num += 1
			bouqName = bouquet[0].replace(' ','_')
			fileName = "/tmp/%s-%s.ini" % (boxName, bouqName)
			fo = open(filename, "wt")
			# head
			fo.write("[SATTYPE]\n" + "1=6500\n" + "2=%s - %s\n\n" % (boxName, bouquet[0]) + "[DVB]\n")
			# services
			fo.write("0=%s\n" % len(tmp))
			for i in tmp:
				fo.write(i)
			fo.close()
			self.session.open(MessageBox, _("TE file %s.ini was created.") % filename, type = MessageBox.TYPE_INFO, timeout = 3)

#
# Save RefreshBouquetBackup name:orbital_position services parameters in selected bouquet to /etc/enigma2/bouquetname.rbb file
#
	def saveRbbBouquet(self):
		nr = 0
		bouquet, t1, t2 = self.prepareSingleBouquetOperation()
		if bouquet:
			item = self.getServices(bouquet[0])
			if not len(item):
				self["info"].setText("%s" % t1)
				return
			new = []
			new = self.addToBouquetFiltered(item)
			if not len(new):
				self["info"].setText("s" % t2)
				return
			fo = open("%s/%s.rbb" % (E2,bouquet[0]), "wt")
			for t in new: # bouquet for save
				if self.isNotService(t[1]):
					continue
				name = self.prepareStr(t[0])
				if name.upper() == '<N/A>':
					nr += 1
				splited = t[1].split(':') # split target service_reference
				fo.write("%s:%s\n" % (name.replace(':','%3a'), splited[6]))
			fo.close()
			txt = _("File %s.rbb was created.") % bouquet[0]
			text, delay, msgtype = (_("%s\n<N/A> items in source bouquet: %s") % (txt, nr), 8, MessageBox.TYPE_WARNING) if nr else (txt, 3, MessageBox.TYPE_INFO)
			self.session.open(MessageBox, text, type = msgtype, timeout = delay)

#
# Replace service-reference for services in selected RBB bouquet
#

# Test if exist rbb file

	def isRbbFile(self):
		for x in os.listdir(E2):
			if x.endswith(".rbb"):
				return True
		return False

# call screen for selection rbb file

	def createRbbBouquet(self):
		if self.sourceItem: # must be selected source bouquet
			from rbbmanager import refreshBouquetRbbManager
			self.session.openWithCallback(self.fillRbbBouquet, refreshBouquetRbbManager)

# create bouquet as valid source services filled to bouquet created from rbb file

	def fillRbbBouquet(self, rbb_name):
		if not rbb_name:
			return
		def getRbbBouquetContent(path):
			list = []
			fi = open(path, "rt")
			for line in fi:
				list.append((line.replace('\n','')))
			fi.close()
			return list

		if self.addBouquet(rbb_name, None):
			data = MySelectionList([])
			if self.sourceItem:  # must be selected source bouquet (f.eg. lastscanned)
				target = getRbbBouquetContent("%s/%s.rbb" % (E2, rbb_name))
				source = self.getServices(self.sourceItem[0])
				if not len(target):
					self["info"].setText(_("File %s is empty!") % rbb_name)
					return
				if not len(source):
					self["info"].setText(_("Source bouquet is empty!"))
					return
				setIcon() # icons for selecting must be set before adding to list in compareServices
				(data, length) = self.compareRbbServices(source, target, cfg.rbb_dotted.value)
				if length:
					def reloadList(remove=False):
						if remove: # it was canceled by user => remove created empty bouquet
							self.removeBouquetNameRef(self.targetItem)
						else:
							self.getBouquetList()
					self.session.openWithCallback(reloadList, refreshBouquetCopyServices, data, self.targetItem)
				else:
					self.session.open(MessageBox, _("No item in '%s.rbb' file matches item in selected source bouquet!") % rbb_name, type = MessageBox.TYPE_INFO, timeout = 10)
		else:
			self.session.open(MessageBox, _("Bouquet '%s' was not created!"), type = MessageBox.TYPE_ERROR, timeout = 5)

# looking new service reference for target service - returns service name, old service reference, new service reference and position in target bouquet

	def compareRbbServices(self, source_services, target_services, dotted):
		differences = MySelectionList([])
		names = []
		results = []
		potencialy_duplicity = []
		i = 0 # index
		length = 0 # found items
		for target in target_services: # bouquet for refresh
			ts = target.split(':')

			### for rbb with freq
			freq = None
			if len(ts) > 2 and ts[2] != "":
				freq = int(ts[2].strip())
			###

			target_name = self.prepareStr(ts[0]).replace('%3A',':').replace('%3a',':')
			if target_name == '<N/A>':
				target_name = _("unknown")
			target_op = ts[1]
			t_op = target_op[:-4]
			found = False
			for source in source_services: # source bouquet - with fresh scan - f.eg. created by Fastscan or Last Scanned
				if self.isNotService(source[1]): # skip all non playable
					continue
				source_name = self.prepareStr(source[0])

				if target_name[0] != source_name[0]: # basic acceleration
					continue

				source_splited = source[1].split(':') # split service_reference
				s_op = source_splited[6][:-4]
				if cfg.orbital.value != "x": # only on selected op
					if s_op != cfg.orbital.value:
						continue
				if target_name == source_name or dotted and target_name+'.' == source_name: # services with same name founded
					if t_op == s_op: # same orbital position only
						if not source_splited[10]: # if source is not stream
							### for rbb with freq
							same_service = False
							if freq:
								frequency = self.getTransponderInfo(source[1],"frequency")/1000
								if abs(frequency - freq) < 10:
									same_service = True
							###

							length += 1
							select = True
							try:
								tmp = potencialy_duplicity.index(self.charsOnly(source[0])) # same services_name in source = could be duplicity ... set in list as unselected
								if cfg.debug.value:
									debug("Founded: %s" % self.charsOnly(source[0]))
								select = False
							except:
								if cfg.debug.value:
									debug("Unique: %s" % self.charsOnly(source[0]))

							### for rbb with freq
							if freq:
								if same_service:
									select = True
								else:
									select = False
							###

							# name, new ref, index, selected
							results.append((source[0], source[1], i, select))
							names.append(source[0].upper())
							i += 1
							found = True
							if cfg.debug.value:
								debug("Added: %s" % self.charsOnly(source[0]))
						potencialy_duplicity.append(self.charsOnly(source[0])) # add to list for next check duplicity
			if not found:
				target_name = "--- %s" % target_name
				mode = "1" if config.servicelist.lastmode.value == "tv" else "2"
				target_pars= ":".join(("1","0",mode,"0","0","0",target_op,"0","0","0", target_name))
				results.append((target_name, target_pars, i, False))
				names.append(target_name)
				i += 1
		# unique item set as marked
		for i, item in enumerate(names):
			# replace not marked to marked for "unique and founded and not marked"
			if names.count(item) == 1  and "---" not in item and not results[i][3]:
				results[i] = results[i][0:3] + (True,)
		# Copy results to MySelectionList
		for item in results:
			differences.list.append(MySelectionEntryComponent(item[0], item[1], item[2], item[3]))
		self.l = MySelectionList(differences)
		self.l.setList(differences)
		return differences, length

###
# add new bouquet	
###
	def newBouquet(self):
		def runCreate(searchString = None):
			if searchString:
				self.addBouquet(searchString, None)
				self.getBouquetList()
		self.session.openWithCallback(runCreate, VirtualKeyBoard, title = _("Enter new bouquet name"), text = "")

###
# add bouquet with bName
###
	def addBouquet(self, bName, services):
		mode = config.servicelist.lastmode.value
		serviceHandler = eServiceCenter.getInstance()
		bouquet_root = self.getRoot()
		mutableBouquetList = serviceHandler.list(bouquet_root).startEdit()
		if mutableBouquetList:
			name = unicodedata.normalize('NFKD', unicode(bName, 'utf_8', errors='ignore')).encode('ASCII', 'ignore').translate(None, '<>:"/\\|?*() ')
			while os.path.isfile((mode == "tv" and '%s/userbouquet.%s.tv' or '%s/userbouquet.%s.radio') % (E2,name)):
				name = name.rsplit('_', 1)
				name = ('_').join((name[0], len(name) == 2 and name[1].isdigit() and str(int(name[1]) + 1) or '1'))
			new_bouquet_ref = eServiceReference((mode == "tv" and '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.%s.tv" ORDER BY bouquet' or '1:7:2:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.%s.radio" ORDER BY bouquet') % name)
			if not mutableBouquetList.addService(new_bouquet_ref):
				mutableBouquetList.flushChanges()
				eDVBDB.getInstance().reloadBouquets()
				mutableBouquet = serviceHandler.list(new_bouquet_ref).startEdit()
				if mutableBouquet:
					mutableBouquet.setListName(bName)
					if services is not None:
						for service in services:
							if mutableBouquet.addService(eServiceReference(service[1])):
								print "[RefreshBouquet] add", service, "to new bouquet failed"
					mutableBouquet.flushChanges()
				else:
					print "[RefreshBouquet] get mutable list for new created bouquet failed"
					return False
				self.getTarget((bName, new_bouquet_ref))
				return True
			else:
				print "[RefreshBouquet] add", str, "to bouquets failed"
				return False
		else:
			print "[RefreshBouquet] bouquetlist is not editable"
			return False

###
# update moved Bouquet
###
	def updateMovedBouquet(self):
		mode = config.servicelist.lastmode.value
		serviceHandler = eServiceCenter.getInstance()
		bouquet_root = self.getRoot()
		mutableBouquetList = serviceHandler.list(bouquet_root).startEdit()
		if mutableBouquetList:
			name = self["config"].getCurrent()[0]
			cur_ref = self["config"].getCurrent()[1]
			index = self["config"].getIndex()
			if not mutableBouquetList.removeService(cur_ref, False):
				mutableBouquetList.addService(cur_ref)
				mutableBouquetList.moveService(cur_ref, index)
				mutableBouquetList.flushChanges()
				eDVBDB.getInstance().reloadBouquets()
				self.clearInput(name)
				self.getBouquetList()

###
# Rename Bouquet
###
	def renameBouquet(self):
		def renameEntryCallback(name):
			if name:
				mode = config.servicelist.lastmode.value
				serviceHandler = eServiceCenter.getInstance()
				bouquet_root = self.getRoot()
				mutableBouquetList = serviceHandler.list(bouquet_root).startEdit()
				if mutableBouquetList:
					cur_ref = self["config"].getCurrent()[1]
					cur_ref.setName(name)
					index = self["config"].getIndex()
					if not mutableBouquetList.removeService(cur_ref, False):
						mutableBouquetList.addService(cur_ref)
						mutableBouquetList.moveService(cur_ref, index)
						mutableBouquetList.flushChanges()
						eDVBDB.getInstance().reloadBouquets()
						self.clearInput(name)
						self.getBouquetList()
		currname = self["config"].getCurrent()[0]
		if currname:
			self.session.openWithCallback(renameEntryCallback, VirtualKeyBoard, title=_("Please enter new bouquet name"), text=currname)

###
# Remove Bouquet as current item from list
###
	def removeBouquetFromList(self):
		def callbackErase(answer):
			if answer:
				name, cur_ref = self["config"].getCurrent()
				self.removeBouquet(name, cur_ref)
		if self["config"].getCurrent():
			name = self["config"].getCurrent()[0]
			self.session.openWithCallback(callbackErase, MessageBox, _("Are You sure to remove bouquet?") + "\n\n%s" % name, type=MessageBox.TYPE_YESNO, default=False)

###
# Remove Bouquet as (name , cur_ref)
###
	def removeBouquetNameRef(self, target):
		name, cur_ref = target
		self.removeBouquet(name, cur_ref)

###
# Remove Bouquet
###
	def removeBouquet(self, name, cur_ref):
		if name and cur_ref:
			mode = config.servicelist.lastmode.value
			serviceHandler = eServiceCenter.getInstance()
			bouquet_root = self.getRoot()
			mutableBouquetList = serviceHandler.list(bouquet_root).startEdit()
			if mutableBouquetList:
				if not mutableBouquetList.removeService(cur_ref, False):
					mutableBouquetList.flushChanges()
					eDVBDB.getInstance().reloadBouquets()
					self.clearInput(name)
					self.getBouquetList()

###
# Prepare bouquet and text for operation with one bouquet (moveServices, removeServices)
###
	def prepareSingleBouquetOperation(self):
		if self.sourceItem and not self.targetItem or self.sourceItem:
			Bouquet = self.sourceItem
			t1 = _("Source bouquet is empty!")
			t2 = _("No services in source bouquet!")
			return self.sourceItem, t1, t2
		elif self.targetItem and not self.sourceItem:
			Bouquet = self.targetItem
			t1 = _("Target bouquet is empty!")
			t2 = _("No services in target bouquet!")
			return self.targetItem, t1, t2
		return None, None, None

###
# get selected bouquet valid for operation: or source, or target or source if both are selected
###
	def getSelectedBouquetName(self):
		bouquet, t1, t2 = self.prepareSingleBouquetOperation()
		if bouquet:
			return bouquet[0]
		return None
###
# move selected service (by user) in source bouquet
###
	def moveServices(self):
		data = MySelectionList([])
		bouquet, t1, t2 = self.prepareSingleBouquetOperation()
		if bouquet:
			item = self.getServices(bouquet[0])
			if not len(item):
				self["info"].setText("%s" % t1)
				return
			new = []
			new = self.addToBouquetFiltered(item)
			if not len(new):
				self["info"].setText("s" % t2)
				return
			nr = 0
			if cfg.debug.value:
				debug(">>> Read bouquet <<<")
			for i in new:
				nr +=1
				if cfg.debug.value:
					debug("nr: %s %s\t\t%s" % (nr, i[0],i[1]))
				# service name, service reference, index, selected
				data.list.append(MySelectionEntryComponent(i[0], i[1], nr, False))
			self.l = MySelectionList(data)
			self.l.setList(data)
			self.session.openWithCallback(boundFunction(self.moveServicesCallback, self.close), refreshBouquetMoveServices, data, bouquet, new)

###
# remove selected service (by user) in source bouquet
###
	def removeServices(self):
		data = MySelectionList([])
		bouquet, t1, t2 = self.prepareSingleBouquetOperation()
		if bouquet:
			item = self.getServices(bouquet[0])
			if not len(item):
				self["info"].setText("%s" % t1)
				return
			new = []
			new = self.addToBouquetFiltered(item)
			if not len(new):
				self["info"].setText("%s" % t1)
				return
			nr = 0
			if cfg.debug.value:
				debug(">>> Read bouquet <<<")
			for i in new:
				nr +=1
				if cfg.debug.value:
					debug("nr: %s %s\t\t%s" % (nr, i[0],i[1]))
				# service name, service reference, index, selected
				data.list.append(MySelectionEntryComponent(i[0], i[1], nr, False))
			self.l = MySelectionList(data)
			self.l.setList(data)
			self.session.open(refreshBouquetRemoveServices, data, bouquet)

###
# replace service in target manually by user (all sources)
###
	def replaceSelectedServicesManually(self): 
		if self.sourceItem and self.targetItem:
			target = self.getServices(self.targetItem[0])
			source = self.getServices(self.sourceItem[0])
			if not len(target):
				self["info"].setText(_("Target bouquet is empty!"))
				return
			if not len(source):
				self["info"].setText(_("Source bouquet is empty!"))
				return
			source_services = []
			if cfg.diff.value: # only missing services
				source_services = self.getMissingSourceServices(source, target)
			else:
				source_services = self.addToBouquetFiltered(source)
			if not len(source_services):
				self["info"].setText(_("No services in source bouquet!"))
				return
			sourceList = MenuList(source_services) # name, service reference
			target_services = self.addToBouquetAllIndexed(target) # name, service reference, index in bouquet
			self.session.open(refreshBouquetManualSelection, sourceList, target_services, self.sourceItem[0], self.targetItem)

# returns all source services (with marks too) and with true positions in bouquet (target)

	def addToBouquetAllIndexed(self, bouquet):
		# bouquet[0] - name, bouquet[1] - service reference
		mode = config.servicelist.lastmode.value
		new = []
		index = 0
		for s in bouquet: # bouquet
			if self.isNotService(s[1]):
				new.append((s[0], s[1], -1))
				index += 1
				continue
			s_splited = s[1].split(':') # split ref
			if s_splited[10] == '' or s_splited[10].startswith('--- '): # it is not stream
				if mode == "tv":
					if int(s_splited[2],16) in TV:
						new.append((s[0], s[1], index))
						index += 1
				else:
					if int(s_splited[2],16) in RADIO:
						new.append((s[0], s[1], index))
						index += 1
			else:
				if cfg.debug.value:
					debug("Dropped stream 2: %s %s" % (s[0], s[1]))
		return new

# optionaly uppercase or remove control character in servicename ( removed for testing only)

	def prepareStr(self, name):
		if cfg.case_sensitive.value == False:
			name = name.upper()
		if cfg.omit_first.value == True:
			if name[0] < ' ':
				return name[1:]
		return name

# returns name without control code on 1st position, optionaly as uppercase

	def charsOnly(self, name):
		if cfg.case_sensitive.value == False:
			name = name.upper()
		if name[0] < ' ':
			return name[1:]
		return name

###
# Add selected services (by user) to target bouquet
###
	def addServices(self):
		data = MySelectionList([])
		if self.sourceItem and self.targetItem:
			target = self.getServices(self.targetItem[0])
			source = self.getServices(self.sourceItem[0])
			if not len(source):
				self["info"].setText(_("Source bouquet is empty!"))
				return
			new = []
			new = self.addToBouquetFiltered(source)
			if not len(new):
				self["info"].setText(_("No services in source bouquet!"))
				return
			nr = 0
			if cfg.debug.value:
				debug(">>> All <<<")
			for i in new:
				nr +=1
				if cfg.debug.value:
					debug("nr:\t%s %s\t\t%s" % (nr, i[0],i[1]))
				# service name, service reference, index, selected
				data.list.append(MySelectionEntryComponent(i[0], i[1], nr, False))
			self.l = MySelectionList(data)
			self.l.setList(data)
			self.session.open(refreshBouquetCopyServices, data, self.targetItem)

# returns all services from bouquet (without notes atc ...)

	def addToBouquetFiltered(self, source):
		# source[0] - name, source[1] - service reference
		mode = config.servicelist.lastmode.value
		new = []
		for s in source: # source bouquet
			if self.isNotService(s[1]):
				if cfg.debug.value:
					debug("Drop: %s %s" % (s[0], s[1]))
				continue
			if cfg.used_services.value != "all":
				if cfg.used_services.value is "HD4K":
					if not self.isHDinName(s[0]) and not self.isUHDinName(s[0]):
						if cfg.debug.value:
							debug("Drop (SD): %s %s" % (s[0], s[1]))
						continue
				elif cfg.used_services.value == "HD":
					if not self.isHDinName(s[0]):
						if cfg.debug.value:
							debug("Drop (not HD): %s %s" % (s[0], s[1]))
						continue
				elif cfg.used_services.value == "4K":
					if not self.isUHDinName(s[0]):
						if cfg.debug.value:
							debug("Drop (not UHD): %s %s" % (s[0], s[1]))
						continue
			s_splited = s[1].split(':') # split ref
			if cfg.orbital.value != "x":
				if s_splited[6][:-4] != cfg.orbital.value:
					continue
			if s_splited[10] == '' or s_splited[10].startswith('--- '): # it is not stream
				if mode == "tv":
					if int(s_splited[2],16) in TV:
						new.append((s[0], s[1]))
				else:
					if int(s_splited[2],16) in RADIO:
						new.append((s[0], s[1]))
			else:
				if cfg.debug.value:
					debug("Dropped stream 3: %s %s" % (s[0], s[1]))
		return new

# test for "noplayable" service

	def isNotService(self, refstr):
		if eServiceReference(refstr).flags & (eServiceReference.isDirectory | eServiceReference.isMarker | eServiceReference.isGroup | eServiceReference.isNumberedMarker):
			return True
		return False

# test for 'HD' in service name

	def isHDinName(self, name):
		if name.find('HD') != -1 and name.find('UHD') == -1: # do not take 'UHD'
			return True
		return False

# test for 'UHD' in service name

	def isUHDinName(self, name):
		if name.find('4K') != -1 or name.find('4k') != -1 or name.find('UHD') != -1 or name.find('uhd') != -1:
			return True
		return False

#
	def getRoot(self):
		from Screens.ChannelSelection import service_types_tv, service_types_radio

		if config.servicelist.lastmode.value == "tv":
			service_types = service_types_tv
			if config.usage.multibouquet.value:
				bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.tv" ORDER BY bouquet'
			else:
				bouquet_rootstr = '%s FROM BOUQUET "userbouquet.favourites.tv" ORDER BY bouquet'%(service_types)
		else:
			service_types = service_types_radio
			if config.usage.multibouquet.value:
				bouquet_rootstr = '1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "bouquets.radio" ORDER BY bouquet'
			else:
				bouquet_rootstr = '%s FROM BOUQUET "userbouquet.favourites.radio" ORDER BY bouquet'%(service_types)
		self.bouquet_rootstr = bouquet_rootstr
		self.bouquet_root = eServiceReference(self.bouquet_rootstr)
		bouquet_root = eServiceReference(bouquet_rootstr)	
		return bouquet_root

# returns bouquets list

	def getBouquetList(self):
		bouquet_root = self.getRoot()
		serviceHandler = eServiceCenter.getInstance()
		bouquets = []
		if config.usage.multibouquet.value:
			list = serviceHandler.list(bouquet_root)
			if list:
				while True:
					bouquet = list.getNext()
					if not bouquet.valid():
						break
					if bouquet.flags & eServiceReference.isDirectory and not bouquet.flags & eServiceReference.isInvisible:
						info = serviceHandler.info(bouquet)
						if info:
							#print ">>> ", info.getName(bouquet), bouquet
							bouquets.append((info.getName(bouquet), bouquet))
				self["config"].setList(bouquets)
				return bouquets
			return None
		else:
			info = serviceHandler.info(bouquet_root)
			if info:
				bouquets.append((info.getName(bouquet_root), bouquet_root))
				self['config'].setList(bouquets)
				return bouquets
			return None

# returns bouquet by name

	def getBouquet(self, name):
		bouquet_root = self.getRoot()
		serviceHandler = eServiceCenter.getInstance()
		if config.usage.multibouquet.value:
			list = serviceHandler.list(bouquet_root)
			if list:
				while True:
					bouquet = list.getNext()
					if not bouquet.valid():
						break
					if bouquet.flags & eServiceReference.isDirectory and not bouquet.flags & eServiceReference.isInvisible:
						info = serviceHandler.info(bouquet)
						if info:
							if info.getName(bouquet) == name:
								return bouquet
			return None
		else:
			info = serviceHandler.info(bouquet_root)
			if info:
				return bouquet_root
				#bouquets.append((info.getName(bouquet_root), bouquet_root))
			return None

# returns services in bouquet Name,Service reference

	def getServices(self, bouquet_name):
		bouquet = self.getBouquet(bouquet_name)
		if bouquet is None:
			return ""
		serviceHandler = eServiceCenter.getInstance()
		list = serviceHandler.list(bouquet)
		services = list.getContent("NS", False)
		if list:
#			for service in services:
#				print ">>>>>>", service[0], "\t\t", service[1]
			return services

# call Options

	def options(self):
		self.session.openWithCallback(self.afterConfig, refreshBouquetCfg)

# callBack for Config

	def afterConfig(self, data=None):
		self.showMenu()

# manual replace
class refreshBouquetManualSelection(Screen):
	y = 25 * 4 if getDesktop(0).size().height() > 576 else 0 # added 4 bouquet's rows if screen height > 576
	pars = (511+y,250+y,250+y,343+y,347+y,370+y,375+y,398+y,492+y,373+y)
	skin = """
	<screen name="refreshBouquetManualSelection" position="center,center" size="700,%d" title="RefreshBouquet - manual">
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on"/>
		<widget objectTypes="key_green,StaticText" source="key_green" render="Pixmap"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on">
			<convert type="ConditionalShowHide"/>
		</widget>
		<widget objectTypes="key_yellow,StaticText" source="key_yellow" render="Pixmap" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on">
			<convert type="ConditionalShowHide"/>
		</widget>
		<widget objectTypes="key_blue,StaticText" source="key_blue" render="Pixmap" position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on">
			<convert type="ConditionalShowHide"/>
		</widget>
		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget objectTypes="key_green,StaticText" source="key_green" render="Label" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget objectTypes="key_yellow,StaticText" source="key_yellow" render="Label" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget objectTypes="key_blue,StaticText" source="key_blue" render="Label" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="source" position="5,40" zPosition="2" size="345,28"  font="Regular;25" foregroundColor="white"/>
		<widget name="target" position="360,40" zPosition="2" size="345,28"  font="Regular;25" foregroundColor="white"/>
		<widget name="source_label" position="5,68" zPosition="2" size="345,25"  font="Regular;18" foregroundColor="yellow"/>
		<widget name="target_label" position="360,68" zPosition="2" size="345,25"  font="Regular;18" foregroundColor="blue"/>

		<widget name="sources" position="3,90" zPosition="2" size="345,%d"  font="Regular;22" foregroundColor="white"/>
		<widget name="targets" position="360,90" zPosition="2" size="345,%d"  font="Regular;22" foregroundColor="white"/>
		<ePixmap pixmap="skin_default/div-h.png" position="5,%d" zPosition="2" size="690,2"/>
		<widget source="TransponderInfo" render="Label" position="5,%d" size="690,23" font="Regular;20" valign="center" halign="left" transparent="1" zPosition="1">
			<convert type="TransponderInfo"></convert>
		</widget>
		<ePixmap pixmap="skin_default/div-h.png" position="5,%d" zPosition="2" size="690,2"/>
		<widget source="Service" render="Label" position="5,%d" zPosition="1" size="690,18" font="Regular;18" foregroundColor="yellow" noWrap="1">
			<convert type="ServiceName">Name</convert>
		</widget>
		<widget source="Service" render="Label" position="5,%d" zPosition="1" size="690,90" font="Regular;18" foregroundColor="#00c0c0c0">
			<convert type="EventName">FullDescription</convert>
		</widget>
		<widget source="Service" render="NextEpgInfo" position="5,%d" size="690,18" transparent="1" foregroundColor="yellow" noWrap="1" font="Regular;18"/>
		<widget name="info" position="5,%d" zPosition="2" size="690,138" valign="center" halign="left" font="Regular;20" foregroundColor="#00c0c0c0"/>
	</screen>""" % pars

	def __init__(self, session, sourceList, target_services, source_name, target):
		self.skin = refreshBouquetManualSelection.skin
		Screen.__init__(self, session)
	
		self["Service"] = ServiceEvent()
		self["TransponderInfo"] = ServiceEvent()
		self.display_epg = False

		self.setTitle(_("RefreshBouquet %s" % _("- select service for replace with OK")))
		self.session = session

		( self.target_bouquetname, self.target ) = target

		self.listSource = sourceList
		self["sources"] = self.listSource

		self.origList = sourceList.list[:]

		self.target_services = target_services

		self.listTarget = MenuList(self.target_services)
		self["targets"] = self.listTarget

		self["source"] = Label()
		self["target"] = Label()
		self["info"] = Label()
		self["source_label"] = Label()
		self["target_label"] = Label()

		self["refreshbouquetmanualselectionactions"] = ActionMap(["OkCancelActions", "RefreshBouquetActions", "DirectionActions"],
			{
				"cancel": self.exit,
				"ok": self.ok,
				"red": self.exit,
				"green": self.replaceService,
				"yellow": self.previewService,
				"blue": self.keyBlue,

				"play": self.previewService,
				"stop":	self.stopPreview,

				"prevBouquet": self.switchLists,
				"nextBouquet": self.switchLists,
	
				"up": self.up,
				"upRepeated": self.up,
				"down": self.down,
				"downRepeated": self.down,
	
				"left": self.left,
				"leftRepeated": self.left,
				"right": self.right,
				"rightRepeated": self.right,

				"clearInputs": self.clearInputs,
				"menu": self.sortMenu,
				"next": self.lookServiceInSource,
				"prev": self.lookServiceInSource,

				"epg": self.displayEPG,
			},-2)

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = StaticText("")
		self["key_yellow"] = StaticText("")
		self["key_blue"] = StaticText("")

		name_s = " " + addBouqetName(source_name)
		name_t = " " + addBouqetName(self.target_bouquetname)
		self["source_label"] = Label(_("source bouquet") + name_s )
		self["target_label"] = Label(_("target bouquet") + name_t )

		text =  _("Toggle source and target bouquets with Bouq +/- .") + " "
		text += _("Or toggle with 'Prev/Next', which trying to find a similar name in source.") + " "
		text += _("Prepare replacement target's service by service in source bouquet (both select with 'OK') and replace it with 'Replace'. Repeat it as you need. Finish all with 'Apply and close'.")+ " "
		text += _("Marking can be canceled with key '0'.") + " "
		text += _("Source can be sorted with 'Menu'.") + " "
		text += _("Epg or Info toggles between EPG and Info text.") + " "
		text += _("'Stop' button stops Preview.")
		self["info"].setText(text)

		self.targetRecord = ""
		self.sourceRecord = ""
		self.currList = "sources"
		self.currLabel = "source"
		self.changedTargetdata = []

		if cfg.debug.value:
			debug("changed bouquet: %s" % self.target_bouquetname)
		self.playingRef = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		self.onLayoutFinish.append(self.switchLists)
		self.sortSourceList()

	def sortMenu(self):
		menu = []
		for x in cfg.mr_sortsource.choices.choices:
			menu.append((x[1], x[0]))
		self.session.openWithCallback(self.sortbyCallback, ChoiceBox, title=_("Sort source bouquet:"), list=menu, selection=int(cfg.mr_sortsource.value))

	def sortbyCallback(self, choice):
		if choice is None:
			return
		config.plugins.refreshbouquet.mr_sortsource.value = choice[1]
		config.plugins.refreshbouquet.mr_sortsource.save()
		self.sortSourceList()

	def sortSourceList(self):
		name = self["sources"].getCurrent()[0]
		if cfg.mr_sortsource.value == "1":
			self.listSource.list.sort()
		elif cfg.mr_sortsource.value == "2":
			self.listSource.list.sort(reverse=True)
		else:
			self.listSource.setList(self.origList[:])
		self["sources"].moveToIndex(self.getSourceIndex(name))

	def ok(self): # get source and target items
		if self.currList == "targets":
			index = self["targets"].getCurrent()[2]
			if index < 0:
				self["target"].setText("")
				self.targetRecord = ""
			else:
				self["target"].setText(self[self.currList].getCurrent()[0])
				self.targetRecord = self[self.currList].getCurrent()
		else:
			self[self.currLabel].setText(self[self.currList].getCurrent()[0])
			self.sourceRecord = self[self.currList].getCurrent()
		if self.targetRecord != "" and self.sourceRecord != "":
			self["key_blue"].setText(_("Replace"))
		if cfg.autotoggle.value:
			self.switchLists()

	def getSourceIndex(self,name):
		for idx, source in enumerate(self["sources"].list):
			if source[0] == name:
				return idx
		return 0
	def getSourceIndexUpper(self,name):
		name = name.upper()
		for idx, source in enumerate(self["sources"].list):
			if source[0].upper() == name:
				return idx
		return 0
	def getSourceSimilarIndexUpper(self,name):
		uName = name.upper().replace(' ','')
		for n in range(len(uName),0,-1):
			for idx, source in enumerate(self["sources"].list):
				sName = source[0].upper().replace(' ','')
				if uName[0] != sName[0]:
					continue
				if sName.startswith(uName[:n]):
					return idx
		return 0

	def lookServiceInSource(self):
		if self.currList == "targets":
			name = self["targets"].getCurrent()[0]
			idx = self.getSourceIndex(name)
			if not idx:
				idx = self.getSourceIndexUpper(name)
				if not idx:
					idx = self.getSourceSimilarIndexUpper(name)
			self["sources"].moveToIndex(idx)
		self.switchLists()

	def keyBlue(self):
		if self.targetRecord != "" and self.sourceRecord != "":
			self.replaceTarget()

	def replaceTarget(self):
		if self.targetRecord != "" and self.sourceRecord != "":
#		insert(index, hodnota)
#		remove(hodnota)
#		del list[index]
			position = self.target_services.index(self.targetRecord)
			del self.target_services[position]
								# new name, new ref, index replaced service in target bouquet
			self.target_services.insert(position, (self.sourceRecord[0], self.sourceRecord[1], self.targetRecord[2]))
							# new name, new ref, old ref, index replaced service in target bouquet, old name 
			self.changedTargetdata.append((self.sourceRecord[0], self.targetRecord[1], self.sourceRecord[1], self.targetRecord[2], self.targetRecord[0]))
			if self.currList == "sources": # only for refresh
				self.switchToTargetList()
			else:
				self.switchToSourceList() # trick - must be both lines
				self.switchToTargetList()
			self.clearInputs()
			self["key_green"].setText(_("Apply and close"))

	def displayService(self):
		ref = self[self.currList].getCurrent()[1]
		if not self.isNotService(ref):
			self["TransponderInfo"].newService(eServiceReference(ref))
			if self.display_epg:
				self["Service"].newService(eServiceReference(ref))
				self["info"].hide()
			else:
				self["Service"].newService(None)
				self["info"].show()

			if cfg.preview.value:
				self.previewService()
			else:
				self["key_yellow"].setText(_("Preview"))
		else:
			self["key_yellow"].setText("")
			self["Service"].newService(None)
			self["TransponderInfo"].newService(None)

	def previewService(self):
		ref = self[self.currList].getCurrent()[1]
		if not self.isNotService(ref):
			self.session.nav.playService(eServiceReference(ref))
	def stopPreview(self):
		self.session.nav.playService(self.playingRef)

	def displayEPG(self):
		self.display_epg = not self.display_epg
		self.displayService()

	def clearInputs(self):
		self.targetRecord = ""
		self.sourceRecord = ""
		self["target"].setText("")
		self["source"].setText("")
		self["key_blue"].setText("")
	
	def switchLists(self):
		if self.currList == "sources":
			self.switchToTargetList()
			return
		self.switchToSourceList()

	def switchToSourceList(self):
		self.currList = "sources"
		self.currLabel = "source"
		self.listTarget.selectionEnabled(0)
		self.listSource.selectionEnabled(1)
		self.displayService()

	def switchToTargetList(self):
		self.currList = "targets"
		self.currLabel = "target"
		self.listSource.selectionEnabled(0)
		self.listTarget.selectionEnabled(1)
		self.displayService()

	def up(self):
		self[self.currList].up()
		self.displayService()

	def down(self):
		self[self.currList].down()
		self.displayService()

	def left(self):
		self[self.currList].pageUp()
		self.displayService()

	def right(self):
		self[self.currList].pageDown()
		self.displayService()

	def replaceService(self):
		nr_items = len(self.changedTargetdata)
		if nr_items:
			text = ngettext("Are you sure to apply %d change and close?" ,"Are you sure to apply all %d changes and close?", nr_items) % nr_items
			self.session.openWithCallback(self.replaceTargetBouquet, MessageBox, text, MessageBox.TYPE_YESNO, default=False )
		else:
			self.session.open(MessageBox, _("Nothing for processing..."), MessageBox.TYPE_INFO, timeout=3 )

	def replaceTargetBouquet(self, answer): # self.target_services: [0] - new name, [1] - old ref, [2] - new ref, [3] - index,
		if answer == True:
			if cfg.log.value:
				fo = open("/var/log/replaced.log", "a")
				fo.write("new name|old ref| replaced by |new name|new ref| at |index\n")
			for data in self.changedTargetdata:
				index = data[3]
				old = eServiceReference(data[1])
				new = eServiceReference(data[2])
				if cfg.case_sensitive.value == False: # trick for changing name - it cannot be made in one step, imho
					old.setName(data[0])
				serviceHandler = eServiceCenter.getInstance()
				list = self.target and serviceHandler.list(self.target)
				if list is not None:
					mutableList = list.startEdit()
					if mutableList:
						if cfg.case_sensitive.value == False: # trick for changing name - it cannot be made in one step
							mutableList.removeService(old, False)
							mutableList.addService(old)
							mutableList.moveService(old, index)
							mutableList.flushChanges()
						mutableList.removeService(old, False)
						mutableList.addService(new)
						mutableList.moveService(new, index)
						mutableList.flushChanges()
						if cfg.log.value:
							fo.write("%s|%s| replaced with |%s|%s| at |%s\n" % (data[4],data[1],data[0],data[2],data[3]+1))
			if cfg.log.value:
				fo.close()
			self.close()
		return

	def isNotService(self, refstr):
		if eServiceReference(refstr).flags & (eServiceReference.isDirectory | eServiceReference.isMarker | eServiceReference.isGroup | eServiceReference.isNumberedMarker):
			return True
		return False

	def exit(self):
		nr_items = len(self.changedTargetdata)
		if nr_items:
			text = ngettext("Are you sure to close and lost %d change?", "Are you sure to close and lost all %d changes?", nr_items) % nr_items
			self.session.openWithCallback(self.callBackExit, MessageBox, text, MessageBox.TYPE_YESNO, default=False )
		else:
			self.close()

	def callBackExit(self, answer):
		if answer == True:
			self.close()

# display and refresh services with different service references
class refreshBouquetRefreshServices(Screen):
	def __init__(self, session, list, target):
		self.skin = refreshBouquetCopyServices.skin
		Screen.__init__(self, session)
		self.skinName = ["refreshBouquetRefreshServices", "refreshBouquetCopyServices"]

		( self.target_bouquetname, self.target ) = target

		name = addBouqetName(self.target_bouquetname) + " "
		self.texttitle = _("RefreshBouquet %s") % name + _("- results")
		self.setTitle(self.texttitle)

		self["Service"] = ServiceEvent()
		self["TransponderInfo"] = ServiceEvent()
		self.display_epg = False

		self.list = list
		self["services"] = self.list
		self.sortList()

		self["actions"] = ActionMap(["OkCancelActions", "RefreshBouquetActions"],
			{
				"cancel": self.exit,
				"red": self.exit,
				"ok": self.list.toggleSelection,
				"green": self.replaceSelectedEntries,
				"yellow": self.previewService,
				"blue": self.list.toggleAllSelection,

				"play": self.previewService,
				"stop": self.stopPreview,
				"menu": self.sortMenu,

				"epg": self.displayEPG,
			})

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Refresh selected"))
		self["key_yellow"] = StaticText("")
		self["key_blue"] = Button(_("Inversion"))

		self["info"] = Label()

		text = _("This feature looking for differences in service parameters with same names in source and target bouquets. Parameters for marked services will be replaced.") + " "
		text += _("It can be in most cases useful for bouquets with services gained by Fastscan searching.") + " "
		text += _("Possible duplicates will not be marked in list. Check validity with 'Preview' before mark and before 'Refresh selected'.") + " "
		text += _("Epg or Info toggles between EPG and Info text.") + " "
		text += _("'Stop' button stops Preview.")
		self["info"].setText(text)

		self.playingRef = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		self.onSelectionChanged = []
		self["services"].onSelectionChanged.append(self.displayService)
		self.onLayoutFinish.append(self.displayService)

	def sortMenu(self):
		menu = []
		for x in cfg.sortmenu.choices.choices:
			menu.append((x[1], x[0]))
		self.session.openWithCallback(self.sortbyCallback, ChoiceBox, title=_("Sort bouquet:"), list=menu, selection=int(cfg.sortmenu.value))

	def sortbyCallback(self, choice):
		if choice is None:
			return
		config.plugins.refreshbouquet.sortmenu.value = choice[1]
		config.plugins.refreshbouquet.sortmenu.save()
		self.sortList()

	def sortList(self):
		if len(self["services"].list):
			item = self["services"].getCurrent()[0]
			sort = int(cfg.sortmenu.value)
			if sort == 0:	#default
				self.list.sort(sortType=2)
			elif sort == 1:	#A-z
				self.list.sort(sortType=0)
			elif sort == 2:	#Z-a
				self.list.sort(sortType=0, flag=True)
			elif sort == 3:	#selected top
				self.list.sort(sortType=3, flag=True)
			elif sort == 4:	#default reversed
				self.list.sort(sortType=2, flag=True)
			idx = self.getItemIndex(item)
			self["services"].moveToIndex(idx)

	def getItemIndex(self, item):
		for idx, service in enumerate(self["services"].list):
			if service[0] == item:
				return idx
		return 0

	def displayService(self):
		if not len(self["services"].list):
			return
		ref = self["services"].getCurrent()[0][1][0]
		index = self["services"].getCurrent()[0][2] + 1
		self.setTitle("%s\t%s: %s" % (self.texttitle, _("Position"), index))
		if not self.isNotService(ref):
			self["TransponderInfo"].newService(eServiceReference(ref))
			if self.display_epg:
				self["Service"].newService(eServiceReference(ref))
				self["info"].hide()
			else:
				self["Service"].newService(None)
				self["info"].show()

			if cfg.preview.value:
				self.previewService()
			else:
				self["key_yellow"].setText(_("Preview"))
		else:
			self["key_yellow"].setText("")
			self["Service"].newService(None)
			self["TransponderInfo"].newService(None)

	def previewService(self):
		ref = self["services"].getCurrent()[0][1][0]
		if not self.isNotService(ref):
			self.session.nav.playService(eServiceReference(ref))
	def stopPreview(self):
		self.session.nav.playService(self.playingRef)

	def displayEPG(self):
		self.display_epg = not self.display_epg
		self.displayService()

	def replaceSelectedEntries(self):
		nr_items = len(self.list.getSelectionsList())
		if nr_items:
			text = ngettext("Are you sure to refresh this %d service?", "Are you sure to refresh this %d services?", nr_items) % nr_items
			self.session.openWithCallback(self.replaceService, MessageBox, text, MessageBox.TYPE_YESNO, default=False )
		else:
			self.session.open(MessageBox, _("Nothing for processing..."), MessageBox.TYPE_INFO, timeout=3 )

	def replaceService(self, answer):
		if answer == True:
			refresh = self.list.getSelectionsList() # data: [0] - name, [1][0] - new ref, [1][1] - old ref, [2] - index,
			serviceHandler = eServiceCenter.getInstance()
			list = self.target and serviceHandler.list(self.target)
			if list is not None:
				for data in refresh:
					mutableList = list.startEdit()
					if mutableList:
						index = data[2]
						old = eServiceReference(data[1][1])
						new = eServiceReference(data[1][0])
						if cfg.debug.value:
							debug("Replace - name: %s new ref: %s old ref: %s index: %s" % (data[0], data[1][0], data[1][1], data[2]))
						if cfg.case_sensitive.value == False: # trick for changing name - it cannot be made in one step
							old.setName(data[0])
							mutableList.removeService(old, False)
							mutableList.addService(old)
							mutableList.moveService(old, index)
							mutableList.flushChanges()
						mutableList.removeService(old, False)
						mutableList.addService(new)
						mutableList.moveService(new, index)
						mutableList.flushChanges()
			self.close()
		return

	def isNotService(self, refstr):
		if eServiceReference(refstr).flags & (eServiceReference.isDirectory | eServiceReference.isMarker | eServiceReference.isGroup | eServiceReference.isNumberedMarker):
			return True
		return False

	def exit(self):
		nr_items = len(self.list.getSelectionsList())
		if nr_items:
			text = ngettext("Are you sure to close and lost %d selection?", "Are you sure to close and lost all %d selections?", nr_items) % nr_items
			self.session.openWithCallback(self.callBackExit, MessageBox, text, MessageBox.TYPE_YESNO, default=False )
		else:
			self.close()

	def callBackExit(self, answer):
		if answer == True:
			self.close()

# copy services from source list
class refreshBouquetCopyServices(Screen):
	skin = """
		<screen name="refreshBouquetDisplayServices" position="center,center" size="710,505" title="RefreshBouquet - results">
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on"/>
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on"/>
		<widget objectTypes="key_yellow,StaticText" source="key_yellow" render="Pixmap" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on">
			<convert type="ConditionalShowHide"/>
		</widget>
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on"/>
		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget objectTypes="key_yellow,StaticText" source="key_yellow" render="Label" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="services" position="5,50" zPosition="2" size="705,300" itemHeight="25" font="Regular;22" foregroundColor="white"/>
		<ePixmap pixmap="skin_default/div-h.png" position="5,351" zPosition="2" size="700,2"/>
		<widget source="TransponderInfo" render="Label" position="5,354" size="700,23" font="Regular;20" valign="center" halign="left" transparent="1" zPosition="1">
			<convert type="TransponderInfo"></convert>
		</widget>
		<ePixmap pixmap="skin_default/div-h.png" position="5,377" zPosition="2" size="700,2"/>
		<widget source="Service" render="Label" position="5,380" zPosition="1" size="705,18" font="Regular;18" foregroundColor="yellow" noWrap="1">
			<convert type="ServiceName">Name</convert>
		</widget>
		<widget source="Service" render="Label" position="5,398" zPosition="1" size="705,90" font="Regular;18" foregroundColor="#00c0c0c0">
			<convert type="EventName">FullDescription</convert>
		</widget>
		<widget source="Service" render="NextEpgInfo" position="5,488" size="705,16" transparent="1" foregroundColor="yellow" noWrap="1" font="Regular;16"/>
		<widget name="info" position="5,380" zPosition="2" size="705,120" valign="center" halign="left" font="Regular;20" foregroundColor="#00c0c0c0"/>
	</screen>"""

	def __init__(self, session, list, target, missing=None, parent=None):
		self.skin = refreshBouquetCopyServices.skin
		Screen.__init__(self, session, parent=None)
		self.session = session
		self.missing = missing
		self.parent = parent

		( self.target_bouquetname, self.target ) = target
		name = addBouqetName(self.target_bouquetname)
		self.setTitle(_("RefreshBouquet %s" % _("- select service(s) for adding with OK")) + name)

		self["Service"] = ServiceEvent()
		self["TransponderInfo"] = ServiceEvent()
		self.display_epg = False

		self["info"] = Label()

		setIcon()

		self.list = list
		self["services"] = self.list
		self.sortList()

		self["actions"] = ActionMap(["OkCancelActions", "RefreshBouquetActions"],
			{
				"cancel": self.exit,
				"ok": self.list.toggleSelection,
				"red": self.exit,
				"green": self.copyCurrentEntries,
				"blue": self.list.toggleAllSelection,
				"yellow": self.previewService,
				"play": self.previewService,
				"stop": self.stopPreview,
				"prevBouquet": boundFunction(self.selectGroup, False),
				"nextBouquet": boundFunction(self.selectGroup, True),
				"menu": self.sortMenu,
				"epg": self.displayEPG,
			})

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Copy selected"))
		self["key_yellow"] = StaticText("")
		self["key_blue"] = Button(_("Inversion"))

		text =_("Mark services with OK button or use group selection (Ch+/Ch-) and then copy these with 'Copy selected'.") + " "
		text += _("Use 'Menu' for sorting.") + " "
		text += _("Epg or Info toggles between EPG and Info text.") + " "
		text += _("'Stop' button stops Preview.")
		self["info"].setText(text)

		self.onSelectionChanged = []
		self["services"].onSelectionChanged.append(self.displayService)
		self.onLayoutFinish.append(self.displayService)

		self.playingRef = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if cfg.debug.value:
			debug("changed bouquet: %s" % self.target_bouquetname)

	def sortMenu(self):
		menu = []
		for x in cfg.sortmenu.choices.choices:
			menu.append((x[1], x[0]))
		self.session.openWithCallback(self.sortbyCallback, ChoiceBox, title=_("Sort bouquet:"), list=menu, selection=int(cfg.sortmenu.value))

	def sortbyCallback(self, choice):
		if choice is None:
			return
		config.plugins.refreshbouquet.sortmenu.value = choice[1]
		config.plugins.refreshbouquet.sortmenu.save()
		self.sortList()

	def sortList(self):
		if len(self["services"].list):
			item = self["services"].getCurrent()[0]
			sort = int(cfg.sortmenu.value)
			if sort == 0:	#default
				self.list.sort(sortType=2)
			elif sort == 1:	#A-z
				self.list.sort(sortType=0)
			elif sort == 2:	#Z-a
				self.list.sort(sortType=0, flag=True)
			elif sort == 3:	#selected top
				self.list.sort(sortType=3, flag=True)
			elif sort == 4:	#default reversed
				self.list.sort(sortType=2, flag=True)
			idx = self.getItemIndex(item)
			self["services"].moveToIndex(idx)

	def getItemIndex(self, item):
		for idx, service in enumerate(self["services"].list):
			if service[0] == item:
				return idx
		return 0

	def displayService(self):
		ref = self["services"].getCurrent()[0][1]
		if not self.isNotService(ref):
			self["TransponderInfo"].newService(eServiceReference(ref))
			if self.display_epg:
				self["Service"].newService(eServiceReference(ref))
				self["info"].hide()
			else:
				self["Service"].newService(None)
				self["info"].show()
			if cfg.preview.value:
				self.previewService()
			else:
				self["key_yellow"].setText(_("Preview"))
		else:
			self["key_yellow"].setText("")
			self["Service"].newService(None)
			self["TransponderInfo"].newService(None)

	def previewService(self):
		ref = self["services"].getCurrent()[0][1]
		if not self.isNotService(ref):
			self.session.nav.playService(eServiceReference(ref))
	def stopPreview(self):
		self.session.nav.playService(self.playingRef)

	def displayEPG(self):
		self.display_epg = not self.display_epg
		self.displayService()

	def selectGroup(self, mark=True):
		if mark:
			txt = _("Add to selection (starts with...)")
		else:
			txt = _("Remove from selection (starts with...)")
		item = self["services"].getCurrent()
		length = int(cfg.vk_length.value)
		name = ""
		if item and length:
			name = item[0][0].decode('UTF-8', 'replace')[0:length]
			txt += "\t%s" % length
		self.session.openWithCallback(boundFunction(self.changeItems, mark), VirtualKeyBoard, title = txt, text = name)

	def changeItems(self, mark, searchString = None):
		if searchString:
			searchString = searchString.decode('UTF-8', 'replace')
			if not cfg.vk_sensitive.value:
				searchString = searchString.lower()
			for item in self.list.list:
				if cfg.vk_sensitive.value:
					exist = item[0][0].decode('UTF-8', 'replace').startswith(searchString)
				else:
					exist = item[0][0].decode('UTF-8', 'replace').lower().startswith(searchString)
				if exist:
					if mark:
						if not item[0][3]:
							self.list.toggleItemSelection(item[0])
					else:
						if item[0][3]:
							self.list.toggleItemSelection(item[0])

	def copyCurrentEntries(self):
		nr_items = len(self.list.getSelectionsList())
		if nr_items:
			text = ngettext("Are you sure to copy this %d service?", "Are you sure to copy this %d services?", nr_items) % nr_items
			list = [(_("Yes"), True), (_("No"), False)]
			if self.missing: # for 'Add selected missing services to target bouquet' only 
				list.append((_("Yes, add to new bouquet..."), "new"))
			self.session.openWithCallback(self.copyToTarget, MessageBox, text, MessageBox.TYPE_YESNO, default=False, list=list )
		else:
			self.session.open(MessageBox, _("Nothing for processing..."), MessageBox.TYPE_INFO, timeout=3 )

	def copyToTarget(self, answer):
		if answer == True:
			data = self.list.getSelectionsList()
			serviceHandler = eServiceCenter.getInstance()
			list = self.target and serviceHandler.list(self.target)
			if list is not None:
				mutableList = list.startEdit()
				if mutableList:
					for item in data:
						new = eServiceReference(item[1])
						if not mutableList.addService(new):
							mutableList.flushChanges()
			self.close()
		elif answer == "new":
			def runCreate(searchString = None):
				if not searchString:
					self.session.open(MessageBox, _("You did not enter the bouquet name!"), MessageBox.TYPE_WARNING, timeout=3 )
					return
				services = self.list.getSelectionsList()
				self.parent.addBouquet(searchString, services)
				self.parent.getBouquetList()
				self.close()
			self.session.openWithCallback(runCreate, VirtualKeyBoard, title = _("Enter new bouquet name"), text = "")
		return

	def isNotService(self, refstr):
		if eServiceReference(refstr).flags & (eServiceReference.isDirectory | eServiceReference.isMarker | eServiceReference.isGroup | eServiceReference.isNumberedMarker):
			return True
		return False

	def exit(self):
		nr_items = len(self.list.getSelectionsList())
		if nr_items:
			text = ngettext("Are you sure to close and lost %d selection?", "Are you sure to close and lost all %d selections?", nr_items) % nr_items
			self.session.openWithCallback(self.callBackExit, MessageBox, text, MessageBox.TYPE_YESNO, default=False )
		else:
			self.close()

	def callBackExit(self, answer):
		if answer == True:
			self.close(True) # True = remove empty bouquet

# remove services from source list
class refreshBouquetRemoveServices(Screen):
	def __init__(self, session, list, source):
		self.skin = refreshBouquetCopyServices.skin
		Screen.__init__(self, session)
		self.session = session
		self.skinName = ["refreshBouquetRemoveServices", "refreshBouquetCopyServices"]

		( self.source_bouquetname, self.source ) = source
		name = addBouqetName(self.source_bouquetname)
		self.setTitle(_("RefreshBouquet %s" % _("- select service(s) for remove with OK")) + name)

		setIcon(True)

		self.list = list
		self["services"] = self.list
		self.sortList()

		self["Service"] = ServiceEvent()
		self["TransponderInfo"] = ServiceEvent()
		self.display_epg = False

		self["info"] = Label()

		self["actions"] = ActionMap(["OkCancelActions", "RefreshBouquetActions"],
			{
				"cancel": self.exit,
				"ok": self.list.toggleSelection,
				"red": self.exit,
				"green": self.removeCurrentEntries,
				"blue": self.list.toggleAllSelection,
				"yellow": self.previewService,
				"play": self.previewService,
				"stop": self.stopPreview,
				"prevBouquet": boundFunction(self.selectGroup, False),
				"nextBouquet": boundFunction(self.selectGroup, True),
				"menu": self.sortMenu,
				"epg": self.displayEPG,
			})

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Remove selected"))
		self["key_yellow"] = StaticText("")
		self["key_blue"] = Button(_("Inversion"))

		text = _("Mark services with OK button or use group selection (Ch+/Ch-) and then remove these with 'Remove selected'.") + " "
		text += _("Use 'Menu' for sorting.") + " "
		text += _("Epg or Info toggles between EPG and Info text.") + " "
		text += _("'Stop' button stops Preview.")
		self["info"].setText(text)

		self.onSelectionChanged = []
		self["services"].onSelectionChanged.append(self.displayService)
		self.onLayoutFinish.append(self.displayService)

		self.playingRef = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if cfg.debug.value:
			debug("changed bouquet: %s" % self.source_bouquetname)

	def sortMenu(self):
		menu = []
		for x in cfg.sortmenu.choices.choices:
			menu.append((x[1], x[0]))
		self.session.openWithCallback(self.sortbyCallback, ChoiceBox, title=_("Sort bouquet:"), list=menu, selection=int(cfg.sortmenu.value))

	def sortbyCallback(self, choice):
		if choice is None:
			return
		config.plugins.refreshbouquet.sortmenu.value = choice[1]
		config.plugins.refreshbouquet.sortmenu.save()
		self.sortList()

	def sortList(self):
		if len(self["services"].list):
			item = self["services"].getCurrent()[0]
			sort = int(cfg.sortmenu.value)
			if sort == 0:	#default
				self.list.sort(sortType=2)
			elif sort == 1:	#A-z
				self.list.sort(sortType=0)
			elif sort == 2:	#Z-a
				self.list.sort(sortType=0, flag=True)
			elif sort == 3:	#selected top
				self.list.sort(sortType=3, flag=True)
			elif sort == 4:	#default reversed
				self.list.sort(sortType=2, flag=True)
			idx = self.getItemIndex(item)
			self["services"].moveToIndex(idx)

	def getItemIndex(self, item):
		for idx, service in enumerate(self["services"].list):
			if service[0] == item:
				return idx
		return 0

	def displayService(self):
		ref = self["services"].getCurrent()[0][1]
		if not self.isNotService(ref):
			self["TransponderInfo"].newService(eServiceReference(ref))
			if self.display_epg:
				self["Service"].newService(eServiceReference(ref))
				self["info"].hide()
			else:
				self["Service"].newService(None)
				self["info"].show()

			if cfg.preview.value:
				self.previewService()
			else:
				self["key_yellow"].setText(_("Preview"))
		else:
			self["key_yellow"].setText("")
			self["Service"].newService(None)
			self["TransponderInfo"].newService(None)

	def previewService(self):
		ref = self["services"].getCurrent()[0][1]
		if not self.isNotService(ref):
			self.session.nav.playService(eServiceReference(ref))
	def stopPreview(self):
		self.session.nav.playService(self.playingRef)

	def displayEPG(self):
		self.display_epg = not self.display_epg
		self.displayService()

	def selectGroup(self, mark=True):
		if mark:
			txt = _("Add to selection (starts with...)")
		else:
			txt = _("Remove from selection (starts with...)")
		item = self["services"].getCurrent()
		length = int(cfg.vk_length.value)
		name = ""
		if item and length:
			name = item[0][0].decode('UTF-8', 'replace')[0:length]
			txt += "\t%s" % length
		self.session.openWithCallback(boundFunction(self.changeItems, mark), VirtualKeyBoard, title = txt, text = name)

	def changeItems(self, mark, searchString = None):
		if searchString:
			searchString = searchString.decode('UTF-8', 'replace')
			if not cfg.vk_sensitive.value:
				searchString = searchString.lower()
			for item in self.list.list:
				if cfg.vk_sensitive.value:
					exist = item[0][0].decode('UTF-8', 'replace').startswith(searchString)
				else:
					exist = item[0][0].decode('UTF-8', 'replace').lower().startswith(searchString)
				if exist:
					if mark:
						if not item[0][3]:
							self.list.toggleItemSelection(item[0])
					else:
						if item[0][3]:
							self.list.toggleItemSelection(item[0])

	def removeCurrentEntries(self):
		nr_items = len(self.list.getSelectionsList())
		if nr_items:
			text = ngettext("Are you sure to remove this %d service?", "Are you sure to remove this %d services?", nr_items) % nr_items
			self.session.openWithCallback(self.removeFromSource, MessageBox, text, MessageBox.TYPE_YESNO, default=False )
		else:
			self.session.open(MessageBox, _("Nothing for processing..."), MessageBox.TYPE_INFO, timeout=3 )

	def removeFromSource(self, answer):
		if answer == True:
			data = self.list.getSelectionsList()
			serviceHandler = eServiceCenter.getInstance()
			list = self.source and serviceHandler.list(self.source)
			if list is not None:
				mutableList = list.startEdit()
				if mutableList:
					for item in data:
						removed = eServiceReference(item[1])
						if not removed.valid():
							continue
						if not mutableList.removeService(removed):
							mutableList.flushChanges()
			self.close()
		return

	def isNotService(self, refstr):
		if eServiceReference(refstr).flags & (eServiceReference.isDirectory | eServiceReference.isMarker | eServiceReference.isGroup | eServiceReference.isNumberedMarker):
			return True
		return False

	def exit(self):
		nr_items = len(self.list.getSelectionsList())
		if nr_items:
			text = ngettext("Are you sure to close and lost %d selection?", "Are you sure to close and lost all %d selections?", nr_items) % nr_items
			self.session.openWithCallback(self.callBackExit, MessageBox, text, MessageBox.TYPE_YESNO, default=False )
		else:
			self.close()

	def callBackExit(self, answer):
		if answer == True:
			self.close()

# move services in source list
class refreshBouquetMoveServices(Screen):
	def __init__(self, session, list, source, services):
		self.skin = refreshBouquetCopyServices.skin
		Screen.__init__(self, session)
		self.session = session
		self.skinName = ["refreshBouquetMoveServices", "refreshBouquetCopyServices"]

		( self.source_bouquetname, self.source ) = source
		name = addBouqetName(self.source_bouquetname)
		self.setTitle(_("RefreshBouquet %s" % _("- select service(s) for move with OK")) + name)

		setIcon(False)

		self.services = services
		self.list = list
		self["services"] = self.list
		self.sortList()

		self["Service"] = ServiceEvent()
		self["TransponderInfo"] = ServiceEvent()
		self.display_epg = False

		self["info"] = Label()

		self["actions"] = ActionMap(["OkCancelActions", "RefreshBouquetActions"],
			{
				"cancel": self.exit,
				"ok": self.list.toggleSelection,
				"red": self.exit,
				"green": self.actionGreen,
				"yellow": self.previewService,
				"play": self.previewService,
				"stop": self.stopPreview,
				"prevBouquet": boundFunction(self.selectGroup, False),
				"nextBouquet": boundFunction(self.selectGroup, True),
				"menu": self.sortMenu,
				"epg": self.displayEPG,
			})

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Move selected"))
		self["key_yellow"] = StaticText("")
		self["key_blue"] = Button()

		text = _("Mark service(s) with OK button or use group selection (Ch+/Ch-), move selector to new position and finish with 'Move selected'. Selected service(s) will be moved top new position.") + " "
		text += _("Use 'Menu' for sorting.") + " "
		text += _("Sorting has not effect for finaly bouquet sorting.") + " "
		text += _("Epg or Info toggles between EPG and Info text.") + " "
		text += _("'Stop' button stops Preview.")
		self["info"].setText(text)

		self.onSelectionChanged = []
		self["services"].onSelectionChanged.append(self.displayService)
		self.onLayoutFinish.append(self.setPosition)

		self.playingRef = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		if cfg.debug.value:
			debug("changed bouquet: %s" % self.source_bouquetname)

	def sortMenu(self):
		menu = []
		for x in cfg.sortmenu.choices.choices:
			menu.append((x[1], x[0]))
		self.session.openWithCallback(self.sortbyCallback, ChoiceBox, title=_("Sort bouquet:"), list=menu, selection=int(cfg.sortmenu.value))

	def sortbyCallback(self, choice):
		if choice is None:
			return
		config.plugins.refreshbouquet.sortmenu.value = choice[1]
		config.plugins.refreshbouquet.sortmenu.save()
		self.sortList()

	def sortList(self):
		if len(self["services"].list):
			item = self["services"].getCurrent()[0]
			sort = int(cfg.sortmenu.value)
			if sort == 0:	#default
				self.list.sort(sortType=2)
			elif sort == 1:	#A-z
				self.list.sort(sortType=0)
			elif sort == 2:	#Z-a
				self.list.sort(sortType=0, flag=True)
			elif sort == 3:	#selected top
				self.list.sort(sortType=3, flag=True)
			elif sort == 4:	#default reversed
				self.list.sort(sortType=2, flag=True)
			idx = self.getItemIndex(item)
			self["services"].moveToIndex(idx)

	def getItemIndex(self, item):
		for idx, service in enumerate(self["services"].list):
			if service[0] == item:
				return idx
		return 0

	def selectGroup(self, mark=True):
		if mark:
			txt = _("Add to selection (starts with...)")
		else:
			txt = _("Remove from selection (starts with...)")
		item = self["services"].getCurrent()
		length = int(cfg.vk_length.value)
		name = ""
		if item and length:
			name = item[0][0].decode('UTF-8', 'replace')[0:length]
			txt += "\t%s" % length
		self.session.openWithCallback(boundFunction(self.changeItems, mark), VirtualKeyBoard, title = txt, text = name)

	def changeItems(self, mark, searchString = None):
		if searchString:
			searchString = searchString.decode('UTF-8', 'replace')
			if not cfg.vk_sensitive.value:
				searchString = searchString.lower()
			for item in self.list.list:
				if cfg.vk_sensitive.value:
					exist = item[0][0].decode('UTF-8', 'replace').startswith(searchString)
				else:
					exist = item[0][0].decode('UTF-8', 'replace').lower().startswith(searchString)
				if exist:
					if mark:
						if not item[0][3]:
							self.list.toggleItemSelection(item[0])
					else:
						if item[0][3]:
							self.list.toggleItemSelection(item[0])

	def actionGreen(self):
		index = self["services"].getCurrent()[0][2]
		#[0][x] ... x: 0 - service name, 1 - service reference, 2 - index from 1, 3 - selected/unselected
		self.moveCurrentEntries(index)

	def setPosition(self):
		global sel_position
		if sel_position:
			self["services"].moveToIndex(sel_position-1)
			sel_position = None
		else:
			self["services"].moveToIndex(0)
			self.displayService()

	def displayService(self):
		ref = self["services"].getCurrent()[0][1]
		if not self.isNotService(ref):
			self["TransponderInfo"].newService(eServiceReference(ref))
			if self.display_epg:
				self["Service"].newService(eServiceReference(ref))
				self["info"].hide()
			else:
				self["Service"].newService(None)
				self["info"].show()

			if cfg.preview.value:
				self.previewService()
			else:
				self["key_yellow"].setText(_("Preview"))
		else:
			self["key_yellow"].setText("")
			self["Service"].newService(None)
			self["TransponderInfo"].newService(None)

	def previewService(self):
		ref = self["services"].getCurrent()[0][1]
		if not self.isNotService(ref):
			self.session.nav.playService(eServiceReference(ref))
	def stopPreview(self):
		self.session.nav.playService(self.playingRef)

	def displayEPG(self):
		self.display_epg = not self.display_epg
		self.displayService()

	def moveCurrentEntries(self, index):
		nr_items = len(self.list.getSelectionsList())
		if nr_items:
			text = ngettext("Are you sure to move this %d service?", "Are you sure to move this %d services?", nr_items) % nr_items
			self.index = index
			if cfg.confirm_move.value:
				self.session.openWithCallback(self.moveFromSource, MessageBox, text, MessageBox.TYPE_YESNO, default=False )
			else:
				self.moveFromSource(True)
		else:
			self.session.open(MessageBox, _("Nothing for processing..."), MessageBox.TYPE_INFO, timeout=3 )

	def moveFromSource(self, answer):
		if answer == True:
			new_list = self.rebuildList()
			data = self.services
			serviceHandler = eServiceCenter.getInstance()
			list = self.source and serviceHandler.list(self.source)
			if list is not None:
				mutableList = list.startEdit()
				if mutableList:
					for item in data:
						removed = eServiceReference(item[1])
						if not removed.valid():
							continue
						if not mutableList.removeService(removed):
							mutableList.flushChanges()
			data = new_list
			serviceHandler = eServiceCenter.getInstance()
			list = self.source and serviceHandler.list(self.source)
			if list is not None:
				mutableList = list.startEdit()
				if mutableList:
					for item in data:
						new = eServiceReference(item[1])
						if not mutableList.addService(new):
							mutableList.flushChanges()
			self.close(False)
		return

	def rebuildList(self):	# self.index ... selector position - insert will be top this position
		newList = []
		marked = []
		pos = 0
		for i in self.list.getSelectionsList():		# marked services
			marked.append(i[2]) 			# indexes of marked services
			if i[2] > self.index:			# how many item bottom selector ?
				pos += 1
		last = None
		for s in range(len(self.services)):
			source = s+1				# services are indexed from 0, but marked are indexed from 1 => increase source index
			if source == self.index:
				for n in self.list.getSelectionsList():
					if n[2] != self.index:	# add items, but item under selector add as last
						newList.append(n)
					else:
						last = n
				if last:
					newList.append(last)
			if source in marked:
				continue
			newList.append(self.services[source-1])
		global sel_position
		sel_position = self.index + pos
		return newList

	def isNotService(self, refstr):
		if eServiceReference(refstr).flags & (eServiceReference.isDirectory | eServiceReference.isMarker | eServiceReference.isGroup | eServiceReference.isNumberedMarker):
			return True
		return False

	def exit(self):
		nr_items = len(self.list.getSelectionsList())
		if nr_items:
			text = ngettext("Are you sure to close and lost %d selection?", "Are you sure to close and lost all %d selections?", nr_items) % nr_items
			self.session.openWithCallback(self.callBackExit, MessageBox, text, MessageBox.TYPE_YESNO, default=False )
		else:
			self.close(True)

	def callBackExit(self, answer):
		if answer == True:
			self.close(True)

# options
class refreshBouquetCfg(Screen, ConfigListScreen):
	skin = """
	<screen name="refreshBouquetCfg" position="center,center" size="560,380" title="RefreshBouquet Setup" >
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on"/>
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on"/>
		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="config" position="10,40" size="540,300" zPosition="1" transparent="0" scrollbarMode="showOnDemand"/>
		<ePixmap pixmap="skin_default/div-h.png" position="5,355" zPosition="1" size="550,2"/>
		<ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,361" size="14,14" zPosition="3"/>
		<widget font="Regular;18" halign="right" position="495,358" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
			<convert type="ClockToText">Default</convert>
		</widget>
		<widget name="statusbar" position="10,359" size="460,20" font="Regular;18"/>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skin = refreshBouquetCfg.skin
		self.skinName = ["refreshBouquetCfg", "Setup"]
		self.setup_title = _("RefreshBouquet Setup")

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))

		self["description"] = Label()
		self["statusbar"] = Label("ims (c) 2019. v%s" % VERSION)

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"green": self.save,
			"ok": self.save,
			"red": self.exit,
			"cancel": self.exit
		}, -2)

		refreshBouquetCfglist = []
		refreshBouquetCfglist.append(getConfigListEntry(_("Compare case sensitive"), cfg.case_sensitive))
		refreshBouquetCfglist.append(getConfigListEntry(_("Skip 1st nonstandard char in name"), cfg.omit_first, _("Omit any control character in service name. Default set 'yes'.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("Omit last char in target names"), cfg.ignore_last_char, _("You can omit last service name char if provider added it for his planned 're-tuning' and You want use 'Refresh services' for this services too.")+" "+_("On plugin exit it will be set to 'no' again.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("Auto toggle in manually replacing"), cfg.autotoggle, _("In 'Manually replacing' automaticaly toggles between columns when is used 'OK' button.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("Missing source services for manually replace only"), cfg.diff, _("In 'Manually replacing' in source services column will be displayed missing services in target column only.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("Filter services by orbital position in source"), cfg.orbital, _("You can select valid orbital position as filter for display services in source bouquet.")+" "+_("On plugin exit it will be set to 'no' again.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("Using 'service type' in automatic replacing"), cfg.stype, _("Take into account 'service type' in automatic replacing too.")+" "+_("Fastcans changing 'service type' parameter to 'basic' value.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("Programs with 'HD/4K(UHD)' in name only for source"), cfg.used_services,_("Plugin will be display in service bouquet services with HD,4K/UHD in service name only.")+" "+_("On plugin exit it will be set to 'no' again.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("Preview on selection"), cfg.preview, _("Automaticaly preview current service in bouquet list.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("Confirm services moving"), cfg.confirm_move, _("It will require confirmation for moving selected services in the source bouquet.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("Display in Channellist context menu"), cfg.channel_context_menu, _("Plugin will be placed into Channellist menu.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("Return to previous service on end"), cfg.on_end, _("The service being played before the plugin is started on exit again.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("On plugin start use current bouquet as source or as target"), cfg.current_bouquet, _("When the plugin is launched, current bouquet can be set as source or target bouquet.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("Selector to current bouquet"), cfg.selector2bouquet, _("When the plugin is launched, the selector will be set in the bouquets list on current bouquet.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("Display bouquet name"), cfg.bouquet_name, _("Display bouquet name in the screen header or above the list.")))
#		refreshBouquetCfglist.append(getConfigListEntry(_("Save log for manual replace"), cfg.log))
		refreshBouquetCfglist.append(getConfigListEntry(_("Debug info"), cfg.debug))
		refreshBouquetCfglist.append(getConfigListEntry(_("Pre-fill first 'n' servicename chars to virtual keyboard"), cfg.vk_length))
		refreshBouquetCfglist.append(getConfigListEntry(_("Compare virtual keyboard input as case sensitive"), cfg.vk_sensitive))
		refreshBouquetCfglist.append(getConfigListEntry(_("Use dotted service name for 'rbb' files"), cfg.rbb_dotted, _("When is creating a bouquet from 'rbb' file, dotted names can be compared too. You need then manually remove duplicates. Default set is 'no'.")))
		refreshBouquetCfglist.append(getConfigListEntry(_("Show full filenames for deleted bouquets"), cfg.deleted_bq_fullname, _("'Manage deleted bouquets' will display full filenames instead bouquet names only.")))
		ConfigListScreen.__init__(self, refreshBouquetCfglist, session, on_change = self.changedEntry)

		self.onChangedEntry = []
		self.onShown.append(self.setWindowTitle)

	# for summary:
	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]
	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())
	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary
	###
	def setWindowTitle(self):
		self.setTitle(_("RefreshBouquet Setup"))

	def save(self):
		self.keySave()

	def exit(self):
		self.keyCancel()

# change select icons in list operation

select_PNG = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "icons/lock_on.png"))

def setIcon(delete=False):
	global select_PNG
	resolution = ""
	if getDesktop(0).size().width() <= 1280:
		resolution = "_sd"

	select_PNG = None
	if delete:
		select_PNG = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, plugin_path + "/png/select_del%s.png" % resolution))
	else:
		select_PNG = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, plugin_path + "/png/select_on%s.png" % resolution))
	if select_PNG is None:
		select_PNG = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "icons/lock_on.png"))

def MySelectionEntryComponent(description, value, index, selected):
	dx, dy, dw, dh = skin.parameters.get("ImsSelectionListDescr",(35, 2, 650, 30))
	res = [
		(description, value, index, selected),
		(eListboxPythonMultiContent.TYPE_TEXT, dx, dy, dw, dh, 0, RT_HALIGN_LEFT, description)
	]
	if selected:
		ix, iy, iw, ih = skin.parameters.get("ImsSelectionListLock",(0, 0, 24, 24))
		res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, ix, iy, iw, ih, select_PNG))
	return res

class MySelectionList(MenuList):
	def __init__(self, list = None, enableWrapAround = False):
		MenuList.__init__(self, list or [], enableWrapAround, content = eListboxPythonMultiContent)
		font = skin.fonts.get("ImsSelectionList", ("Regular", 20, 30))
		self.l.setFont(0, gFont(font[0], font[1]))
		self.l.setItemHeight(font[2])

	def addSelection(self, description, value, index, selected = True):
		self.list.append(MySelectionEntryComponent(description, value, index, selected))
		self.setList(self.list)

	def toggleSelection(self):
		if len(self.list):
			idx = self.getSelectedIndex()
			item = self.list[idx][0]
			self.list[idx] = MySelectionEntryComponent(item[0], item[1], item[2], not item[3])
			self.setList(self.list)

	def getSelectionsList(self):
		return [ (item[0][0], item[0][1], item[0][2]) for item in self.list if item[0][3] ]

	def toggleAllSelection(self):
		for idx,item in enumerate(self.list):
			item = self.list[idx][0]
			self.list[idx] = MySelectionEntryComponent(item[0], item[1], item[2], not item[3])
		self.setList(self.list)

	def removeSelection(self, item):
		for it in self.list:
			if it[0][0:3] == item[0:3]:
				self.list.pop(self.list.index(it))
				self.setList(self.list)
				return

	def toggleItemSelection(self, item):
		for idx, i in enumerate(self.list):
			if i[0][0:3] == item[0:3]:
				item = self.list[idx][0]
				self.list[idx] = MySelectionEntryComponent(item[0], item[1], item[2], not item[3])
				self.setList(self.list)
				return

	def sort(self, sortType=False, flag=False):
		# sorting by sortType: # 0 - name, 1 - item, 2 - index, 3 - selected
		self.list.sort(key=lambda x: x[0][sortType],reverse=flag)
		self.setList(self.list)

	def len(self):
		return len(self.list)

def addBouqetName(bouquet_name):
	if cfg.bouquet_name.value:
		return " <%s>" % bouquet_name
	return ""

def debug(message):
	print "[RefreshBouquet] %s" % message

def freeMemory():
	import os
	os.system("sync")
	os.system("echo 3 > /proc/sys/vm/drop_caches")

def closed(ret=False):
	freeMemory()

