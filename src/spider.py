#!/usr/bin/env python
#-*- coding:UTF-8 -*-

#Program:   a small spider written in python
#Author :   uygnin
#Date   :   2013-4-3
#Version:   v0.1

import urllib2
import urllib
import os
import sys 
import subprocess
import math
import codecs
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf8')

domain='http://www.xiami.com'

#获取页面内容
def getPage(domain, path, params={}):
	url=''.join([domain,path])
	user_agent = '	Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'
	headers={'User-Agent':user_agent}
	data=urllib.urlencode(params)
	req=urllib2.Request(url, data, headers)
	content=urllib2.urlopen(req).read()
	return content

#获取虾米音乐排行榜首页的歌曲ID列表
def getSongsInfos(content):
	HtmlEncoding='utf-8'
	soup = BeautifulSoup(content, from_encoding=HtmlEncoding)
	song_td = soup.find_all("td", class_="song_name")
	music_ids = {
		song_td[i].a['href'].split('/')[-1] : song_td[i].a['title']
		for i in range(0,len(song_td))}
	return music_ids

def getAlbumInfos(content):
	HtmlEncoding='utf-8'
	soup = BeautifulSoup(content, from_encoding=HtmlEncoding)
	song_td = soup.find_all("td", class_="song_name")
	songs_info = {
		song_td[i].a['href'].split('/')[-1] : song_td[i].a.string
		for i in range(0,len(song_td))}
	return songs_info

def getTitle(song_id):
	path="/song/%s" %(song_id,)
	content=getPage(domain, path)
	soup = BeautifulSoup(content)
	title=soup.find(id="title").h1.string
	return title

#由歌曲id检索出加密的URL
def getLocation(song_id):
	print 'looking up song id: %s ' %(song_id.encode('utf8'))
	pathTemp=r"/song/playlist/id/%s/object_name/default/object_id" 
	location=None
	path=pathTemp %(song_id,)
	content=getPage(domain, path)

	soup=BeautifulSoup(content)
	if soup.playlist.tracklist.track is not None:
		location=soup.playlist.tracklist.track.location.string
	soup.decompose()
	return location

#破解虾米对url的变形处理，从加密的url还原出正确的mp3链接
def parseLocation(loc):
	if(loc is None):
		return

	parts=(int)(loc[0])
	ency_url=loc[1:]
	leng=len(ency_url)
	each_nums = (int)(math.floor(leng/parts))
	mino_nums= leng%parts

	code=[ency_url[i*(each_nums+1):(i+1)*(each_nums+1)] for i in range(0,mino_nums)]
	offset= (mino_nums)*(each_nums+1)
	code+=[ency_url[offset+i*each_nums:offset+(i+1)*each_nums] for i in range(0,parts-mino_nums)]		
	
	msg=''
	for i in range(0,each_nums+1):
		for item in code:
			if(i==each_nums and len(item)<each_nums+1):
				break
			msg+=item[i]
	msg=urllib2.unquote(msg).replace('^','0')
	return msg

def saveFile(url, path, title):
	print repr("Saving file at :" + path)
	print "Saving File to:%s" %(title,)
	default_name=os.path.basename(url)
	ext=os.path.splitext(default_name)[1]
	old_name="".join((path,default_name))
	update_name="".join((path,title,'%s' %ext))

	if os.path.exists(update_name):
			print 'file already exists.'
			return 5
	cmd=u"..%swget.exe -t 3 --restrict-file-name=windows %s -O %s"  %(os.sep,url, old_name)
	try:
		retcode=subprocess.call(cmd.encode('utf8'), shell = True)
#		print "wget return code:", retcode
		if retcode!=0:
			print "\tFailed"
			return 1
		if os.path.exists(old_name):
			os.rename(old_name, update_name)
			print "%s.%s Saved" %(title, ext)
	except KeyboardInterrupt,e:
		print >>sys.stderr, "User Interrupt!",e
		return 2
	except OSError,e:
		print >>sys.stderr, "Execution failed!",e
		return 3

def downSingleSong(save_path='f:'+os.path.sep):
	s_id=raw_input('Song ID: (e.g. for URL "http://www.xiami.com/song/xxxx", song id is xxxx) ');
	loc=getLocation(s_id)
	url=parseLocation(loc)
	title=getTitle(s_id)
	if title is None:
		title=s_id
	if(url is not  None):
		saveFile(url, save_path, title)

def  downAlbum(save_path='f:'+os.path.sep):
	album_id=raw_input('Album ID: (e.g. for URL "http://www.xiami.com/album/xxxx", Album ID is xxxx") ')
	path="/album/%s" %(album_id,)
	content = getPage(domain, path)
	album = getAlbumInfos(content)
	for (each_id, title) in album.items():
		location=getLocation(each_id)
		url=parseLocation(location)
		if(url is not  None):
			saveFile(url, save_path, title)	

def donwHotSongs(save_path='f:'+os.path.sep):
	path='/music/hot'
	print 'Downloading Hots songs in the hit @' + "".join([domain,path])
	content=getPage(domain,path)
	infos=getSongsInfos(content)
	for (each_id, title) in infos.items():
		location=getLocation(each_id)
		url=parseLocation(location)
		if(url is not  None):
			saveFile(url, save_path, title)

def main():
	if len(sys.argv)==2:
		save_path=sys.argv[1]
	save_path = raw_input("Save Path: (default path @ F:\ ) ")
	if save_path=='':
		save_path='f:'+os.path.sep
	print save_path
	print """Xiami Music (http://www.xiami.com) Donwload script:
		
		Download Options: 
			'1':	Single Song
			'2':	Album
			'3':	Hot Songs
	"""
	actions={
	'1':	downSingleSong,
	'2':	downAlbum,
	'3':	donwHotSongs
	}

	choice=raw_input("Your Option:");
	actions.get(choice)(save_path)

if __name__=="__main__":
	main()