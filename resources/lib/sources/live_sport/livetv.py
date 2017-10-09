from resources.lib.modules import client,webutils,control
import re,sys
from resources.lib.modules.log_utils import log
import json
import urllib

class info():
    def __init__(self):
        self.mode = 'livetv'
        self.name = 'Livetv.sx'
        self.icon = 'livetv.png'
        self.categorized = True
        self.paginated = False
        self.multilink = True

class main():
    def __init__(self):
        self.base = control.setting('livetv_base')

    def categories(self):
        import requests
        self.html = requests.get(self.base + '/fr/allupcoming').text
        
        cats = re.findall('<tr>\s*<[^<]*<a class="main" href="([^"]*allupcomingsports/(\d+)/)"><img[^>]*src="([^"]+)"></a></td>\s*<td align="left">[^<]*<a[^<]*<b>([^<]*)</b></a>\s*</td>\s*<td width=\d+ align="center">\s*<a [^<]*<b>\+(\d+)</b></a>\s*</td>\s*</tr>', self.html)
        cats = self.__prepare_cats(cats)
        return cats

    def events2(self,url):
        import requests
        html = requests.get(url).text
        soup = webutils.bs(html)
        soup = soup.find('table',{'class':'main'})
        events = soup.findAll('td',{'colspan':'2', 'height':'38'})
        events = self.__prepare_events(events)
        return events
        
    def events(self,sport):
        import requests
        #with open('C:\\Users\\jahbobs\\AppData\\Roaming\\Kodi\\addons\\plugin.video.karim\\data.json') as data_file:
        url = "http://bit.do/livetvsx"
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        events = self.__prepare_events(data,sport)
        return events        

    def links(self,sport):
        #with open('C:\\Users\\jahbobs\\AppData\\Roaming\\Kodi\\addons\\plugin.video.karim\\data.json') as data_file:
        #    data = json.load(data_file)
        url = "http://bit.do/livetvsx"
        response = urllib.urlopen(url)
        data = json.loads(response.read())      
        links = self.__prepare_links(data,sport)
        return links



    @staticmethod
    def convert_time(time,month, day):
        def month_converter(month):
            months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            return months.index(month) + 1
        li = time.split(':')
        hour,minute=li[0],li[1]
        month = month_converter(month)
        import datetime
        from resources.lib.modules import pytzimp
        d = pytzimp.timezone(str(pytzimp.timezone('Europe/London'))).localize(datetime.datetime(2000 , int(month), int(day), hour=int(hour), minute=int(minute)))
        timezona= control.setting('timezone_new')
        my_location=pytzimp.timezone(pytzimp.all_timezones[int(timezona)])
        convertido=d.astimezone(my_location)
        fmt = "%m/%d %H:%M"
        time=convertido.strftime(fmt)
        return time
        

    def __prepare_links(self,events,wanted_sport):
        new = []
        for sport in events['sports']:
            if sport['name'] == wanted_sport:
                for match in sport['matches']:
                    for link in match['links']:
                        if link['streamer'] == 'acestream' or  link['streamer'] == 'sopcast':
                            log(link)
                            bitrate = link['bitrate']
                            lang = link['lang']
                            url = link['url']
                            title = link['title']
                            import HTMLParser
                            title = HTMLParser.HTMLParser().unescape(title)
                            title = title.encode('utf-8')         
                            new.append((url,title))
        return new




    def __prepare_cats(self,cats):
        new = []
        for cat in cats:
            url = self.base + cat[0]
            title = cat[3] + ' (%s)'%cat[4]
            id = self.get_id(cat[3])
            img = 'icons/%s.png'%id
            new.append((url,title,img))

        return new

    def get_id(self,id):
        id = id.lower().replace(' ','_')
        id = id.replace('ice_hockey','hockey').replace('football','soccer').replace('american_soccer','football').replace('rugby_union','rugby').replace('combat_sport','fighting').replace('winter_sport','skiing').replace('water_sports','waterpolo').replace('billiard','snooker')
        return id


    def __prepare_events(self,events,wanted_sport):
        new=[]
        for sport in events['sports']:
            if sport['name'] == wanted_sport:
                for match in sport['matches']:
                    for link in match['links']:
                        if link['streamer'] == 'acestream' or  link['streamer'] == 'sopcast':
                            log(link)
                            url = link['url']
                            event = link['title']
                            info = match['datetime']
                            time = re.findall('(\d+:\d+:\d+)',info)[0]
                            #day = re.findall('(\d+-\d+-\d+)',info)[0]
                            color = 'orange'
                            league = 'essai'
                            title = '[COLOR %s](%s)[/COLOR] (%s) [B]%s[/B]'%(color,time,league,event)
                            import HTMLParser
                            title = HTMLParser.HTMLParser().unescape(title)
                            title = title.encode('utf-8')         
                            new.append((url,title))
        return new
       

    def resolve(self,url):
        import liveresolver
        return liveresolver.resolve(url,cache_timeout=0)