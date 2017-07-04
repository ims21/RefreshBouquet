# -*- coding: utf-8 -*-
# for localized messages  	 
from . import _
#
#  Refresh Bouqurt - Plugin E2 for OpenPLi
#
#  by ims (c) 2016-2017 ims21@users.sourceforge.net
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
from Components.config import ConfigSubsection, config, ConfigYesNo

config.plugins.refreshbouquet = ConfigSubsection()
config.plugins.refreshbouquet.channel_context_menu = ConfigYesNo(default = True)

plugin_path = None

def main(session, servicelist=None, **kwargs):
	import Screens.InfoBar
	Servicelist = servicelist or Screens.InfoBar.InfoBar.instance.servicelist
	currentBouquet = Servicelist and Servicelist.getRoot()
	if currentBouquet is not None:
		import ui
		ui.setPluginCatalog() # for prlugin's xgettext catalog
		session.openWithCallback(ui.closed, ui.refreshBouquet, Servicelist, currentBouquet)

def Plugins(path,**kwargs):
	global plugin_path
	plugin_path = path
	name= _("RefreshBouquet")
	descr=_("Actualize services in bouquets")
	list = [PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_PLUGINMENU, icon = "refreshbouquet.png", needsRestart = False, fnc=main)]
	if config.plugins.refreshbouquet.channel_context_menu.value:
		list.append(PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_CHANNEL_CONTEXT_MENU, needsRestart = False, fnc=main))
	return list
