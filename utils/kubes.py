from kubernetes import client, config
from utils.get_config import PORT
import requests

config.load_kube_config()
v1 = client.CoreV1Api()

def get_pods():
    pods = v1.list_namespaced_pod(namespace="default", label_selector="app=llm")
    return [p.status.pod_ip for p in pods.items]

def get_status_of_pod(ip):
    status = requests.get(f"http://{ip}:{PORT}/status").json()
    print(status)
    return status["state"]

pods = get_pods()

print(get_status_of_pod(pods[0]))