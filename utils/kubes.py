from kubernetes import config
from kubernetes.client import CoreV1Api, Configuration
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
import yaml
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
    pod_manifest = yaml.safe_load(f)

with open(config_dir + "ollama-pv-pvc.yaml", "r") as f:
    storage_manifests = list(yaml.safe_load_all(f))


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
        for manifest in storage_manifests:
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
    manifest = pod_manifest.copy()
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
def integration_test():
    # Load kubeconfig
    config.load_kube_config()

    c = Configuration().get_default_copy()
    Configuration.set_default(c)

    api = CoreV1Api()

    # Launch PV + PVC
    launch_storage(api)

    # Launch multiple pods
    for i in range(3):
        name = f"llama-{i}"
        launch_pod_if_not_exists(api, name)

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


if __name__ == "__main__":
    integration_test()
