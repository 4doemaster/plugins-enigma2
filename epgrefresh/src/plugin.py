from __future__ import print_function

# for localized messages
from . import _

# Config
from Components.config import config, ConfigYesNo, ConfigNumber, \
	ConfigSelection, ConfigSubsection, ConfigClock, ConfigYesNo

# Calculate default begin/end
from time import time, localtime, mktime
now = localtime()
begin = mktime((
	now.tm_year, now.tm_mon, now.tm_mday, 20, 15, \
	0, now.tm_wday, now.tm_yday, now.tm_isdst)
)
end = mktime((
	now.tm_year, now.tm_mon, now.tm_mday, 06, 30, \
	0, now.tm_wday, now.tm_yday, now.tm_isdst)
)

#Configuration
config.plugins.epgrefresh = ConfigSubsection()
config.plugins.epgrefresh.enabled = ConfigYesNo(default = False)
config.plugins.epgrefresh.begin = ConfigClock(default = int(begin))
config.plugins.epgrefresh.end = ConfigClock(default = int(end))
config.plugins.epgrefresh.interval = ConfigNumber(default = 2)
config.plugins.epgrefresh.delay_standby = ConfigNumber(default = 10)
config.plugins.epgrefresh.inherit_autotimer = ConfigYesNo(default = False)
config.plugins.epgrefresh.afterevent = ConfigYesNo(default = False)
config.plugins.epgrefresh.force = ConfigYesNo(default = False)
config.plugins.epgrefresh.enablemessage = ConfigYesNo(default = True)
config.plugins.epgrefresh.wakeup = ConfigYesNo(default = False)
config.plugins.epgrefresh.lastscan = ConfigNumber(default = 0)
config.plugins.epgrefresh.parse_autotimer = ConfigYesNo(default = False)
config.plugins.epgrefresh.adapter = ConfigSelection(choices = [
		("main", _("Main Picture")),
		("pip", _("Picture in Picture")),
		("pip_hidden", _("Picture in Picture (hidden)")),
		("record", _("Fake recording")),
	], default = "main"
)
config.plugins.epgrefresh.show_in_extensionsmenu = ConfigYesNo(default = False)
config.plugins.epgrefresh.show_help = ConfigYesNo(default = True)

# convert previous parameter
config.plugins.epgrefresh.background = ConfigYesNo(default = False)
if config.plugins.epgrefresh.background.value:
	config.plugins.epgrefresh.adapter.value = "pip_hidden"
	config.plugins.epgrefresh.background.value = False
	config.plugins.epgrefresh.save()

del now, begin, end

#pragma mark - Workaround for unset clock

from enigma import eDVBLocalTimeHandler

def timeCallback(isCallback=True):
	"""Time Callback/Autostart management."""
	thInstance = eDVBLocalTimeHandler.getInstance()
	if isCallback:
		# NOTE: this assumes the clock is actually ready when called back
		# this may not be true, but we prefer silently dying to waiting forever
		thInstance.m_timeUpdated.get().remove(timeCallback)
	elif not thInstance.ready():
		thInstance.m_timeUpdated.get().append(timeCallback)
		return

	if config.plugins.epgrefresh.wakeup.value:
		now = localtime()
		begin = int(mktime(
			(now.tm_year, now.tm_mon, now.tm_mday,
			config.plugins.epgrefresh.begin.value[0],
			config.plugins.epgrefresh.begin.value[1],
			0, now.tm_wday, now.tm_yday, now.tm_isdst)
		))
		# booted +- 10min from begin of timespan
		if abs(time() - begin) < 600:
			from Screens.MessageBox import MessageBox
			from Tools.Notifications import AddNotificationWithCallback
			from Tools.BoundFunction import boundFunction
			# XXX: we use a notification because this will be suppressed otherwise
			AddNotificationWithCallback(
				boundFunction(standbyQuestionCallback, epgrefresh.session),
				MessageBox,
				_("This might have been an automated bootup to refresh the EPG. For this to happen it is recommended to put the receiver to Standby.\nDo you want to do this now?"),
				timeout = 15
			)
	epgrefresh.start()

#pragma mark - Help
try:
	from Plugins.SystemPlugins.MPHelp import registerHelp, XMLHelpReader
	from Tools.Directories import resolveFilename, SCOPE_PLUGINS
	reader = XMLHelpReader(resolveFilename(SCOPE_PLUGINS, "Extensions/EPGRefresh/mphelp.xml"))
	epgrefreshHelp = registerHelp(*reader)
