from Plugins.Extensions.WebInterface.WebChilds.Toplevel import addExternalChild
from Plugins.Extensions.AutoTimer.AutoTimerResource import AutoTimerDoParseResource, \
	AutoTimerListAutoTimerResource, AutoTimerAddOrEditAutoTimerResource, \
	AutoTimerRemoveAutoTimerResource, AutoTimerChangeSettingsResource, \
	AutoTimerSettingsResource, API_VERSION

root = AutoTimerListAutoTimerResource()
root.putChild('parse', AutoTimerDoParseResource())
root.putChild('remove', AutoTimerRemoveAutoTimerResource())
root.putChild('edit', AutoTimerAddOrEditAutoTimerResource())
root.putChild('get', AutoTimerSettingsResource())
root.putChild('set', AutoTimerChangeSettingsResource())
addExternalChild( ("autotimer", root , "AutoTimer-Plugin", API_VERSION) )

