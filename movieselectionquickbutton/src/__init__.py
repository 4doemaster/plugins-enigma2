# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
	gettext.bindtextdomain("MovieSelectionQuickButton", resolveFilename(SCOPE_PLUGINS, "Extensions/MovieSelectionQuickButton/locale"))

def _(txt):
	t = gettext.dgettext("MovieSelectionQuickButton", txt)
	if t == txt:
		print "[MovieSelectionQuickButton] fallback to default translation for", txt
		t = gettext.gettext(txt)
	return t

localeInit()
language.addCallback(localeInit)

