"""
move get config functions here -

ask someone for the ettiquette of detecting if kuebs is setup or just doing it yourself
probably should just be done from readme really

from kubes-setup.sh:
get which line has "port-forward" - get word with ":", get first part of split,
parse to int
"""
import os.path

import yaml

PORT = 8080

if os.path.basename(os.path.normpath(os.getcwd())) == "utils":
    config_dir = os.path.dirname(os.getcwd()) + "//"
else:
    config_dir = os.getcwd() + "//"

with open(config_dir + "ollama-deployment.yaml", "r") as deployment_file:
    deployment_data = yaml.safe_load(deployment_file)

with open(config_dir + "ollama-service.yaml", "r") as service_file:
    service_data = yaml.safe_load(service_file)

with open(config_dir + "kubes-setup.sh", "r") as kubes_bash_file:
    for line in kubes_bash_file.readlines():
        if "port-forward" in line.lower():
            PORT=int(list(filter(lambda x: ":" in x, line.split(" ")))[0].split(":")[0])
    print(PORT)