"""
so far don't have a way to get article and citations
will do it later


"""
import json
from utils.scraping import get_news, parallel_get_articles_details
from utils.kubes import kubes_parallel_analysis
from utils.prompting import is_this_scientific, does_this_support_our_text



def get_top_articles(n=3, days=1):
    return get_news(n, days)



"""
Wish to go through, in a multiprocessed manner, the top articles and get the top X 
that are actually scientific

probably go in batches, add correct articles to the batch count, and when count>=X return
"""
def get_relevant_articles(articles, n):
    id_prompts = list(map(lambda x : (x[0], is_this_scientific(x[1]["title"], x[1]["description"])), enumerate(articles)))
    science_articles = []
    results = kubes_parallel_analysis(id_prompts, n, lambda x : x.startswith("Yes"))
    for i, r in results:
        if not r.startswith("Yes"):
            continue
        science_articles.append(articles[i])

    science_articles =  parallel_get_articles_details(science_articles)
    return science_articles




def analyze_articles(articles):
    citation_chain = []
    for i, article in enumerate(articles):
        citation_chain.append((i, article["title"], article["text"]))
        for topic, text_list in article["citations"].items():
            for text in text_list:
                citation_chain.append((i, does_this_support_our_text(topic, text)))

    results = kubes_parallel_analysis(citation_chain)
    for r in results:
        id_, out = r
        if "analysis" in articles[id_].keys():
            articles[id_]["analysis"].append(out)
        else:
            articles[id_]["analysis"] = [out]




#print(get_top_articles(1,3))
url = "https://www.cnn.com/2021/10/12/health/plastic-chemical-early-death-wellness/index.html"
def exec():
    articles = get_top_articles(10,1)
    articles = get_relevant_articles(articles, 3)
    articles = analyze_articles(articles)
    print(json.dumps(articles, indent=4))

exec()

#get_test_data(url)
#print(get_text(url))
