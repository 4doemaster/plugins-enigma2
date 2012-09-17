# -*- coding: utf-8 -*-
'''
general functions for FritzCall plugin
'''
from Components.config import config #@UnresolvedImport
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE #@UnresolvedImport
import gettext, os
from enigma import eBackgroundFileEraser

def localeInit():
	gettext.bindtextdomain("FritzCall", resolveFilename(SCOPE_PLUGINS, "Extensions/FritzCall/locale/"))

localeInit()
language.addCallback(localeInit)

def _(txt): # pylint: disable-msg=C0103
	td = gettext.dgettext("FritzCall", txt)
	if td == txt:
		td = gettext.gettext(txt)
	return td

def initDebug():
	try:
		# os.remove("/tmp/FritzDebug.log")
		eBackgroundFileEraser.getInstance().erase("/tmp/FritzDebug.log")
	except OSError:
		pass

from time import localtime
def debug(message):
	if config.plugins.FritzCall.debug.value:
		try:
			# ltim = localtime()
			# headerstr = u"%04d%02d%02d %02d:%02d " %(ltim[0],ltim[1],ltim[2],ltim[3],ltim[4])
			deb = open("/tmp/FritzDebug.log", "aw")
			# deb.write(headerstr + message.decode('utf-8') + u"\n")
			deb.write(message + "\n")
			deb.close()
		except Exception, e:
			debug("%s (retried debug: %s)" % (repr(message), str(e)))
		

import re
def normalizePhoneNumber(intNo):
	
	found = re.match('^\+' + config.plugins.FritzCall.country.value.replace('00','') + '(.*)', intNo)
	if found:
		intNo = '0' + found.group(1)
	found = re.match('^\+(.*)', intNo)
	if found:
		intNo = '00' + found.group(1)
	intNo = intNo.replace('(', '').replace(')', '').replace(' ', '').replace('/', '').replace('-', '')
	found = re.match('^49(.*)', intNo) # this is most probably an error
	if found:
		intNo = '0' + found.group(1)
	found = re.match('.*?([0-9]+)', intNo)
	if found:
		return found.group(1)
	else:
		return '0'
