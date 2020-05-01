import csv

import requests
import json
import pandas
import csv
import requests
from datetime import datetime, timedelta
import pytz
from pytz import timezone
from operator import itemgetter




world_data_json_url = "https://pomber.github.io/covid19/timeseries.json"
world_updated_data_json_url = "https://corona.lmao.ninja/v2/countries"
world_state_data_confirmed = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
world_state_data_recovered = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
world_state_data_death = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
us_daily_data = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/"
us_state_data_url = "https://covidtracking.com/api/states.json"
us_state_daily_data_url = "https://covidtracking.com/api/v1/states/daily.json"
us_states = {'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas', 'AS': 'American Samoa', 'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District Of Columbia', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia', 'GU': 'Guam', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 'MN': 'Minnesota', 'MO': 'Missouri', 'MP': 'Northern Mariana Islands', 'MS': 'Mississippi', 'MT': 'Montana', 'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'PR': 'Puerto Rico', 'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VI': 'US Virgin Islands', 'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'}

def collect_world_covid_19_data(total_world_data):
    request_data = requests.get(world_data_json_url)
    world_countries_data = request_data.json()
    last_hour_date_time = (datetime.now() - timedelta(hours=1)).strftime('%d/%m/%Y %H:%M:%S')
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





def collect_world_updated_covid_19_data(total_world_data,ref,world_data_coverage):
    request_data = requests.get(world_updated_data_json_url)
    world_countries_data = request_data.json()
    last_hour_date_time = (datetime.now() - timedelta(hours=1)).strftime('%d/%m/%Y %H:%M:%S')
    world_state_data = segregate_world_state_data()
    world_recovered_data = json.loads(ref.get())

    now = datetime.now()


    for index,country in enumerate(world_countries_data):
        if country["country"] != "India":
            states = []
            todaytotalrecovered = 0
            if country["country"] in world_state_data.keys():
                states = world_state_data[country["country"]]["states"]
                todaytotalrecovered = int(country["recovered"]) - int(world_recovered_data[country["country"]])

            country_data = dict(id=index+3,name=country["country"],Confirmed=country["cases"],
                                   Recovered=(country["cases"] - country["active"] - country["deaths"]),Active=country["active"],
                                   Deaths=country["deaths"],todaytotalconfirmed=country["todayCases"],
                                   todaytotaldeaths=country["todayDeaths"],todaytotalrecovered=todaytotalrecovered,
                                   lastupdatedtime=last_hour_date_time,states=states,totaltest=country["tests"])
            total_world_data.append(country_data)
            world_recovered_data[country["country"]] = country["recovered"]

            #Adding up the world data while iterating
            world_data_coverage["Confirmed"].append(country["cases"])
            world_data_coverage["Recovered"].append((country["cases"] - country["active"] - country["deaths"]))
            world_data_coverage["Active"].append(country["active"])
            world_data_coverage["Deaths"].append(country["deaths"])
            world_data_coverage["todaytotalconfirmed"].append(country["todayCases"])
            world_data_coverage["todaytotaldeaths"].append(country["todayDeaths"])
            world_data_coverage["todaytotalrecovered"].append(country_data["todaytotalrecovered"])
            world_data_coverage["states"].append({key:val for key, val in country_data.items() if key != 'states'})
            world_data_coverage["states"][index]["dists"] = []



    total_world_data.append(find_the_total_count(world_data_coverage))
    if(now >= now.replace(hour=1,minute=15) and now <= now.replace(hour=9,minute=15)):
        print("Inside if condition")
        ref.delete()
        ref.set(json.dumps(world_recovered_data))
    return total_world_data

            

