from datetime import date
from datetime import timedelta
# from datetime import datetime
import requests
from datetime import datetime
from pytz import timezone
import json

world_data_json_url = "https://pomber.github.io/covid19/timeseries.json"
country_list = {"US":"USA","Angola":"Anguilla","Congo (Kinshasa)":"Congo","Cote d'Ivoire":"Côte d'Ivoire","Holy See":"Holy See (Vatican City State)",
                "United Kingdom":"UK","United Arab Emirates":"UAE","Syria":"Syrian Arab Republic","Taiwan*":"Taiwan","Korea, South":"S. Korea"}

def divide_data_into_weeks(dict_with_date,sortorder):
    week = 0
    india_time_zone = timezone('Asia/Kolkata')
    today = datetime.now(india_time_zone)
    total_week_data = {}
    for week in collect_week_in_list(dict_with_date):
        weeks_data = {"totalconfirmed": [], "totaldeceased": [], "totalrecovered": []}
        total_daily_data = []
        for i in range(1, week+1):
            previous_day = (today - timedelta(days=i)).strftime("%d %B")
            if previous_day in dict_with_date.keys():
                weeks_data["totalconfirmed"].append(int(dict_with_date[previous_day]["dailyconfirmed"]))
                weeks_data["totaldeceased"].append(int(dict_with_date[previous_day]["dailydeceased"]))
                weeks_data["totalrecovered"].append(int(dict_with_date[previous_day]["dailyrecovered"]))
                total_daily_data.append(dict(date=previous_day,
                                             dailyconfirmed=int(dict_with_date[previous_day]["dailyconfirmed"]),
                                             dailydeceased=int(dict_with_date[previous_day]["dailydeceased"]),
                                             dailyrecovered=int(dict_with_date[previous_day]["dailyrecovered"])))
        
        if sortorder == "desc":
         total_daily_data.reverse()


        total_week_data[week] = dict(totalconfirmed=sum(weeks_data["totalconfirmed"]),totaldeceased=sum(weeks_data["totaldeceased"]),
                                          totalrecovered=sum(weeks_data["totalrecovered"]),dailydata=total_daily_data)


    return total_week_data


def world_weekly_data(weekly_ind_data):
    request_data = requests.get(world_data_json_url)
    world_countries_data = request_data.json()
    world_weekly_data = {}
    world_collab_data = get_week_data()
    country_name = None
    world_weekly_data["India"] = weekly_ind_data
    for index,country in enumerate(world_countries_data):
        if country in country_list.keys():
            country_name = country_list[country]
        else:
            country_name = country
        if country == "Afghanistan":
            weekly_dict_data = {}
            index = 0
            for week in collect_week_in_list(world_countries_data[country]):
                index += 1
                week_data = []
                if index > 5:
                     break
                for i in range(0,week):
                    reversed_list = world_countries_data[country][::-1]
                    cur_date = datetime.strptime(reversed_list[i]["date"],'%Y-%m-%d')
                    cur_date = cur_date.strftime("%d %B")
                    if i != len(world_countries_data[country]) - 1:
                        week_data.append(dict(dailyconfirmed=reversed_list[i]["confirmed"] - reversed_list[i+1]["confirmed"],
                                              dailydeceased=reversed_list[i]["deaths"] - reversed_list[i+1]["deaths"],
                                              dailyrecovered=reversed_list[i]["recovered"] - reversed_list[i+1]["recovered"],
                                              date=cur_date))
                        if week in world_collab_data.keys() and len(world_collab_data[week]["dailydata"]) == 0:
                             world_collab_data[week]["dailydata"].append(week_data[0])
                             #world_collab_data[week]["dailydata"][i]["dailyconfirmed"] = world_collab_data[week]["dailydata"][i]["dailyconfirmed"] + week_data[i]["dailyconfirmed"]
                        else:
                            pass


                    else:
                        week_data.append(dict(dailyconfirmed=reversed_list[i]["confirmed"],
                                              dailydeceased=reversed_list[i]["deaths"],
                                              dailyrecovered=reversed_list[i]["recovered"],
                                              date=cur_date))

                week_data.reverse()
                weekly_dict_data[week] = {"dailydata":week_data}
            world_weekly_data[country_name] = weekly_dict_data
            print(world_collab_data)

    return  world_weekly_data
                



def collect_world_graph_data(world_weekly_data):
    world_data_graph = {}
    for country in world_weekly_data.keys():
        for week in world_weekly_data[country].keys():
            if week not in world_data_graph.keys():
                world_data_graph[week] = world_weekly_data[country][week]
            else:
                pass



def collect_week_in_list(dict_with_date):
    date_list = []
    for i in range(1,(len(dict_with_date)//7)+1):
        date_list.append(i*7)
    date_list.append(len(dict_with_date))
    return date_list



def get_week_data():
    week_list = [7,14,21,35,42]
    week_dict = {}
    for i in week_list:
        week_dict[i] = dict(dailydata=[])
    return week_dict




#world_weekly_data()

# tracker_data = requests.get('https://api.covid19india.org/data.json')
# formatted_tracker_data = tracker_data.json()
# tested_data = formatted_tracker_data["tested"]
# dict_with_date = {}
# # for data in formatted_tracker_data:
# #          current_date=str(data["date"]).strip()
# #          dict_with_date[current_date] = dict(dailyconfirmed=data["dailyconfirmed"],dailydeceased=data["dailydeceased"],dailyrecovered=data["dailyrecovered"])
#
# #print(dict_with_date)
# print(tested_data[len(tested_data) - 1]["totalsamplestested"])
# #print(data)





