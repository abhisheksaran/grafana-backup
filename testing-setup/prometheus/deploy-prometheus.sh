#!/bin/bash
kubectl apply -f prometheus-operator-django-app.yaml
kubectl apply -f prometheus-cluster-role-binding.yaml
kubectl apply -f prometheus-service-monitor.yaml
kubectl apply -f prometheus-service.yaml
