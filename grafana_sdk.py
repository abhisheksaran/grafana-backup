import requests 
import json
import sys 
import logging 

def get_logger():
    logging.basicConfig(stream=sys.stdout, level="INFO", format="[%(asctime)s %(levelname)s [%(threadName)s] [%(filename)s:%(funcName)s:%(lineno)s] %(message)s",datefmt='%Y-%m-%dT%H:%M:%S')
    logger = logging.getLogger("grafana_backup")
    return logger

class GrafanaApi:
	
    def __init__(self, grafana_url, api_key):
	    self.grafana_url = grafana_url
	    self.api_key = api_key

    def __get_header(self):
        return {"Authorization": "Bearer {}".format(self.api_key)}

    def search_db(self):
        """
        API to get all the grafana-dashboards
        """
        url = "{}/api/search?type=dash-db".format(self.grafana_url)
        get_logger().info("Request To : URL {}".format(url))
        response = requests.get(url, headers=self.__get_header())
        if response.status_code != 200:
            get_logger().info("API Call error, API: {}, status_code:{}, error: {}".format(url, response.status_code, response.text))
        return response.json()


    def dashboard_details(self, dashboard_uid):
        """
        API to get the details about particular dashboards given its unique UID
        """
        url = "{}/api/dashboards/uid/{}".format(self.grafana_url, dashboard_uid)
        get_logger().info("Request To : URL {}".format(url))
        response = requests.get(url, headers=self.__get_header())
        if response.status_code != 200:
            get_logger().info("API Call error, API: {}, status_code:{}, error: {}".format(url, response.status_code, response.text))
        #print(response.json())
        return response.json()

    def search_folder(self, folder_id):
        """
        API to get a particular dashboard-folder given its unique folder_id
        """
        url = "{}/api/folders/id/{}".format(self.grafana_url, folder_id)
        get_logger().info("Request To : URL {}".format(url))
        response = requests.get(url, headers=self.__get_header())
        if response.status_code != 200:
            get_logger().info("API Call Error, API: {}, status_code: {}, error: {}".format(url, response.status_code, response.text))
        return response

    def create_folder(self, folder_title):
        """
        API to create a new grafana-dashboard folder of title provided as parameter
        """
        url = "{}/api/folders".format(self.grafana_url)
        data = { "title": folder_title,}
        get_logger().info("Request To : URL {}".format(url))
        response = requests.post(url, data= data,  headers=self.__get_header())
        if response.status_code != 200:
            get_logger().info("API Call Error, API: {}, status_code: {}, error: {}".format(url, response.status_code, response.text))
        return response.json()

    def restore(self, json_content):
        """
        API to create a new dashbord from the .json file given as parameter
        """
        headers=self.__get_header()
        headers['Content-Type'] = 'application/json'
        url = "{}/api/dashboards/db/".format(self.grafana_url)
        get_logger().info("Request To : URL {}".format(url))
        response = requests.post(url, data = json_content, headers=headers)
        if response.status_code != 200:
            get_logger().info("API Call error, API: {}, status_code:{}, error: {}".format(url, response.status_code, response.text))
        return response

    def dashboard_versions(self, dashboard_id):
        url = "{}/api/dashboards/id/{}/versions/{}".format(self.grafana_url, dashboard_id, version_no)
        get_logger().info("Request To : URL {}".format(url))
        response = requests.get(url, headers=self.__get_header())
        if response.status_code != 200:
            get_logger().error("API Call Error, API: {}, status_code: {}, error: {}".format(url, response.status_code, response.text))
        return response.json

    def tags(self):
        url = "{}/api/dashboards/tags".format(self.grafana_url)
        get_logger().info("Request To : URL {}".format(url))
        response - requests.get(url, headers=self.__get_header)
        if response.status_code != 200:
            get_logger().error("API Call Error, API: {}, status_code: {}, error: {}".format(url, response,status_code, response.text))
        return response.json



    


