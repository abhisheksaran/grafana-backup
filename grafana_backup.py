import sys
import os
import json
import grafana_sdk
import argparse

class GrafanaBackupManager:

    grafana_config = "grafana_urls.json"

    def __init__(self, name, grafana_url, api_key):
        self.name = name
        self.grafana_api = grafana_sdk.GrafanaApi(grafana_url, api_key)
        if os.path.exists(GrafanaBackupManager.grafana_config) == True:
            grafana_config_content = GrafanaBackupManager.get_grafana_content(GrafanaBackupManager.grafana_config)
            local_backup_content = grafana_config_content['backup'].get('local', dict())
            self.local = local_backup_content.get('enabled', True) == True
            if self.local:
                self.backup_folder = local_backup_content.get('backup_folder', '')
                print("Local backup is enabled and storing under : {}".format(self.backup_folder))
                

    def dashboard_backup(self, folder_name):
        try:
            dashboards = self.grafana_api.search_db()
            if len(dashboards) == 0:
                print("Could not find any data for backup under {}".format(folder_name))
            else:
                print("Scanned data for backup - {}".format(len(dashboards)))

            for dashboard in dashboards:
                print(dashboard)
                dashboard_uri = dashboard['uid']
                dashboard_title = dashboard['title'].replace(" ","")
                dashboard_details_json = self.grafana_api.dashboard_details(dashboard_uri)
                self.__store(folder_name, "{}_{}.json".format(dashboard_title.lower(), dashboard_uri.lower()), dashboard_details_json)
        except Exception as exc:
            print("Error taking backup {}, error : {}".format(folder_name, str(exc)))


    def __store(self, folder_name, file_name, response):

        try:
            if self.local: 
                folder_name = self.backup_folder+folder_name
                print("Storing data on folder : {}".format(folder_name))
                os.makedirs(folder_name, exist_ok  =True)
                with open(folder_name+file_name,'w') as fp:
                    json.dump(response, fp, indent = 4, sort_keys=True)
                fp.close()
        except Exception as exc:
            print("Error storing backup locally, error : {}".format( str(exc)))

    def dashboard_restore(self,folder_name):
        try:
            backup_file_list = os.listdir(self.backup_folder+folder_name)
            if len(backup_file_list) == 0:
                print("couldn't find any files to restore in folder {}".format(backup_folder+folder_name))
            else:
                print("Scanned data to create db- {}".format(backup_file_list))
            
            for backup_file in backup_file_list:
                dashboard_content_json = self.get_backup_meta_content(self.backup_folder+folder_name+backup_file)
                folder_id = dashboard_content_json['meta']['folderId']
                folder_title = dashboard_content_json['meta']['folderTitle']
                if folder_id !=0:
                    #need to create a folder using create folder api
                    pass
                del dashboard_content_json['dashboard']['uid']
                del dashboard_content_json['dashboard']['id']
                dashboard_content_json['folderId'] = folder_id
                dashboard_content_json['message'] = "Restored the dashboard with backup file {}".format(backup_file)
                #we only want to restore deleted dashboards 
                dashboard_content_json['overwrite'] = False
                #print(json.dumps(dashboard_content_json, indent=4))
                print("\n\n")
                response = self.grafana_api.restore(json.dumps(dashboard_content_json))
                #print(json.dumps(response.json, indent=4))
                if response.status_code == 200:
                    print("Restored the dashboard with backup file {}".format(backup_file))
        
                    
        except Exception as exc : 
            print("Error restroing the dashboard: {}, error : {}".format(backup_file,str(exc)))
    
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
            print("error reading file {}, error: {}".format(file_name, str(exc)))


def get_grafana_mapper(grafana_url):
    try:
        name = grafana_url['name']
        url = grafana_url['url']
        api_key = grafana_url['api_key']
        return name, url, api_key
    except Exception as exc:
        print("error mapping grafana host config file, {}".format(str(exc)))

#get the url file
grafana_url = GrafanaBackupManager.get_grafana_content(GrafanaBackupManager.grafana_config)['grafana_urls']
name, url, api_key = get_grafana_mapper(grafana_url[0])
gbm = GrafanaBackupManager(name, url, api_key)
backup_folder = "test-1/"
#gbm.dashboard_backup(backup_folder)
gbm.dashboard_restore(backup_folder)



    

