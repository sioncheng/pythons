#/usr/bin/python
#encoding=utf8

'''
download high quality mp3 from music.baidu.com
usage : python BaiduMusic.py username=yourusername password=yourpassword key=陈奕迅
will download hight quality music from page 1 of http://music.baidu.com/search?key=陈奕迅 to your Downloads directory
'''

import sys
import urllib,urllib2,re,cookielib
from sgmllib import SGMLParser
import os

class MyHTMLParser(SGMLParser) :
    songs = []
    status = -1 # -1 none, 0 song item , 1 song title , 2 high quality
    songItem = None

    count = 0

    def start_li(self,attrs) :
        
        self.count = self.count + 1
        
        #print attrs

        if ( len(attrs) == 2 and attrs[0][0] == 'data-songitem' ) :
            self.status = 0
            #print 'songItemStart'

    def start_span(self,attrs) :
        self.count = self.count + 1
        
        if (self.status == 0 and len(attrs) == 2 and attrs[0][1] == 'song-title' ) :
            self.status = 1
            
        
    def start_a (self,attrs) :
        self.count = self.count + 1
        
        if (self.status == 1 and len(attrs) == 4 and attrs[2][0] == 'data-songdata') :
                #print attrs
                self.songItem = []
                self.songItem.append(attrs[0][1])
                self.songItem.append(attrs[3][1])
        
        if ( self.status == 1 and len(attrs) == 3 and attrs[1][1] == 'high-rate-icon' ) :
                self.status = 2
                self.songs.append(self.songItem)
                self.status = -1

    def end_a (self):
        self.count = self.count - 1
        self.check_count()

    def end_span(self):
        self.count = self.count - 1
        self.check_count()

    def end_li(self):
        self.count = self.count - 1
        self.check_count()
    
    def check_count(self):
        if self.count <= 0 :
                self.status = -1

    def get_songs(self):
            return self.songs
#class MyHTMLParser

class BaiduMusic :
	def __init__(self) :
		#
		self.cj = cookielib.CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
		self.opener.addheaders = [('User-agent','Opera/9.23')]
		urllib2.install_opener(self.opener)

	def login(self,username,password):
		get_api_url = 'http://passport.baidu.com/v2/api/?getapi&class=login&tpl=music&tangram=false'
		req = urllib2.Request(get_api_url)
		page = urllib2.urlopen(req)
		
		req = urllib2.Request(get_api_url)
		page = urllib2.urlopen(req)
		c = page.read()
		#print c

		tokent_regex = re.compile('''bdPass\.api\.params\.login_token='(.*?)';''',re.DOTALL)
		match = tokent_regex.findall(c)
		if match :
			self.token = match[0]
			#print self.token
		else :
			print c
			raise Exception,"can not get login token"

		login_url = 'https://passport.baidu.com/v2/api/?login'
		params = {}
		params['charset'] = 'UTF-8'
		params['codestring'] = ''
		params['token'] = self.token
		params['isPhone'] = 'false'
		params['index'] = '0'
		params['u'] = ''
		params['safeflg'] = '0'
		params['staticpage'] = 'pass_jump.html'
		params['loginType'] = '1'
		params['tpl'] = 'music'
		params['callback'] = 'callback'
		params['username'] = username
		params['password'] = password
		params['verifycode'] = ''
		params['mem_pass'] = 'on'
		req = urllib2.Request(login_url)
		#req.add_header('Cookie',urllib.urlencode(self.cookies))
		page = urllib2.urlopen(req,urllib.urlencode(params))
		c = page.read()
		#
		
	def search_download(self,key):
		#
		url = 'http://music.baidu.com/search?' + urllib.urlencode({'key':key})
		req = urllib2.Request(url)
		page = urllib2.urlopen(req)
		c = page.read()
		parser = MyHTMLParser()
		parser.feed(c)
		#print parser.get_songs()
		for s in parser.get_songs() :
			print s[0],s[1]
			self.download(s[0],s[1])
			

	def download(self,id,name):
		#
		url = 'http://music.baidu.com%s/download' % id
		req = urllib2.Request(url)
		page = urllib2.urlopen(req)
		c = page.read()
		regex = re.compile('''<li  class="high-rate" data-data = '{(.*?)}'>''')
		match = regex.findall(c)
		if match :
			regex = re.compile('''"link":"(.*?)"''')
			match = regex.findall(match[0])
			if match:
				mp3_url = 'http://music.baidu.com%s' % match[0].replace('\\','')
				urllib.urlretrieve(mp3_url,os.path.expanduser('~/Downloads/%s.mp3' % name))
				print mp3_url
		else :
			print 'not found'



def get_params(argv):
	params = {}
	for arg in argv:
		#print arg,len(arg)
		tmp = arg.split('=')
		if len(tmp) < 2 : continue
		params[tmp[0]] = tmp[1]

	for k in params.keys():
		print k, params[k]

	return params

def main(argv):
	#
	params = get_params(argv)

	bm = BaiduMusic()
	bm.login(params['username'],params['password'])
	bm.search_download(params['key'])
	#bm.download(7316463,'')
	#print 'http://music.baidu.com/search?' + urllib.urlencode({'key':params['key']})

if __name__ == '__main__' :
	main(sys.argv)