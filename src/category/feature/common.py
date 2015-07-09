

def getCandidateCategory(category_id):
	print '-reading category'
	category_set = set([])
	infile = open('../preprocess/candidate_category/'+str(category_id)+'.txt','rb')
	for row in infile:
		items = row.strip().split(',')
		word = items[0].decode('utf-8')
		fre = int(items[1])
		category_set.add(word)
	print '-category size: '+str(len(category_set))
	return category_set