
#  Quickbutton
#
#  $Id$
#
#  Coded by Dr.Best (c) 2009
#  Support: www.dreambox-tools.info
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

from Screens.Screen import Screen
from Screens.ChannelSelection import ChannelSelection
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.PluginComponent import plugins
from Plugins.Plugin import PluginDescriptor
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import ConfigSubsection, ConfigText, configfile, ConfigSelection, getConfigListEntry
from Components.config import config
from Components.Button import Button
from Screens.MessageBox import MessageBox
from Tools.HardwareInfo import HardwareInfo
# for localized messages
from . import _

config.plugins.Quickbutton = ConfigSubsection()
config.plugins.Quickbutton.red = ConfigText(default = _("Nothing"), visible_width = 50, fixed_size = False)
config.plugins.Quickbutton.red_b = ConfigText(default = _("Nothing"), visible_width = 50, fixed_size = False)
config.plugins.Quickbutton.green = ConfigText(default = _("Nothing"), visible_width = 50, fixed_size = False)
config.plugins.Quickbutton.yellow = ConfigText(default = _("Nothing"), visible_width = 50, fixed_size = False)
config.plugins.Quickbutton.blue = ConfigText(default = _("Nothing"), visible_width = 50, fixed_size = False)


from  Screens.InfoBarGenerics import InfoBarPlugins
baseInfoBarPlugins__init__ = None
DM8000 = False

def autostart(reason, **kwargs):
	global baseInfoBarPlugins__init__,DM8000
	if "session" in kwargs:
		session = kwargs["session"]
		if baseInfoBarPlugins__init__ is None:
			baseInfoBarPlugins__init__ = InfoBarPlugins.__init__
		InfoBarPlugins.__init__ = InfoBarPlugins__init__
		InfoBarPlugins.greenlong = greenlong
		InfoBarPlugins.yellowlong = yellowlong
		InfoBarPlugins.redlong = redlong
		InfoBarPlugins.bluelong = bluelong
		if HardwareInfo().get_device_name() == "dm8000":
			DM8000 = True		
			InfoBarPlugins.red = red

def setup(session,**kwargs):
	session.open(QuickbuttonSetup)

def Plugins(**kwargs):

	list = [PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc = autostart)]	
	list.append(PluginDescriptor(name="Setup Quickbutton", description=_("setup for Quickbutton"), where = [PluginDescriptor.WHERE_PLUGINMENU], fnc=setup))
	return list

def InfoBarPlugins__init__(self):
	from Screens.InfoBarGenerics import InfoBarEPG
	if isinstance(self, InfoBarEPG):
		x = {	"green_l": (self.greenlong, _("Assign plugin to long green key pressed")),
			"yellow_l": (self.yellowlong, _("Assign plugin to long yellow key pressed")),
			"red_l": (self.redlong, _("Assign plugin to long red key pressed")),
			"blue_l": (self.bluelong, _("Assign plugin to long blue key pressed"))}
		if DM8000:
			x["red_b"] = (self.red, _("Assign plugin to red key pressed"))
		self["QuickbuttonActions"] = HelpableActionMap(self, "QuickbuttonActions",x)
	else:
		InfoBarPlugins.__init__ = InfoBarPlugins.__init__
		InfoBarPlugins.greenlong = None
		InfoBarPlugins.yellowlong = None
		InfoBarPlugins.redlong = None
		InfoBarPlugins.bluelong = None
		if DM8000:
			InfoBarPlugins.red = None
	baseInfoBarPlugins__init__(self)

def greenlong(self):
	startPlugin(self,str(config.plugins.Quickbutton.green.value))

def yellowlong(self):
	startPlugin(self, str(config.plugins.Quickbutton.yellow.value))

def redlong(self):
	startPlugin(self, str(config.plugins.Quickbutton.red.value))

def bluelong(self):
	startPlugin(self, str(config.plugins.Quickbutton.blue.value))

def red(self):
	startPlugin(self, str(config.plugins.Quickbutton.red_b.value))

def startPlugin(self,pname):
	msgText = _("Unknown Error")
	no_plugin = True
	if pname != _("Nothing"):
		if pname == _("Single EPG"):
			from Screens.InfoBarGenerics import InfoBarEPG
			if isinstance(self, InfoBarEPG):
				self.openSingleServiceEPG()
			no_plugin = False
		elif pname == _("Multi EPG"):
			from Screens.InfoBarGenerics import InfoBarEPG
			if isinstance(self, InfoBarEPG):
				self.openMultiServiceEPG()
			no_plugin = False
		elif pname == _("MediaPlayer"):
			try: # falls es nicht installiert ist
				from Plugins.Extensions.MediaPlayer.plugin import MediaPlayer
				self.session.open(MediaPlayer)
				no_plugin = False
			except Exception, e:
				msgText = _("Error!\nError Text: %s"%e)
		elif pname == _("Plugin browser"):
			from Screens.PluginBrowser import PluginBrowser
			self.session.open(PluginBrowser)
			no_plugin = False
		elif pname == _("switch 4:3 content display"):
			ar = {	"pillarbox": _("Pillarbox"), 
				"panscan": _("Pan&Scan"),  
				"scale": _("Just Scale")}
			switch = { "pillarbox":"panscan", "panscan":"scale", "scale":"pillarbox" }
			config.av.policy_43.value =  switch[config.av.policy_43.value]
			config.av.policy_43.save()
			self.session.open(MessageBox,_("Display 4:3 content as") + " " + ar[config.av.policy_43.value], MessageBox.TYPE_INFO, timeout = 3)
			no_plugin = False
		elif pname == _("Timer"):
			from Screens.TimerEdit import TimerEditList
			self.session.open(TimerEditList)
			no_plugin = False
		else:
			plugin = None
			for p in plugins.getPlugins(where = [PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU]):
				if pname == str(p.name):
					plugin = p
			if plugin is not None:
				try:
					self.runPlugin(plugin)
					no_plugin = False
				except Exception, e:
					msgText = _("Error!\nError Text: %s"%e)
			else: 
				msgText = _("Plugin not found!")
	else:
		msgText = _("No plugin assigned!")
	if no_plugin:
		self.session.open(MessageBox,msgText, MessageBox.TYPE_INFO)


