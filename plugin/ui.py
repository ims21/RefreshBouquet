# -*- coding: utf-8 -*-
# for localized messages
from . import _

#
#  Refresh Bouquet - Plugin E2 for OpenPLi
VERSION = "1.66"
#  by ims (c) 2016-2018 ims21@users.sourceforge.net
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
from enigma import eServiceCenter, eServiceReference, eListboxPythonMultiContent, eListbox, gFont, RT_HALIGN_LEFT, getDesktop
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.config import config, ConfigYesNo, getConfigListEntry, ConfigSelection, NoSave
from Components.Label import Label
from Components.Button import Button
from Components.Sources.List import List
from Screens.ChoiceBox import ChoiceBox
from Components.ScrollLabel import ScrollLabel
from Components.MenuList import MenuList
from Components.ConfigList import ConfigListScreen
from Screens.MessageBox import MessageBox
from Components.Sources.ServiceEvent import ServiceEvent
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
import skin
from plugin import plugin_path

config.plugins.refreshbouquet.case_sensitive = ConfigYesNo(default = True)
config.plugins.refreshbouquet.strip = ConfigYesNo(default = False)
config.plugins.refreshbouquet.debug = ConfigYesNo(default = False)
config.plugins.refreshbouquet.log = ConfigYesNo(default = False)
config.plugins.refreshbouquet.sort = ConfigYesNo(default = False)
config.plugins.refreshbouquet.hd = ConfigSelection(default = "SD", choices = [("SD",_("no")),("HD",_("HD")),("4K",_("4K/UHD")),("HD4K",_("HD or 4K/UHD"))])
config.plugins.refreshbouquet.diff = ConfigYesNo(default = False)
config.plugins.refreshbouquet.preview = ConfigYesNo(default = False)
config.plugins.refreshbouquet.autotoggle = ConfigYesNo(default = True)
config.plugins.refreshbouquet.on_end = ConfigYesNo(default = True)
config.plugins.refreshbouquet.orbital = NoSave(ConfigSelection(default = "x", choices = [("x",_("no")),]))
config.plugins.refreshbouquet.current_bouquet = ConfigSelection(default = "0", choices = [("0",_("no")),("source",_("source bouquet")),("target",_("target bouquet"))])
config.plugins.refreshbouquet.bouquet_name = ConfigYesNo(default = True)
config.plugins.refreshbouquet.confirm_move = ConfigYesNo(default = True)
choicelist = []
for i in range(1, 11, 1):
	choicelist.append(("%d" % i))
choicelist.append(("15","15"))
choicelist.append(("20","20"))
config.plugins.refreshbouquet.vk_length = ConfigSelection(default = "3", choices = [("0", _("No"))] + choicelist + [("255", _("All"))])
config.plugins.refreshbouquet.vk_sensitive = ConfigYesNo(default=False)
cfg = config.plugins.refreshbouquet

TV = (1, 17, 22, 25, 31, 134, 195)
RADIO = (2, 10)

sel_position = None

