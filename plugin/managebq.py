#
#  RefreshBouquet
#
#
#  Coded by ims (c) 2016-2022
#  Support: openpli.org
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
# for localized messages

from . import _

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Button import Button
from Components.Label import Label
from Components.ActionMap import ActionMap
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from Screens.ChoiceBox import ChoiceBox
from Components.config import config
from enigma import eDVBDB
import skin
import os
from .ui import E2, cfg
from .ui import MySelectionList
from .ui import setIcon


class refreshBouquetManageDeletedBouquets(Screen):
	skin = """
		<screen name="refreshBouquetManageDeletedBouquets" position="center,center" size="560,410" title="refreshBouquet - manage deleted bouquets">
		<ePixmap name="red" position="0,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on"/>
		<ePixmap name="green" position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on"/>
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on"/>
		<ePixmap name="blue" position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on"/>
		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2"/>
		<widget name="config" position="5,50" zPosition="2" size="550,300" itemHeight="30" font="Regular;20" foregroundColor="white" scrollbarMode="showOnDemand"/>
		<ePixmap pixmap="skin_default/div-h.png" position="5,355" zPosition="2" size="545,2"/>
		<widget name="text" position="5,360" zPosition="2" size="550,50" valign="center" halign="left" font="Regular;20" foregroundColor="white"/>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session

		self.skin = refreshBouquetManageDeletedBouquets.skin
		self.skinName = ["refreshBouquetManageDeletedBouquets"]

		self.setTitle(_("Manage deleted bouquets"))

		setIcon(True)

		data = MySelectionList([])
		nr = 0
		for x in os.listdir(E2):
			if x.startswith("userbouquet") and x.endswith(".del"):
				data.addSelection(self.fileName(x), "%s/%s" % (E2, x), nr, False)
				nr += 1
		self.list = data
		self.list.sort()

		self["config"] = self.list
		self["text"] = Label()

		self["actions"] = ActionMap(["OkCancelActions", "RefreshBouquetActions"],
			{
				"cancel": self.exit,
				"ok": self.toggleSelection,
				"red": self.exit,
				"green": self.restoreCurrentEntries,
				"yellow": self.removeCurrentEntries,
				"blue": self.list.toggleAllSelection,
			})

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Restore"))
		self["key_yellow"] = Button(_("Remove"))
		self["key_blue"] = Button(_("Inversion"))

		self["text"].setText(_("On deleted userbouquet press 'Restore' or 'Remove' or mark more deleted bouquets with 'OK' and then use 'Restore' or 'Remove'."))

	def toggleSelection(self):
		self.list.toggleSelection()
		if cfg.move_selector.value:
			idx = self.list.list.index(self["config"].getCurrent())
			self["config"].moveToIndex(idx+1)

	def removeCurrentEntries(self):
		marked = len(self.list.getSelectionsList())
		if marked:
			text = _("Are you sure to remove %s selected deleted bouquets?") % marked
		else:
			text = _("Are you sure to remove deleted userbouquet?\n\n%s") % self.fileName(self["config"].getCurrent()[0][1])
		self.session.openWithCallback(self.removeFromSource, MessageBox, text, MessageBox.TYPE_YESNO, default=False)

	def removeFromSource(self, answer):
		if answer == True:
			data = self.list.getSelectionsList()
			if data:
				for i in data:
					os.unlink(i[1])
					self.list.removeSelection(i)
			else:
				os.unlink(self["config"].getCurrent()[0][1])
				self.list.removeSelection(self["config"].getCurrent()[0])
		if not len(self.list.list):
			self.exit()

	def restoreCurrentEntries(self):
		marked = len(self.list.getSelectionsList())
		if marked:
			text = _("Are you sure to restore %s selected deleted bouquets?") % marked
		else:
			text = _("Are you sure to restore deleted userbouquet?\n\n%s") % self.fileName(self["config"].getCurrent()[0][1])
		self.session.openWithCallback(self.restoreSelected, MessageBox, text, MessageBox.TYPE_YESNO, default=False)

	def restoreSelected(self, answer):
		if answer == True:
			data = self.list.getSelectionsList()
			if data:
				for i in data:
					os.rename(i[1], i[1][:-4])
					self.list.removeSelection(i)
			else:
				name = self["config"].getCurrent()[0][1]
				os.rename(name, name[:-4])
				self.list.removeSelection(self["config"].getCurrent()[0])
			eDVBDBInstance = eDVBDB.getInstance()
			eDVBDBInstance.setLoadUnlinkedUserbouquets(True)
			eDVBDBInstance.reloadBouquets()
			eDVBDBInstance.setLoadUnlinkedUserbouquets(config.misc.load_unlinked_userbouquets.value)
		if not self.list.len():
			self.exit()

	def fileName(self, filename):
		if cfg.deleted_bq_fullname.value:
			return filename
		return filename.split('.')[1]

	def exit(self):
		self.close()
