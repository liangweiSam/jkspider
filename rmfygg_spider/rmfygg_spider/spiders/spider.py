#-*- coding:utf-8 -*-
import scrapy
import json
import xlrd, xlwt
import re
from rmfygg_spider.items import RmfyggSpiderItem

class rmfy_spider(scrapy.Spider):
	name = 'rmfy_spider'
	allowed_domains = ['rmfygg.court.gov.cn']


	def start_requests(self):
		headers = {
		'User-Agent' : r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36',
		}
		return [scrapy.Request(url = r'https://rmfygg.court.gov.cn', headers = headers, callback = self.search)]

	def getDataFromEx(self):
		workBook = xlrd.open_workbook('C:/Users/Administrator/Desktop/python/jkspider/SpiderFiles/所有报告单new.xls')
		sheet1_name = workBook.sheet_names()[0]
		sheet1 = workBook.sheet_by_name(sheet1_name)
		rows = sheet1.col_values(0)[1:]
		rows = rows
		new_rows = []
		for i in rows:
			if re.search('.+?(公司|厂|加油站|店|集团|所|中心|院)', i) is not None:
				s = re.search('.+?(公司|厂|加油站|店|集团|所|中心|院)', i).group(0).strip()	
				s = s.replace('(', '（')
				s = s.replace(')', '）')	
				new_rows.append(s)
		return new_rows	

	def search(self, response):
		page = 1
		headers = {
		'User-Agent' : r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36',
		}
		rows = self.getDataFromEx()
		for row in rows[6500:]:
			form_data = {
						'_noticelist_WAR_rmfynoticeListportlet_content' : '',
						'_noticelist_WAR_rmfynoticeListportlet_searchContent' : '%s' %(row),
						'_noticelist_WAR_rmfynoticeListportlet_IEVersion' : 'ie',
						'_noticelist_WAR_rmfynoticeListportlet_flag' : 'click',				
						'_noticelist_WAR_rmfynoticeListportlet_aoData' : '[{"name":"sEcho","value":%d},{"name":"iColumns","value":6},{"name":"sColumns","value":",,,,,"},{"name":"iDisplayStart","value":0},{"name":"iDisplayLength","value":10},{"name":"mDataProp_0","value":null},{"name":"mDataProp_1","value":null},{"name":"mDataProp_2","value":null},{"name":"mDataProp_3","value":null},{"name":"mDataProp_4","value":null},{"name":"mDataProp_5","value":null}]' %(page)
						}
	
			yield scrapy.FormRequest('https://rmfygg.court.gov.cn/web/rmfyportal/noticeinfo?p_p_id=noticelist_WAR_rmfynoticeListportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=initNoticeList&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1',
				 headers = headers, formdata = form_data, callback = self.search_total, meta = {'business' : '%s' %(row)})


	def search_total(self, response):
		item = response.meta['business']
		print(item)
		headers = {
		'User-Agent' : r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36',
		}
		
		data = json.loads(response.text)
		totalRecords = data['iTotalDisplayRecords']
		pageNum = 0
		if int(totalRecords) < 10:
			pageNum = 1
		elif int(totalRecords) % 10 == 0:
			pageNum = totalRecords//10
		else:
			pageNum = totalRecords//10 + 1	
		for i in range(0, pageNum):
			page = i
			form_data = {
						'_noticelist_WAR_rmfynoticeListportlet_content' : '',
						'_noticelist_WAR_rmfynoticeListportlet_searchContent' : '%s' %(item),
						'_noticelist_WAR_rmfynoticeListportlet_IEVersion' : 'ie',
						'_noticelist_WAR_rmfynoticeListportlet_flag' : 'click',				#这个位置是页数
						'_noticelist_WAR_rmfynoticeListportlet_aoData' : '[{"name":"sEcho","value":%d},{"name":"iColumns","value":6},{"name":"sColumns","value":",,,,,"},{"name":"iDisplayStart","value":%d},{"name":"iDisplayLength","value":10},{"name":"mDataProp_0","value":null},{"name":"mDataProp_1","value":null},{"name":"mDataProp_2","value":null},{"name":"mDataProp_3","value":null},{"name":"mDataProp_4","value":null},{"name":"mDataProp_5","value":null}]' %(page, i*10)
						}
			print(form_data)
			return scrapy.FormRequest('https://rmfygg.court.gov.cn/web/rmfyportal/noticeinfo?p_p_id=noticelist_WAR_rmfynoticeListportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=initNoticeList&p_p_cacheability=cacheLevelPage&p_p_col_id=column-1&p_p_col_count=1',
			 headers = headers, formdata = form_data, callback = self.parse, meta = {'business' : '%s' %(item)})

	def parse(self, response):
		item = response.meta['business']
		data = json.loads(response.text)['data']
		for i in data:
			rmfy = RmfyggSpiderItem()
			rmfy['company'] = item
			rmfy['court'] = i['court'] 
			rmfy['noticeCode'] = i['noticeCode']
			rmfy['noticeContent'] = i['noticeContent']
			rmfy['payStatus'] = i['payStatus']
			rmfy['publishDate'] = i['publishDate']
			rmfy['tosendPeople'] = i['tosendPeople']
			rmfy['uuid'] = i['uuid']
			yield rmfy
  