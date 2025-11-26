from itertools import batched
from multiprocessing.pool import ThreadPool

from kubernetes import config
from kubernetes.client import CoreV1Api, Configuration
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
import yaml
import json
import time
import os.path

if os.path.basename(os.path.normpath(os.getcwd())) == "utils":
    config_dir = os.path.dirname(os.getcwd()) + "//"
else:
    config_dir = os.getcwd() + "//"

# --------------------------------------------------------
# Load manifests
# --------------------------------------------------------
with open(config_dir + "ollama-pod.yaml", "r") as f:
    pod_MANIFEST = yaml.safe_load(f)

with open(config_dir + "ollama-pv-pvc.yaml", "r") as f:
    STORAGE_MANIFESTs = list(yaml.safe_load_all(f))

with open(config_dir + "config.json") as f:
    CONFIG = json.load(f)
    NUM_PODS = int(CONFIG["NUM_PODS"])

POD_NAME_I = lambda i : f"llama-{i}"

# --------------------------------------------------------
# Helpers
# --------------------------------------------------------
def wait_for_pv(api: CoreV1Api, name: str):
    print(f"Waiting for PV '{name}' to be Available/Bound...")
    while True:
        pv = api.read_persistent_volume(name)
        if pv.status.phase in ("Available", "Bound"):
            print(f"PV '{name}' is {pv.status.phase}.")
            break
        time.sleep(1)


def wait_for_pvc(api: CoreV1Api, name: str, namespace: str):
    print(f"Waiting for PVC '{name}' to be Bound...")
    while True:
        pvc = api.read_namespaced_persistent_volume_claim(name, namespace)
        if pvc.status.phase == "Bound":
            print(f"PVC '{name}' is Bound.")
            break
        time.sleep(1)


def wait_for_pod_ready(api: CoreV1Api, name: str, namespace: str):
    print(f"Waiting for pod '{name}' to be Running...")
    while True:
        pod = api.read_namespaced_pod(name=name, namespace=namespace)
        if pod.status.phase == "Running":
            print(f"Pod '{name}' is Running.")
            break
        time.sleep(1)


# --------------------------------------------------------
# Storage creation
# --------------------------------------------------------
def launch_storage(api: CoreV1Api):
    print("Launching storage resources…")
    try:
        for manifest in STORAGE_MANIFESTs:
            kind = manifest.get("kind")

            if kind == "PersistentVolume":
                print(f"Creating PV: {manifest['metadata']['name']}")
                api.create_persistent_volume(body=manifest)

            elif kind == "PersistentVolumeClaim":
                print(f"Creating PVC: {manifest['metadata']['name']}")
                api.create_namespaced_persistent_volume_claim(
                    namespace="default", body=manifest
                )

            else:
                print(f"Unknown manifest type: {kind}")

        # Wait for storage to be usable
        wait_for_pv(api, "ollama-pv")
        wait_for_pvc(api, "ollama-pvc", "default")
    except Exception as E:
        if E.status == 409:
            print("Storage already exists")
            return
        print(E)


# --------------------------------------------------------
# Pod creation
# --------------------------------------------------------
def launch_pod(api: CoreV1Api, name: str):
    print(f"Creating pod: {name}")
    manifest = pod_MANIFEST.copy()
    manifest["metadata"]["name"] = name

    api.create_namespaced_pod(namespace="default", body=manifest)
    wait_for_pod_ready(api, name, "default")


def launch_pod_if_not_exists(api: CoreV1Api, name: str):
    try:
        api.read_namespaced_pod(name, "default")
        print(f"Pod '{name}' already exists.")
    except ApiException as e:
        if e.status == 404:
            launch_pod(api, name)
        else:
            print(f"Unexpected error: {e}")
            raise


# --------------------------------------------------------
# Exec support (multiple output lines)
# --------------------------------------------------------
def exec_stream(api, pod, command):
    """
    Returns ALL output lines from stdout and stderr.
    """
    print(f"Executing on pod '{pod}': {command}")

    resp = stream(
        api.connect_get_namespaced_pod_exec,
        pod,
        "default",
        command=["/bin/sh", "-c", command],
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False,
        _preload_content=False,
    )

    output_lines = []

    while resp.is_open():
        resp.update(timeout=1)

        if resp.peek_stdout():
            out = resp.read_stdout()
            output_lines.append(out)

        if resp.peek_stderr():
            err = resp.read_stderr()
            output_lines.append(err)

    resp.close()
    return "".join(output_lines)


# --------------------------------------------------------
# Main
# --------------------------------------------------------
def setup():
    # Load kubeconfig
    config.load_kube_config()

    c = Configuration().get_default_copy()
    Configuration.set_default(c)

    api = CoreV1Api()

    # Launch PV + PVC
    launch_storage(api)

    # Launch multiple pods
    for i in range(NUM_PODS):
        name = POD_NAME_I(i)
        launch_pod_if_not_exists(api, name)
    return api

def integration_test(api):

    # Exec test
    print("\n=== Exec Test ===")
    command_test00 = "ollama ls"
    command_test01 = "ollama run embeddinggemma \"Hello world\""
    command_test02 = "ollama run gemma3 \"tell me a joke\""
    result0 = exec_stream(api, "llama-0", command_test00)
    result1 = exec_stream(api, "llama-1", command_test01)
    result2 = exec_stream(api, "llama-2", command_test02)

    print(result0)
    print(result1)
    print(result2)

    print("\n=== Done ===")



def send_payload_to_pod(api, pod_name, payload):
    output = exec_stream(api, pod_name, f"ollama run {payload["model"]} {payload["prompt"]}")
    return output



def kubes_parallel_analysis(id_prompts, filter_func = None, limit=-1):
    pods = [POD_NAME_I(i) for i in range(NUM_PODS)]
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

if __name__ == "__main__":
    api = setup()
    integration_test(api)
