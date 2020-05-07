from tweepy import API 
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import requests

def get_twitter_timeline_data(twitter_client):
    total_tweet_data = {}
    with open('twitter_channel.json','r+') as a:
        channel_list_with_country = json.loads(a.read())
        for country in channel_list_with_country.keys():
            tweets = []
            if len(channel_list_with_country[country]) > 0:
                for tweet in Cursor(twitter_client.user_timeline, id=channel_list_with_country[country],tweet_mode="extended").items(50):
                    if "RT" not in str(tweet.full_text):
                        tweets.append(dict(data=str(tweet.full_text).replace("\n","").replace("&amp;","&"),
                                      name=tweet.user.name,screen_name=tweet.user.screen_name,
                                      profile_background_image_url=tweet.user.profile_background_image_url,
                                      profile_image_url=tweet.user.profile_image_url))
                total_tweet_data[country] = tweets
            
        
    return json.dumps(total_tweet_data,ensure_ascii=False)

