minikube start
kubectl apply -f ollama-pv-pvc.yaml
kubectl apply -f ollama-deployment.yaml
kubectl apply -f ollama-service.yaml
kubectl get pods
kubectl get svc
sleep 5
kubectl port-forward service/ollama-service 11434:11434
