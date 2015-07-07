#encoding=utf-8
import jft
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

infile = open('../category_path.txt','rb')
outfile = open('../category_path_clean.txt','wb')
row_index = 0
for row in infile:
	row_index += 1
	print row_index
	fanti_items = row.strip().split(',')
	jianti_items = []
	try:
		for fanti_item in fanti_items:
			fanti_item.encode('utf-8')
			jianti_item = jft.f2j('utf-8','gbk',fanti_item)
			jianti_item = unicode(jianti_item,'gbk').decode('utf-8')
			jianti_items.append(jianti_item)
		outfile.write(','.join(jianti_items)+'\r\n')
	except:
		print 'ohh'