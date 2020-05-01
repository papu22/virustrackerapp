from newsapi import NewsApiClient
import requests
import json
from datetime import datetime
from pytz import timezone
from datetime import datetime, timedelta
import pandas



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
            desc = str(article["description"]).replace("<ol><li>","").replace("</li><li>","")
            data_list.append(dict(title=article["title"],description=desc,
                                  urlToImage=article["urlToImage"],url=article["url"],id=article["source"]["id"],
                                  name=article["source"]["name"]))
    
    news_data["todaynews"] = data_list
    
    return json.dumps(news_data)




    

def get_zone_list():
    zone_data = pandas.read_csv("zone-list.csv")
    filtered_zip_list = zip(list(zone_data["DIST"]),list(zone_data["STATE"]),list(zone_data["ZONE"]))
    total_zone_data = {}
    for dist,state,zone in filtered_zip_list:
        if state not in total_zone_data.keys():
            total_zone_data[str(state)] = dict(dists=[dict(dist=str(dist),zone=str(zone))])
        else:
            total_zone_data[str(state)]["dists"].append(dict(dist=str(dist),zone=str(zone)))
    
    return json.dumps(total_zone_data)

    
#get_zone_list()   
# =============================================================================
# data = get_today_news()
# print(data)
# =============================================================================
