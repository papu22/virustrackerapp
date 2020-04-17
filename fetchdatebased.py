from datetime import date
from datetime import timedelta
# from datetime import datetime
import requests
from datetime import datetime
from pytz import timezone

world_data_json_url = "https://pomber.github.io/covid19/timeseries.json"

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
                                             dailyconfirmed=dict_with_date[previous_day]["dailyconfirmed"],
                                             dailydeceased=dict_with_date[previous_day]["dailydeceased"],
                                             dailyrecovered=dict_with_date[previous_day]["dailyrecovered"]))
        
        if sortorder == "desc":
         total_daily_data.reverse()


        total_week_data[str(week)] = dict(totalconfirmed=sum(weeks_data["totalconfirmed"]),totaldeceased=sum(weeks_data["totaldeceased"]),
                                          totalrecovered=sum(weeks_data["totalrecovered"]),dailydata=total_daily_data)


    return total_week_data


# =============================================================================
# def world_weekly_data(weekly_ind_data):
#     request_data = requests.get(world_data_json_url)
#     world_countries_data = request_data.json()
#     for index,country in enumerate(world_countries_data):
#         if country != "India":
#             recent_data_len = len(world_countries_data[country])-1
# =============================================================================


def collect_week_in_list(dict_with_date):
    date_list = []
    for i in range(1,(len(dict_with_date)//7)+1):
        date_list.append(i*7)
    date_list.append(len(dict_with_date))
    return date_list





# =============================================================================
# tracker_data = requests.get('https://api.covid19india.org/data.json')
# formatted_tracker_data = tracker_data.json()["cases_time_series"]
# dict_with_date = {}
# for data in formatted_tracker_data:
#          current_date=str(data["date"]).strip()
#          dict_with_date[current_date] = dict(dailyconfirmed=data["dailyconfirmed"],dailydeceased=data["dailydeceased"],dailyrecovered=data["dailyrecovered"])
# 
# #print(dict_with_date)
# val =[]
# data = divide_data_into_weeks(dict_with_date,val)
# #print(data)
# =============================================================================




