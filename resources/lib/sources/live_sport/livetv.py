from resources.lib.modules import client,webutils,control
import re,sys,os
from resources.lib.modules.log_utils import log
import json
import urllib
from datetime import datetime, timedelta

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
		self.streamerFilter = []
		self.getStreamerFilter()
		self.json=""
		self.getJson()
	
	def getJson(self):
		if os.path.isfile(control.jsonFile):
			with open(control.jsonFile, "r") as f:
				self.json=f.read()
		if self.json=="" :
			self.downloadJson()
			with open(control.jsonFile, "w") as f:
				f.write(self.json)
		
		self.data = json.loads(self.json)
		dt=datetime.strptime(self.data["datetime"], "%Y-%m-%d %H:%M:%S.%f")
		
		if datetime.now()>dt+timedelta(minutes=int(control.setting("delay"))):
			self.downloadJson()
			with open(control.jsonFile, "w") as f:
				f.write(self.json)
		
		self.data = json.loads(self.json)
			
		
		
	def getStreamerFilter(self):
		lst=["streamer_acestream", "streamer_sopcast", "streamer_youtube", "streamer_aliez", "streamer_web"]
		for s in lst:
			if control.setting(s)=="true":
				name=s.split("_")[-1]
				self.streamerFilter.append(name)
		
		
	
	def downloadJson(self):
		url = control.setting('livetvsx_json_url')
		response = urllib.urlopen(url)
		self.json=response.read()

	def categories(self):
		cats = self.__prepare_cats()
		return cats
		
	def events(self,sportUrl):
		events = self.__prepare_events(sportUrl)
		return events		

	def links(self,matchUrl):  
		links = self.__prepare_links(matchUrl)
		return links

	def __prepare_cats(self):
		new = []
		for sport in self.data["sports"]:
			matches=self.getDesiredMatches(sport["url"])
			nb=len(matches)
			if nb>0:
				url=sport["url"]
				title="{} ({})".format(sport["name"].encode("utf-8"), nb)
				img=self.getIcon(url)
				new.append((url,title,img))

		return new


	def __prepare_events(self,sportUrl):
		new=[]
		matches=self.getDesiredMatches(sportUrl)
		for match in matches:
			nb=len(self.getDesiredLinks(match["url"]))
			if nb>0:
				strdt=match["datetime"][-8:-3]
				url=match["url"]
				pattern="[COLOR orange][{}][/COLOR] [B]{}[/B] [COLOR green][I]{}[/I][/COLOR] [COLOR blue]({})[/COLOR]"
				title=pattern.format(strdt, match["name"].encode('utf-8'), match["competition"], nb)
				new.append((url,title))
		return new
		
	def __prepare_links(self,matchUrl):
		new = []
		
		links=self.getDesiredLinks(matchUrl)
		for link in links:
			url=link["url"]
			pattern="[COLOR orange][{}][/COLOR] [COLOR blue]({}%)[/COLOR] [B]{}[/B] [COLOR green][I]{}[/I][/COLOR]"
			sInfos="/".join([link["lang"].encode('utf-8'), link["bitrate"].encode('utf-8')]).strip()
			if sInfos!="":
				sInfos=" ["+sInfos+"]"
			title=pattern.format(link["streamer"].encode('utf-8'), link["health"].encode('utf-8'), link["matchname"].encode('utf-8'), link["lang"].encode('utf-8'), sInfos)
			new.append((url,title))
			
		return new
	
	def getDesiredLinks(self, matchUrl):
		for sport in self.data["sports"]:
			res=[m for m in sport["matches"] if m["url"]==matchUrl]
			if len(res)>0:
				match=res[0]
				break
		links=[l for l in match["links"] if l["url"].strip()!="" and l["streamer"] in self.streamerFilter]
		return(links)
		
	def getDesiredMatches(self, sportUrl):
		ret=[]
		sport=[s for s in self.data["sports"] if s["url"]==sportUrl][0]
		for match in sport["matches"]:
			nb=len(self.getDesiredLinks(match["url"]))
			if nb>0:
				ret.append(match)
		return(ret)
	
	def resolve(self,url):
		import liveresolver
		return liveresolver.resolve(url,cache_timeout=0)
		
	def getIcon(self, sportUrl):
		table={
			"1":	"soccer.png",
			"2":	"hockey.png",
			"3":	"basketball.png",
			"4":	"tennis.png",
			"5":	"volleyball.png",
			"6":	"fighting.png",
			"7":	"f1.png",
			"9":	"athletics.png",
			"12":	"soccer.png",
			"13":	"handball.png",
			"17":	"rugby.png",
			"18":	"skiing.png",
			"19":	"baseball.png",
			"20":	"curling.png",
			"21":	"volleyball.png",
			"27":	"football.png",
			"29":	"snooker.png",
			"30":	"darts.png",
			# "32":	"floorball.png",
			"33":	"rugby.png",
			"37":	"golf.png",
			"38":	"hockey.png",
			"39":	"table_tennis.png",
			"40":	"cycling.png",
			"41":	"cricket.png",
			"54":	"tennis.png",
			"59":	"hockey.png",
			"72":	"horse_racing.png",
			# "74":	"esport.png",
			"75":	"fighting.png",
			# "93":	"climbing.png",
			"96":	"volleyball.png",
		}
		id=sportUrl.split("/")[-2]
		if id in table:
			return("icons/"+table[id])
		else:
			return("live_sport.jpg")