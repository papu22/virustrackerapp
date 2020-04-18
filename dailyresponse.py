from flask import Flask
from flask import jsonify
from flask import request
import requests
import json
from flask_cors import CORS, cross_origin
from map import map_data
from flask import Response
from fetchdatebased import divide_data_into_weeks
#from fetchdatebased import world_weekly_data
from getWorldData import collect_world_covid_19_data
from getWorldData import india_district_data
import logging
import requests_cache
import time
from operator import itemgetter



app = Flask(__name__)


#requests_cache.install_cache('covid_cache', backend='sqlite', expire_after=180)

covid_19_india_url = 'https://api.covid19india.org/data.json'
dist_data_url = "https://api.covid19india.org/state_district_wise.json"


@app.route('/')
@cross_origin()
def daily_data():
    try:
        tracker_data = requests.get(covid_19_india_url)
        formatted_tracker_data = tracker_data.json()
        dist_tracker_data = requests.get(dist_data_url)
        dist_total_data = dist_tracker_data.json()
        statewise_total_data = []
        total_world_data = []
        india_data = {}
        
        formatted_tracker_data = sorted(formatted_tracker_data["statewise"], key=itemgetter("state","confirmed"))

        now = time.ctime(int(time.time()))
        # print("Time: {0} / Used Cache For india dist json data : {1}".format(now, dist_tracker_data.from_cache))
        # print("Time: {0} / Used Cache For india json data : {1}".format(now, tracker_data.from_cache))


        for index, data in enumerate(formatted_tracker_data):
            if data["state"] != "Total":
                statewise_total_data.append(dict(id=index, name=data["state"], Confirmed=data["confirmed"], Active=data["active"],
                         Recovered=data["recovered"], Deaths=data["deaths"], todayconfirmed=data["deltaconfirmed"],
                         todaydeath=data["deltadeaths"], todayrecovered=data["deltarecovered"],statecode=data["statecode"]))
            else:
                india_data = data

        state_with_dist_data = india_district_data(statewise_total_data,dist_total_data)
        india_data = dict(id="1", name="India", Confirmed=india_data["confirmed"],
                                Recovered=india_data["recovered"],
                                Active=india_data["active"],
                                Deaths=india_data["deaths"],
                                todaytotalconfirmed=india_data["deltaconfirmed"],
                                todaytotaldeaths=india_data["deltadeaths"],
                                todaytotalrecovered=india_data["deltarecovered"],
                                lastupdatedtime=india_data["lastupdatedtime"],
                                states=state_with_dist_data)
        total_world_data.append(india_data)
        collect_world_covid_19_data(total_world_data)

        return json.dumps(total_world_data, indent=4), 200, {'ContentType': 'application/json'}


    except Exception as e:
        logging.error("Exception Occured inside daaily_data function",exc_info=True)
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
        #print("Time: {0} / Used Cache For previous json data : {1}".format(now, tracker_data.from_cache))

        for data in formatted_tracker_data:
            current_date = str(data["date"]).strip()
            dict_with_date[current_date] = dict(dailyconfirmed=data["dailyconfirmed"], dailydeceased=data["dailydeceased"],
                                                dailyrecovered=data["dailyrecovered"])
        weekly_ind_data = divide_data_into_weeks(dict_with_date,sortorder)
        
# =============================================================================
#         if sortorder == "desc":
#             world_weekly_data(weekly_ind_data)
# =============================================================================
            
        return json.dumps(weekly_ind_data), 200, {'ContentType': 'application/json'}
    except Exception:
        logging.error("Exception Occured inside get_previous_data function", exc_info=True)
        return json.dumps({"Error": "Can not able to process data at this moment", "Error Code": "500"}), 500, {
            'ContentType': 'application/json'}



if __name__ == '__main__':
    requests_cache.install_cache('covid_cache', backend='sqlite', expire_after=240)
    requests_cache.clear()
    #app.debug = True
    app.run()

