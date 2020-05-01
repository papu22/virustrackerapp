from flask import Flask
from flask import jsonify
from flask import request
import requests
import json
from flask_cors import CORS, cross_origin
from map import map_data
from flask import Response
from fetchdatebased import divide_data_into_weeks
from fetchdatebased import world_weekly_data
from getWorldData import collect_world_covid_19_data
from getWorldData import collect_world_updated_covid_19_data
from getWorldData import india_district_data
import logging
import requests_cache
import time
from operator import itemgetter
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import datetime, timedelta
from news_twitter import get_today_news
from news_twitter import get_zone_list
from datetime import datetime
from pytz import timezone
from datetime import datetime, timedelta

app = Flask(__name__)

# requests_cache.install_cache('covid_cache', backend='sqlite', expire_after=180)

covid_19_india_url = 'https://api.covid19india.org/data.json'
dist_data_url = "https://api.covid19india.org/state_district_wise.json"

cred = credentials.Certificate('covid-data-224-firebase-adminsdk-k9mfg-45460159ac.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://covid-data-224.firebaseio.com/'
})
ref = db.reference('/')


@app.route('/')
@cross_origin()
def daily_data():
    try:
        india_time_zone = timezone('Asia/Kolkata')
        tracker_data = requests.get(covid_19_india_url)
        formatted_tracker_data = tracker_data.json()
        tested_data = formatted_tracker_data["tested"]
        dist_tracker_data = requests.get(dist_data_url)
        dist_total_data = dist_tracker_data.json()
        statewise_total_data = []
        total_world_data = []
        india_data = {}
        india_in_world = {}

        last_hour_date_time = (datetime.now(india_time_zone)).strftime('%d/%m/%Y %H:%M:%S')

        # sorted_data = sorted(formatted_tracker_data["statewise"], key = lambda i: int(i['active']))
        formatted_tracker_data = sorted(formatted_tracker_data["statewise"], key=lambda i: int(i['confirmed']),
                                        reverse=True)

        now = time.ctime(int(time.time()))
        # print("Time: {0} / Used Cache For india dist json data : {1}".format(now, dist_tracker_data.from_cache))
        # print("Time: {0} / Used Cache For india json data : {1}".format(now, tracker_data.from_cache))

        for index, data in enumerate(formatted_tracker_data):
            if data["state"] != "Total":
                statewise_total_data.append(
                    dict(id=index, name=data["state"], Confirmed=data["confirmed"], Active=data["active"],
                         Recovered=data["recovered"], Deaths=data["deaths"], todaytotalconfirmed=data["deltaconfirmed"],
                         todaytotaldeaths=data["deltadeaths"], todaytotalrecovered=data["deltarecovered"],
                         statecode=data["statecode"]))
            else:
                india_data = data


        state_with_dist_data = india_district_data(statewise_total_data, dist_total_data)
        india_data = dict(id="1", name="India", Confirmed=int(india_data["confirmed"]),
                          Recovered=int(india_data["recovered"]),
                          Active=int(india_data["active"]),
                          Deaths=int(india_data["deaths"]),
                          todaytotalconfirmed=int(india_data["deltaconfirmed"]),
                          todaytotaldeaths=int(india_data["deltadeaths"]),
                          todaytotalrecovered=int(india_data["deltarecovered"]),
                          lastupdatedtime=india_data["lastupdatedtime"],
                          states=state_with_dist_data,totaltest=tested_data[len(tested_data) - 1]["totalsamplestested"])
        total_world_data.append(india_data)

        world_data_coverage = dict(id=2, name="World", Confirmed=[india_data["Confirmed"]],
                                   Recovered=[total_world_data[0]["Recovered"]],
                                   Active=[total_world_data[0]["Active"]], Deaths=[total_world_data[0]["Deaths"]],
                                   todaytotalconfirmed=[total_world_data[0]["todaytotalconfirmed"]],
                                   todaytotaldeaths=[total_world_data[0]["todaytotaldeaths"]],
                                   todaytotalrecovered=[total_world_data[0]["todaytotalrecovered"]],
                                   lastupdatedtime=last_hour_date_time, states=[{key:val for key, val in india_data.items() if key != 'states'}])

        # collect_world_covid_19_data(total_world_data)
        collect_world_updated_covid_19_data(total_world_data, ref,world_data_coverage)

        return json.dumps(total_world_data, indent=4), 200, {'ContentType': 'application/json'}


    except Exception as e:
        logging.error("Exception Occured inside daaily_data function", exc_info=True)
        return json.dumps({"Error": "Can not able to process data at this moment", "Error Code": "500"}), 500, {
            'ContentType': 'application/json'}


