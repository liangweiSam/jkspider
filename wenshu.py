# -*- coding:utf-8 -*-
import requests
import json
import re
import random
import hmac
import base64
from hashlib import md5
from hashlib import sha1
import execjs
import win32com
from lxml import etree
from win32com.client import Dispatch, constants
import time
import threading

class wenshu(object):

	def __init__(self):
		self.headers  = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3376.400 QQBrowser/9.6.11924.400',
						'Connection' : 'keep-alive'}

	def CreatGuid(self):
		x = int(((1 + random.random()) * 0x10000)) | 0
		return str(hex(x))[3:]

	def getCode(self, guid):
		url = 'http://wenshu.court.gov.cn/ValiCode/GetCode'
		data = {'guid' : guid}
		response = requests.post(url, headers = self.headers, data = data)
		return response.text

	def getGuid(self):
		s = self.CreatGuid() + self.CreatGuid() +'-'+ self.CreatGuid() +'-'+ self.CreatGuid() + self.CreatGuid() +'-'+ self.CreatGuid() + self.CreatGuid() + self.CreatGuid()
		return s

	def de(self, s, count, strReplace):
		arrReplace = strReplace.split('|')
		for i in range(0, count):
			s = s.replace("{%s}" %(i), arrReplace[i])
		return s

	def exeJs(self, cookies):
		
		with open('ws.js', 'r', encoding = 'utf-8') as f:
			line = f.readline()  
			htmlstr = ''  
			while line:  
				htmlstr = htmlstr + line  
				line = f.readline()  
			 
		ctx = execjs.compile(htmlstr)
		return ctx.call("makeKey_%s" %(self.strToLong(cookies)), cookies)

	def strToLong(self, s):
		l = 0
		for i in range(0, len(s)):
			l += ord(s[i]) << (i %16)
		return l % 300

	def getWSId(self, company):
		session = requests.Session()
		guid = self.getGuid()
		number = self.getCode(guid)
		url1 = 'http://wenshu.court.gov.cn/list/list/?sorttype=1&number=%s&guid=%s&conditions=searchWord+QWJS+++全文检索:%s' %(number, guid, company)
		response = session.get(url1, headers = self.headers)
		cookies = response.cookies.get('vjkl5')
		url = 'http://wenshu.court.gov.cn/List/ListContent'
		data = {'Param' : '全文检索:%s' %(company),
				'vl5x' : self.exeJs(cookies),
				'Index' : '1',
				'Page' : '20',
				'Order' : '法院层级',
				'Direction' : 'asc',
				'guid' : guid,
				'number' : number
				}
		response2 = session.post(url, data = data, headers = self.headers)
		jsonData = json.loads(response2.text)
		count = re.search(r'"Count":"(\d{0,1000})"', jsonData).group(1)
		wsIds = re.findall(r'"文书ID":"(.{8}-.{4}-.{4}-.{4}-.{12})",', jsonData)

		if int(count) % 20 > 0:
			t = int(count)/20 + 1
		else:
			t = int(count)/20
		for i in range(2, int(t)+1):
			data['Index'] = '%s' %(i)
			jsonData = json.loads(session.post(url, data = data, headers = self.headers).text)
			wsIds += re.findall(r'"文书ID":"(.{8}-.{4}-.{4}-.{4}-.{12})",', jsonData)
			time.sleep(random.random())

		t = threading.Thread(target = self.threadDoc, args = (wsIds[:len(wsIds)//2], 1))
		t1 = threading.Thread(target = self.threadDoc, args = (wsIds[len(wsIds)//2:], 2))
		t1.start()
		t.start()
		t1.join()
		t.join()

	def threadDoc(self, wsIds, index):
		t = 0
		for wsId in wsIds:
			self.getDoc(wsId)
			time.sleep(1+random.random())
		print('录入完成')
			
	def getDoc(self, DocID):
		print('正在录入 %s ' %(DocID))

		url = 'http://wenshu.court.gov.cn/CreateContentJS/CreateContentJS.aspx?DocID=%s' %(DocID)
		response = requests.get(url, headers = self.headers)
		Data = re.search('jsonHtmlData = "(\{.+\})";', response.text)
		jsonData = json.loads(Data.group(1).replace('\\', ''))

		html = etree.HTML(jsonData['Html'])
		divs = html.xpath('//div')
		with open('File/%s+%s.txt' %(jsonData['Title'], DocID), 'w') as f:
			f.write(jsonData['Title']+'\n')
			f.write(jsonData['PubDate']+'\n')
			for div in divs:
				if len(div.xpath('text()')) > 0:
					f.write(div.xpath('text()')[0]+'\n')
				
					
		


if __name__ == '__main__':
	w = wenshu()
	w.getWSId('哈尔滨泰富电气有限公司')
	# w.strToLong('cd148beb79dffe3c775015e18abc025536f6c994')
	# w.getDoc('7483b84a-2f09-4249-9d11-a81d01165dd4')
