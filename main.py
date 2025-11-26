"""
so far don't have a way to get article and citations
will do it later


"""
import json
from utils.scraping import get_news, parallel_get_articles_details
from utils.kubes import kubes_parallel_analysis, setup
from utils.prompting import is_this_scientific, does_this_support_our_text


API = setup()


def test_send_payload_to_pod(api, pod_name, payload):
    output = (api, pod_name, f"ollama run {payload["model"]} {payload["prompt"]}")
    print(output)
    return str(output)

def get_top_articles(n=3, days=1, get_news=get_news):
    return get_news(n, days)

"""
Wish to go through, in a multiprocessed manner, the top articles and get the top X 
that are actually scientific

probably go in batches, add correct articles to the batch count, and when count>=X return
"""
def get_relevant_articles(articles, n, is_this_scientific=is_this_scientific, kubes_parallel_analysis = kubes_parallel_analysis, parallel_get_articles_details=parallel_get_articles_details):
    id_prompts = list(map(lambda x : {"article_id":x[0], "payload":is_this_scientific(x[1]["title"], x[1]["description"])}, enumerate(articles)))
    science_articles = []
    kubes_parallel_analysis(API, id_prompts, count_func=lambda r: r.startswith("Yes"), count_max = n, send_payload_to_pod=test_send_payload_to_pod)
    for d in id_prompts:
        if not d["result"].startswith("Yes"):
            continue
        science_articles.append(articles[d["article_id"]])

    science_articles =  parallel_get_articles_details(science_articles)
    return science_articles




def analyze_articles(articles, does_this_support_our_text = does_this_support_our_text, kubes_parallel_analysis=kubes_parallel_analysis):
    citation_chain = []
    for i, article in enumerate(articles):
        citation_chain.append((i, does_this_support_our_text(article["title"], article["text"])))
        for topic, text_list in article["citations"].items():
            for text in text_list:
                citation_chain.append({"article_id":i, "payload":does_this_support_our_text(topic, text)})

    kubes_parallel_analysis(citation_chain, send_payload_to_pod=test_send_payload_to_pod)
    for d in citation_chain:
        id_  = d["article_id"]
        out = d["result"]
        if "analysis" in articles[id_].keys():
            articles[id_]["analysis"].append(out)
        else:
            articles[id_]["analysis"] = [out]
    return articles




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