def find_the_total_count(world_data_coverage):
    world_data_coverage["Confirmed"] = sum(world_data_coverage["Confirmed"])
    world_data_coverage["Recovered"] = sum(world_data_coverage["Recovered"])
    world_data_coverage["Active"] = sum(world_data_coverage["Active"])
    world_data_coverage["Deaths"] = sum(world_data_coverage["Deaths"])
    world_data_coverage["todaytotalconfirmed"] = sum(world_data_coverage["todaytotalconfirmed"])
    world_data_coverage["todaytotaldeaths"] = sum(world_data_coverage["todaytotaldeaths"])
    world_data_coverage["todaytotalrecovered"] = sum(world_data_coverage["todaytotalrecovered"])
    world_data_coverage["states"] = sorted(world_data_coverage["states"], key=lambda i: int(i['Confirmed']),
                                        reverse=True)

    return world_data_coverage



def india_district_data(state_based_data,dist_total_data):

    for state in state_based_data:
        dist_list = []
        if state["name"] in dist_total_data.keys():
            for data in dist_total_data[state["name"]]["districtData"]:
                dist_list.append(dict(name=data,confirmed=dist_total_data[state["name"]]["districtData"][data]["confirmed"],
                                      todayconfirmed=dist_total_data[state["name"]]["districtData"][data]["delta"]["confirmed"]))


        sorted_dist_list = sorted(dist_list, key=itemgetter("confirmed"))
        state["dists"] = sorted_dist_list

    return state_based_data



def segregate_world_state_data():
    
    seggregate_data_dict = {}
    
    try:
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
                                   todaytotalconfirmed=dt_cnf - prev_conf,todaytotaldeaths=dt_dth - prev_dth,
                                   todaytotalrecovered = todayrecovered,dists=[]))
                seggregate_data_dict[cont_cnf] = dict(states=states)
            else:
                seggregate_data_dict[cont_cnf]["states"].append(dict(id=index,name=st_cnf,Confirmed=dt_cnf,Deaths=dt_dth,
                                   Active=dt_cnf - dt_dth - recovered,
                                   Recovered = recovered,
                                   todaytotalconfirmed=dt_cnf - prev_conf,todaytotaldeaths=dt_dth - prev_dth,
                                   todaytotalrecovered = todayrecovered,dists=[]))
                
    except Exception as e:
        print("Some error during process of world state data")
      
    seggregate_data_dict["USA"] = dict(states=[])
    seggregate_data_dict = get_all_us_state_data(seggregate_data_dict)
    return seggregate_data_dict
            

# =============================================================================
# def get_all_us_state_data(seggregate_data_dict):
#     us_time_zone = timezone('America/New_York')
#     today = datetime.now(us_time_zone)
#     today_data = []
#     last_day_data = []
#     total_state_data = {}
# 
#     try:
#         today_data = pandas.read_csv(us_daily_data+(today - timedelta(days=0)).strftime("%m-%d-%Y")+".csv").sort_values('Province_State')
#         last_day_data = pandas.read_csv(us_daily_data+(today - timedelta(days=1)).strftime("%m-%d-%Y")+".csv").sort_values('Province_State')
#         
#     except Exception as e:
#         print("Exception raised: ",e.__traceback__)
#         today_data = pandas.read_csv(us_daily_data+(today - timedelta(days=1)).strftime("%m-%d-%Y")+".csv").sort_values('Province_State')
#         last_day_data = pandas.read_csv(us_daily_data+(today - timedelta(days=2)).strftime("%m-%d-%Y")+".csv").sort_values('Province_State')
# 
#     
#     today_data = today_data.fillna(0)
#     last_day_data = last_day_data.fillna(0)
#     data = zip(list(today_data["Country_Region"]),list(today_data["Province_State"]),list(last_day_data["Province_State"]),list(today_data["Confirmed"]),
#                list(last_day_data["Confirmed"]),list(today_data["Recovered"]),list(last_day_data["Recovered"]),list(today_data["Deaths"]),
#                list(last_day_data["Deaths"]),list(today_data["Active"]),list(last_day_data["Active"]))
#     
#     index = 0
#     
#     for cnt,st,ls_st,tdy_cnf,last_cnf,tdy_rcv,last_rcv,tdy_dth,last_dth,tdy_act,last_act in data:
#         if cnt == "US":
#             if st not in total_state_data.keys():
#                 if st == ls_st:
#                     index += 1
#                     total_state_data[st] = dict(id=index,name=st,Confirmed=round(tdy_cnf),Active=round(tdy_act),
#                                                 Recovered=round(tdy_rcv),Deaths=round(tdy_dth),todaytotalconfirmed=round(tdy_cnf-last_cnf),
#                                                 todaytotaldeaths=round(tdy_dth-last_dth),todaytotalrecovered=round(tdy_rcv-last_rcv),dists=[])
#             else:
#                 if st == ls_st:
#                     total_state_data[st]["Confirmed"] = total_state_data[st]["Confirmed"] + tdy_cnf
#                     total_state_data[st]["Active"] = total_state_data[st]["Active"] + tdy_act
#                     total_state_data[st]["Recovered"] = total_state_data[st]["Recovered"] + tdy_rcv
#                     total_state_data[st]["Deaths"] = total_state_data[st]["Deaths"] + tdy_dth
#                     total_state_data[st]["todaytotalconfirmed"] = round(total_state_data[st]["todaytotalconfirmed"] + round(tdy_cnf-last_cnf))
#                     total_state_data[st]["todaytotaldeaths"] = round(total_state_data[st]["todaytotaldeaths"] + round(tdy_dth-last_dth))
#                     total_state_data[st]["todaytotalrecovered"] = round(total_state_data[st]["todaytotalrecovered"] + round(tdy_rcv-last_rcv))
# 
#     
#     #print(json.dumps(list(total_state_data.values())))
#     seggregate_data_dict["USA"]["states"] = list(total_state_data.values())
#     return seggregate_data_dict
# =============================================================================


