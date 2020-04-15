import csv

import requests
import json
import pandas
import csv
import requests
from datetime import datetime, timedelta



world_data_json_url = "https://pomber.github.io/covid19/timeseries.json"
world_state_data_confirmed = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
world_state_data_recovered = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
world_state_data_death = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"

def collect_world_covid_19_data(total_world_data):
    request_data = requests.get(world_data_json_url)
    world_countries_data = request_data.json()
    last_hour_date_time = (datetime.now() - timedelta(hours=6)).strftime('%d/%m/%Y %H:%M:%S')
    world_state_data = segregate_world_state_data()


    for index,country in enumerate(world_countries_data):
        if country != "India":
            recent_data = len(world_countries_data[country])-1
            previous_day_data = len(world_countries_data[country])-2
            today_confirmed_cases = world_countries_data[country][recent_data]["confirmed"] - world_countries_data[country][previous_day_data]["confirmed"]
            today_recovered = world_countries_data[country][recent_data]["recovered"] - world_countries_data[country][previous_day_data]["recovered"]
            today_deaths = world_countries_data[country][recent_data]["deaths"] - world_countries_data[country][previous_day_data]["deaths"]
            states = []
            
            if country in world_state_data.keys():
                states = world_state_data[country]["states"]
            
            active_cases = world_countries_data[country][recent_data]["confirmed"] - world_countries_data[country][recent_data]["deaths"] - world_countries_data[country][recent_data]["recovered"]
            total_world_data.append(dict(id=index+2,name=country,Confirmed=world_countries_data[country][recent_data]["confirmed"],
                                   Recovered=world_countries_data[country][recent_data]["recovered"],Active=active_cases,
                                   Deaths=world_countries_data[country][recent_data]["deaths"],todaytotalconfirmed=today_confirmed_cases,
                                   todaytotaldeaths=today_deaths,todaytotalrecovered=today_recovered,
                                   lastupdatedtime=last_hour_date_time,states=states))



    return total_world_data



def india_district_data(state_based_data,dist_total_data):

    for state in state_based_data:
        dist_list = []
        if state["name"] in dist_total_data.keys():
            for data in dist_total_data[state["name"]]["districtData"]:
                dist_list.append(dict(name=data,confirmed=dist_total_data[state["name"]]["districtData"][data]["confirmed"],
                                      todayconfirmed=dist_total_data[state["name"]]["districtData"][data]["delta"]["confirmed"]))


        state["dists"] = dist_list

    return state_based_data



def segregate_world_state_data():
    csv_data_confirmed = pandas.read_csv(world_state_data_confirmed).sort_values('Country/Region')
    csv_data_recovered = pandas.read_csv(world_state_data_recovered).sort_values('Country/Region')
    csv_data_death = pandas.read_csv(world_state_data_death).sort_values('Country/Region')
    
    data_confirmed = csv_data_confirmed[pandas.notnull(csv_data_confirmed["Province/State"])]
    data_recover = csv_data_recovered[pandas.notnull(csv_data_recovered["Province/State"])]
    data_death = csv_data_death[pandas.notnull(csv_data_death["Province/State"])]
    
    headers = list(data_confirmed.keys())
    cur_date = headers[len(headers) - 1]
    prev_date = headers[len(headers) - 2]
    
    formatted_recovery_data_total= dict(zip(list(data_recover["Province/State"]),list(data_recover[cur_date])))
    formatted_recovery_data_daily = dict(zip(list(data_recover["Province/State"]),list(data_recover[prev_date])))
    
    total_data = zip(list(data_confirmed["Country/Region"]),list(data_confirmed["Province/State"]),list(data_confirmed[cur_date]),
                     list(data_confirmed[prev_date]),list(data_death["Country/Region"]),list(data_death["Province/State"]),
                     list(data_death[cur_date]),list(data_death[prev_date]))
    
    seggregate_data_dict = {}
    index = 0
    
    for cont_cnf,st_cnf,dt_cnf,prev_conf,cont_dth,st_dth,dt_dth,prev_dth in total_data:
        index += 1
        states = []
        recovered = 0
        todayrecovered = 0
        if st_cnf in formatted_recovery_data_total.keys():
                recovered = formatted_recovery_data_total[st_cnf]
                todayrecovered = formatted_recovery_data_total[st_cnf] - formatted_recovery_data_daily[st_cnf]
        if cont_cnf not in seggregate_data_dict.keys():
            
            states.append(dict(id=index,name=st_cnf,Confirmed=dt_cnf,Deaths=dt_dth,
                               Active=dt_cnf - dt_dth - recovered,
                               Recovered = recovered,
                               todayconfirmed=dt_cnf - prev_conf,todaydeath=dt_dth - prev_dth,
                               todayrecovered = todayrecovered,dists=[]))
            seggregate_data_dict[cont_cnf] = dict(states=states)
        else:
            seggregate_data_dict[cont_cnf]["states"].append(dict(id=index,name=st_cnf,Confirmed=dt_cnf,Deaths=dt_dth,
                               Active=dt_cnf - dt_dth - recovered,
                               Recovered = recovered,
                               todayconfirmed=dt_cnf - prev_conf,todaydeath=dt_dth - prev_dth,
                               todayrecovered = todayrecovered,dists=[]))
        
    return seggregate_data_dict
            




def isNan(data):
    return data != data

#segregate_world_state_data()


# tracker_data = requests.get('https://api.covid19india.org/data.json')
# dist_total_data = requests.get("https://api.covid19india.org/state_district_wise.json").json()
# formatted_tracker_data = tracker_data.json()
# dict_with_date = {}
# statewise_total_data = []
# for index, data in enumerate(formatted_tracker_data["statewise"]):
#     if index != 0:
#         statewise_total_data.append(dict(name=data["state"], Confirmed=data["confirmed"], Active=data["active"],
#                  Recovered=data["recovered"], Deaths=data["deaths"], todayconfirmed=data["deltaconfirmed"],
#                  todaydeath=data["deltadeaths"], todayrecovered=data["deltarecovered"], statecode=data["statecode"]))
#
# india_district_data(statewise_total_data, dist_total_data)
#
# print(dict_with_date)

# collect_world_covid_19_data()