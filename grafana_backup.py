import sys
import os
import json
import grafana_sdk
import glob
#import boto3
from datetime import datetime

class GrafanaBackupManager:

    grafana_config = "grafana_urls.json"

    def __init__(self, name, grafana_url, api_key):
        """
        Initialising grafana backup manager
        """
        self.name = name
        self.grafana_api = grafana_sdk.GrafanaApi(grafana_url, api_key)
        self.s3 = True
        current_date = datetime.now().strftime("%d-%m-%YT%H:%M:%S")
        self.folder_name = current_date+'/'
        if os.path.exists(GrafanaBackupManager.grafana_config) == True:
            grafana_config_content = GrafanaBackupManager.get_grafana_content(GrafanaBackupManager.grafana_config)
            local_backup_content = grafana_config_content['backup'].get('local', dict())
            self.local = local_backup_content.get('enabled', True) == True
            if self.local:
                self.backup_folder = local_backup_content.get('backup_folder', '')+self.name+'/daily/'
                grafana_sdk.get_logger().info("Local backup is enabled and storing under : {}".format(self.backup_folder))
                

    def dashboard_backup(self):
        """
        Get all the dashboards in all folder 
        """
        try:
            dashboards = self.grafana_api.search_db()
            if len(dashboards) == 0:
                grafana_sdk.get_logger().info("Could not find any data for backup under")
            else:
                grafana_sdk.get_logger().info("Scanned {} dashboards for backup -".format(len(dashboards)))

            for dashboard in dashboards:
                dashboard_uri = dashboard['uid']
                dashboard_title = dashboard['title'].replace(" ","")
                dashboard_details_json = self.grafana_api.dashboard_details(dashboard_uri)
                # Store the dashboard in the folder_name location
                folder_name = self.backup_folder+self.folder_name
                self.__store(folder_name, "{}_{}.json".format(dashboard_title.lower(), dashboard_uri.lower()), dashboard_details_json)
        except Exception as exc:
            grafana_sdk.get_logger().info("Error taking backup, error : {}".format(str(exc)))


    def __store(self, folder_name, file_name, response):
        """
        Backup all the dashbaords in .json format 
        """
        try:
            if self.local: 
                grafana_sdk.get_logger().info("Storing dashboard-data in folder : {}".format(folder_name))
                os.makedirs(folder_name, exist_ok  =True)
                with open(folder_name+file_name,'w') as fp:
                    json.dump(response, fp, indent = 4, sort_keys=True)
                fp.close()
        except Exception as exc:
            grafana_sdk.get_logger().info("Error storing backup locally, error : {}".format( str(exc)))

    def dashboard_restore(self):
        """
        Restore all the dashboards from the recent backup
        """
        try:
            # Restore most recent backup
            most_recent_backup = max(glob.glob(os.path.join(self.backup_folder, '*/')), key=os.path.getmtime)
            grafana_sdk.get_logger().info("Most recent backup is {}".format(most_recent_backup))
            backup_file_list = os.listdir(most_recent_backup)
            if len(backup_file_list) == 0:
                grafana_sdk.get_logger().info("Couldn't find any files to restore in folder {}".format(self.backup_folder+self.folder_name))
            else:
                grafana_sdk.get_logger().info("Scanned data to create db- {}".format(backup_file_list))
            for backup_file in backup_file_list:
                dashboard_content_json = self.get_backup_meta_content(most_recent_backup+backup_file)
                folder_id = dashboard_content_json['meta']['folderId']
                folder_title = dashboard_content_json['meta']['folderTitle']
                if folder_id != 0:
                    folder_response = self.grafana_api.search_folder(folder_id)
                    if folder_response.status_code != 200:
                        new_folder_response = self.grafana_api.create_folder(folder_title)
                        folder_id = new_folder_response['id']
                    else:
                        folder_response = folder_response.json()
                        folder_id = folder_response['id']
                del dashboard_content_json['dashboard']['uid']
                del dashboard_content_json['dashboard']['id']
                dashboard_content_json['folderId'] = folder_id
                dashboard_content_json['message'] = "Restored the dashboard with backup file {} on {}".format(backup_file, datetime.now().strftime("%d-%m-%YT%H:%M:%S"))
                # We only want to restore deleted dashboards 
                dashboard_content_json['overwrite'] = False
                grafana_sdk.get_logger().info("\n\n")
                response = self.grafana_api.restore(json.dumps(dashboard_content_json))
                if response.status_code == 200:
                    grafana_sdk.get_logger().info("Restored the dashboard with backup file {}".format(backup_file))
        except Exception as exc : 
            grafana_sdk.get_logger().info("Error restoring the dashboard, error : {}".format(str(exc)))
    
    def get_backup_meta_content(self, file_name):
        return GrafanaBackupManager.get_grafana_content(file_name)

    @staticmethod
    def get_grafana_content(file_name):
        try:
            grafana_url_file = open(file_name)
            grafana_url_data = json.load(grafana_url_file)
            grafana_url_file.close()
            return grafana_url_data
        except Exception as exc:
            grafana_sdk.get_logger().info("Error reading file {}, error: {}".format(file_name, str(exc)))


def get_grafana_mapper(grafana_url):
    """
    Helper method to map dictionary
    """
    try:
        name = grafana_url['name']
        url = grafana_url['url']
        api_key = grafana_url['api_key']
        return name, url, api_key
    except Exception as exc:
        grafana_sdk.get_logger().info("Error mapping grafana host config file, {}".format(str(exc)))

if __name__=="__main__":
    # Get the url file
    grafana_url = GrafanaBackupManager.get_grafana_content(GrafanaBackupManager.grafana_config)['grafana_urls']
    name, url, api_key = get_grafana_mapper(grafana_url[0])
    gbm = GrafanaBackupManager(name, url, api_key)

    if input("Enter 'backup' for backup and 'restore' for restore\n") == 'backup':
        gbm.dashboard_backup()
    else:
        gbm.dashboard_restore()


        