class refreshBouquet(Screen, HelpableScreen):
	skin = """
	<screen name="refreshBouquet" position="center,center" size="560,400" title="Refresh Bouquet">
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> 
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 
		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="source_text" position="10,50" zPosition="2" size="200,25" valign="center" halign="left" font="Regular;22" foregroundColor="yellow" />
		<widget name="target_text" position="10,75" zPosition="2" size="200,25" valign="center" halign="left" font="Regular;22" foregroundColor="blue" />
		<widget name="source_name" position="220,50" zPosition="2" size="330,25" valign="center" halign="left" font="Regular;22" foregroundColor="white" />
		<widget name="target_name" position="220,75" zPosition="2" size="330,25" valign="center" halign="left" font="Regular;22" foregroundColor="white" />
		<ePixmap pixmap="skin_default/div-h.png" position="5,102" zPosition="2" size="550,2" />
		<widget source="config" render="Listbox" position="5,112" size="550,250" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
				{"template": [
						MultiContentEntryText(pos = (0, 0), size = (550, 25), font=0, flags = RT_HALIGN_LEFT, text = 0),
						],
					"fonts": [gFont("Regular", 22)],
					"itemHeight": 25
				}
			</convert>
		</widget>
		<ePixmap pixmap="skin_default/div-h.png" position="5,365" zPosition="2" size="550,2" />
		<widget name="info" position="5,368" zPosition="2" size="550,25" valign="center" halign="left" font="Regular;22" foregroundColor="white" />
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
			"yellow": (self.getSource, _("select source bouquet ")),
			"blue": (self.getTarget, _("select target bouquet ")),
			"menu": (self.showMenu, _("select action")),
			}, -2)

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Run"))
		self["key_yellow"] = Button(_("Set source"))
		self["key_blue"] = Button(_("Set target"))

		self["config"] = List([])
		self["source_text"] = Label(_("Source bouquet:"))
		self["target_text"] = Label(_("Target bouquet:"))
		self["source_name"] = Label()
		self["target_name"] = Label()
		self["info"] = Label(_("Select or source or source and target bouquets !"))

		self.sourceItem = None
		self.targetItem = None

		self.playingRef = self.session.nav.getCurrentlyPlayingServiceOrGroup()
		self.onLayoutFinish.append(self.getBouquetList)

		if cfg.current_bouquet.value == "source":
			self.getSource(currentBouquet)
		elif cfg.current_bouquet.value == "target":
			self.getTarget(currentBouquet)

	def exit(self):
		self.Servicelist.servicelist.resetRoot()
		if cfg.on_end.value:
			self.session.nav.playService(self.playingRef)
		self.close()

	def showMenu(self):
		text = _("Select action for bouquet:")
		buttons = []
		menu = []
		if self.sourceItem and self.targetItem:
			if self.sourceItem == self.targetItem:
				menu.append((_("Remove selected services in source bouquet"),3))
				menu.append((_("Move selected services in source bouquet"),5))
				buttons = ["4","6"]
			else:
				menu.append((_("Manually replace services"),0))
				menu.append((_("Add selected services to target bouquet"),1))
				menu.append((_("Add selected missing services to target bouquet"),2))
				menu.append((_("Remove selected services in source bouquet"),3))
				menu.append((_("Refresh services in target bouquet"),4))
				menu.append((_("Move selected services in source bouquet"),5))
				buttons = ["1","2","3","4","5","6"]
		elif self.sourceItem:
			menu.append((_("Remove selected services from source bouquet"),3))
			menu.append((_("Move selected services in source bouquet"),5))
			buttons = ["4","6"]
		else:
			text = _("Select or source or source and target bouquets !")
			self["info"].setText(text)

		menu.append((_("Settings..."),10))
		buttons.append("menu")
		self.session.openWithCallback(self.menuCallback, ChoiceBox, title=text, list=menu, keys=buttons)

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
		else:
			self["info"].setText(_("Wrong selection!"))
			return

# get name for source bouquet
	def getSource(self, currentBouquet=None):
		if currentBouquet is not None: # set current bouquet
			current = currentBouquet
		else:
			current = self["config"].getCurrent()
			self["info"].setText("")
		self["source_name"].setText(current[0])
		self.sourceItem = current
		self.setBouquetsOrbitalPositionsConfigFilter(self.sourceItem)
# get name for target bouquet
	def getTarget(self, currentBouquet=None):
		if currentBouquet is not None: # set current bouquet
			current = currentBouquet
		else:
			current = self["config"].getCurrent()
			self["info"].setText("")
		self["target_name"].setText(current[0])
		self.targetItem = current
# get services orbital positions in source bouquets to config for filtering
	def setBouquetsOrbitalPositionsConfigFilter(self, sourceItem):
		def op2human(orb_pos):
			if orb_pos == 0xeeee:
				return _("Terrestrial")
			elif orb_pos == 0xffff:
				return _("Cable")
			if orb_pos > 1800:
				return str((float(3600 - orb_pos)) / 10.0) + "° W"
			elif orb_pos > 0:
				return str((float(orb_pos)) / 10.0) + "° E"
			return "unknown"
		op = []
		new_choices = [("x",_("no"))]
		source = self.getServices(sourceItem[0])
		if not source:
			return
		for service in source:
			if self.isNotService(service[1]):
				continue
			op_hex_str = service[1].split(':')[6][0:-4]
			op_txt = op2human(int(op_hex_str,16))
			try:
				tmp = op.index((op_hex_str,op_txt))
			except:
				op.append((op_hex_str,op_txt))
				new_choices.append(("%s" % op_hex_str ,"%s" % op_txt))
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
			t_name = self.prepareStr(t[0])
			t_splited = t[1].split(':') # split target service_reference
			t_core = ":".join((t_splited[3],t_splited[4],t_splited[5],t_splited[6]))
			t_op = t_splited[6][0:-4]
			for s in source_services: # source bouquet - with fresh scan - f.eg. created by Fastscan or Last Scanned
				if self.isNotService(s[1]): # skip all non playable
					continue
				s_splited = s[1].split(':') # split service_reference
				s_core = ":".join((s_splited[3],s_splited[4],s_splited[5],s_splited[6]))
				if cfg.orbital.value != "x": # only on selected op
					if s_splited[6][:-4] != cfg.orbital.value:
						continue
				if t_name == self.prepareStr(s[0]): # services with same name founded
					s_splited = s[1].split(':') # split ref
					if t_op == s_splited[6][0:-4]: # same orbital position only
						if t_core != s_core and not t_splited[10] and not s_splited[10]: # is different ref ([3]-[6])and is not stream
							length += 1
							select = True
							try:
								tmp = potencialy_duplicity.index(self.charsOnly(s[0])) # same services_name in source = could be duplicity ... set in list as unselected
								debug("Founded: %s" % self.charsOnly(s[0]))
								select = False
							except:
								debug("Unique: %s" % self.charsOnly(s[0]))
							# name, [new ref, old ref], index, selected
							differences.addSelection(s[0], [s[1], t[1]], i, select)
							debug("Added: %s" % self.charsOnly(s[0]))
						potencialy_duplicity.append(self.charsOnly(s[0])) # add to list for next check duplicity
			i += 1
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
				self["info"].setText(_("No services in source bouquet !"))
				return
			nr = 0
			debug(">>> New <<<")
			for i in new:
				nr +=1
				debug("nr:\t%s %s\t\t%s" % (nr, i[0],i[1]))
				# service name, service reference, index, selected
				data.addSelection(i[0], i[1], nr, False)
			self.session.open(refreshBouquetCopyServices, data, self.targetItem)

# returns source services not existing in target service (filtered)

	def getMissingSourceServices(self, source, target):
		mode = config.servicelist.lastmode.value
		differences = []
		for s in source: # services in source bouquet
			if self.isNotService(s[1]):
				debug("Drop: %s %s" % (s[0], s[1]))
				continue
			if cfg.hd.value != "SD":
				if cfg.hd.value is "HD4K":
					if not self.isHDinName(s[0]) and not self.isUHDinName(s[0]):
						debug("Drop (SD): %s %s" % (s[0], s[1]))
						continue
				elif cfg.hd.value == "HD":
					if not self.isHDinName(s[0]):
						debug("Drop (not HD): %s %s" % (s[0], s[1]))
						continue
				elif cfg.hd.value == "4K":
					if not self.isUHDinName(s[0]):
						debug("Drop (not UHD): %s %s" % (s[0], s[1]))
						continue
			if cfg.orbital.value != "x":
				if s[1].split(':')[6][:-4] != cfg.orbital.value:
					continue
			add = 1
			for t in target: # services in target bouquet
				if self.isNotService(t[1]):
					debug("Drop: %s %s" % (t[0], t[1]))
					continue
				if self.prepareStr(s[0]) == self.prepareStr(t[0]): # service exist in target (test by service name)
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
					debug("Dropped stream: %s %s" % (s[0], s[1]))
		return differences

###
# close moveServices or call again moveServices
###
	def moveServicesCallback(self, close, answer):
		if not close or not answer:
			self.moveServices()

###
# move selected service (by user) in source bouquet
###
	def moveServices(self):
		data = MySelectionList([])
		if self.sourceItem:
			source = self.getServices(self.sourceItem[0])
			if not len(source):
				self["info"].setText(_("Source bouquet is empty !"))
				return
			new = []
			new = self.addToBouquetFiltered(source)
			if not len(new):
				self["info"].setText(_("No services in source bouquet !"))
				return
			nr = 0
			debug(">>> Read bouquet <<<")
			for i in new:
				nr +=1
				debug("nr: %s %s\t\t%s" % (nr, i[0],i[1]))
				# service name, service reference, index, selected
				data.addSelection(i[0], i[1], nr, False)
			from Tools.BoundFunction import boundFunction
			self.session.openWithCallback(boundFunction(self.moveServicesCallback, self.close), refreshBouquetMoveServices, data, self.sourceItem, new)

###
# remove selected service (by user) in source bouquet
###
	def removeServices(self):
		data = MySelectionList([])
		if self.sourceItem:
			source = self.getServices(self.sourceItem[0])
			if not len(source):
				self["info"].setText(_("Source bouquet is empty !"))
				return
			new = []
			new = self.addToBouquetFiltered(source)
			if not len(new):
				self["info"].setText(_("No services in source bouquet !"))
				return
			nr = 0
			debug(">>> Read bouquet <<<")
			for i in new:
				nr +=1
				debug("nr: %s %s\t\t%s" % (nr, i[0],i[1]))
				# service name, service reference, index, selected
				data.addSelection(i[0], i[1], nr, False)
			self.session.open(refreshBouquetRemoveServices, data, self.sourceItem)

###
# replace service in target manually by user (all sources)
###
	def replaceSelectedServicesManually(self): 
		if self.sourceItem and self.targetItem:
			target = self.getServices(self.targetItem[0])
			source = self.getServices(self.sourceItem[0])
			if not len(target):
				self["info"].setText(_("Target bouquet is empty !"))
				return
			if not len(source):
				self["info"].setText(_("Source bouquet is empty !"))
				return
			source_services = []
			if cfg.diff.value: # only missing services
				source_services = self.getMissingSourceServices(source, target)
			else:
				source_services = self.addToBouquetFiltered(source)
			if not len(source_services):
				self["info"].setText(_("No services in source bouquet !"))
				return
			if cfg.sort.value:
				source_services.sort()
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
			if s_splited[10] == '': # it is not stream
				if mode == "tv":
					if int(s_splited[2],16) in TV:
						new.append((s[0], s[1], index))
						index += 1
				else:
					if int(s_splited[2],16) in RADIO:
						new.append((s[0], s[1], index))
						index += 1
			else:
				debug("Dropped stream: %s %s" % (s[0], s[1]))
		return new

# optionaly uppercase or remove control character in servicename ( removed for testing only)

	def prepareStr(self, name):
		if cfg.case_sensitive.value == False:
			name = name.upper()
		if cfg.strip.value == True:
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
				self["info"].setText(_("Source bouquet is empty !"))
				return
			new = []
			new = self.addToBouquetFiltered(source)
			if not len(new):
				self["info"].setText(_("No services in source bouquet !"))
				return
			nr = 0
			debug(">>> All <<<")
			for i in new:
				nr +=1
				debug("nr:\t%s %s\t\t%s" % (nr, i[0],i[1]))
				# service name, service reference, index, selected
				data.addSelection(i[0], i[1], nr, False)
			self.session.open(refreshBouquetCopyServices, data, self.targetItem)

# returns all services from bouquet (without notes atc ...)

	def addToBouquetFiltered(self, source):
		# source[0] - name, source[1] - service reference
		mode = config.servicelist.lastmode.value
		new = []
		for s in source: # source bouquet
			if self.isNotService(s[1]):
				debug("Drop: %s %s" % (s[0], s[1]))
				continue
			if cfg.hd.value != "SD":
				if cfg.hd.value is "HD4K":
					if not self.isHDinName(s[0]) and not self.isUHDinName(s[0]):
						debug("Drop (SD): %s %s" % (s[0], s[1]))
						continue
				elif cfg.hd.value == "HD":
					if not self.isHDinName(s[0]):
						debug("Drop (not HD): %s %s" % (s[0], s[1]))
						continue
				elif cfg.hd.value == "4K":
					if not self.isUHDinName(s[0]):
						debug("Drop (not UHD): %s %s" % (s[0], s[1]))
						continue
			s_splited = s[1].split(':') # split ref
			if cfg.orbital.value != "x":
				if s_splited[6][:-4] != cfg.orbital.value:
					continue
			if s_splited[10] == '': # it is not stream
				if mode == "tv":
					if int(s_splited[2],16) in TV:
						new.append((s[0], s[1]))
				else:
					if int(s_splited[2],16) in RADIO:
						new.append((s[0], s[1]))
			else:
				debug("Dropped stream: %s %s" % (s[0], s[1]))
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
				self['list'].setList(bouquets)
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
	skin = """
	<screen name="refreshBouquetManualSelection" position="center,center" size="710,545" title="RefreshBouquet - manual">
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> 
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 
		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="source" position="5,40" zPosition="2" size="350,30"  font="Regular;25" foregroundColor="white" />
		<widget name="target" position="360,40" zPosition="2" size="350,30"  font="Regular;25" foregroundColor="white" />
		<widget name="source_label" position="5,67" zPosition="2" size="350,25"  font="Regular;18" foregroundColor="yellow" />
		<widget name="target_label" position="360,67" zPosition="2" size="350,25"  font="Regular;18" foregroundColor="blue" />
		<widget name="sources" position="3,90" zPosition="2" size="350,300"  font="Regular;22" foregroundColor="white" />
		<widget name="targets" position="360,90" zPosition="2" size="350,300"  font="Regular;22" foregroundColor="white" />
		<ePixmap pixmap="skin_default/div-h.png" position="5,393" zPosition="2" size="700,2" />
		<widget source="Service" render="Label" position="5,397" size="700,23" font="Regular;20" valign="center" halign="left" transparent="1" zPosition="1">
			<convert type="TransponderInfo"></convert>
		</widget>
		<ePixmap pixmap="skin_default/div-h.png" position="5,420" zPosition="2" size="700,2" />
		<widget name="info" position="5,423" zPosition="2" size="705,120" valign="center" halign="left" font="Regular;20" foregroundColor="white" />
	</screen>"""

	def __init__(self, session, sourceList, target_services, source_name, target):
		self.skin = refreshBouquetManualSelection.skin
		Screen.__init__(self, session)
	
		self["Service"] = ServiceEvent()

		self.setTitle(_("RefreshBouquet %s" % _("- select service for replace with OK")))
		self.session = session

		( self.target_bouquetname, self.target ) = target

		self.listSource = sourceList
		self["sources"] = self.listSource

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
				"blue": self.replaceTarget,

				"play": self.previewService,

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
			},-2)

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Apply and close"))
		self["key_yellow"] = Button("")
		self["key_blue"] = Button("")

		name_s = " " + addBouqetName(source_name)
		name_t = " " + addBouqetName(self.target_bouquetname)
		self["source_label"] = Label(_("source bouquet") + name_s )
		self["target_label"] = Label(_("target bouquet") + name_t )

		text = _("Toggle source and target bouquets with Bouq +/-\n")
		text += _("Prepare replacement target's service by service in source bouquet (both select with 'OK') and replace it with 'Replace'. Repeat it as you need. Finish all with 'Apply and close'")
		self["info"].setText(text)

		self.targetRecord = ""
		self.sourceRecord = ""
		self.currList = "sources"
		self.currLabel = "source"
		self.changedTargetdata = []

		debug("changed bouquet: %s" % self.target_bouquetname)
		self.onLayoutFinish.append(self.switchLists)

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

	def displayService(self):
		ref = self[self.currList].getCurrent()[1]
		if not self.isNotService(ref):
			self["Service"].newService(eServiceReference(ref))
			if cfg.preview.value:
				self.previewService()
			else:
				self["key_yellow"].setText(_("Preview"))
		else:
			self["key_yellow"].setText("")
			self["Service"].newService(None)

	def previewService(self):
		ref = self[self.currList].getCurrent()[1]
		if not self.isNotService(ref):
			#self["Service"].newService(eServiceReference(ref))
			self.session.nav.playService(eServiceReference(ref))

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

		self.list = list
		if cfg.sort.value:
			self.list.sort()
		self["services"] = self.list

		self["actions"] = ActionMap(["OkCancelActions", "RefreshBouquetActions"],
			{
				"cancel": self.exit,
				"red": self.exit,
				"ok": self.list.toggleSelection,
				"green": self.replaceSelectedEntries,
				"yellow": self.previewService,
				"blue": self.list.toggleAllSelection,

				"play": self.previewService,
			})

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Refresh selected"))
		self["key_yellow"] = Button()
		self["key_blue"] = Button(_("Inversion"))

		self["info"] = Label()

		text = _("This feature looking for differences in service parameters with same names in source and target bouquets. Parameters for marked services will be replaced. ")
		text += _("It can be in most cases useful for bouquets with services gained by Fastscan searching. ")
		text += _("Posible duplicates will not be marked in list. Check validity with 'Preview' before mark and before 'Refresh selected'.")
		self["info"].setText(text)

		self.onSelectionChanged = []
		self["services"].onSelectionChanged.append(self.displayService)
		self.onLayoutFinish.append(self.displayService)

	def displayService(self):
		ref = self["services"].getCurrent()[0][1][0]
		index = self["services"].getCurrent()[0][2] + 1
		self.setTitle("%s\t%s: %s" % (self.texttitle, _("Position"), index))
		if not self.isNotService(ref):
			self["Service"].newService(eServiceReference(ref))
			if cfg.preview.value:
				self.previewService()
			else:
				self["key_yellow"].setText(_("Preview"))
		else:
			self["key_yellow"].setText("")
			self["Service"].newService(None)

	def previewService(self):
		ref = self["services"].getCurrent()[0][1][0]
		if not self.isNotService(ref):
			self.session.nav.playService(eServiceReference(ref))

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
					index = data[2]
					old = eServiceReference(data[1][1])
					new = eServiceReference(data[1][0])
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
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="services" position="5,50" zPosition="2" size="705,300" itemHeight="25" font="Regular;22" foregroundColor="white" />
		<ePixmap pixmap="skin_default/div-h.png" position="5,351" zPosition="2" size="700,2" />
		<widget source="Service" render="Label" position="5,354" size="700,23" font="Regular;20" valign="center" halign="left" transparent="1" zPosition="1">
			<convert type="TransponderInfo"></convert>
		</widget>
		<ePixmap pixmap="skin_default/div-h.png" position="5,377" zPosition="2" size="700,2" />
		<widget name="info" position="5,380" zPosition="2" size="705,120" valign="center" halign="left" font="Regular;20" foregroundColor="white" />
	</screen>"""

	def __init__(self, session, list, target):
		self.skin = refreshBouquetCopyServices.skin
		Screen.__init__(self, session)
		self.session = session

		( self.target_bouquetname, self.target ) = target
		name = addBouqetName(self.target_bouquetname)
		self.setTitle(_("RefreshBouquet %s" % _("- select service(s) for adding with OK")) + name)

		self["Service"] = ServiceEvent()

		self["info"] = Label()

		setIcon()

		self.list = list
		if cfg.sort.value:
			self.list.sort()
		self["services"] = self.list

		self["actions"] = ActionMap(["OkCancelActions", "RefreshBouquetActions"],
			{
				"cancel": self.exit,
				"ok": self.list.toggleSelection,
				"red": self.exit,
				"green": self.copyCurrentEntries,
				"blue": self.list.toggleAllSelection,
				"yellow": self.previewService,
				"play": self.previewService,
				"prevBouquet": self.getUnselectString,
				"nextBouquet": self.getSelectString
			})

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Copy selected"))
		self["key_yellow"] = Button("")
		self["key_blue"] = Button(_("Inversion"))

		self["info"].setText(_("Mark services with OK button and then copy these with 'Copy selected'"))

		self.onSelectionChanged = []
		self["services"].onSelectionChanged.append(self.displayService)
		self.onLayoutFinish.append(self.displayService)

		debug("changed bouquet: %s" % self.target_bouquetname)

	def displayService(self):
		ref = self["services"].getCurrent()[0][1]
		if not self.isNotService(ref):
			self["Service"].newService(eServiceReference(ref))
			if cfg.preview.value:
				self.previewService()
			else:
				self["key_yellow"].setText(_("Preview"))
		else:
			self["key_yellow"].setText("")
			self["Service"].newService(None)

	def previewService(self):
		ref = self["services"].getCurrent()[0][1]
		if not self.isNotService(ref):
			self.session.nav.playService(eServiceReference(ref))

	def getSelectString(self):
		name = ""
		n = ""
		item = self["services"].getCurrent()
		length = int(cfg.vk_length.value)
		if item and length:
			name = item[0][0].decode('UTF-8', 'replace')[0:length]
			n = "\t%s" % length
		self.session.openWithCallback(self.selectItems, VirtualKeyBoard, title = _("Add to selection (starts with...)") + n, text = name)

	def selectItems(self, searchString = None):
		if searchString:
			searchString = searchString.decode('UTF-8', 'replace')
			if cfg.vk_sensitive.value:
					for item in self.list.list:
						if item[0][0].decode('UTF-8', 'replace').startswith(searchString):
							if not item[0][3]:
								self.list.toggleItemSelection(item[0])
			else:
				searchString = searchString.lower()
				for item in self.list.list:
					if item[0][0].decode('UTF-8', 'replace').lower().startswith(searchString):
						if not item[0][3]:
							self.list.toggleItemSelection(item[0])
		self.displaySelectionPars()

	def getUnselectString(self):
		name = ""
		n = ""
		item = self["services"].getCurrent()
		length = int(cfg.vk_length.value)
		if item and length:
			name = item[0][0].decode('UTF-8', 'replace')[0:length]
			n = "\t%s" % length
		self.session.openWithCallback(self.unselectItems, VirtualKeyBoard, title = _("Remove from selection (starts with...)") + n, text = name)

	def unselectItems(self, searchString = None):
		if searchString:
			searchString = searchString.decode('UTF-8', 'replace')
			if cfg.vk_sensitive.value:
					for item in self.list.list:
						if item[0][0].decode('UTF-8', 'replace').startswith(searchString):
							if item[0][3]:
								self.list.toggleItemSelection(item[0])
			else:
				searchString = searchString.lower()
				for item in self.list.list:
					if item[0][0].decode('UTF-8', 'replace').lower().startswith(searchString):
						if item[0][3]:
							self.list.toggleItemSelection(item[0])
		self.displaySelectionPars()

	def displaySelectionPars(self, singleToggle=False):
		# TODO: label with number of selected
		pass

	def copyCurrentEntries(self):
		nr_items = len(self.list.getSelectionsList())
		if nr_items:
			text = ngettext("Are you sure to copy this %d service?", "Are you sure to copy this %d services?", nr_items) % nr_items
			self.session.openWithCallback(self.copyToTarget, MessageBox, text, MessageBox.TYPE_YESNO, default=False )
		else:
			self.session.open(MessageBox, _("Nothing for processing..."), MessageBox.TYPE_INFO, timeout=3 )

	def copyToTarget(self, answer):
		if answer == True:
			data = self.list.getSelectionsList()
			serviceHandler = eServiceCenter.getInstance()
			list = self.target and serviceHandler.list(self.target)
			if list is not None:
				mutableList = list.startEdit()
				for item in data:
					new = eServiceReference(item[1])
					if not mutableList.addService(new):
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
		if cfg.sort.value:
			self.list.sort()
		self["services"] = self.list

		self["Service"] = ServiceEvent()

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
				"prevBouquet": self.getUnselectString,
				"nextBouquet": self.getSelectString
			})

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Remove selected"))
		self["key_yellow"] = Button()
		self["key_blue"] = Button(_("Inversion"))

		self["info"].setText(_("Mark services with OK button and then remove these with 'Remove selected'"))

		self.onSelectionChanged = []
		self["services"].onSelectionChanged.append(self.displayService)
		self.onLayoutFinish.append(self.displayService)

		debug("changed bouquet: %s" % self.source_bouquetname)

	def displayService(self):
		ref = self["services"].getCurrent()[0][1]
		if not self.isNotService(ref):
			self["Service"].newService(eServiceReference(ref))
			if cfg.preview.value:
				self.previewService()
			else:
				self["key_yellow"].setText(_("Preview"))
		else:
			self["key_yellow"].setText("")
			self["Service"].newService(None)

	def getSelectString(self):
		name = ""
		n = ""
		item = self["services"].getCurrent()
		length = int(cfg.vk_length.value)
		if item and length:
			name = item[0][0].decode('UTF-8', 'replace')[0:length]
			n = "\t%s" % length
		self.session.openWithCallback(self.selectItems, VirtualKeyBoard, title = _("Add to selection (starts with...)") + n, text = name)

	def selectItems(self, searchString = None):
		if searchString:
			searchString = searchString.decode('UTF-8', 'replace')
			if cfg.vk_sensitive.value:
					for item in self.list.list:
						if item[0][0].decode('UTF-8', 'replace').startswith(searchString):
							if not item[0][3]:
								self.list.toggleItemSelection(item[0])
			else:
				searchString = searchString.lower()
				for item in self.list.list:
					if item[0][0].decode('UTF-8', 'replace').lower().startswith(searchString):
						if not item[0][3]:
							self.list.toggleItemSelection(item[0])
		self.displaySelectionPars()

	def getUnselectString(self):
		name = ""
		n = ""
		item = self["services"].getCurrent()
		length = int(cfg.vk_length.value)
		if item and length:
			name = item[0][0].decode('UTF-8', 'replace')[0:length]
			n = "\t%s" % length
		self.session.openWithCallback(self.unselectItems, VirtualKeyBoard, title = _("Remove from selection (starts with...)") + n, text = name)

	def unselectItems(self, searchString = None):
		if searchString:
			searchString = searchString.decode('UTF-8', 'replace')
			if cfg.vk_sensitive.value:
					for item in self.list.list:
						if item[0][0].decode('UTF-8', 'replace').startswith(searchString):
							if item[0][3]:
								self.list.toggleItemSelection(item[0])
			else:
				searchString = searchString.lower()
				for item in self.list.list:
					if item[0][0].decode('UTF-8', 'replace').lower().startswith(searchString):
						if item[0][3]:
							self.list.toggleItemSelection(item[0])
		self.displaySelectionPars()

	def displaySelectionPars(self, singleToggle=False):
		# TODO: label with number of selected
		pass

	def previewService(self):
		ref = self["services"].getCurrent()[0][1]
		if not self.isNotService(ref):
			self.session.nav.playService(eServiceReference(ref))

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
from Screens.VirtualKeyBoard import VirtualKeyBoard
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

		self["Service"] = ServiceEvent()

		self["info"] = Label()

		self["actions"] = ActionMap(["OkCancelActions", "RefreshBouquetActions"],
			{
				"cancel": self.exit,
				"ok": self.list.toggleSelection,
				"red": self.exit,
				"green": self.actionGreen,
				"yellow": self.previewService,
				"play": self.previewService,
				"prevBouquet": self.getUnselectString,
				"nextBouquet": self.getSelectString
			})

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Move selected"))
		self["key_yellow"] = Button()
		self["key_blue"] = Button()
		self["info"].setText(_("Mark service(s) with OK button, move selector to new position and finish with 'Move selected'. Selected service(s) will be moved top new position."))

		self.onSelectionChanged = []
		self["services"].onSelectionChanged.append(self.displayService)
		self.onLayoutFinish.append(self.setPosition)

		debug("changed bouquet: %s" % self.source_bouquetname)

	def getSelectString(self):
		name = ""
		n = ""
		item = self["services"].getCurrent()
		length = int(cfg.vk_length.value)
		if item and length:
			name = item[0][0].decode('UTF-8', 'replace')[0:length]
			n = "\t%s" % length
		self.session.openWithCallback(self.selectItems, VirtualKeyBoard, title = _("Add to selection (starts with...)") + n, text = name)

	def selectItems(self, searchString = None):
		if searchString:
			searchString = searchString.decode('UTF-8', 'replace')
			if cfg.vk_sensitive.value:
					for item in self.list.list:
						if item[0][0].decode('UTF-8', 'replace').startswith(searchString):
							if not item[0][3]:
								self.list.toggleItemSelection(item[0])
			else:
				searchString = searchString.lower()
				for item in self.list.list:
					if item[0][0].decode('UTF-8', 'replace').lower().startswith(searchString):
						if not item[0][3]:
							self.list.toggleItemSelection(item[0])
		self.displaySelectionPars()

	def getUnselectString(self):
		name = ""
		n = ""
		item = self["services"].getCurrent()
		length = int(cfg.vk_length.value)
		if item and length:
			name = item[0][0].decode('UTF-8', 'replace')[0:length]
			n = "\t%s" % length
		self.session.openWithCallback(self.unselectItems, VirtualKeyBoard, title = _("Remove from selection (starts with...)") + n, text = name)

	def unselectItems(self, searchString = None):
		if searchString:
			searchString = searchString.decode('UTF-8', 'replace')
			if cfg.vk_sensitive.value:
					for item in self.list.list:
						if item[0][0].decode('UTF-8', 'replace').startswith(searchString):
							if item[0][3]:
								self.list.toggleItemSelection(item[0])
			else:
				searchString = searchString.lower()
				for item in self.list.list:
					if item[0][0].decode('UTF-8', 'replace').lower().startswith(searchString):
						if item[0][3]:
							self.list.toggleItemSelection(item[0])
		self.displaySelectionPars()

	def displaySelectionPars(self, singleToggle=False):
		# TODO: label with number of selected
		pass

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
			self["Service"].newService(eServiceReference(ref))
			if cfg.preview.value:
				self.previewService()
			else:
				self["key_yellow"].setText(_("Preview"))
		else:
			self["key_yellow"].setText("")
			self["Service"].newService(None)

	def previewService(self):
		ref = self["services"].getCurrent()[0][1]
		if not self.isNotService(ref):
			self.session.nav.playService(eServiceReference(ref))

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
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="config" position="10,40" size="540,300" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="skin_default/div-h.png" position="5,355" zPosition="1" size="550,2" />
		<ePixmap alphatest="on" pixmap="skin_default/icons/clock.png" position="480,361" size="14,14" zPosition="3"/>
		<widget font="Regular;18" halign="right" position="495,358" render="Label" size="55,20" source="global.CurrentTime" transparent="1" valign="center" zPosition="3">
			<convert type="ClockToText">Default</convert>
		</widget>
		<widget name="statusbar" position="10,359" size="460,20" font="Regular;18" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skin = refreshBouquetCfg.skin
		self.skinName = ["refreshBouquetCfg", "Setup"]
		self.setup_title = _("RefreshBouquet Setup")

		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("OK"))

		self["statusbar"] = Label("ims (c) 2016. v%s" % VERSION)

		self["actions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"green": self.save,
			"ok": self.save,
			"red": self.exit,
			"cancel": self.exit
		}, -2)

		refreshBouquetCfglist = []
		refreshBouquetCfglist.append(getConfigListEntry(_("Compare case sensitive"), cfg.case_sensitive))
		refreshBouquetCfglist.append(getConfigListEntry(_("Skip 1st nonstandard char in name"), cfg.strip))
		refreshBouquetCfglist.append(getConfigListEntry(_("Sort services in source bouquets"), cfg.sort))
		refreshBouquetCfglist.append(getConfigListEntry(_("Missing source services for manually replace only"), cfg.diff))
		refreshBouquetCfglist.append(getConfigListEntry(_("Filter services by orbital position in source"), cfg.orbital))
		refreshBouquetCfglist.append(getConfigListEntry(_("Programs with 'HD/4K(UHD)' in name only for source"), cfg.hd))
		refreshBouquetCfglist.append(getConfigListEntry(_("Preview on selection"), cfg.preview))
		refreshBouquetCfglist.append(getConfigListEntry(_("Confirm services moving"), cfg.confirm_move))
		refreshBouquetCfglist.append(getConfigListEntry(_("Auto toggle in manually replacing"), cfg.autotoggle))
		refreshBouquetCfglist.append(getConfigListEntry(_("Display in Channellist context menu"), cfg.channel_context_menu))
		refreshBouquetCfglist.append(getConfigListEntry(_("Return to previous service on end"), cfg.on_end))
		refreshBouquetCfglist.append(getConfigListEntry(_("On plugin start use current bouquet as source or as target"), cfg.current_bouquet))
		refreshBouquetCfglist.append(getConfigListEntry(_("Display bouquet name"), cfg.bouquet_name))
