## install Kubectl
brew install kubectl

## deploy app
kubectl create deployment hello-k8s --image=nginx

## expose the port 
kubectl expose deployment hello-k8s --type=NodePort --port=80

## See Your Resources:
kubectl get pods
kubectl get deployments
kubectl get services

## Clean Up
kubectl delete service hello-k8s
kubectl delete deployment hello-k8s
kubectl delete pods nginx

