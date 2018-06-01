#-*- coding:utf-8 -*-
from datetime import date
import logging
import os



class log(object):

	def __init__(self):
		self.logger = logging.getLogger()
	# logging.basicConfig(level=logging.INFO,
	# 					filename = './logs/log.log',	
	# 					filemode = 'a',
	# 					format='%(asctime)s - %(filename)s[line:%(lineno)d - %(levelname)s: %(message)s]')
	def get_loger(self):

		if os.path.exists('logs') is False:
			os.mkdir('logs')

		self.logger.setLevel(logging.INFO)

		today = date.today()
		# 文件纪录
		logfile = './logs/%s_log.log' %(today)
		f = logging.FileHandler(logfile, mode='a')
		f.setLevel(logging.INFO)

		# 控制台
		c = logging.StreamHandler()
		c.setLevel(logging.INFO)

		# 格式化
		formatter = logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s: %(message)s")
		f.setFormatter(formatter)
		c.setFormatter(formatter)

		self.logger.addHandler(f)
		self.logger.addHandler(c)
		return self.logger



if __name__ == '__main__':
	log = log()
	logger = log.get_loger()

	logger.info(date.today())
	logger.debug('日志纪录：debug')
	logger.info('工作流程：xxxx')
	logger.warning('请注意，下车')