#		refreshBouquetCfglist.append(getConfigListEntry(_("Save log for manual replace"), cfg.log))
		refreshBouquetCfglist.append(getConfigListEntry(_("Debug info"), cfg.debug))
		refreshBouquetCfglist.append(getConfigListEntry(_("Pre-fill first 'n' servicename chars to virtual keyboard"), cfg.vk_length))
		refreshBouquetCfglist.append(getConfigListEntry(_("Compare virtual keyboard input as case sensitive"), cfg.vk_sensitive))
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
def setIcon(delete=False):
	global select_png
	resolution = ""
	if getDesktop(0).size().width() <= 1280:
		resolution = "_sd"
	select_png = None
	if delete:
		select_png = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, plugin_path + "/png/select_del%s.png" % resolution))
	else:
		select_png = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, plugin_path + "/png/select_on%s.png" % resolution))
	if select_png is None:
		select_png = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_on.png"))

select_png = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_on.png"))

def MySelectionEntryComponent(description, value, index, selected):
	dx, dy, dw, dh = skin.parameters.get("SelectionListDescr",(35, 2, 650, 30))
	res = [
		(description, value, index, selected),
		(eListboxPythonMultiContent.TYPE_TEXT, dx, dy, dw, dh, 0, RT_HALIGN_LEFT, description)
	]
	if selected:
		ix, iy, iw, ih = skin.parameters.get("SelectionListLock",(0, 0, 24, 24))
		res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, ix, iy, iw, ih, select_png))
	return res

