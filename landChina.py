#-*- coding:utf-8 -*-
from lxml import etree
from urllib.parse import urlencode, unquote
from time import sleep
from gevent import monkey, pool; monkey.patch_socket()

import gevent
import requests
import user_agent_Pool
import random
import urllib.request
import csv


class landChina(object):

	def __init__(self):
		self.UA = random.choice(user_agent_Pool.user_agent)
		self.headers  = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
						'Connection' : 'keep-alive',
						'context-type' : 'text/xml;charset=GB2312',
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
		start_p = 1		
		total_list = []
		viewstate, even, hidComName = self.header_page()
		TAB_QueryConditionItem1 = '1ede469f-2e86-4e4a-a505-d6d9fdcf8d16'
		TAB_QueryConditionItem2 = 'e1098f89-81bb-4e36-bfb7-be69c34d8b4b'
		searchword = ':▓%s▓|' %(searchword)
		date = ':%s~%s' %(str_date, end_date)
		TAB_QuerySubmitConditionData = TAB_QueryConditionItem1 + '%s' %(searchword) + TAB_QueryConditionItem2 + '%s' %(date)
		formdata = {
				'__VIEWSTATE' : viewstate[0],
				'__EVENTVALIDATION' : even[0],
				'hidComName' : hidComName[0],
				'TAB_QueryConditionItem' : {'0': '1ede469f-2e86-4e4a-a505-d6d9fdcf8d16', '1' : 'e1098f89-81bb-4e36-bfb7-be69c34d8b4b'},
				'TAB_QuerySubmitConditionData' : TAB_QuerySubmitConditionData,
				'TAB_QuerySubmitOrderData' : '',
				'TAB_RowButtonActionControl' : '',
				'TAB_QuerySubmitPagerData' : '%d'  %(start_p),
				'TAB_QuerySubmitSortData' : ''
		}
		data = urlencode(formdata, encoding = 'gbk').encode('gbk')
		url = 'http://www.landchina.com/default.aspx?tabid=349'
		req = urllib.request.Request(url, headers = self.headers, data = data)
		page = urllib.request.urlopen(req).read()
		# response = self.sess.post(url, headers = self.headers, data = data)
		html = etree.HTML(page.decode('gbk'))
		content = html.xpath('.//table[@id="TAB_contentTable"]')
		page = html.xpath('.//div[@class="pager"]/table/tbody/tr/td[1]/text()')[0]
		total_p = page.split('页')[0][1:]

		# 第一页的href
		print('正在爬取第1页...')
		for i in content[0].xpath('.//tr')[1:]:
			href = i.xpath('td[3]/a/@href')[0]
			total_list.append(href)

		# 后续的href
		for i in range(1, int(total_p)):
			print('正在爬取第%s页...' %(i+1))
			sleep(random.random()*2)
			start_p = i+1
			formdata['TAB_QuerySubmitPagerData'] = start_p
			data = urlencode(formdata, encoding = 'gbk').encode('gbk')
			url = 'http://www.landchina.com/default.aspx?tabid=349'
			req = urllib.request.Request(url, headers = self.headers, data = data)
			page = urllib.request.urlopen(req).read()
			html = etree.HTML(page.decode('gbk'))
			content = html.xpath('.//table[@id="TAB_contentTable"]')

			for i in content[0].xpath('.//tr')[1:]:
				href = i.xpath('td[3]/a/@href')[0]
				total_list.append(href)
				# print(href[0])
				# self.details(href[0])
		with open('land_china/%s-%s-%s.txt' %('company', str_date, end_date), 'w') as f:
			f.write(str(total_list))

		p = pool.Pool(5)
		threads = [p.spawn(self.details(url)) for url in total_list]
		gevent.joinall(threads)

	def details(self, details_h, times = 0):
		sleep(random.random()*2)
		url = 'http://www.landchina.com/%s' %(details_h)
		headers = ['原土地使用权人', '现土地使用权人', '宗地标识', '宗地编号', '宗地座落', '所在行政区', '土地面积(公顷)', '土地用途', '土地使用权类型', '土地使用年限',
				'土地利用状况', '土地级别', '转让方式', '转让价格(万元)','成交时间']		
		flag2 = 0		
		response = self.sess.get(url, headers = self.headers)
		html = etree.HTML(response.text)
		old_owner = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c2_ctrl"]/text()')
		new_owner = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c4_ctrl"]/text()')
		land_mark = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c2_ctrl"]/text()')
		land_no = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c4_ctrl"]/text()')
		land_address = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c2_ctrl"]/text()')
		admin_area = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r11_c2_ctrl"]/text()')
		square_area = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r4_c2_ctrl"]/text()')
		purpose = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r4_c4_ctrl"]/text()')
		tp = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r5_c2_ctrl"]/text()')
		age_limit = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r5_c4_ctrl"]/text()')
		land_status = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r6_c2_ctrl"]/text()')
		land_level = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r6_c4_ctrl"]/text()')
		transfer_mode = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r8_c2_ctrl"]/text()')
		transfer_price = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r8_c4_ctrl"]/text()')
		deal_time = html.xpath('.//span[@id="mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r7_c2_ctrl"]/text()')
		
		if len(new_owner) > 0:
			data = (
					old_owner[0].strip() if len(old_owner) > 0 else '',
					new_owner[0].strip() if len(new_owner) > 0 else '',
					land_mark[0].strip() if len(land_mark) > 0 else '',
					land_no[0].strip() if len(land_no) > 0  else '',
					land_address[0].strip() if len(land_address) > 0  else '',
					admin_area[0].strip() if len(admin_area) > 0  else '',
					square_area[0].strip() if len(square_area) > 0  else '',
					purpose[0].strip() if len(purpose) > 0  else '',
					tp[0].strip() if len(tp) > 0  else '',
					age_limit[0].strip() if len(age_limit) > 0  else '',
					land_status[0].strip() if len(land_status) > 0  else '',
					land_level[0].strip() if len(land_level) > 0  else '',
					transfer_mode[0].strip() if len(transfer_mode) > 0  else '',
					transfer_price[0].strip() if len(transfer_price) > 0  else '',
					deal_time[0].strip() if len(deal_time) > 0 else ''
					)

			try:
				with open('land_china/land_details.csv', 'r') as f:
					readers = csv.reader(f)
					for row in readers:
						if row != None:
							flag2 = 1
							break	
			except Exception as e:
				print(e)
				pass	
					
			with open('land_china/land_details.csv', 'a+', encoding = 'utf-8') as f:
				f_csv = csv.writer(f)
				if flag2 == 0:
					f_csv.writerow(headers)
				f_csv.writerow(data)
				print('%s数据写入...' %(data[1]))
		else:
			if times < 10:
				times+= 1
				sleep(random.random() * 1)
				self.details(details_h, times)
			else:
				print('多次访问失败....')

	def gbk_encode(self, text):
		s = str(text.encode('gbk'))[2:-1].replace(r'\x', '%').upper()
		return s

if __name__ == '__main__':
	lc = landChina()
	# print(value, ..., sep, end, file, flush) unquote('▓有限公司▓')
	# print(lc.gbk_encode(''))
	lc.get_data('有限公司', '2017-1-1', '2017-12-31')
