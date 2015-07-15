#encoding=utf-8
import sys
sys.path.append('../common')
import file_utils
import gzip
import re

def read():
	print 'reading browse data'
	tag_fre_dict = {}
	main_sub_dict = {}
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
			logtime = items[0].decode('utf-8','ignore')
			ip = items[1].decode('utf-8','ignore')
			fm = items[2].decode('utf-8','ignore')

			main_tag = "null"
			for fm_item in fm.split('_'):
				if 'tag' in fm_item and 'tagapplist' not in fm_item:
					main_tag = fm_item
				if 'tagapplist' in fm_item and main_tag != 'null':
					main_sub_dict.setdefault(main_tag,{}).setdefault(fm_item,0)
					main_sub_dict[main_tag][fm_item] += 1

			# pattern = re.compile(r'tag[^_]+')
			# match_list = pattern.findall(fm)
			# for item in match_list:
			# 	tag_fre_dict.setdefault(item,0)
			# 	tag_fre_dict[item] += 1

		# break

	for main_tag in main_sub_dict.keys():
		print main_tag
		sorted_list = sorted(main_sub_dict[main_tag].items(),key=lambda p:p[1],reverse=True)
		for val in sorted_list:
			print '   '+val[0]+' '+str(val[1])

	# sorted_list = sorted(tag_fre_dict.items(),key=lambda p:p[1],reverse=True)
	# for val in sorted_list:
	# 	print val[0]+' '+str(val[1])
	# print len(sorted_list)

def main():
	reload(sys)
	sys.setdefaultencoding('utf-8')
	read()

if __name__ == '__main__':
	main()