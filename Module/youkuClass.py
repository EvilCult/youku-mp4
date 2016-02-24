#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import hashlib
import base64
import urllib
import re
from Library import toolClass

class ChaseYouku :

	def __init__ (self) :
		self.videoLink     = ''
		self.cookieUrl     = 'http://p.l.youku.com/ypvlog'
		self.infoUrl       = 'http://play.youku.com/play/get.json?ct=12&vid='
		self.fileUrlPrefix = 'http://pl.youku.com/playlist/m3u8?ctype=12&ev=1&keyframe=1'
		self.videoTypeList = {'n': 'flv', 'h': 'mp4', 's': 'hd2'}
		self.videoType     = 's'
		self.tempCookie    = ''
		self.Tools         = toolClass.Tools()

	def chaseUrl (self) :
		result = {'stat': 0, 'msg': ''}
		videoID = self.__getVideoID(self.videoLink)
		if videoID :
			self.__auth()
			info = self.__getVideoInfo(videoID)
			fileUrl = self.__getVideoFileUrl(info)
			listFile = self.__getFileList(fileUrl)
			if len(listFile) > 0:
				result['msg'] = listFile
			else:
				result['stat'] = 1
		else :
			result['stat'] = 2

		return result

	def __getVideoID(self, link):
		result = re.findall(r"id_(.*)\.html", link)
		if len(result) > 0 :
			videoID = result[0]
		else :
			videoID = False

		return videoID

	def __auth (self) :
		pageHeader, pageBody = self.Tools.getPage(self.cookieUrl)

		self.tempCookie = 'Cookie: '
		for i in pageHeader:
			cookie = re.findall(r"Set-Cookie:(.*?;)\s*?domain", i)
			if len(cookie) > 0 :
				self.tempCookie += cookie[0].strip() + ' '

	def __getVideoInfo (self, videoID) :
		pageHeader, pageBody = self.Tools.getPage(self.infoUrl + videoID, ['Referer:http://c-h5.youku.com/', self.tempCookie])

		return pageBody
			
	def __getVideoFileUrl (self, videoInfo) :
		videoInfo = json.JSONDecoder().decode(videoInfo)
		if 'security' in videoInfo['data']:
			ep = videoInfo['data']['security']['encrypt_string']
		else :
			ep = False

		if ep :
			oip   = videoInfo['data']['security']['ip']
			vid   = videoInfo['data']['video']['encodeid']
			temp  = self.__yk_e('becaf9be', base64.decodestring(ep))
			sid   = temp.split('_')[0]
			token = temp.split('_')[1]
			ep    = urllib.quote(base64.encodestring(self.__yk_e('bf7e5f01', str(sid) + '_' + str(vid) + '_' + str(token))), '')[0:-3]
			fileUrl = self.fileUrlPrefix + '&ep=' + str(ep) + '&oip=' + str(oip) + '&sid=' + str(sid) + '&token=' + str(token) + '&vid=' + str(vid) + '&type=' + self.videoTypeList[self.videoType]
		else :
			fileUrl = False

		return fileUrl

	def __getFileList (self, fileUrl) :
		pageHeader, pageBody = self.Tools.getPage(fileUrl, [self.tempCookie])

		data = self.__formatList(pageBody)
		return data

	def  __formatList (self, data):
		result = []
		listContent = re.findall(r"(.*)\.ts\?", data)
		for x in listContent:
			if x not in result :
				result.append(x)
		return result

	def __yk_e (self, a, c) : 
		f = 0
		i = 0
		h = 0
		b = {}
		e = ''
		for h in xrange(0, 256) :
			b[h] = h;

		for h in xrange(0, 256) :
			f = ((f + b[h]) + self.__charCodeAt(a, h % len(a))) % 256;
			i = b[h]
			b[h] = b[f]
			b[f] = i

		f = h = 0
		for q in xrange(0, len(c)) :
			h = (h + 1) % 256
			f = (f + b[h]) % 256
			i = b[h]
			b[h] = b[f]
			b[f] = i
			e = e + self.__fromCharCode(self.__charCodeAt(c, q) ^ b[(b[h] + b[f]) % 256]);

		return e

	def __charCodeAt (self, data, index) :
		charCode = {}
		md5 = hashlib.md5() 
		md5.update(data) 
		key = md5.hexdigest()

		return ord(data[index])

	def __fromCharCode (self, codes) :
		return chr(codes)
