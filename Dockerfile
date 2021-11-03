FROM python:3.8 as builder

COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install awscli

# Install all dependencies
RUN pip3 install -r requirements.txt

# Copy the files 
COPY ./ /src
WORKDIR /src

LABEL APP_NAME="grafana-snapshot-restore"
LABEL COMPONENT="dashbord-backup-restore"

# Grafana env varibles
ENV APP_PATH "/src"
ENV PYTHONPATH "${PYTONPATH}:/src"
ENV PARAMS "PARAMS"
ENV GRAFANA_HOST_NAME "GRAFANA_HOST_NAME"
ENV GRAFANA_URL "GRAFANA_URL"
ENV GRAFANA_KEY "GRAFANA_KEY"
ENV BACKUP_FOLDER_NAME "BACKUP_FOLDER_NAME"
ENV LOCAL_BACKUP "LOCAL_BACKUP"
ENV SHOW_BACKUP "SHOW_BACKUP"

# To set default values grafana config env variables or we can set these directly from .yaml files in kubernetes
#ARG GRAFANA_HOST_NAME="eks-cluster-test-dashboards"
#ARG GRAFANA_URL="<grafana-instance-url>"
#ARG GRAFANA_KEY="<grafana-api-key>"
#ARG BACKUP_FOLDER_NAME="grafana-backup"
#ARG LOCAL_BACKUP=True
ARG SHOW_BACKUP="10"

ENV GRAFANA_HOST_NAME=$GRAFANA_HOST_NAME
ENV GRAFANA_URL=$GRAFANA_URL
ENV GRAFANA_KEY=$GRAFANA_KEY
ENV BACKUP_FOLDER_NAME=$BACKUP_FOLDER_NAME
ENV LOCAL_BACKUP=$LOCAL_BACKUP
ENV SHOW_BACKUP=$SHOW_BACKUP

# Run the script
CMD python3 grafana_backup.py ${PARAMS}

