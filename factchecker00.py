import yaml

import requests

def setup():
    """
    chmod +x kubes-setup.sh
    run kubes-setup


    might just have this as instructions
    currently just have
    :return:
    """


with open("ollama-deployment.yaml", "r") as deployment_file:
    deployment_data = yaml.safe_load(deployment_file)

with open("ollama-service.yaml", "r") as service_file:
    service_data = yaml.safe_load(service_file)

PORT = 11434
REPLICAS = deployment_data["spec"]["replicas"]


def query_ollama(prompt):
    payload = {"model": "llama3", "prompt": prompt}
    response = requests.post("http://localhost:11434/api/generate", json=payload, stream=True)
    output = ""
    for line in response.iter_lines():
        if line:
            data = line.decode("utf-8")
            resp = yaml.safe_load(data)["response"]
            output += resp
    return output

print(query_ollama("tell me a joke."))