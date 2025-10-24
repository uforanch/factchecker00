"""
so far don't have a way to get article and citations
will do it later


"""
import json
from itertools import batched
from multiprocessing import Pool
from utils.scraping import get_news, get_citations, get_text
#from utils.kubes import get_pods
from utils.get_config import config_dir

print(config_dir)



PODS =  ["A", "B", "C", "D"]

def get_top_articles(n=3, days=1):
    return get_news(n, days)


"""
s
"""
def get_article_citations_and_summary(article):
    # scrape for text and citatations
    # return as dictionary
    pass

"""
scrape articles in parallel
"""
def get_articles_details(articles):
    pool = Pool(len(articles))
    details = pool.map(lambda x: get_article_citations_and_summary(x), articles)
    for i, article in enumerate(articles):
        article["details"] = details[i]
    pool.close()
    return articles



def get_article_relevancy(pod, article):
    # get prompt
    # pass to pod
    # return true, false
    pass

"""
Wish to go through, in a multiprocessed manner, the top articles and get the top X 
that are actually scientific

probably go in batches, add correct articles to the batch count, and when count>=X return
"""
def get_relevant_articles(articles, n):
    pool = Pool(len(PODS))
    science_articles = []
    for article_batch in batched(articles, len(PODS)):
        results = pool.map(lambda x: get_article_relevancy(x[1], x[0]), article_batch)
        for i, r in enumerate(results):
            if r:
                science_articles.append(article_batch[i])
        if len(science_articles) >= n:
            break
    pool.close()
    return science_articles[:n]


def analyze_article_citations(pod, topic, text):
    #
    pass

def analyze_articles(articles):
    pool = Pool(len(PODS))
    # think this is it
    citation_chain = []
    for i, article in enumerate(articles):
        citation_chain.extend([(i, c["topic"], c["text"]) for c in article["details"]["citations"]])
    for citation_batch in batched(citation_chain, len(PODS)):
        results = pool.map(lambda x: (x[1][0], analyze_article_citations(x[0],x[1][1],x[1][2]), citation_batch))
        for i, r in results:
            # add these details back to article i
            pass
    return



#print(get_top_articles(1,3))
url = "https://www.cnn.com/2021/10/12/health/plastic-chemical-early-death-wellness/index.html"
def exec():
    articles = get_top_articles(10,1)
    articles = get_relevant_articles(articles, 3)
    articles = get_articles_details(articles)


def get_test_data(url):
    cit_dict = get_citations(url)
    cit_list = []
    for sent, url_list in cit_dict.items():
        for url in url_list:
            if "#" in url or "mailto:" in url:
                continue
            t = get_text(url)
            if t is not None:
                print("*")
                cit_list.append({"topic":sent, "text":get_text(url)})
    with open("cit_json_00.json", "w") as f:
        json.dump({"citations": cit_list},f)


get_test_data(url)
#print(get_text(url))