@app.route('/previousdata', methods=['GET'])
@cross_origin()
def get_previous_data():
    try:
        tracker_data = requests.get(covid_19_india_url)
        sortorder = request.args.get('sortOrder')
        formatted_tracker_data = tracker_data.json()["cases_time_series"]
        dict_with_date = {}

        now = time.ctime(int(time.time()))
        # print("Time: {0} / Used Cache For previous json data : {1}".format(now, tracker_data.from_cache))

        for data in formatted_tracker_data:
            current_date = str(data["date"]).strip()
            dict_with_date[current_date] = dict(dailyconfirmed=data["dailyconfirmed"],
                                                dailydeceased=data["dailydeceased"],
                                                dailyrecovered=data["dailyrecovered"])
        weekly_ind_data = divide_data_into_weeks(dict_with_date, sortorder)


        if sortorder == "desc":
            
            india_time_zone = timezone('Asia/Kolkata')
            time_now = datetime.now(india_time_zone)
            future_date_to_set = (datetime.now(india_time_zone) + timedelta(hours=4,minutes=5)).strftime("%Y-%m-%d %H:%M:%S")

            with open('timeTracker.json','r+') as a,open('time-series.json','r+') as b:
                    future_date = json.loads(a.read())
                    if time_now < india_time_zone.localize(datetime.strptime(future_date["currenttrackingdate"],'%Y-%m-%d %H:%M:%S')):
                        print("Inside if , for timeseries")  
                        weekly_ind_data = json.loads(b.read())
                          
                    else:
                        print("Inside Else future date to set :"+future_date_to_set)
                        b.truncate()
                        weekly_ind_data = world_weekly_data(weekly_ind_data)
                        b.write(json.dumps(weekly_ind_data))
                        a.close()
                        if a.closed:
                          with open('timeTracker.json','r+') as track:
                             track.truncate()
                             #track.write(json.dumps({"currenttrackingdate":future_date_to_set}))
                             future_date["currenttrackingdate"] = future_date_to_set
                             track.write(json.dumps(future_date))


        return json.dumps(weekly_ind_data), 200, {'ContentType': 'application/json'}
    except Exception:
        logging.error("Exception Occured inside get_previous_data function", exc_info=True)
        return json.dumps({"Error": "Can not able to process data at this moment", "Error Code": "500"}), 500, {
            'ContentType': 'application/json'}
    
    
    
    
@app.route('/news', methods=['GET'])
@cross_origin()
def get_news_details():
    news_data = {}
    try:
        india_time_zone = timezone('Asia/Kolkata')
        time_now = datetime.now(india_time_zone)
        future_date_to_set = (datetime.now(india_time_zone) + timedelta(hours=0,minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
        with open('timeTracker.json','r+') as a,open('news.json','r+') as b:
                    future_date = json.loads(a.read())
                    if time_now < india_time_zone.localize(datetime.strptime(future_date["currenttrackingnewsdate"],'%Y-%m-%d %H:%M:%S')):
                        print("Inside news if , for news")  
                        news_data = json.loads(b.read())
                    else:
                        print("Inside news Else future date to set :"+future_date_to_set)
                        b.truncate()
                        news_data = get_today_news()
                        b.write(json.dumps(news_data))
                        a.close()
                        if a.closed:
                          with open('timeTracker.json','r+') as track:
                             track.truncate()
                             #track.write(json.dumps({"currenttrackingdate":future_date_to_set}))
                             future_date["currenttrackingnewsdate"] = future_date_to_set
                             track.write(json.dumps(future_date))
        
        return news_data, 200, {'ContentType': 'application/json'}
    except Exception as e:
        return json.dumps({"Error": "Can not able to stream news at this moment", "Error Code": "500"}), 500, {
            'ContentType': 'application/json'}




@app.route('/zones', methods=['GET'])
@cross_origin()
def get_zone_details():
    zone_list = {}
    try:
        zone_list = get_zone_list()
        return zone_list, 200, {'ContentType': 'application/json'}
    except Exception:
        return json.dumps({"Error": "Can not able to get the zone data", "Error Code": "500"}), 500, {
            'ContentType': 'application/json'}



if __name__ == '__main__':
    requests_cache.install_cache('covid_cache', backend='sqlite', expire_after=240)
    requests_cache.clear()
    # app.debug = True
    app.run()