class MySelectionList(MenuList):
	def __init__(self, list = None, enableWrapAround = False):
		MenuList.__init__(self, list or [], enableWrapAround, content = eListboxPythonMultiContent)
		font = skin.fonts.get("SelectionList", ("Regular", 20, 30))
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
		# sorting by sortType: # 0 - description, 1 - value, 2 - index, 3 - selected
		self.list.sort(key=lambda x: x[0][sortType],reverse=flag)
		self.setList(self.list)

	def len(self):
		return len(self.list)

def addBouqetName(bouquet_name):
	if cfg.bouquet_name.value:
		return " <%s>" % bouquet_name
	return ""

def debug(message):
	if cfg.debug.value:
		print "[RefreshBouquet] %s" % message

def freeMemory():
	import os
	os.system("sync")
	os.system("echo 3 > /proc/sys/vm/drop_caches")

def closed(ret=False):
	setEnigmaCatalog()
	freeMemory()

# for ngettext in external plugin
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE

def setPluginCatalog():
	# for generate gettext strings into .pot - this strings are displayed by enigma's functions:
	dummy_text = _("Question") + _("yes")+ _("Select") + _("Information") + _("Really close without saving settings?")
	del dummy_text
	try:
		gettext.translation('RefreshBouquet', resolveFilename(SCOPE_PLUGINS, 'Extensions/RefreshBouquet/locale'), languages=[language.getLanguage()]).install(names=("ngettext", "pgettext"))
	except:
		debug("missing %s translation" % language.getLanguage())
def setEnigmaCatalog():
	gettext.translation('enigma2', resolveFilename(SCOPE_LANGUAGE, ""), languages=[language.getLanguage()]).install(names=("ngettext", "pgettext"))
