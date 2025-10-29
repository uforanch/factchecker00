from kubernetes import client, config
from utils.get_config import PORT
import requests
import yaml

config.load_kube_config()
v1 = client.CoreV1Api()

def get_pods():
    pods = v1.list_namespaced_pod(namespace="default", label_selector="app=llm")
    return [p.status.pod_ip for p in pods.items]

def get_status_of_pod(pod):
    status = requests.get(f"http://{pod}:{PORT}/status").json()
    print(status)
    return status["state"]

def send_payload_to_pod(payload, pod):
    response = requests.post(f"http://{pod}:{PORT}/api/generate", json=payload, stream=True)
    output = ""
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8")
            resp = yaml.safe_load(data)["response"]
            output += resp
    return output

pods = get_pods()

print(get_status_of_pod(pods[0]))