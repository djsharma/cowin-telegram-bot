import requests
import pymongo
import time
from multiprocessing import Pool
import requests
from fake_useragent import UserAgent
import time
from random import randint




API_KEY_TOKEN = 'TOKEN'

BASE_URL = "https://api.telegram.org/bot{}/sendMessage".format(API_KEY_TOKEN)



temp_user_agent = UserAgent(verify_ssl=False)
browser_header = {'User-Agent': temp_user_agent.random}



# myclient = pymongo.MongoClient("mongodb://localhost:27017/")
# mydb = myclient["Book"]
# collection = mydb["customers"]


clientdata = {}


def fire_request(payload):
	# print(payload)
	res = requests.post(BASE_URL, data=payload)
	print(res)


def inform_customers(availableCenters, district, coll):
	#read all chatIds from dict for given district for specific age group
	# print(availableCenters)
	ABOVE = False
	BELOW = False
	#below 45 age group
	# print('A')
	# print(availableCenters)
	below45_text = 'Available Slot (18+): \n'
	for center in availableCenters:
		for session in center['sessions']:
			if session['min_age_limit'] == 18 and session['available_capacity'] > 0 :
				BELOW = True
				below45_text = below45_text + '\n' + 'Date: {} \n Center Name: {} \n Locality: {} \n Availablility: {} \n ----------------------------'.format(session['date'], center['name'], center['block_name'], session['available_capacity'])

	# print('B')
	#above 45 age group
	above45_text = 'Available Slot (45+): \n'
	for center in availableCenters:
		for session in center['sessions']:
			if session['min_age_limit'] == 45 and session['available_capacity'] > 0 :
				ABOVE = True
				above45_text = above45_text + '\n' + 'Date: {} \n Center Name: {} \n Locality: {} \n Availablility: {} \n ----------------------------'.format(session['date'], center['name'], center['block_name'], session['available_capacity'])


	# all customers above 45 age group
	#print(above45_text)
	for client in  clientdata[district]:

		# print('D')
		chatId = client['clientId']
		payload = {
    		'chat_id': chatId,
    		'parse_mode':'markdown'
		}	
		if client['ageGroup'] == 'below45' and BELOW == True :
			payload['text'] = below45_text
			# print('E')
			fire_request(payload)
		elif client['ageGroup'] == 'above45' and ABOVE == True :
			payload['text'] = above45_text
			# print('F')
			fire_request(payload)
		# print('G')
		###required set to false in db 
		if (ABOVE == True and client['ageGroup'] == 'above45') or (BELOW == True and client['ageGroup'] == 'below45'):
			print('FOUND SLOT IN DISTRICT: {}'.fomrat(district))
			payload['text'] = "If you cannot register and want to listen for more notifications press /more , for help press /help"
			# print('H')
			fire_request(payload)
			res = coll.update_many({"chatId": chatId }, { '$set' : { "required" : False } } )
			print(res.modified_count)
			time.sleep(5)
		# print('III')
		#remove user from broadcast list until he require more notifications
		
	del clientdata[district]
	pass





def check_available_center(options):
	for session in  options['sessions']:
		if session['available_capacity'] > 0 :
			return True
		else: 
			return False
	pass


def find_availability(options, district, coll):
	available = []
		
	centers = options.json()['centers']
	for center in centers:
		if check_available_center(center) == True:
			# print('FA1')
			available.append(center)
	# print('FA2')
	if len(available) > 0 :
		# print('FA3')
		#print(available)
		inform_customers(available, district, coll)
		pass
	
	time.sleep(15)
	pass


def call_for_district(district):
	try:
		#initialise mongoDB
		myclientO = pymongo.MongoClient("mongodb://localhost:27017/")
		mydbO = myclientO["Book"]
		coll = mydbO["customers"]
		# print('CFD1')
		response = requests.get('https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date=14-05-2021'.format(district), headers=browser_header)
		if response.status_code == 200:
			find_availability(response , district, coll)
		else:
			print('API call failed for district {} response {}'.format(district, response.status_code))
			#print(response.status_code)
			time.sleep(30)
	except Exception as e:
		print(e)
	finally:
		myclientO.close()
	pass



def prepareClientData(list):
	
	clientdata.clear()
	# print('-----')
	# print(clientdata)
	# print('------')
	for district in list:
		#get all clientIds and age for a given district
		clientdata[district] = []
		clientlist = collection.find({ 'districtCode': district, "required" : True })
		
		for client in clientlist:
			# print('-----%%%-')
			# print(client)
			# print('-----%%%-')
			if 'ageGroup' not in client :
				clientdata[district].append({ 'clientId' : client['chatId'], 'ageGroup' : 'below45' })
				clientdata[district].append({ 'clientId' : client['chatId'], 'ageGroup' : 'above45' })
			else :
				clientdata[district].append({ 'clientId' : client['chatId'], 'ageGroup' : client['ageGroup'] })
		clientlist = None
	# print('PCD1-A')
	# print(clientdata)
	pass





while True:
	# read all districts
	myclient = pymongo.MongoClient("mongodb://localhost:27017/")
	mydb = myclient["Book"]
	collection = mydb["customers"]

	try:
		res_districts = collection.distinct('districtCode',{})
		districts = [] # create from result
		for rec in res_districts:
			districts.append(rec)
		
		t0_seconds=time.time()
		while time.time() <= (t0_seconds+75):
			with Pool(processes=5) as p:
				prepareClientData(districts)
				p.map(call_for_district, districts)
		myclient.close()	
	except Exception as e:
		print(e)
	
		# break
	# break				

		
