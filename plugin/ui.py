# for localized messages  	 
from . import _
#
#  Refresh Bouquet - Plugin E2 for OpenPLi
VERSION = "1.39"
#  by ims (c) 2016 ims21@users.sourceforge.net
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
from enigma import eServiceCenter, eServiceReference
from ServiceReference import ServiceReference

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.config import config, ConfigYesNo, getConfigListEntry
from Components.Label import Label
#import enigma
from Components.Button import Button
from Components.Sources.List import List
from Screens.ChoiceBox import ChoiceBox
from Components.ScrollLabel import ScrollLabel
from Components.SelectionList import SelectionList
from Components.MenuList import MenuList
from Components.ConfigList import ConfigListScreen
from Screens.MessageBox import MessageBox
from Components.Sources.ServiceEvent import ServiceEvent

config.plugins.refreshbouquet.case_sensitive = ConfigYesNo(default = True)
config.plugins.refreshbouquet.strip = ConfigYesNo(default = False)
config.plugins.refreshbouquet.debug = ConfigYesNo(default = False)
config.plugins.refreshbouquet.log = ConfigYesNo(default = False)
config.plugins.refreshbouquet.sort = ConfigYesNo(default = False)
config.plugins.refreshbouquet.hd = ConfigYesNo(default = False)
config.plugins.refreshbouquet.diff = ConfigYesNo(default = False)
config.plugins.refreshbouquet.preview = ConfigYesNo(default = False)
config.plugins.refreshbouquet.autotoggle = ConfigYesNo(default = True)
cfg = config.plugins.refreshbouquet

