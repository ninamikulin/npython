import requests
import lxml
from bs4 import BeautifulSoup
import simplejson

# returns all urls for a website from ahrefs
def ahrefs_api(token, webiste, res_num)
	set_final=set()
	# GET THE DATA in the for of .json and parse it then get the pages from the json document
	ahrefs_response = requests.get('https://apiv2.ahrefs.com?token='+token+'&target='+website+'&limit='+res_num+'&output=json&from=pages_extended&mode=domain')
	ahrefs_data=simplejson.loads(ahrefs_response.text)
	ahrefs_pages= ahrefs_data['pages']
	for ahrefs_item in ahrefs_pages:
		ahrefs_url=ahrefs_item['url']
		set_final.add(ahrefs_url)
	return set_final