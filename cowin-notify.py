from collections import defaultdict
import datetime
import requests
import sys

#Phonenum and apikey - configured from callmebot ( https://www.callmebot.com/blog/free-api-whatsapp-messages/ )
#phone should include +internationalcode too
ph = sys.argv[1]
apikey = sys.argv[2]
callmebot_d = [{'phone': ph, 'apikey': apikey}]

def get_open_slot_centers(l, exclude_pins=None, include_pins=None):
    #To ignore locations that are not needed
    if exclude_pins and l['pincode'] in exclude_pins:
        return None
    free_sessions = []
    #Check each hospital
    for i in l['sessions']:
        #Check age limit and available dose 1
        if i['min_age_limit'] == 18 and (i['available_capacity_dose1'] > 0):
            #append the session
            free_sessions.append(i)
    #If no sessions return None
    if not free_sessions:
        return None
    #Otherwise update the dictionary to include only the free sessions
    out_d = l
    out_d['sessions'] = free_sessions
    return out_d

#Get the url for today
date = datetime.datetime.now().strftime('%d-%m-%Y')
#URL generated for each day
public_url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=294&date={}'.format(date)
user_url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id=294&date={}'.format(date)
url = user_url

#Have a set of User-Agents to use
# Looks like an empty user-agent header also works
# But future proofing this by retaining the user-agenrs
user_agent_list = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
                   'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
                   'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1']

#Randomise a choice of user agent
import random
user_agent = random.choice(user_agent_list)
headers = {'user-agent': user_agent}
#Fetch the page from user-url first
page = requests.get(url, headers=headers)
#If we dont'get a success, try the public url
if page.status_code != 200:
    page = requests.get(public_url, headers=headers)
#Logging
print('URL: ', page.url)
#Get all the centers
centers  = page.json()['centers']
#Filter the centers according to the logic
open_centers = list(filter(None, map(lambda l:get_open_slot_centers(l), centers)))

#Log data to terminal
print("{}: HTTP response {}, count:{}".format(datetime.datetime.now().strftime('%c'), page.status_code, len(centers)))
maxi = '' #For many details
mini = '' #For limited details
for i in open_centers:
    #Initialise data to empty strings
    price = ''
    slots = ''
    minislots = ''
    #Collect vaccine price info
    for v in i.get('vaccine_fees', []):
        price += '{}={}|'.format(v['vaccine'], v['fee'])
    #Collection vaccine session info
    for s in i.get('sessions', []):
        slots += '{}: {}:Dose1 - {}, {}\n'.format(s['date'], s['vaccine'], s['available_capacity_dose1'],  '|'.join(s['slots']))
        minislots += '{}:{}:Dose1={} | '.format(s['date'], s['vaccine'], s['available_capacity_dose1'])
    #Build a maxi and a mini message with additional details
    maxi += '{}: {} - {}\nPrice: {}\nFreeSlots: {}\n'.format(i['name'], i['address'], i['pincode'], price, slots)
    mini += '{}: {}\nAddr:{}\n\n'.format(i['name'], minislots, i['address'])
print(maxi)

#If message to whatsapp is enabled and we have open centers
# Send a message to the user
whatsapp = True
if whatsapp and open_centers:
    print("Whatsapp'd message: {}".format(mini))
    for c in callmebot_d:
        sent = requests.get('https://api.callmebot.com/whatsapp.php?phone={}&text={}&apikey={}'.format(c['phone'], mini, c['apikey']))
        print('msg to: {} ... httpstatus: {}'.format(c['phone'], sent.status_code))
#Separator
print('='*80)
