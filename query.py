"""
	This file is used to parse the query into the multi filters and modify 
	the query sentense, so that the search engine is able to retrive a 
	list of business from dataset which meeting all requirements of query.

	The filters include location limit, open time limit, happy hour, suitable
	for group, suitable for kids, outdoor table availability, various price
	level, take-out and delivery availability, reservation availability, and 
	parking availability

	The words shows in the filter will be removed from query string so that
	search engine is able to get a more fair and relevant ranking of different
	business.

	@ Input: the string of query sentense
	@ Output: the imporved query sentense and a list of filters.

	@ Package used: nltk, time, geonamescache
"""
import nltk
import speech_recognition as sr
import time
import geonamescache

times = time.localtime()
nums = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', \
		'nigh', 'ten', 'eleven', 'twelve', 'thirtenn', 'fourteen', 'fifteen', \
		'sixteen', 'seventeen', 'eighteen', 'ninteen', 'twenty']
Cities = {}
States = {}
States_abbr = {}
laititude = 36.169941
longitude = -115.139830


""" 
	This function will set three dictionary of python.
	
	The package geonamescache contians a list of cities in the World and
	a list of states in Unite States
	After scan the list of cities and the list of states, the name of cities
	and the name of states of America with all lower-case will be loaded into
	dictionary Cities and States separately.
""" 
def all_cities():
	gc = geonamescache.GeonamesCache()
	for state in gc.get_us_states() :
		States_abbr[state.lower()] = state
		States[gc.get_us_states()[state]['name'].lower()] = state
	for city in gc.get_cities() :
		Cities[gc.get_cities()[city]['name'].lower()] = gc.get_cities()[city]['name']
	Cities['new york'] = "New York"


"""
	This function is a helper function, which will be recursively called to 
	separate one sentense into various words group. And from the groups of 
	word, the city name and state name can be extracted as filter
"""
def extract_entity_names(t):
	entity_names = []

	if hasattr(t, 'label') and t.label():
		if t.label() in ['PERSON' , 'GPE' , 'ORGANIZATION', 'FACILITY']: 
			entity_names.append(' '.join([child[0] for child in t]))
		else:
			for child in t:
				entity_names.extend(extract_entity_names(child))

	return entity_names


"""
	This funciton will extract location information from query sentence, 
	including identified city name, state name, and the distance limit
	from the current location. If the query try to find near business, the
	default distance limit is 5 miles.
"""
def parse_location(original_setence) :
	temp = original_setence
	orig_setence = ' '.join(i.capitalize() for i in temp.split(' '))
	filters = {}
	
	sentences = nltk.sent_tokenize(orig_setence)
	tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
	tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
	chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=False)


	entity_names = []
	for tree in chunked_sentences:
		#print tree
		entity_names.extend(extract_entity_names(tree))

	name_dict = {}

	for name in entity_names:
		n_list = name.split()
		name_dict[n_list[0]] = name

	chunking_list = list(tree.flatten())
	#print chunking_list
	if len(chunking_list) > 1:
		for index in range(1, len(chunking_list)):
			if chunking_list[index][0] in name_dict and chunking_list[index-1][1] == 'IN':
				items = name_dict[chunking_list[index][0]].lower()
				itemsrcd = items
				itemlist = items.split(' ')
				if itemlist[-1] in States :
					filters['state'] = States[itemlist[-1]]
					items = ' '.join(itemlist[:-1])
				if itemlist[-1] in States_abbr :
					filters['state'] = States_abbr[itemlist[-1]]
					items = ' '.join(itemlist[:-1])
				if items in Cities :
					filters['city'] = Cities[items]
					#print original_setence.replace(itemsrcd, "")
					original_setence = original_setence.replace(itemsrcd, "")
					#print original_setence

	if 'las vegas' in original_setence :
		filters['city'] = 'Las Vegas'
		original_setence = original_setence.replace('las vegas', "")
	if 'montreal' in original_setence :
		filters['city'] = 'Montreal'
		original_setence = original_setence.replace('montreal', "")
	if 'edinburgh' in original_setence :
		filters['city'] = 'Edinburgh'
		original_setence = original_setence.replace('edinburgh', "")
	if 'urbana-champaign' in original_setence :
		filters['city'] = 'Urbana-Champaign'
		original_setence = original_setence.replace('urbana-champaign', "")

	if 'near' in original_setence :
		filters['distance'] = [5, (laititude, longitude)]
		original_setence = original_setence.replace(' near', "")
					

	itemlist = original_setence.lower().split(' ')
	for idx, item in  enumerate(itemlist) :
		if idx == 0 :
			continue
		if 'mile' in item :
			try :
				dist = float(itemlist[idx-1])
				filters['distance'] = [dist, (laititude, longitude)]
				if (idx + 1) < len(itemlist) :
					original_setence = ' '.join(itemlist[:idx-1] + itemlist[idx+1:])
				else :
					original_setence = ' '.join(itemlist[:idx-1])
			except :
				for i, num in enumerate(nums) :
					if num  == itemlist[idx-1] :
						filters['distance'] = [i+1, (laititude, longitude)]
						if (idx + 1) < len(itemlist) :
							original_setence = ' '.join(itemlist[:idx-1] + itemlist[idx+1:])
						else :
							original_setence = ' '.join(itemlist[:idx-1])
	return original_setence, filters


