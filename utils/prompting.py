import os.path
import json

if os.path.basename(os.path.normpath(os.getcwd())) == "utils":
    config_dir = os.path.dirname(os.getcwd()) + "//"
else:
    config_dir = os.getcwd() + "//"

with open(config_dir + "config.json") as f:
    CONFIG = json.load(f)
    MODEL = CONFIG["MODEL"]

def is_this_scientific(article_topic, article_desc):
    prompt = f"Please answer the following quesiton with \"Yes\" or \"No\" before supporting your conclusion:  Does \"{article_topic + ": "+article_desc}\" describe a science news article's headline and description?"
    return {"model": MODEL, "prompt": prompt}

def does_this_support_our_text(sentence, citation_text):
    prompt = f"Please answer the following quesiton with \"Yes\" or \"No\" before supporting your conclusion:  Does the following article support the conclusion that \"{sentence}\": {citation_text}"
    return {"model": MODEL, "prompt": prompt}