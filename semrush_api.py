import requests
import json
import re
import unicodedata
from bs4 import BeautifulSoup
import csv

	
def semrush_api(api_key, website, res_num)
	response = requests.get('https://api.semrush.com/analytics/v1/?key=' + api_key + '&target=' + website + '&type=backlinks_pages&target_type=root_domain&display_limit=' + res_num)
	soup = BeautifulSoup (response.text, 'lxml')
	# Splitting the result string to get individual items
	sr_all = re.split('[\n;'']+', soup.text)
	# get only the urls from the list of items
	for sr_url in sr_all:
		set_final.add(sr_url)
	
	# Returning the set prepared in the beginning with all the unique urls from databases.
	return (set_final)