#!/bin/bash

echo "stopping..."
## Stop skaffold
echo "> stopping kubernetes"
skaffold delete
kubectl delete -f kubernetes-manifests/adservice.yaml
kubectl delete -f kubernetes-manifests/cartservice.yaml
kubectl delete -f kubernetes-manifests/checkoutservice.yaml
kubectl delete -f kubernetes-manifests/currencyservice.yaml
kubectl delete -f kubernetes-manifests/emailservice.yaml
kubectl delete -f kubernetes-manifests/loadgenerator.yaml
kubectl delete -f kubernetes-manifests/paymentdbservice.yaml
kubectl delete -f kubernetes-manifests/productcatalogservice.yaml
kubectl delete -f kubernetes-manifests/recommendationservice.yaml
kubectl delete -f kubernetes-manifests/redis.yaml
kubectl delete -f kubernetes-manifests/shippingservice.yaml
echo "> stopping agent"
helm uninstall datadog-agent
echo "> stopping minikube"
minikube stop