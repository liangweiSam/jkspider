#-*- coding:utf-8 -*-
from lxml import etree

import requests
import user_agent_Pool
import random


class langChina(object):

	def __init__(self):
		self.UA = random.choice(user_agent_Pool.user_agent)
		self.headers  = {'User-Agent' : self.UA,
						'Connection' : 'keep-alive',
						}
		self.sess = requests.Session()

	def header_page(self):
		url = 'http://www.landchina.com/default.aspx?tabid=349'
		response = self.sess.get(url, headers = self.headers)
		html = etree.HTML(response.text)
		VIEWSTATE = html.xpath('.//input[@id="__VIEWSTATE"]/@value')
		EVENTVALIDATION = html.xpath('.//input[@id="__EVENTVALIDATION"]/@value')
		hidComName = html.xpath('.//input[@id="hidComName"]/@value')

		TAB_QuerySubmitConditionData = '1ede469f-2e86-4e4a-a505-d6d9fdcf8d16:▓有限公司▓|e1098f89-81bb-4e36-bfb7-be69c34d8b4b:2018-1-1~2018-6-7'
		return VIEWSTATE, EVENTVALIDATION, hidComName


	def get_data(self, searchword, str_date, end_date):
		viewstate, even, hidComName = self.header_page()
		TAB_QueryConditionItem1 = '1ede469f-2e86-4e4a-a505-d6d9fdcf8d16'
		TAB_QueryConditionItem2 = 'e1098f89-81bb-4e36-bfb7-be69c34d8b4b'
		# searchword = self.gbk_encode(':%s|' %(searchword))
		searchword = ':▓%s▓|' %(searchword)
		date = self.gbk_encode(':%s~%s' %(str_date, end_date)) 
		TAB_QuerySubmitConditionData = TAB_QueryConditionItem1 + '%s' %(searchword) + TAB_QueryConditionItem2 + '%s' %(date)

		formdata = {
				'__VIEWSTATE' : viewstate[0],
				'__EVENTVALIDATION' : even[0],
				'hidComName' : hidComName[0],
				'TAB_QueryConditionItem' : '1ede469f-2e86-4e4a-a505-d6d9fdcf8d16',
				'TAB_QueryConditionItem' : 'e1098f89-81bb-4e36-bfb7-be69c34d8b4b',
				'TAB_QuerySubmitConditionData' : TAB_QuerySubmitConditionData,
				'TAB_QuerySubmitOrderData' : '',
				'TAB_RowButtonActionControl' : '',
				'TAB_QuerySubmitPagerData' : '1',
				'TAB_QuerySubmitSortData' : ''
		}
		url = 'http://www.landchina.com/default.aspx?tabid=349'
		response = self.sess.post(url, headers = self.headers, data = formdata)
		assert False, print(response.text)
		html = etree.HTML(response.text)
		content = html.xpath('.//table[@id="TAB_contentTable"]')
		for i in content[0].xpath('.//tr')[1:]:
			area = i.xpath('td[2]/text()')
			href = i.xpath('td[3]/a/@href')
			oldowner = i.xpath('td[4]/text()')
			newowner = i.xpath('td[5]/text()')
			print(area)
			print(href)
			print(oldowner)
			print(newowner)
		# print(content[0].xpath('.//tr'))
				

	def gbk_encode(self, text):
		s = str(text.encode('gb2312'))[2:-1].replace(r'\x', '%').upper()
		return s

# 1ede469f-2e86-4e4a-a505-d6d9fdcf8d16  %3A%A8%88%D3%D0%CF%DE%B9%AB%CB%BE%A8%88 %7C   e1098f89-81bb-4e36-bfb7-be69c34d8b4b%3A2018-1-1%7E2018-6-7
if __name__ == '__main__':
	lc = langChina()
	# print(lc.gbk_encode(''))
	lc.get_data('有限公司', '2018-1-1', '2018-6-7')
	# TAB_QuerySubmitConditionData = '▓有限公司▓'
	# print(str(TAB_QuerySubmitConditionData.encode('gbk'))[2:-1].replace(r'\x', '%').upper())