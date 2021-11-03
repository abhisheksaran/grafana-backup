import sys
import os
import json
import grafana_sdk
import glob
import argparse
from argparse import RawTextHelpFormatter
import pytz 
import shutil
#import boto3
from datetime import datetime

class GrafanaBackupManager:

    def __init__(self, name, grafana_url, api_key, show_backup ):
        """
        Initialising grafana backup manager
        """
        self.name = name
        self.grafana_api = grafana_sdk.GrafanaApi(grafana_url, api_key)
        self.show_backup = show_backup
        self.s3 = True

        # Standardizing time in IST = UTC + 05:30
        IST = pytz.timezone('Asia/Kolkata')
        current_date = datetime.now(IST).strftime("%d-%m-%YT%H:%M:%S")
        self.folder_name = current_date+'/'

        # Get grafana config from environment variables
        grafana_config_content = GrafanaBackupManager.get_grafana_content()
        local_backup_content = grafana_config_content['backup'].get('local', dict())
        self.local = local_backup_content.get('enabled', True) == True
        
        if self.local:
            self.parent_backup_folder = local_backup_content.get('backup_folder', '')+'/'+self.name+'/daily/'
            

    def dashboard_backup(self):
        """
        Get all the dashboards in all folder 
        """
        try:
                
            if self.local:
                grafana_sdk.get_logger().info("Local backup is enabled and storing under : {}".format(self.parent_backup_folder))
                grafana_sdk.get_logger().info("Each Backup folder will have format like this : %d-%m-%YT%H:%M:%S")
        
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
                    folder_name = self.parent_backup_folder+self.folder_name
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

    def dashboard_restore(self, backup_folder):
        """
        Restore all the dashboards from the given backup folder, if no folder specified, we will restore from the most recent backup. 
        """
        try:
            # If a backup_folder is not specified, restore the most recent backup
            if backup_folder is None:
                backup_folder = max(glob.glob(os.path.join(self.parent_backup_folder, '*/')), key=os.path.getmtime)
                grafana_sdk.get_logger().info("Restoring from recent backup: {}".format(backup_folder))
                backup_file_list = os.listdir(backup_folder)
            else:
                backup_folder = self.parent_backup_folder+backup_folder+'/'
                grafana_sdk.get_logger().info("Restoring from the specified backup: {}".format(backup_folder))
                backup_file_list = os.listdir(backup_folder)
        
            #print(backup_folder)

            if len(backup_file_list) == 0:
                grafana_sdk.get_logger().info("Couldn't find any files to restore in folder {}".format(self.parent_backup_folder+backup_folder))
            else:
                grafana_sdk.get_logger().info("Scanned {} dashboard data to create db- {}".format(len(backup_file_list), backup_file_list))
            for backup_file in backup_file_list:
                dashboard_content_json = self.get_backup_meta_content(backup_folder+backup_file)
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
                
                # Overwrite property is needs to be discussed
                dashboard_content_json['overwrite'] = True
                
                #grafana_sdk.get_logger().info("\n\n")
                response = self.grafana_api.restore(json.dumps(dashboard_content_json))
                if response.status_code == 200:
                    grafana_sdk.get_logger().info("Restored the dashboard with backup file {}".format(backup_file))
        except Exception as exc : 
            grafana_sdk.get_logger().info("Error restoring the dashboard, error : {}".format(str(exc)))
    
    def get_backup_meta_content(self, file_name):
        """
        Return the backup dashboard in dictionary
        """
        try:
            grafana_url_file = open(file_name)
            grafana_url_data = json.load(grafana_url_file)
            grafana_url_file.close()
            return grafana_url_data
        except Exception as exc:
            grafana_sdk.get_logger().error("error reading file {} , error {}".format(file_name, str(exc)))
    
    @staticmethod
    def get_grafana_content():
        """
        Get grafana configuration from env variables
        """
        try:
            grafana_url_data =  {
                "grafana_urls":[
                    {
                        "name": os.environ['GRAFANA_HOST_NAME'],
                        "url": os.environ['GRAFANA_URL'],
                        "api_key": os.environ['GRAFANA_KEY'],
                        "show_backup": int(os.environ['SHOW_BACKUP'])
                    }
                ],
                "backup":{
                    "local":{
                        "backup_folder": os.environ['BACKUP_FOLDER_NAME'],
                        "enabled": os.getenv('LOCAL_BACKUP','False').lower() in ('true','1','t')
                    }
                }
            }
            #print(grafana_url_data)
            return grafana_url_data
        except Exception as exc:
            grafana_sdk.get_logger().info("Error getting grafana-config env variables, error: {}".format(str(exc)))
    
    def get_last_n_backup(self,n):
        """
        Return the list of recent n backup
        """
        x= sorted(glob.glob(os.path.join(self.parent_backup_folder, '*/')), key=os.path.getmtime)[-n:]
        x.reverse()
        return x

def get_grafana_mapper(grafana_url):
    """
    Helper method to map dictionary
    """
    try:
        name = grafana_url['name']
        url = grafana_url['url']
        api_key = grafana_url['api_key']
        show_backup = grafana_url['show_backup']
        return name, url, api_key, show_backup
    except Exception as exc:
        grafana_sdk.get_logger().info("Error mapping grafana host config file, {}".format(str(exc)))

def main():
    """
    Main method to drive the backup and restore. 
    """
    # Get the env variables
    grafana_url = GrafanaBackupManager.get_grafana_content()
    #grafana_sdk.get_logger().info("The grafana configuration is: {}".format(grafana_url))
    name, url, api_key, show_backup = get_grafana_mapper(grafana_url['grafana_urls'][0])
    gbm = GrafanaBackupManager(name, url, api_key, show_backup)

    
    # Argument parser
    parser = argparse.ArgumentParser(description='Grafana backup and restoration script.', formatter_class=RawTextHelpFormatter) 
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('-b','--backup', action='store_true',help=
            'take a backup of all the dashboards, \nlast {} backups are as follows: {}'.format(gbm.show_backup ,gbm.get_last_n_backup(show_backup))
    )
    group.add_argument('-r','--restore', type=str, nargs='?', default='',  metavar='BACKUP_DIRECTORY', help="restore all the dashboard from most recent backup, \nspecify a \"backup_directory\" if you want to restore a particular backup; for eg: \"-r 25-10-2021T15:59:54\", \nset the env variable SHOW_BACKUP to see last n backup in help")
    
    args = parser.parse_args()
    #print(args)    
    
    if args.backup:
        grafana_sdk.get_logger().info("Recieved input -b for backup ")
        gbm.dashboard_backup()        
    elif 'restore' in args:
        grafana_sdk.get_logger().info("Recieved input -r for  restore ")
        gbm.dashboard_restore(args.restore)
    else:
        parser.error('No action requested, add -b for backup or -r for restore.')

if __name__=="__main__":
    main()
           

