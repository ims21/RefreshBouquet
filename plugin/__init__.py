# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from os import environ as os_environ
import gettext

def localeInit():
	localedir = resolveFilename(SCOPE_PLUGINS, "Extensions/RefreshBouquet/locale")
	gettext.bindtextdomain('RefreshBouquet', localedir)

def _(txt):
	t = gettext.dgettext("RefreshBouquet", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def ngettext(singular, plural, n):
	t = gettext.dngettext('RefreshBouquet', singular, plural, n)
	if t in (singular, plural):
		t = gettext.ngettext(singular, plural, n)
	return t

localeInit()
language.addCallback(localeInit)
