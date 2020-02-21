import requests
import json
import re
import unicodedata
from bs4 import BeautifulSoup
import csv


# GETS THE ARTICLES, URL, BODY, CONTRIBUTOR

def soup(soup):
	soupy = '"""' + soup + '"""'
	text = BeautifulSoup(soupy, 'lxml')
	return text.text

# prepare writer
csv_writer_file = open('CSV_FILE', 'w', newline='')
csv_writer = csv.writer(csv_writer_file, delimiter=';')

# settings
endpoint = 'https://content.guardianapis.com/search?'
api_key= 'API-KEY'
start_date = 'DATE'
end_date = 'DATE'
q= 'SEARCH_TERM'
page_size = 'PAGE_SIZE_FROM_1_TO_200'

# make request
response = requests.get(endpoint + q + & + 'api-key=' + api_key + & + 'from-date=' + start_date + 'to-date=' + end_date + '&format=json&page-size=' + page_size + '&show-tags=contributor&show-fields=body')
dicti = json.loads(response.text)

# write results to csv
for l in dicti['response']['results']:
	g= soup(l["fields"]['body']).encode('ASCII', 'ignore')
	try:
		csv_writer.writerow([l["webTitle"],l['webPublicationDate'],l["webUrl"],g])
	except UnicodeEncodeError:
		csv_writer.writerow([l["webTitle"].encode('ASCII', 'ignore'),l['webPublicationDate'].encode('ASCII', 'ignore'),l["webUrl"].encode('ASCII', 'ignore'),g])

csv_writer_file.close()
