#encoding=utf-8
import sys
import json

def readJson():
	print 'reading json'
	infile = open('category_path.json',"rb") 
	outfile = open('category_path.txt',"wb")
	row_index = 0 
	for row in infile:
		row_index += 1
		try:
			json_list = json.loads(row.strip())
			# print ','.join([item.decode('utf-8') for item in json_list])
			outfile.write(','.join([item.decode('utf-8') for item in json_list])+'\r\n')
		except:
			print 'ohh'
		# if row_index == 100:
		# 	break
def main():
	reload(sys)
	sys.setdefaultencoding('utf-8')
	readJson()

if __name__ == '__main__':
	main()