# What's the problem we are solving ?
In a unfortunate crash, we might lose our data stored in the disk (EBS). Though, to eliminate such a single point of failure, we can take the EBS snapshots on regular intervals and store them in the Amazon S3.
Furthermore, if such an EBS containing our Grafana Dashboard data crashes, we will be able to get the data back by above mentioned appraoch but dashbaords still have to be manually built which can be quite large in number. 

# What's our solution ?
To solve the same, We will be using Grafana APIs to backup the dashboards as .json files in timestamp based folders.

To restore, every dashboards in such a timestamp based folder will be created after creating required dashboard parent folder as required. 

# Directory Structure
```bash
.
├── Dockerfile                      # Dockerfile to build docker image of the solution
├── README.md                       # README file for the project 
├── grafana-backup                  # The parent folder where local backups will be stored, 
|   |                               # can be set via env varaible BACKUP_FOLDER
│   └── grafana-demo-dashboards     # Env variable GRAFANA_HOST_NAME
│       └── daily
│           ├── 26-10-2021T23:06:52 # Timestamp based backup folders (UTC+5:30)
|           |   |                   # Dashbords will be store in the format DASHBOARD-NAME_UID.json
│           │   ├── clustermonitoringforkubernetes_5feiaponk.json 
│           │   └── prometheusstats_udqjcfo7k.json 
│           |
│           └── 27-10-2021T00:14:43
│               ├── clustermonitoringforkubernetes_5feiaponk.json
│               └── prometheusstats_udqjcfo7k.json
├── grafana_backup.py               # DRIVE SCRIPT
├── grafana_sdk.py                  # GRAFANA APIs MODULE
├── k8s                             # JOBS NEEDED IN K8S ENVIRONMENT 
│   ├── backup-cronjob.yaml         # CRON-JOB TO RUN SCHEDULED BACKUPs
│   ├── backup-job.yaml             # JOB TO RUN A SINGLE BACKUP
│   ├── help-job.yaml               # JOB TO SEE HELP IN LOGs
│   ├── pvc_gb.yaml                 # CREATE PV AND PVC 
│   └── restore-job.yaml            # JOB TO RUN THE RESTORE 
└── requirements.txt    

```
# Environment Variables
    ```bash
        GRAFANA_HOST_NAME
        GRAFANA_URL
        GRAFANA_KEY
        BACKUP_FOLDER_NAME 
        LOCAL_BACKUP
        S3_BACKUP
        S3_BUCKET_NAME
        SHOW_BACKUP
        ```
        - The env variable GRAFANA_HOST_NAME is the name of Grafana-Instance you are taking backup of. 
        - The env variable GRFANA_URL is the address of the grafana instance.
        - The env variable GRAFANA_KEY is the API KEY with editor permission. https://grafana.com/docs/grafana/latest/http_api/auth/ 
        - The env variable BACKUP_FOLDER is the name of the parent folder to store all such backups. 
        - The env variable LOCAL_BACKUP is set to True when you want to run a local backup instead of storing in S3. 
        - The env variable S3_BACKUP is set to True when you want to store backups/restore in/from S3 instead local backup. 
        - The env variable S3_BUCKET_NAME is S3 bucket name where you want to store your backups. If
          the bucket is not already there, a new bucket will be created. You must set it when S3_BACKUP is enabled.
        - The env variable SHOW_BACKUP is to see last n backups when we run the script with '-h' option.
          This is only supported in local backups not in S3.
	
	- Note: The phrase "backup as local backup" means having LOCAL_BACKUP as True and S3_BACKUP as False
	- Note: The phrase "backup as S3 backup" means having LOCAL_BACKUP as True and S3_BACKUP as False 
	<br>

# Testing in Local System
1. Clone the repository in your local system.
2. Export the required env variables in your .zprofile or .bash-profile based on your default shell.
   For eg.: If you want to store backups locally, set the env variable LOCAL_BACKUP to True and
   S3_BACKUP to False and vice versa for S3 backup. An example for local s3-testing is given below. 
   ```bash
        export GRAFANA_HOST_NAME=<grafana-host-name>
        export GRAFANA_URL=<grafana-url>
        export GRAFANA_KEY=<grafana-API-key-with-editor-permission>
        export BACKUP_FOLDER_NAME=grafana-backup 
        export LOCAL_BACKUP=false
        expory S3_BACKUP=True
        export S3_BUCKET_NAME=<S3-bucket-name>
        export SHOW_BACKUP=10 
	```
 
3. Running the script-
    - To take the backup:   
        >python3 grafana_backup.py -b    
    - To restore from the most recent backup:
        >python3 grafana_backup.py -r  
    - To restore from the specific backup: 
        >python3 grafana_backup.py -r 26-10-2021T23:06:52
    - To show help:
        >python3 grafana_backup.py -h 
Note: If you are storing backups in S3, make sure you have configured AWS credentials. And if you are accessing company S3, you must be connected to company VPN as well. 

# Testing in K8s as backup in PV
1. Create the docker image with a version tag: 
    >docker build -t grafana-backup:5.0 .
2. Tag the docker image with your own dockerhub repository (For example mine is- abhitrone):
    >docker tag grafana-backup:5.0 abhitrone/grafana-backup:5.0
3. Push the docker image in your dockerhub repository:
    >docker push abhitrone/grafana-backup:5.0
4. Change directory to k8s and Create a pv (EBS) and pvc in dev environment:
    >kubectl apply -f pvc_gb.yaml
5. Create a backup job in same env with "backup as local backup":
    >kubectl apply -f backup-job.yaml
6. Create a help job in same env with "backup as local backup":
    >kubectl apply -f help-job.yaml
7. Create a restore job in same env with "backup as local backup"::
    >kubectl apply -f restore-job.yaml
8. If you want, now you can schedule the backup as a cronjob with "backup as local backup":
    >kubectl apply -f backup-cronjob.yaml 

# Finally, Running in K8s as backup in S3
1. Have docker image ready and pushed to dockerhub as earlier. 
2. You might need to implement IRSA to enable pods to access S3.
3. Create a backup job in same env with "backup as local backup":
    >kubectl apply -f backup-job.yaml
4. Create a help job in same env with "backup as local backup":
    >kubectl apply -f help-job.yaml
5. Create a restore job in same env with "backup as local backup"::
    >kubectl apply -f restore-job.yaml
6. If you want, now you can schedule the backup as a cronjob with "backup as local backup":
    >kubectl apply -f backup-cronjob.yaml 


