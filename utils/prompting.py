from utils.get_config import MODEL# get this from config later

def is_this_scientific(article_topic, article_desc):
    prompt = f"Does \"{article_topic + ": "+article_desc}\" describe a science news article's headline and description?"
    return {"model": MODEL, "prompt": prompt}

def does_this_support_our_text(sentence, citation_text):
    prompt = f"Does the following article support the conclusion that \"{sentence}\": {citation_text}"
    return {"model": MODEL, "prompt": prompt}