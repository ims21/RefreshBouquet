#
#  RefreshBouquet
#
#
#  Coded by ims (c) 2018
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
from Components.Button import Button
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.SelectionList import SelectionList
import skin
import os

class refreshBouquetRbbManager(Screen):
	skin = """
		<screen name="refreshBouquetRbbManager" position="center,center" size="560,410" title="RefreshBouquet - rbb files">
		<ePixmap name="red"    position="0,0"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
		<ePixmap name="green"  position="140,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />
		<ePixmap name="yellow" position="280,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />
		<ePixmap name="blue"   position="420,0" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />
		<widget name="key_red" position="0,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_green" position="140,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" /> 
		<widget name="key_yellow" position="280,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="key_blue" position="420,0" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;20" transparent="1" shadowColor="background" shadowOffset="-2,-2" />
		<widget name="config" position="5,50" zPosition="2" size="550,300" itemHeight="30" font="Regular;20" foregroundColor="white" scrollbarMode="showOnDemand" />
		<ePixmap pixmap="skin_default/div-h.png" position="5,355" zPosition="2" size="545,2" />
		<widget name="text" position="5,360" zPosition="2" size="550,50" valign="center" halign="left" font="Regular;20" foregroundColor="white" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.setTitle(_("Select rbb file"))

		data = SelectionList([])
		nr = 0
		for x in os.listdir("/etc/enigma2"):
			if x.endswith(".rbb"):
				data.addSelection(x, "/etc/enigma2/%s" % x, nr, False)
				nr += 1

		self.list = data
		self.list.sort()

		self["config"] = self.list
		self["text"] = Label()

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
			{
				"cancel": self.exit,
				"ok": self.ok,
				"red": self.exit,
			})

		self["key_red"] = Button(_("Cancel"))
		text = _("Select rbb file with 'OK' and create bouquet with same name.")
		text += _("If You will add to bouquet some missing services (start with '---'), You can then finalize created bouquet with '%s' etc.") % _("Manually replace services")
		self["text"].setText(text)

	def ok(self):
		if self["config"].getCurrent():
			self.close(self["config"].getCurrent()[0][0].split('.')[0])

	def exit(self):
		self.close(False)
