"""
so far don't have a way to get article and citations
will do it later


"""
import json
from itertools import batched
import multiprocessing

from utils.scraping import get_news, get_citations, get_text

from utils.get_config import config_dir

print(config_dir)

def get_top_articles(n=3, days=1):
    return get_news(n, days)

def get_citations_and_summary(article):
    """
    pass to somewhere else as above

    :param article:
    :return:
    """

def citation_point_response(data=None):
    """
    use util functions to
    :param data:
    :return:
    """

def get_article_relevancy(article):
    pass

def get_headline_source(article):
    return ""
"""
reading about workerpool... don't think below will work
iterate into new one
"""
def analyze_articles(articles):
    output_map = {}
    pods = 5 ## get from config
    pool = multiprocessing.Pool()# configure
    for article in articles:
        result_list = []
        #below blocks until ready
        citation_data_list = get_citations_and_summary(article)
        #create a pod assignment to a worker
        available_worker = 0
        for citation_data_batch in batched(citation_data_list, n=pods):
            result_batch = pool.apply(citation_point_response, citation_data_batch)
            result_list.extend(result_batch)
        #do something to assemble output into something reasonable for output

        output_map[get_headline_source(article)] = None


#print(get_top_articles(1,3))
url = "https://www.cnn.com/2021/10/12/health/plastic-chemical-early-death-wellness/index.html"
def exec():
    articles = get_top_articles(10,1)

def get_test_data(url):
    cit_dict = get_citations(url)
    cit_list = []
    for sent, url_list in cit_dict.items():
        for url in url_list:
            if "#" in url or "mailto:" in url:
                continue
            cit_list.append({"topic":sent, "text":get_text(url)})
    with open("cit_json_00.json", "w") as f:
        json.dump({"citations": cit_list},f)


