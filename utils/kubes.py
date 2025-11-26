from kubernetes import client, config
#from utils.get_config import PORT
import requests
import yaml
from multiprocessing.pool import ThreadPool
from itertools import batched

config.load_kube_config()
v1 = client.CoreV1Api()

PORT = 11434

def get_pods():
    pods = v1.list_namespaced_pod(namespace="default", label_selector="app=ollama")
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



def kubes_parallel_analysis(id_prompts, filter_func = None, limit=-1):
    pods = get_pods()
    pool = ThreadPool(len(pods))
    # think this is it
    results = []
    for citation_batch in batched(id_prompts, len(pods)):
        r = pool.map(lambda x: (x[0][0], send_payload_to_pod(x[0][1], x[1])), zip(citation_batch, pods))
        results.extend(r)
        if limit>0:
            if filter_func is not None:
                n = len(list(filter(lambda x : filter_func(x[1]), results)))
            else:
                n = len(results)
            if n>=limit:
                results = results[:limit]
            break


    pool.close()
    return results

print(get_pods())
from utils.get_config import MODEL
print(get_status_of_pod(get_pods()[0]))
#print(send_payload_to_pod({"model": MODEL, "prompt": "Tell me a joke."}, get_pods()[0]))
