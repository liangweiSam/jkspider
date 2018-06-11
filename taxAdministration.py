# -*- coding:utf-8 -*-
import requests
from lxml import etree
import csv
import re


class tax(object):

	def __init__(self):
		self.headers  = {'User-Agent' : 'Mozilla/4.0(compatible;MSIE8.0;WindowsNT6.0;Trident/4.0)',
						}
		self.proxies = {
						'http':'113.12.72.24:3128',
						}

	def getData(self, date):
		url = 'http://hd.chinatax.gov.cn/xxk/action/ListXinxikucomXml.do?dotype=casetime&id=%s' %(date)
		response = requests.get(url = url, headers = self.headers, proxies = self.proxies)
		html = etree.HTML(response.content)
		ids = html.xpath('.//item/@id')
		row = []
		if response.status_code is 200 and len(ids) > 0:
			for i in ids:
				fileUrl = 'http://hd.chinatax.gov.cn/xxk/action/GetArticleView1.do?op=xxkweb&id=%s' %(i)
				response2 = requests.get(url = fileUrl, headers = self.headers, proxies = self.proxies)
				fileHtml = etree.HTML(response2.content)
				fileData = fileHtml.xpath('/html/body/table/tr/td//tr')
				# print(response2.text)
				t = []
				for file in fileData:
					if len(file.xpath('./td[2]/text()')) > 0:
						t.append(file.xpath('./td[2]/text()')[0])
					else:
						t.append('  ')
				print(t)
				row.append(list(t))
			print('采集完成..')
		else:
			print('网络被拒绝 或者 没有获取到数据')
	
		self.saveData(row, date)

	def saveData(self, datas, date):
		headers = ['纳税人名称', '纳税人识别号', '组织机构代码', '注册地址', '法定代表人或者负责人姓名、性别、证件名称及号码', 
					'负有直接责任的财务负责人姓名、性别、证件名称及号码', '负有直接责任的中介机构信息及其从业人员信息', 
					 '案件性质', '主要违法事实, 相关法律依据及税务处理处罚情况']

		try:
			with open('%s税务.csv' %(date), 'w') as f:
				f_csv = csv.writer(f)
				f_csv.writerow(headers)
				f_csv.writerows(datas)
		except Exception as e:
			print(e)			 


	def searchCompany(self, searchword):
		url = 'http://hd.chinatax.gov.cn/xxk/action/ListXxk.do'
		formdata = {
					'categeryid': '24',
					'querystring24' : 'articlefield02',
					'querystring25' : 'articlefield02',
					'queryvalue' : searchword
					}
		requests.post(url, headers = self.headers, data = formdata)
		





if __name__ == '__main__':

	tax = tax()
	tax.getData('2018年2月')