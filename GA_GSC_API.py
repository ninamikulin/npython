import requests
import lxml
import csv
import argparse
import re
from bs4 import BeautifulSoup
import simplejson
from apiclient import errors
from apiclient.discovery import build
from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.service_account import ServiceAccountCredentials
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from django.core.exceptions import ValidationError

'''
More on Google OAUTH: 
https://developers.google.com/analytics/devguides/reporting/core/v3/quickstart/service-py
https://developers.google.com/webmaster-tools/search-console-api-original/v3/how-tos/search_analytics
https://developers.google.com/identity/protocols/OAuth2
'''
# credentials from the client secrets file from the console
CLIENT_ID = 'CLIENT_ID'
CLIENT_SECRET = 'CLIENT_SECRET'

# oauth flow step 1
def gsc_1():
	# getting links to temporary tokens for GSC and GA

	GA_SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

	# Check https://developers.google.com/webmaster-tools/search-console-api-original/v3/ for all available scopes
	OAUTH_SCOPE = 'https://www.googleapis.com/auth/webmasters.readonly'

	# Redirect URI for installed apps
	REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

	# Run through the OAuth flow and retrieve credentials
	# step 1
	flow_gsc = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
	authorize_url_gsc = flow_gsc.step1_get_authorize_url()
	
	flow_ga = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, GA_SCOPES, REDIRECT_URI)
	authorize_url_ga = flow_ga.step1_get_authorize_url()

	return (authorize_url_gsc, authorize_url_ga)


# oauth flow step 2
def gsc_2(gsc_property_uri, code_gsc, code_ga, start_date, end_date, ga_view_id):

	# preparing a set to store all the unique urls in
	set_final=set()

	'''
	_____________________________________________________________________________________________________

	GOOGLE Search console 
	_____________________________________________________________________________________________________
	'''

	# Check https://developers.google.com/webmaster-tools/search-console-api-original/v3/ for all available scopes
	OAUTH_SCOPE = 'https://www.googleapis.com/auth/webmasters.readonly'
	GA_SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

	# Redirect URI for installed apps
	REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
	
	# Defining the request made to GSC
	gsc_request={
			'startDate': start_date,
			'endDate': end_date,
			'dimensions': ['page']
		}

	# passing the client ID, client secret, and scope to its constructor
	flow_gsc = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
	 
	# Getting credentials 
	credentials_gsc = flow_gsc.step2_exchange(code_gsc)


	# Create an httplib2.Http object and authorize it with our credentials
	http = httplib2.Http()
	http_gsc = credentials_gsc.authorize(http)


	webmasters_service = build('webmasters', 'v3', http=http, cache_discovery=False)

	# Retrieve list of properties in account
	site_list = webmasters_service.searchanalytics().query(
	 	siteUrl=gsc_property_uri, body=gsc_request).execute()

	# get the urls from the site_list
	for gsc_keys in site_list.values():
		for gsc_item in gsc_keys:
			try:
				for gsc_url in gsc_item['keys']:
					set_final.add(gsc_url)
					print('gsc_url')
					print(gsc_url)
			except Exception as e:
				print(type(e))
				pass
	
	'''
	_____________________________________________________________________________________________________

	GOOGLE ANALYTICS 
	_____________________________________________________________________________________________________
	'''

	# Settings to call GA API
	GA_SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
	GA_DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
	GA_CLIENT_SECRETS_PATH = '' # Path to client_secrets.json file.
	GA_PROPERTY_URL = gsc_property_uri


	# Function to initialize the SERVICE OBJECT
	def initialize_analyticsreporting():
		"""Initializes the analyticsreporting service object.

		Returns:
		analytics an authorized analyticsreporting service object.
	  	"""
		# Parse command-line arguments.
		parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
		parents=[tools.argparser])
		flags = parser.parse_args([])
		# Set up a Flow object to be used if we need to authenticate.
		flow_ga = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, GA_SCOPES, REDIRECT_URI)

		credentials_ga = flow_ga.step2_exchange(code_ga)
		http = httplib2.Http()
		http_ga = credentials_ga.authorize(http)
		

	  	# Build the service object.
		analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=GA_DISCOVERY_URI, cache_discovery=False)

		return analytics

	# Use the SERVICE OBJECT to query the ANLYTICS REPORTING API
	def get_report(analytics):
	  return analytics.reports().batchGet(
	      body={
	        'reportRequests': [
	        {
	          'viewId': ga_view_id,
	          'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
	          'metrics': [{'expression': 'ga:Sessions'}],
	          'dimensions':[{'name': 'ga:landingPagePath'}]
	        }]
	      }
	  ).execute()

	# PARSE and RETURN a list of urls 
	def print_response(response):
		
		all_urls_analytics=[]
		for report in response.get('reports', []):
			r={}
			columnHeader = report.get('columnHeader', {})
			dimensionHeaders = columnHeader.get('dimensions', [])
			metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
			rows = report.get('data', {}).get('rows', [])
			for row in rows:
				dimensions = row.get('dimensions', [])
				dateRangeValues = row.get('metrics', [])

				for header, dimension in zip(dimensionHeaders, dimensions):

					header = 'Landing page URL'
					dimension1 = re.sub("'|b'", "", dimension)
					all_urls_analytics.append(dimension1)
		return all_urls_analytics

	ga_analytics = initialize_analyticsreporting()
	ga_response = get_report(ga_analytics)

	# Iterate throught the list of urls from GA and concatenate with the domain to get the absolute urls
	for ga_url in (print_response(ga_response)):
			ga_url=GA_PROPERTY_URL+ga_url
			print('ga_url')
			print(ga_url)
			set_final.add(ga_url)
	# Returning the set prepared in the beginning with all the unique urls from databases.
	return (set_final)