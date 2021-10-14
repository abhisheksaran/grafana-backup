# grafana-backup
This setup backup all the dashboard in your general folder as of now in directory /backup/test-1.
We save dashboard as .json files.
These json files are letter used to restore the dashboard. 
Restored dashboard will have same title but diff id and uids. 

To run this, 
- clone the repository in your local system
- set the grafana url in grafana-urls.json file
- create a api key from grafana with editor permissions
- put the api key in grafana-urls.json file.
- uncomment the backup, comment our the restore call from grafana-backup.py and run this python script. 
- to restore the saved dashboard, call the corresponding  method as done in previous step.
