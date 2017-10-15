from __future__ import unicode_literals
from resources.lib.modules.addon import Addon
import sys,os
import urlparse,urllib
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from resources.lib.modules import control,myLists,client
from resources.lib.modules.log_utils import log
import re

addon = Addon('plugin.video.castback', sys.argv)
addon_handle = int(sys.argv[1])

if not os.path.exists(control.dataPath):
	os.mkdir(control.dataPath)

AddonPath = addon.get_path()
IconPath = os.path.join(AddonPath , "resources/media/")
fanart = os.path.join(AddonPath + "/fanart.jpg")
def icon_path(filename):
	if 'http://' in filename:
		return filename
	return os.path.join(IconPath, filename)

args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)


# if mode is None:
	
	# sources = os.listdir(AddonPath + '/resources/lib/sources/live_sport')
	# sources.remove('__init__.py')
	# for source in sources:
		# if '.pyo' not in source and '__init__' not in source:
			# try:
				# source = source.replace('.py','')
				# exec "from resources.lib.sources.live_sport import %s"%source
				# info = eval(source+".info()")
				# addon.add_item({'mode': 'open_site_content', 'site': info.mode}, {'title': info.name}, img=icon_path(info.icon), fanart=fanart,is_folder=True)
			# except:
				# pass
	
	# addon.end_of_directory()
	# from resources.lib.modules import cache, control, changelog
	# cache.get(changelog.get, 600000000, control.addonInfo('version'), table='changelog')

	
# elif mode[0] == 'open_site_content':
if mode is None:
	
	# site = args['site'][0]
	site = "livetv"
	
	exec "from resources.lib.sources.live_sport import %s"%site
	info = eval(site+".info()")
	
	source = eval(site+".main()")
	categories  = source.categories()
	for cat in categories:
		addon.add_item({'mode': 'open_sport_cat', 'url': cat[0], 'site': info.mode, 'title': cat[1]}, {'title': cat[1]}, img=icon_path(cat[2]), fanart=fanart,is_folder=True)

	addon.end_of_directory()

elif mode[0]=='open_sport_cat':
	url = args['url'][0]
	site = args['site'][0]
	exec "from resources.lib.sources.live_sport import %s"%site
	info = eval(site+".info()")
	source = eval(site+".main()")
	events = source.events(url)
	for event in events:
		addon.add_item({'mode': 'get_sport_event', 'url': event[0],'site':site , 'title':event[1], 'img': icon_path(info.icon)}, {'title': event[1]}, img=icon_path(info.icon), fanart=fanart,is_folder=True)
		
	
	addon.end_of_directory()	
	
elif mode[0]=='get_sport_event':
	
	url = args['url'][0]
	title = args['title'][0]
	site = args['site'][0]
	img = args['img'][0]
	exec "from resources.lib.sources.live_sport import %s"%site
	info = eval(site+".info()")
	source = eval(site+".main()")
	events = source.links(url)

	autoplay = addon.get_setting('autoplay')
	if autoplay == 'false':
		for event in events:
			browser = 'plugin://plugin.program.chrome.launcher/?url=%s&mode=showSite&stopPlayback=no'%(event[0])
			context = [('Open in browser','RunPlugin(%s)'%browser)]
			addon.add_video_item({'mode': 'play_special_sport', 'url': event[0],'title':title, 'img': img,'site':site}, {'title': event[1]}, img=img, fanart=fanart, contextmenu_items=context)
		addon.end_of_directory()
	else:
		for event in events:
			import liveresolver
			try:
				resolved = liveresolver.resolve(event[0])
			except:
				resolved = None
			if resolved:
				player=xbmc.Player()
				li = xbmcgui.ListItem(title)
				li.setThumbnailImage(img)
				player.play(resolved,listitem=li)
				break
		control.infoDialog("No stream found")

elif mode[0] == 'play_special_sport':
	try:
		url = args['url'][0]
		title = args['title'][0]
		img = args['img'][0]
		site = args['site'][0]
		exec "from resources.lib.sources.live_sport import %s"%(site)
		source = eval(site+'.main()')
		resolved = source.resolve(url)
		li = xbmcgui.ListItem(title, path=resolved)
		li.setThumbnailImage(img)
		li.setLabel(title)
		li.setProperty('IsPlayable', 'true')
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
	except:
		log("[ERROR] Erreur dans en mode 'play_special_sport'")
		pass