except Exception as e:
	print("[EPGRefresh] Unable to initialize MPHelp:", e,"- Help not available!")
	epgrefreshHelp = None
#pragma mark -

# Plugin
from EPGRefresh import epgrefresh
from EPGRefreshConfiguration import EPGRefreshConfiguration
from EPGRefreshService import EPGRefreshService

# Plugins
from Components.PluginComponent import plugins
from Plugins.Plugin import PluginDescriptor

def standbyQuestionCallback(session, res = None):
	if res:
		from Screens.Standby import Standby
		session.open(Standby)

# Autostart
def autostart(reason, **kwargs):
	if reason == 0 and "session" in kwargs:
		session = kwargs["session"]
		epgrefresh.session = session

		if config.plugins.epgrefresh.enabled.value:
			timeCallback(isCallback=False)

	elif reason == 1:
		epgrefresh.stop()

def getNextWakeup():
	# Return invalid time if not automatically refreshing
	if not config.plugins.epgrefresh.enabled.value or \
		not config.plugins.epgrefresh.wakeup.value:

		return -1

	now = localtime()
	begin = int(mktime(
		(now.tm_year, now.tm_mon, now.tm_mday,
		config.plugins.epgrefresh.begin.value[0],
		config.plugins.epgrefresh.begin.value[1],
		0, now.tm_wday, now.tm_yday, now.tm_isdst)
	))
	# todays timespan has not yet begun
	if begin > time():
		return begin
	# otherwise add 1 day
	return begin+86400

# Mainfunction
def main(session, **kwargs):
	epgrefresh.stop()
	session.openWithCallback(
		doneConfiguring,
		EPGRefreshConfiguration
	)

def doneConfiguring(session, **kwargs):
	if config.plugins.epgrefresh.enabled.value:
		epgrefresh.start(session)

# Eventinfo
def eventinfo(session, servicelist, **kwargs):
	ref = session.nav.getCurrentlyPlayingServiceReference()
	if not ref:
		return
	sref = ref.toString()
	# strip all after last :
	pos = sref.rfind(':')
	if pos != -1:
		sref = sref[:pos+1]

	epgrefresh.services[0].add(EPGRefreshService(str(sref), None))

# XXX: we need this helper function to identify the descriptor
# Extensions menu
def extensionsmenu(session, **kwargs):
	main(session, **kwargs)

def housekeepingExtensionsmenu(el):
	if el.value:
		plugins.addPlugin(extDescriptor)
	else:
		try:
			plugins.removePlugin(extDescriptor)
		except ValueError as ve:
			print("[EPGRefresh] housekeepingExtensionsmenu got confused, tried to remove non-existant plugin entry... ignoring.")

config.plugins.epgrefresh.show_in_extensionsmenu.addNotifier(housekeepingExtensionsmenu, initial_call = False, immediate_feedback = True)
extDescriptor = PluginDescriptor(name="EPGRefresh", description = _("Automatically refresh EPG"), where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc = extensionsmenu, needsRestart=False)

def Plugins(**kwargs):
	# NOTE: this might be a little odd to check this, but a user might expect
	# the plugin to resume normal operation if installed during runtime, but
	# this is not given if the plugin is supposed to run in background (as we
	# won't be handed the session which we need to zap). So in turn we require
	# a restart if-and only if-we're installed during runtime AND running in
	# background. To improve the user experience in this situation, we hide
	# all references to this plugin.
	needsRestart = config.plugins.epgrefresh.enabled.value and not plugins.firstRun
	list = [
		PluginDescriptor(
			name = "EPGRefresh",
			where = [
				PluginDescriptor.WHERE_AUTOSTART,
				PluginDescriptor.WHERE_SESSIONSTART
			],
			fnc = autostart,
			wakeupfnc = getNextWakeup,
			needsRestart = needsRestart,
		),
		PluginDescriptor(
			name = _("add to EPGRefresh"),
			where = PluginDescriptor.WHERE_EVENTINFO,
			fnc = eventinfo,
			needsRestart = needsRestart,
		),
		PluginDescriptor(
			name = "EPGRefresh",
			description = _("Automatically refresh EPG"),
			where = PluginDescriptor.WHERE_PLUGINMENU, 
			fnc = main,
			needsRestart = needsRestart,
		),
	]
	if config.plugins.epgrefresh.show_in_extensionsmenu.value:
		extDescriptor.needsRestart = needsRestart
		list.append(extDescriptor)

	return list