def get_all_us_state_data(seggregate_data_dict):
    try:
        request_data = requests.get(us_state_data_url)
        request_state_data = request_data.json()
        prev_day_daily_data = get_prev_day_data()
        us_consolidated_data = {}
        index = 0
        
        for data in request_state_data:
            index += 1
            todayconfirmed = 0
            todaydeath = 0
            todayrecovered = 0
            if data["state"] in us_states.keys():
                if data["state"] in prev_day_daily_data.keys():
                    todayconfirmed = int(data["positive"] or 0) - int(prev_day_daily_data[data["state"]]["Confirmed"] or 0)
                    todayrecovered = int(data["recovered"] or 0) - int(prev_day_daily_data[data["state"]]["Recovered"] or 0)
                    todaydeath = int(data["death"] or 0) - int(prev_day_daily_data[data["state"]]["Deaths"] or 0)
                    
                us_consolidated_data[us_states[data["state"]]] = dict(id=index,name=us_states[data["state"]],Confirmed=int(data["positive"] or 0),
                                                              Active=int(data["positive"] or 0) - int(data["recovered"] or 0) - int(data["death"] or 0),
                                                              Recovered=int(data["recovered"] or 0),Deaths=int(data["death"] or 0),todaytotalconfirmed = todayconfirmed,
                                                              todaytotaldeaths=todaydeath,todaytotalrecovered=todayrecovered,dists=[])
        seggregate_data_dict["USA"]["states"] = list(us_consolidated_data.values())
        return seggregate_data_dict
    except Exception as e:
        return seggregate_data_dict




    
    
def isNan(data):
    return data != data



def get_prev_day_data():
    request_daily_data = requests.get(us_state_daily_data_url)
    request_state_daily_data = request_daily_data.json()
    cur_date = datetime.strptime(str(request_state_daily_data[0]["date"]),'%Y%m%d')
    prev_date = (cur_date - timedelta(days=1)).strftime("%Y%m%d")
    prev_day_daily_data = {}
    for data in request_state_daily_data:
        if data["date"] == int(prev_date):
            prev_day_daily_data[data["state"]] = dict(Confirmed=int(data["positive"] or 0),Recovered=int(data["recovered"] or 0),
                                                      Deaths=int(data["death"] or 0))
    return prev_day_daily_data



#test()        
#get_all_us_state_data()


