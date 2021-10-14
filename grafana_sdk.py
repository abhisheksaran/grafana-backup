import requests 
import json
import sys 
import logging 

class GrafanaApi:
	
    def __init__(self, grafana_url, api_key):
	    self.grafana_url = grafana_url
	    self.api_key = api_key

    def __get_header(self):
        return {"Authorization": "Bearer {}".format(self.api_key)}

    def search_db(self):
        url = "{}/api/search?type=dash-db".format(self.grafana_url)
        response = requests.get(url, headers=self.__get_header())
        if response.status_code != 200:
            print("API Call error, API: {}, status_code:{}, error: {}".format(url, response.status_code, response.text))
        return response.json()


    def dashboard_details(self, dashboard_uid):
        url = "{}/api/dashboards/uid/{}".format(self.grafana_url, dashboard_uid)
        response = requests.get(url, headers = self.__get_header())
        if response.status_code != 200:
            print("API Call error, API: {}, status_code:{}, error: {}".format(url, response.status_code, response.text))
        print(response.json())
        return response.json()

    def restore(self, json_content):
        headers=self.__get_header()
        headers['Content-Type'] = 'application/json'
        url = "{}/api/dashboards/db/".format(self.grafana_url)
        response = requests.post(url, data = json_content, headers=headers)
        if response.status_code != 200:
            print("API Call error, API: {}, status_code:{}, error: {}".format(url, response.status_code, response.text))
        return response

    


