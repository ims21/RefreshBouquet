# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
	gettext.bindtextdomain("RefreshBouquet", resolveFilename(SCOPE_PLUGINS, "Extensions/RefreshBouquet/locale"))

def _(txt):
	t = gettext.dgettext("RefreshBouquet", txt)
	if t == txt:
		#print "[RefreshBouquet] fallback to default translation for", txt
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)
