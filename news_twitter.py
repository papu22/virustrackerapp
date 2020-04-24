from newsapi import NewsApiClient
import requests
import json
from datetime import datetime
from pytz import timezone
from datetime import datetime, timedelta


newsapi = NewsApiClient(api_key='5f7c3d5bb96845fc9e4a16eed0d89aa4')
news_sources = 'the-times-of-india,google-news-in,the-hindu,usa-today,the-washington-times,reuters,reddit-r-all,news24,nbc-news,mtv-news-uk,mtv-news,medical-news-today,google-news-uk,google-news,fox-news,cnn,cnbc,bbc-news,al-jazeera-english,abc-news'

def get_today_news():
    news_data = {}
    india_time_zone = timezone('Asia/Kolkata')
    today = datetime.now(india_time_zone)
    cur_date = (today - timedelta(days=0)).strftime("%Y-%m-%d")
    prev_date = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    data_list = []
    
    
    top_headlines = newsapi.get_top_headlines(q='corona',
                                              sources=news_sources,
                                              language='en',page_size=90)
    
    for article in top_headlines["articles"]:
        if cur_date in article["publishedAt"] or prev_date in article["publishedAt"]:
            data_list.append(dict(title=article["title"],description=article["description"],
                                  urlToImage=article["urlToImage"],url=article["url"]))
    
    news_data["todaynews"] = data_list
    
    return json.dumps(news_data)



    
    
# =============================================================================
# data = get_today_news()
# print(data)
# =============================================================================
