#encoding=utf-8
import sys
sys.path.append('../common')
import file_utils
import gzip
import re

def read():
	print 'reading browse data'
	tag_fre_dict = {}
	click_infos = []
	file_path_list = file_utils.getFilePathList('data/browse_150708/')
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
			tag_path = []
			pattern = re.compile(r'tagapplist[^_]+')
			# print fm
			match_list = pattern.findall(fm)
			for item in match_list:
				# print item
				tag_fre_dict.setdefault(item,0)
				tag_fre_dict[item] += 1
			click_infos.append(fm)
		infile.close()

	sorted_list = sorted(tag_fre_dict.items(),key=lambda p:p[1],reverse=True)
	for val in sorted_list:
		print val[0]+' '+str(val[1])
	print len(sorted_list)

	return click_infos

def main():
	reload(sys)
	sys.setdefaultencoding('utf-8')
	click_infos = read()

if __name__ == '__main__':
	main()