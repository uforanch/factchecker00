from newsapi import NewsApiClient
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize

from collections import defaultdict
from dotenv import load_dotenv
import json
import datetime
import os
load_dotenv()
API_KEY = os.getenv("NEWS_API_KEY")

nltk.download("punkt")
nltk.download("punkt_tab")
newsapi = NewsApiClient(api_key=API_KEY)

def get_news(n, days):
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    ago_str = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    articles = newsapi.get_everything(q="Science",
                                      sources="abc-news,bbc-news,cnn,fox-news,google-news,nbc-news,msnbc,newsweek,new-york-magazine,the-huffington-post,the-washington-post,the-washington-times,usa-today,vice-news",
                                      from_param=ago_str,
                                      to=today_str,
                                      page_size=n,
                                      sort_by="popularity")["articles"]
    return articles


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')
        article_body = ""
        for paragraph in soup.find_all('p'):
            article_body += paragraph.get_text() + "\n"
        return article_body

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return  None

def get_citations(article):
    url = article["url"]
    article["text"] = get_text(url)
    if article["text"] is None:
        article["citations"] = None
        return article
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')
        article_body = ""
        for paragraph in soup.find_all('p'):
            article_body += paragraph.get_text() + "\n"

        sent_list = [sentence for sentence in sent_tokenize(article_body, "en")]
        sent_dict = defaultdict(list)

        sent_list.insert(0, article["title"])
        sent_dict[article["title"]].append(article["text"])

        for a_tag in soup.find_all('a', href=True):
            link_url = a_tag.get('href')
            link_text = a_tag.get_text(strip=True)
            if link_url:
                for sent in sent_list:
                    if link_text in sent:
                        sent_dict[sent].append(link_url)
        article["citations"] = dict(sent_dict)
        return article



    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")