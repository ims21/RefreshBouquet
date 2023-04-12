# -*- coding: utf-8 -*-
# for localized messages  	 
from . import _
#
#  Refresh Bouqurt - Plugin E2 for OpenPLi
#
#  by ims (c) 2016-2023 ims21@users.sourceforge.net
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

from Plugins.Plugin import PluginDescriptor
from Components.config import ConfigSubsection, config, ConfigYesNo, ConfigSelection

config.plugins.refreshbouquet = ConfigSubsection()
config.plugins.refreshbouquet.channel_context_menu = ConfigYesNo(default=True)
config.plugins.refreshbouquet.case_sensitive = ConfigYesNo(default=False)
config.plugins.refreshbouquet.autotoggle = ConfigYesNo(default=True)
config.plugins.refreshbouquet.diff = ConfigYesNo(default=False)
config.plugins.refreshbouquet.preview = ConfigYesNo(default=False)
config.plugins.refreshbouquet.confirm_move = ConfigYesNo(default=True)
config.plugins.refreshbouquet.on_end = ConfigYesNo(default=True)
choicelist = []
for i in range(1, 11, 1):
	choicelist.append(("%d" % i, "%d" % i))
choicelist.append(("15","15"))
choicelist.append(("20","20"))
config.plugins.refreshbouquet.vk_length = ConfigSelection(default="3", choices=[("0", _("No"))] + choicelist + [("255", _("All"))])
config.plugins.refreshbouquet.vk_sensitive = ConfigYesNo(default=False)
config.plugins.refreshbouquet.move_selector = ConfigYesNo(default=False)
config.plugins.refreshbouquet.debug = ConfigYesNo(default=False)

plugin_path = None

def main(session, servicelist=None, **kwargs):
	import Screens.InfoBar
	from . import ui
	Servicelist = servicelist or Screens.InfoBar.InfoBar.instance.servicelist
	currentBouquet = Servicelist and Servicelist.getRoot()
	if currentBouquet is not None:
		session.openWithCallback(ui.closed, ui.refreshBouquet, Servicelist, currentBouquet)

def Plugins(path, **kwargs):
	global plugin_path
	plugin_path = path
	name = _("RefreshBouquet")
	descr = _("Actualize services in bouquets")
	plugin = [PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_PLUGINMENU, icon="refreshbouquet.png", needsRestart=False, fnc=main)]
	if config.plugins.refreshbouquet.channel_context_menu.value:
		plugin.append(PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_CHANNEL_CONTEXT_MENU, needsRestart=False, fnc=main))
	return plugin
