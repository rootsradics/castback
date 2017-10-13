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


if mode is None:
    addon.add_item({'mode': 'live_sport'}, {'title':'Live Sport'}, img=icon_path('live_sport.jpg'), fanart=fanart,is_folder=True)
    addon.add_item({'mode': 'live_tv'}, {'title':'Live TV'}, img=icon_path('live_tv.jpg'), fanart=fanart,is_folder=True)
    addon.add_item({'mode': 'p2p_corner'}, {'title':'P2P Corner'}, img=icon_path('p2p_corner.jpg'), fanart=fanart,is_folder=True)
    addon.add_item({'mode': 'on_demand_sport_categories'}, {'title':'Sport On Demand'}, img=icon_path('sport_on_demand.jpg'), fanart=fanart,is_folder=True)
    addon.add_item({'mode': 'reddit'}, {'title':'Subreddits'}, img=icon_path('reddit.jpg'), fanart=fanart,is_folder=True)
    addon.add_item({'mode': 'my_castaway'}, {'title':'My Castaway'}, img=icon_path('my_castaway.jpg'), fanart=fanart,is_folder=True)
    addon.add_item({'mode': 'tools'}, {'title':'Tools'}, img=icon_path('tools.jpg'), fanart=fanart,is_folder=True)
    
    addon.end_of_directory()
    from resources.lib.modules import cache, control, changelog
    cache.get(changelog.get, 600000000, control.addonInfo('version'), table='changelog')
    
elif mode[0] == 'live_sport':
    sources = os.listdir(AddonPath + '/resources/lib/sources/live_sport')
    sources.remove('__init__.py')
    for source in sources:
        if '.pyo' not in source and '__init__' not in source:
            try:
                source = source.replace('.py','')
                exec "from resources.lib.sources.live_sport import %s"%source
                info = eval(source+".info()")
                addon.add_item({'mode': 'open_live_sport', 'site': info.mode}, {'title': info.name}, img=icon_path(info.icon), fanart=fanart,is_folder=True)
            except:
                pass
    addon.end_of_directory()

elif mode[0] == 'open_live_sport':
    
    site = args['site'][0]
    try:
        next_page = args['next'][0]
    except:
        next_page = None
    exec "from resources.lib.sources.live_sport import %s"%site
    info = eval(site+".info()")
    if not info.categorized:
        if next_page:
            source = eval(site+".main(url=next_page)")
        else:
            source = eval(site+".main()")
        events = source.events()
        for event in events:
            if not info.multilink:
                browser = 'plugin://plugin.program.chrome.launcher/?url=%s&mode=showSite&stopPlayback=no'%(event[0])
                context = [('Open in browser','RunPlugin(%s)'%browser)]
                addon.add_video_item({'mode': 'play_special_sport', 'url': event[0], 'title':event[1], 'img': icon_path(info.icon),'site':site}, {'title': event[1]}, img=icon_path(info.icon), fanart=fanart, contextmenu_items=context)
            else:
                addon.add_item({'mode': 'get_sport_event','site':site, 'url': event[0], 'title':event[1], 'img': icon_path(info.icon)}, {'title': event[1]}, img=icon_path(info.icon), fanart=fanart,is_folder=True)
        if (info.paginated and source.next_page()):
            addon.add_item({'mode': 'open_live_sport', 'site': info.mode, 'next' : source.next_page()}, {'title': 'Next Page >>'}, img=icon_path(info.icon), fanart=fanart,is_folder=True)

    else:
        source = eval(site+".main()")
        categories  = source.categories()
        for cat in categories:
            addon.add_item({'mode': 'open_sport_cat', 'url': cat[0], 'site': info.mode, 'title': cat[1]}, {'title': cat[1]}, img=icon_path(cat[2]), fanart=fanart,is_folder=True)
            # addon.add_item({'mode': 'open_sport_cat', 'url': cat[0], 'site': info.mode, 'title': cat[1]}, {'title': cat[1]}, fanart=fanart,is_folder=True)

    addon.end_of_directory()

elif mode[0]=='open_sport_cat':
    url = args['url'][0]
    #sport = args['title'][0].split()[0] 
    # sport = re.sub(r"(?P<sport>.*) \([0-9]+\)", r"\g<sport>", args['title'][0])
    #log("Mon url : %s"%(url))
    #log("Mon sport : %s"%(sport))
    site = args['site'][0]
    exec "from resources.lib.sources.live_sport import %s"%site
    info = eval(site+".info()")
    source = eval(site+".main()")
    events = source.events(url)
    for event in events:
        if not info.multilink:
            browser = 'plugin://plugin.program.chrome.launcher/?url=%s&mode=showSite&stopPlayback=no'%(event[0])
            context = [('Open in browser','RunPlugin(%s)'%browser)]
            addon.add_video_item({'mode': 'play_special_sport', 'url': event[0],'title':event[1], 'img': icon_path(info.icon),'site':site}, {'title': event[1]}, img=icon_path(info.icon), fanart=fanart, contextmenu_items=context)
        else:
            #log("Mes events : %s %s"%(event[0],event[1]))
            # addon.add_item({'mode': 'get_sport_event', 'url': event[0],'site':site , 'title':event[1], 'sport' : sport, 'img': icon_path(info.icon)}, {'title': event[1]}, img=icon_path(info.icon), fanart=fanart,is_folder=True)
            addon.add_item({'mode': 'get_sport_event', 'url': event[0],'site':site , 'title':event[1], 'img': icon_path(info.icon)}, {'title': event[1]}, img=icon_path(info.icon), fanart=fanart,is_folder=True)
    if (info.paginated and source.next_page()):
        addon.add_item({'mode': 'open_cat', 'site': info.mode, 'url': source.next_page()}, {'title': 'Next Page >>'}, img=icon_path(info.icon), fanart=fanart,is_folder=True)
    
    addon.end_of_directory()    
    
elif mode[0]=='get_sport_event':
    
    url = args['url'][0]
    title = args['title'][0]
    # sport = args['sport'][0]
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
            #log(url)
            #log(title)
            #log(img)
            #log(site)
            #log(event)
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
    #try:
        
        url = args['url'][0]
        title = args['title'][0]
        img = args['img'][0]
        site = args['site'][0]
        print "#######DEBUGK#####"
        #log(url)
        #log(title)
        #log(img)
        #log(site)
        print "#######DEBUGK#####"
        exec "from resources.lib.sources.live_sport import %s"%(site)
        source = eval(site+'.main()')
        resolved = source.resolve(url)
        li = xbmcgui.ListItem(title, path=resolved)
        li.setThumbnailImage(img)
        li.setLabel(title)
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
    #except:
    #    pass