"""
	This funciton will extract time information from query sentence, 
	including identified weekdays and time period like morning and 
	afternoon. The query can alse specify exact time like 5 o'clock
	and 3 pm.
"""
def parse_time(original_setence) :
	#times = time.localtime()
	lower = original_setence.lower()
	filters = {}

	weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
	wday = weekdays[times[6]]
	time = ''
	if 'now' in lower :
		time = str(times[3]) + ':' + str(times[4])
		original_setence = original_setence.replace(' open now', '')
		original_setence = original_setence.replace(' now', '')
	else :
		time = 'no'


	if 'tomorrow' in lower : 
		wday = weekdays[ (times[6]+1) % 7]
		original_setence = original_setence.replace(' tomorrow', '')
		time = '12:00'
	if 'monday' in lower :
		wday = 'Monday'
		original_setence = original_setence.replace(' monday', '')
		time = '12:00'
	if 'tuesday' in lower :
		wday = 'Tuesday'
		original_setence = original_setence.replace(' tuesday', '')
		time = '12:00'
	if 'wednesday' in lower :
		wday = 'Wednesday'
		original_setence = original_setence.replace(' wednesday', '')
		time = '12:00'
	if 'thursday' in lower :
		wday = 'Thursday'
		original_setence = original_setence.replace(' thursday', '')
		time = '12:00'
	if 'friday' in lower :
		wday = 'Friday'
		original_setence = original_setence.replace(' friday', '')
		time = '12:00'
	if 'saturday' in lower :
		wday = 'Saturday'
		original_setence = original_setence.replace(' saturday', '')
		time = '12:00'
	if 'sunday' in lower :
		wday = 'Sunday'
		original_setence = original_setence.replace(' sunday', '')
		time = '12:00'

	words = lower.split(' ')
	for idx, word in enumerate(words[:-1]) :
		if words[idx] in ['in', 'at', 'on', 'tomorrow'] and words[idx+1] in ['morning', 'noon', 'afternoon', 'evening', 'night'] :
			if 'morning' == words[idx+1] :
				time = '09:00'
			if 'noon' == words[idx+1] :
				time = '12:00'
			if 'afternoon' == words[idx+1] :
				time = '15:00'
			if 'evening' == words[idx+1] :
				time = '18:00'
			if 'night' == words[idx+1] :
				time = '20:00'
			if 'midnight' == words[idx+1] :
				time = '23:00'
	for idx, word in enumerate(words) :
		#print idx, "  ", word
		if word in ["o'clock", "am", "pm"] :
			for t, num in enumerate(nums) :
				#print t, "  ", "num"
				if num == words[idx-1] :
					if word == 'pm' and t != 11 :
						time = str(t+13) + ':00'
					elif t < 9 :
						time = '0' + str(t+1) + ':00'
					else :
						time = str(t+1) + ':00'
					break
	if time != 'no' :
		filters['hours'] = [wday, time]
	return original_setence, filters


"""
	This funciton will extract specified attribute of business 
	listed in dataset, like happy hour, suitable for group, 
	suitable for kids, outdoor table availability, various price
	level, take-out and delivery availability, reservation 
	availability, and parking availability. The filters translated
	from the query will locat the specified business meeting all
	requirement
"""
def parse_filters(original_setence) :
	lower = original_setence.lower()
	filters = {}

	if 'happy hour' in lower :
		filters['Happy Hour'] = True;
	if 'credit' in lower :
		filters['Accepts Credit Card'] = True
		original_setence = original_setence.replace(' credit card', '')
		original_setence = original_setence.replace(' credit', '')
	if 'group' in lower :
		filters['Good For Groups'] = True
	if 'kid' in lower or 'child' in lower:
		filters['Good for Kids'] = True
	if 'outdoor' in lower :
		filters['Outdoor Seating'] = True
	if 'very cheap' in lower :
		filters['Price Range'] = 1
	elif 'cheap' in lower :
		filters['Price Range'] = 2
	elif 'not expensive' in lower :
		filters['Price Range'] = 3
	elif 'expensive' in lower :
		filters['Price Range'] = 4
	if 'take out' in lower :
		filters['Take-out'] = True
		original_setence = original_setence.replace(' take out', '')
	if 'drive through' in lower :
		filters['Drive-Thru'] = True
		original_setence = original_setence.replace(' drive through', '')
	if 'reserv' in lower :
		filters['Takes Reservations'] = True
	if 'deliver' in lower :
		filters['Delivery'] = True
		original_setence = original_setence.replace(' delivery', '')
	################ Attention! different attribute for parking ########################
	if 'parking' in lower : 
		filters['Parking'] = True

	return original_setence, filters

"""
	This is main function for parsing query. The input
	is the query sentence and the outputs are modified
	query string and all filters
"""
def query(original) :
	original_setence = original.lower()
	#print original
	all_cities()
	filters = {}
	#print Cities
	original_setence, newfilters = parse_location(original_setence)
	filters.update(newfilters)
	original_setence, newfilters = parse_time(original_setence)
	filters.update(newfilters)
	original_setence, newfilters = parse_filters(original_setence)
	filters.update(newfilters)
	#print original_setence
	#print filters
	return original_setence, filters

#query("Find near Bar in Urbana-Champaign  on tomorrow")