class QuickbuttonSetup(ConfigListScreen, Screen):
	skin = """
		<screen position="center,center" size="550,400" title="Quickbutton Setup" >
			<widget name="config" position="20,10" size="510,330" scrollbarMode="showOnDemand" />
			<widget name="key_red" position="0,350" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>
			<widget name="key_green" position="140,350" size="140,40" valign="center" halign="center" zPosition="5" transparent="1" foregroundColor="white" font="Regular;18"/>
			<ePixmap name="red" pixmap="skin_default/buttons/red.png" position="0,350" size="140,40" zPosition="4" transparent="1" alphatest="on"/>
			<ePixmap name="green" pixmap="skin_default/buttons/green.png" position="140,350" size="140,40" zPosition="4" transparent="1" alphatest="on"/>
		</screen>"""

	def __init__(self, session, args = None):
		Screen.__init__(self, session)
		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("OK"))
		self.entryguilist = []
		red_b_selectedindex = self.getStaticPluginName(config.plugins.Quickbutton.red_b.value)
		red_selectedindex = self.getStaticPluginName(config.plugins.Quickbutton.red.value)
		green_selectedindex = self.getStaticPluginName(config.plugins.Quickbutton.green.value)
		yellow_selectedindex = self.getStaticPluginName(config.plugins.Quickbutton.yellow.value)
		blue_selectedindex = self.getStaticPluginName(config.plugins.Quickbutton.blue.value)
		# feste Vorgaben...koennte man noch erweitern, da hole ich mir sinnvolle Vorschlaege aus Foren noch ein...
		self.entryguilist.append(("0",_("Nothing")))
		self.entryguilist.append(("1",_("Single EPG")))
		self.entryguilist.append(("2",_("Multi EPG")))
		self.entryguilist.append(("3",_("MediaPlayer")))
		self.entryguilist.append(("4",_("Plugin browser")))
		self.entryguilist.append(("5",_("switch 4:3 content display")))
		self.entryguilist.append(("6",_("Timer")))
		# Vorgaben aus EXTENSIONSMENU, PLUGINMENU
		index = 7
		for p in plugins.getPlugins(where = [PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_PLUGINMENU]):
			self.entryguilist.append((str(index),str(p.name)))
			if config.plugins.Quickbutton.red.value == str(p.name):
				red_selectedindex = str(index)
			if config.plugins.Quickbutton.red_b.value == str(p.name):
				red_b_selectedindex = str(index)
			if config.plugins.Quickbutton.green.value == str(p.name):
				green_selectedindex = str(index)
			if config.plugins.Quickbutton.yellow.value == str(p.name):
				yellow_selectedindex = str(index)
			if config.plugins.Quickbutton.blue.value == str(p.name):
				blue_selectedindex = str(index)
			index = index + 1

		self.redchoice = ConfigSelection(default = red_selectedindex, choices = self.entryguilist)
		self.greenchoice = ConfigSelection(default = green_selectedindex, choices = self.entryguilist)
		self.yellowchoice = ConfigSelection(default = yellow_selectedindex, choices = self.entryguilist)
		self.bluechoice = ConfigSelection(default = blue_selectedindex, choices = self.entryguilist)
		cfglist = [
			getConfigListEntry(_("assigned to long red"), self.redchoice),
			getConfigListEntry(_("assigned to long green"), self.greenchoice),
			getConfigListEntry(_("assigned to long yellow"), self.yellowchoice),
			getConfigListEntry(_("assigned to long blue"), self.bluechoice)

			]
		if DM8000:
			self.red_b_choice = ConfigSelection(default = red_b_selectedindex, choices = self.entryguilist)
			cfglist.append(getConfigListEntry(_("assigned to red"), self.red_b_choice))
		ConfigListScreen.__init__(self, cfglist, session)
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
		{
			"green": self.keySave,
			"cancel": self.keyClose,
			"ok": self.keySave,
		}, -2)

	def getStaticPluginName(self,value):
		if value == _("Single EPG"):
			return "1"
		elif value == _("Multi EPG"):
			return "2"
		elif value == _("MediaPlayer"):
			return "3"
		elif value == _("Plugin browser"):
			return "4"
		elif value == _("switch 4:3 content display"):
			return "5"
		if value == _("Timer"):
			return "6"
		else:
			return "0"

	def keySave(self):
		config.plugins.Quickbutton.red.value = self.entryguilist[int(self.redchoice.value)][1]
		config.plugins.Quickbutton.green.value = self.entryguilist[int(self.greenchoice.value)][1]
		config.plugins.Quickbutton.yellow.value = self.entryguilist[int(self.yellowchoice.value)][1]
		config.plugins.Quickbutton.blue.value = self.entryguilist[int(self.bluechoice.value)][1]
		if DM8000:
			config.plugins.Quickbutton.red_b.value = self.entryguilist[int(self.red_b_choice.value)][1]
		config.plugins.Quickbutton.save()
		configfile.save()
		self.close()

	def keyClose(self):
		self.close()
