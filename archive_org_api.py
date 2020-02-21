import requests
import lxml
import csv
import argparse
import re
from bs4 import BeautifulSoup



# Returns all existing urls for a website from archive.org 
def archive_org_api(website,res_limit)
	set_final=set()
	arch_source = requests.get ('http://web.archive.org/cdx/search/cdx?url=' + website + '&matchType=domain&fl=original&collapse=urlkey&limit=' + res_limit + '&output=csv' )
	arch_soup = BeautifulSoup(arch_source.text, 'lxml')
	arch_urls = arch_soup.find('p')
	arch_url_list=((arch_urls.text).split('\n'))
	for arch_url in arch_url_list:
		set_final.add(arch_url)
	return set_final