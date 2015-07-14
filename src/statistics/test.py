#encoding=utf-8
import sys
sys.path.append('../common')
import file_utils
import gzip
import re

def read():
	print 'reading browse data'
	file_path_list = file_utils.getFilePathList('data/search/')
	for file_path in file_path_list:
		if 'crc' in file_path or 'swp' in file_path or 'swo' in file_path:
			continue
		# print file_path
		infile = gzip.open(file_path)
		while True:
			row = infile.readline()
			if not row: break
			items = row.strip().split('\x01')
			log_time = items[0].decode('utf-8','ignore')
			ip = items[1].decode('utf-8','ignore')
			fm = items[2].decode('utf-8','ignore')
			inp = items[3].decode('gbk','ignore')
			print inp

		infile.close()

def main():
	reload(sys)
	sys.setdefaultencoding('utf-8')
	read()

if __name__ == '__main__':
	main()