TV = (1, 17, 22, 25, 31, 134, 195)
RADIO = (2, 10)

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

		<widget name="source_text" position="10,50" zPosition="2" size="200,25" valign="center" halign="left" font="Regular;22" foregroundColor="white" />
		<widget name="target_text" position="10,75" zPosition="2" size="200,25" valign="center" halign="left" font="Regular;22" foregroundColor="white" />
		<widget name="source_name" position="220,50" zPosition="2" size="330,25" valign="center" halign="left" font="Regular;22" foregroundColor="white" />
		<widget name="target_name" position="220,75" zPosition="2" size="330,25" valign="center" halign="left" font="Regular;22" foregroundColor="white" />

		<ePixmap pixmap="skin_default/div-h.png" position="10,102" zPosition="2" size="540,2" />
		<widget source="config" render="Listbox" position="10,112" size="540,250" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
				{"template": [
						MultiContentEntryText(pos = (0, 0), size = (520, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), 
						],
					"fonts": [gFont("Regular", 22)],
					"itemHeight": 25
				}
			</convert>
		</widget>

		<ePixmap pixmap="skin_default/div-h.png" position="10,364" zPosition="2" size="540,2" />
		<widget name="info" position="10,372" zPosition="2" size="540,25" valign="center" halign="left" font="Regular;22" foregroundColor="white" />
	</screen>"""

	def __init__(self, session, Servicelist=None):
		self.skin = refreshBouquet.skin
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)

		self.Servicelist = Servicelist

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

	def exit(self):
		self.Servicelist.servicelist.resetRoot()
		self.session.nav.playService(self.playingRef)
		self.close()

	def showMenu(self):
		text = _("Select action for bouquet:")
		menu = []
		if self.sourceItem and self.targetItem:
			if self.sourceItem == self.targetItem:
				menu.append((_("Remove selected services from source bouquet"),3))
			else:
				menu.append((_("Manually replace services"),0))
				menu.append((_("Add selected services to target bouquet"),1))
				menu.append((_("Add selected missing services to target bouquet"),2))
				menu.append((_("Remove selected services in source bouquet"),3))
				menu.append((_("Test 'Refresh services in target bouquet'"),4))
				menu.append((_("Refresh services in target bouquet"),5))
		elif self.sourceItem:
			menu.append((_("Remove selected services from source bouquet"),3))
		else:
			self["info"].setText(_("Select or source or source and target bouquets !"))
			text = _("Select or source or source and target bouquets !")
		menu.append((_("Settings..."),10))

		self.session.openWithCallback(self.menuCallback, ChoiceBox, title=text, list=menu)	

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
			self.refreshServicesTest()
		elif choice[1] == 5:
			self.refreshServices()
		elif choice[1] == 10:
			self.options()
		else:
			self["info"].setText(_("Wrong selection!"))
			return

# get name for source bouquet
	def getSource(self):
		self["info"].setText("")
		current = self["config"].getCurrent()
		self["source_name"].setText(current[0])
		self.sourceItem = current
# get name for target bouquet
	def getTarget(self):
		self["info"].setText("")
		current = self["config"].getCurrent()
		self["target_name"].setText(current[0])
		self.targetItem = current


# call refreshService as test
	def refreshServicesTest(self):
		self.actualizeServices()

# call refreshService as replace		
	def refreshServices(self):
		self.actualizeServices(True)

#
# Replace service-reference for services with same name
#

	def actualizeServices(self, make_changes=False):
		log = ("%s:%s\n\n" % (_("Service name"), _("Bouquet position")))
		if self.sourceItem and self.targetItem:
			target = self.getServices(self.targetItem[0])
			source = self.getServices(self.sourceItem[0])
			if not len(target):
				self["info"].setText(_("Target bouquet is empty !"))
				return
			if not len(source):
				self["info"].setText(_("Source bouquet is empty !"))
				return
			forReplace = self.compareServices(source, target)
			nr = 0
			self.debug(">>> Diferences <<<")
			for i in forReplace:
				nr +=1
										# nr, index, old ref, new ref, old name
				self.debug("nr: %s  index: %s\t%s <- %s  %s" % (nr, i[3], i[1], i[2], i[0]))
				# name:position in bouquet (=index in bouquet + 1), note: ":" is for divide in ScrollLabel
				log += "%s:%s\n" % (i[0], i[3] + 1)
				if make_changes:
					self.replaceService(i)
			if make_changes:
				log += _("\nRefreshed %d services") % nr
			else:
				log += _("\n%d services for refresh") % nr
			self.session.open(refreshBouquetDisplayServices, log)

# looking new service reference for target service - returns service name, old service reference, new service reference and position in target bouquet

	def compareServices(self, source, target):
		diferences = []
		i = 0 # index
		for t in target: # bouquet for refresh
			if self.isNotService(t[1]):
				i += 1
				continue
			t_name = self.prepareStr(t[0])
			t_splited = t[1].split(':') # split ref
			for s in source: # source bouquet - with lastest scan - f.eg. created by Fastscan
				if self.isNotService(s[1]):
					continue
				s_splited = s[1].split(':') # split ref
				if t_name == self.prepareStr(s[0]): # services with same name founded
					s_splited = s[1].split(':') # split ref
					if t[1] != s[1] and not t_splited[10] and not s_splited[10]: # is different ref and is not stream
						orb_t = t_splited[6]
						orb_s = s_splited[6]
						if orb_t == orb_s: # for same orbital position only
							#name, old ref, new ref, index in target bouquet
							diferences.append((s[0], t[1], s[1], i))
			i += 1
		return diferences
###
# Add missing services to source bouquet or all services to empty bouquet
###
	def addMissingServices(self):
		data = SelectionList([])
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
				new = self.addToBouquetFilteredIndexed(source)
			if not len(new):
				self["info"].setText(_("No services in source bouquet !"))
				return
			nr = 0
			self.debug(">>> New <<<")
			for i in new:
				nr +=1
				self.debug("nr:\t%s %s\t\t%s" % (nr, i[0],i[1]))
				# service name, service reference, index, selected
				data.addSelection(i[0], i[1], nr, False)
			self.session.open(refreshBouquetCopyServices, data, self.targetItem)

# returns source services not existing in target service (filtered)

	def getMissingSourceServices(self, source, target):
		mode = config.servicelist.lastmode.value
		diferences = []
		for s in source: # services in source bouquet
			if self.isNotService(s[1]):
				self.debug("Drop: %s" % s[1])
				continue
			if cfg.hd.value:
				if not self.isHDinName(s[0]):
					self.debug("Drop (no HD): %s" % s[1])
					continue
			add = 1
			for t in target: # services in target bouquet
				if self.isNotService(t[1]):
					self.debug("Drop: %s" % t[1])
					continue
				if self.prepareStr(s[0]) == self.prepareStr(t[0]): # service exist in target (test by service name)
					self.debug("Drop: %s %s" % (s[0], t[0]))
					add = 0
					break
			if add:
				s_splited = s[1].split(':') # split ref
				t_splited = t[1].split(':') # split ref
				if t_splited[10] == '' and s_splited[10] == '': # it is not stream
					if mode == "tv":
						if int(s_splited[2],16) in TV:
							diferences.append((s[0], s[1]))
					else:
						if int(s_splited[2],16) in RADIO:
							diferences.append((s[0], s[1]))
		return diferences

###
# remove selected service (by user) in target directory
###
	def removeServices(self):
		data = SelectionList([])
		if self.sourceItem:
			source = self.getServices(self.sourceItem[0])
			if not len(source):
				self["info"].setText(_("Source bouquet is empty !"))
				return
			new = []
			new = self.addToBouquetFilteredIndexed(source)
			if not len(new):
				self["info"].setText(_("No services in source bouquet !"))
				return
			nr = 0
			self.debug(">>> Read bouquet <<<")
			for i in new:
				nr +=1
				self.debug("nr: %s %s\t\t%s" % (nr, i[0],i[1]))
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
				source_services = self.addToBouquetFilteredIndexed(source)
			if not len(source_services):
				self["info"].setText(_("No services in source bouquet !"))
				return
			if cfg.sort.value:
				source_services.sort()
			sourceList = MenuList(source_services) # name, service reference
			target_services = self.addToBouquetAllIndexed(target) # name, service reference, index in bouquet
			self.session.open(refreshBouquetManualSelection, sourceList, target_services, self.targetItem)

# returns all source services (with marks too) and with true positions in source bouquet

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
				self.debug("Dropped stream: %s" % s[1])
		return new

# replace service reference for old service in target

	def replaceService(self, data): # data: [0] - source name, [1] - old ref, [2] - new ref, [3] - index,
		index = data[3]
		old = eServiceReference(data[1])
		new = eServiceReference(data[2])
		if cfg.case_sensitive.value == False: # trick for changing name - it cannot be made in one step
			old.setName(data[0])
		serviceHandler = eServiceCenter.getInstance()
		list = self.targetItem[1] and serviceHandler.list(self.targetItem[1])
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

# optionaly uppercase or remove control character in servicename ( removed for testing only)

	def prepareStr(self, name):
		if cfg.case_sensitive.value == False:
			name = name.upper()
		if cfg.strip.value == True:
			if name[0] < ' ':
				return name[1:]
		return name

###
# Add selected services (by user) to target bouquet
###
	def addServices(self):
		data = SelectionList([])
		if self.sourceItem and self.targetItem:
			target = self.getServices(self.targetItem[0])
			source = self.getServices(self.sourceItem[0])
			if not len(source):
				self["info"].setText(_("Source bouquet is empty !"))
				return
			new = []
			new = self.addToBouquetFilteredIndexed(source)
			if not len(new):
				self["info"].setText(_("No services in source bouquet !"))
				return
			nr = 0
			self.debug(">>> All <<<")
			for i in new:
				nr +=1
				self.debug("nr:\t%s %s\t\t%s" % (nr, i[0],i[1]))
				# service name, service reference, index, selected
				data.addSelection(i[0], i[1], nr, False)
			self.session.open(refreshBouquetCopyServices, data, self.targetItem)


# returns all services from bouquet (without notes atc ...)

	def addToBouquetFilteredIndexed(self, source):
		# source[0] - name, source[1] - service reference
		mode = config.servicelist.lastmode.value
		new = []
		for s in source: # source bouquet
			if self.isNotService(s[1]):
				self.debug("Drop: %s" % s[1])
				continue
			if cfg.hd.value:
				if not self.isHDinName(s[0]):
					self.debug("Drop (no HD): %s" % s[1])
					continue
			s_splited = s[1].split(':') # split ref
			if s_splited[10] == '': # it is not stream
				if mode == "tv":
					if int(s_splited[2],16) in TV:
						new.append((s[0], s[1]))
				else:
					if int(s_splited[2],16) in RADIO:
						new.append((s[0], s[1]))
			else:
				self.debug("Dropped stream: %s" % s[1])
		return new

# test for "noplayable" service

	def isNotService(self, refstr):
		if eServiceReference(refstr).flags & (eServiceReference.isDirectory | eServiceReference.isMarker | eServiceReference.isGroup | eServiceReference.isNumberedMarker):
			return True
		return False

	def isHDinName(self, name):
		if name.find('HD') != -1:
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
			return
		serviceHandler = eServiceCenter.getInstance()
		list = serviceHandler.list(bouquet)
		services = list.getContent("NS", False)
		if list:
#			for service in services:
#				print ">>>>>>", service[0], "\t\t", service[1]
			return services

# enable debug to telnet

	def debug(self, message):
		if cfg.debug.value:
			print "[RefreshBouquet] %s" % message
# call Options

	def options(self):
		self.session.openWithCallback(self.afterConfig, refreshBouquetCfg)
#		
	def afterConfig(self, data=None):
		self.showMenu()

# manual replace
class refreshBouquetManualSelection(Screen):
	skin = """
	<screen name="refreshBouquetManualSelection" position="center,center" size="710,540" title="RefreshBouquet - manual">
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" /> 
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" /> 
		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="sources" position="5,50" zPosition="2" size="350,450"  font="Regular;22" foregroundColor="white" />
		<widget name="targets" position="360,50" zPosition="2" size="350,450"  font="Regular;22" foregroundColor="white" />
		<ePixmap pixmap="skin_default/div-h.png" position="5,502" zPosition="2" size="700,2" />
		<widget name="source" position="5,510" zPosition="2" size="350,25"  font="Regular;22" foregroundColor="white" />
		<widget name="target" position="360,510" zPosition="2" size="350,25"  font="Regular;22" foregroundColor="white" />
	</screen>"""

	def __init__(self, session, sourceList, target_services, target):
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
		
		self["info"].setText(_("Toggle source and target lists with Bouq +/-\n\nSelect with OK"))

		self.targetRecord = ""
		self.sourceRecord = ""
		self.currList = "sources"
		self.currLabel = "source"
		self.changedTargetdata = []
		
		if cfg.debug.value:
			print "[RefreshBouquet] current bouquet: %s  changed bouquet: %s" % (self.current_bouquetname, self.target_bouquetname)
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
		self.session.openWithCallback(self.replaceTargetBouquet, MessageBox, (_("Are you sure to apply all %d changes and close?") % nr_items), MessageBox.TYPE_YESNO, default=False )

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
			self.session.openWithCallback(self.callBackExit, MessageBox, (_("Are you sure to close and lost all %d changes?") % nr_items), MessageBox.TYPE_YESNO, default=False )
		else:
			self.close()

	def callBackExit(self, answer):
		if answer == True:
			self.close()

# display results of refresh services
class refreshBouquetDisplayServices(Screen):
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
		<widget name="services" position="5,50" zPosition="2" size="705,450"  split="1" dividechar=":" colposition="300" font="Regular;22" foregroundColor="white" />
	</screen>"""

	def __init__(self, session, log):
		self.skin = refreshBouquetDisplayServices.skin
		Screen.__init__(self, session)
		self.setTitle(_("RefreshBouquet %s" % _("- results")))

		self["services"] = ScrollLabel(log)

		self["actions"] = ActionMap(["SetupActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"up": self["services"].pageUp,
				"down": self["services"].pageDown,
				"upRepeated": self["services"].pageUp,
				"downRepeated": self["services"].pageDown,
				"leftUp": self["services"].pageUp,
				"rightUp": self["services"].pageDown,
			})

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button()
		self["key_yellow"] = Button()
		self["key_blue"] = Button()

# copy services from source list
class refreshBouquetCopyServices(Screen):
	def __init__(self, session, list, target):
		self.skin = refreshBouquetDisplayServices.skin
		Screen.__init__(self, session)
		self.skinName = ["refreshBouquetDisplayServices", "refreshBouquetCopyServices"]

		self.setTitle(_("RefreshBouquet %s" % _("- select service(s) for adding with OK")))
		self.session = session

		self["Service"] = ServiceEvent()

		( self.target_bouquetname, self.target ) = target

		self.list = list
		if cfg.sort.value:
			self.list.sort()
		self["services"] = SelectionList()
		self["services"] = self.list

		self["actions"] = ActionMap(["OkCancelActions", "RefreshBouquetActions"],
			{
				"cancel": self.close,
				"ok": self.list.toggleSelection,
				"red": self.close,
				"green": self.copyCurrentEntries,
				"blue": self.list.toggleAllSelection,
				"yellow": self.previewService,
				"play": self.previewService,
			})

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Copy"))
		self["key_yellow"] = Button("")
		self["key_blue"] = Button(_("Inversion"))
		
		self.onSelectionChanged = []
		self["services"].onSelectionChanged.append(self.displayService)
		self.onLayoutFinish.append(self.displayService)

		if cfg.debug.value:
			print "[RefreshBouquet] current bouquet: %s  changed bouquet: %s" % (self.current_bouquetname, self.target_bouquetname)

#	def getCurrentEntry(self):
#		self.displayService()

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
#			self["Service"].newService(eServiceReference(ref))
			self.session.nav.playService(eServiceReference(ref))

	def copyCurrentEntries(self):
		nr_items = len(self.list.getSelectionsList())
		self.session.openWithCallback(self.copyToTarget, MessageBox, (_("Are you sure to copy this %d service(s)?") % nr_items), MessageBox.TYPE_YESNO, default=False )
		
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
			self.session.openWithCallback(self.callBackExit, MessageBox, (_("Are you sure to close and lost all %d selections?") % nr_items), MessageBox.TYPE_YESNO, default=False )
		else:
			self.close()

	def callBackExit(self, answer):
		if answer == True:
			self.close()

# remove services from source list
class refreshBouquetRemoveServices(Screen):
	def __init__(self, session, list, source):
		self.skin = refreshBouquetDisplayServices.skin
		Screen.__init__(self, session)
		self.skinName = ["refreshBouquetRemoveServices", "refreshBouquetDisplayServices"]
		self.setTitle(_("RefreshBouquet %s" % _("- select service(s) for remove with OK")))
		self.session = session

		( self.source_bouquetname, self.source ) = source

		self.list = list
		if cfg.sort.value:
			self.list.sort()
		self["services"] = SelectionList()
		self["services"] = self.list

		self["Service"] = ServiceEvent()

		self["actions"] = ActionMap(["OkCancelActions", "RefreshBouquetActions"],
			{
				"cancel": self.close,
				"ok": self.list.toggleSelection,
				"red": self.close,
				"green": self.removeCurrentEntries,
				"blue": self.list.toggleAllSelection,
				"yellow": self.previewService,
				"play": self.previewService,
			})

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Remove selected"))
		self["key_yellow"] = Button()
		self["key_blue"] = Button(_("Inversion"))
		
		self.onSelectionChanged = []
		self["services"].onSelectionChanged.append(self.displayService)
		self.onLayoutFinish.append(self.displayService)
		
		if cfg.debug.value:
			print "[RefreshBouquet] current bouquet: %s  changed bouquet: %s" % (self.current_bouquetname, self.source_bouquetname)

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
#			self["Service"].newService(eServiceReference(ref))
			self.session.nav.playService(eServiceReference(ref))

	def removeCurrentEntries(self):
		nr_items = len(self.list.getSelectionsList())
		self.session.openWithCallback(self.removeFromSource, MessageBox, (_("Are you sure to remove this %d service(s)?") % nr_items), MessageBox.TYPE_YESNO, default=False )

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
			self.session.openWithCallback(self.callBackExit, MessageBox, (_("Are you sure to close and lost all %d selections?") % nr_items), MessageBox.TYPE_YESNO, default=False )
		else:
			self.close()

	def callBackExit(self, answer):
		if answer == True:
			self.close()

# options
class refreshBouquetCfg(Screen, ConfigListScreen):
	skin = """
	<screen name="refreshBouquetCfg" position="center,center" size="560,380" title="RefreshBouquet Setup" >
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />

		<widget name="config" position="10,40" size="540,300" zPosition="1" transparent="0" scrollbarMode="showOnDemand" />

		<ePixmap pixmap="skin_default/div-h.png" position="0,355" zPosition="1" size="560,2" />
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
		self.skinName = ["Setup", "refreshBouquetCfg"]
		self.setup_title = _("RefreshBouquet Setup")
			
		self["key_green"] = Label(_("OK"))
		self["key_red"] = Label(_("Cancel"))
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
		refreshBouquetCfglist.append(getConfigListEntry(_("Programs with 'HD' in name only for source"), cfg.hd))
		refreshBouquetCfglist.append(getConfigListEntry(_("Preview on selection"), cfg.preview))
		refreshBouquetCfglist.append(getConfigListEntry(_("Auto toggle in manual replacing"), cfg.autotoggle))
		refreshBouquetCfglist.append(getConfigListEntry(_("Display in Channellist context menu"), cfg.channel_context_menu))
#		refreshBouquetCfglist.append(getConfigListEntry(_("Save log for manual replace"), cfg.log))
		refreshBouquetCfglist.append(getConfigListEntry(_("Debug info"), cfg.debug))
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

def freeMemory():
	import os
	os.system("sync")
	os.system("echo 3 > /proc/sys/vm/drop_caches")

def closed(ret=False):
	freeMemory()