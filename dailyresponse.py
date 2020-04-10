from flask import Flask
from flask import jsonify
import requests
import json
from flask_cors import CORS, cross_origin
from map import map_data
from flask import Response
from fetchdatebased import divide_data_into_weeks

app = Flask(__name__)


@app.route('/')
@cross_origin()
def daily_data():
    try:
        tracker_data = requests.get('https://api.covid19india.org/data.json')
        formatted_tracker_data = tracker_data.json()
        statewise_total_data = []

        for index, data in enumerate(formatted_tracker_data["statewise"]):
            if index != 0:
                statewise_total_data.append(
                    dict(id=index, name=data["state"], Confirmed=data["confirmed"], Active=data["active"],
                         Recovered=data["recovered"], Deaths=data["deaths"], todayconfirmed=data["deltaconfirmed"],
                         todaydeath=data["deltadeaths"], todayrecovered=data["deltarecovered"]))

        return json.dumps(
            dict(countries=dict(id="1", name="India", Confirmed=formatted_tracker_data["statewise"][0]["confirmed"],
                                Recovered=formatted_tracker_data["statewise"][0]["recovered"],
                                Active=formatted_tracker_data["statewise"][0]["active"],
                                Deaths=formatted_tracker_data["statewise"][0]["deaths"],
                                todaytotalconfirmed=formatted_tracker_data["statewise"][0]["deltaconfirmed"],
                                todaytotaldeaths=formatted_tracker_data["statewise"][0]["deltadeaths"],
                                todaytotalrecovered=formatted_tracker_data["statewise"][0]["deltarecovered"],
                                states=statewise_total_data)), indent=4), 200, {'ContentType': 'application/json'}


    except Exception:
        return json.dumps({"Error": "Can not able to process data at this moment", "Error Code": "500"}), 500, {
            'ContentType': 'application/json'}


@app.route('/htmldata', methods=['GET'])
@cross_origin()
def get_response_html():
    data_map = map_data()
    return Response(data_map, mimetype="text/html")

@app.route('/previousdata', methods=['GET'])
@cross_origin()
def get_previous_data():
    tracker_data = requests.get('https://api.covid19india.org/data.json')
    formatted_tracker_data = tracker_data.json()["cases_time_series"]
    dict_with_date = {}
    for data in formatted_tracker_data:
        current_date = str(data["date"]).strip()
        dict_with_date[current_date] = dict(dailyconfirmed=data["dailyconfirmed"], dailydeceased=data["dailydeceased"],
                                            dailyrecovered=data["dailyrecovered"])
    return json.dumps(divide_data_into_weeks(dict_with_date)), 200, {'ContentType': 'application/json'}



if __name__ == '__main__':
    app.run()
