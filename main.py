"""
so far don't have a way to get article and citations
will do it later


"""
import json
from itertools import batched
#from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
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
    return get_citations(article)

"""
scrape articles in parallel
"""
def get_articles_details(articles):
    pool = ThreadPool(len(articles))
    articles_with_details = pool.map(lambda x: get_article_citations_and_summary(x), articles)

    pool.close()
    return articles_with_details

def is_article_scientific(pod, article):
    return True

def get_article_relevancy(pod, article):
    # get prompt
    # pass to pod
    # return true, false
    article_scientific = is_article_scientific(pod, article)
    if article_scientific:
        article["text"]=get_text(article["url"])
    return  article if article_scientific else None

"""
Wish to go through, in a multiprocessed manner, the top articles and get the top X 
that are actually scientific

probably go in batches, add correct articles to the batch count, and when count>=X return
"""
def get_relevant_articles(articles, n):
    pool = ThreadPool(len(PODS))
    science_articles = []
    for article_batch in batched(articles, len(PODS)):
        results = pool.map(lambda x: get_article_relevancy(x[1], x[0]), zip(article_batch, PODS))
        science_articles.extend([r for r in results if r is not None])
        if len(science_articles) >= n:
            break
    pool.close()
    return science_articles[:n]


def analyze_article_citations(pod, topic, text):
    print(pod, topic, text)
    return (topic, text)


def analyze_articles(articles):
    pool = ThreadPool(len(PODS))
    # think this is it
    citation_chain = []
    for i, article in enumerate(articles):
        citation_chain.append((i, article["title"], article["text"]))
        #citation_chain.extend([(i, c["topic"], c["text"]) for topic, text in article["citations"].items()])
        for topic, text_list in article["citations"].items():
            for text in text_list:
                citation_chain.append((i, topic, text))
    for citation_batch in batched(citation_chain, len(PODS)):
        results = list(map(lambda x: (x[1], analyze_article_citations(x[0][0],x[0][1],x[0][2])), zip(citation_batch, PODS)))
        for i, r in results:
            if "analysis" in articles[i].keys():
                articles[i]["analysis"].append(r)
            else:
                articles[i]["analysis"] = [r]
    return articles



#print(get_top_articles(1,3))
url = "https://www.cnn.com/2021/10/12/health/plastic-chemical-early-death-wellness/index.html"
def exec():
    articles = get_top_articles(10,1)
    articles = get_relevant_articles(articles, 3)
    articles = get_articles_details(articles)
    articles = analyze_articles(articles)
    #print(json.dumps(articles, indent=4))


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
exec()

#get_test_data(url)
#print(get_text(url))
