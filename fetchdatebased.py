from datetime import date
from datetime import timedelta
# from datetime import datetime
import requests

def divide_data_into_weeks(dict_with_date):
    week = 0
    today = date.today()
    total_week_data = {}
    for week in collect_week_in_list(dict_with_date):
        print("Week Number : "+str(week))
        weeks_data = {"totalconfirmed": [], "totaldeceased": [], "totalrecovered": []}
        total_daily_data = []
        for i in range(0, week):
            previous_day = (today - timedelta(days=i)).strftime("%d %B")
            if previous_day in dict_with_date.keys():
                weeks_data["totalconfirmed"].append(int(dict_with_date[previous_day]["dailyconfirmed"]))
                weeks_data["totaldeceased"].append(int(dict_with_date[previous_day]["dailydeceased"]))
                weeks_data["totalrecovered"].append(int(dict_with_date[previous_day]["dailyrecovered"]))
                total_daily_data.append(dict(date=previous_day,
                                             dailyconfirmed=dict_with_date[previous_day]["dailyconfirmed"],
                                             dailydeceased=dict_with_date[previous_day]["dailydeceased"],
                                             dailyrecovered=dict_with_date[previous_day]["dailyrecovered"]))



        total_week_data[str(week)] = dict(totalconfirmed=sum(weeks_data["totalconfirmed"]),totaldeceased=sum(weeks_data["totaldeceased"]),
                                          totalrecovered=sum(weeks_data["totalrecovered"]),dailydata=total_daily_data)


    return total_week_data



def collect_week_in_list(dict_with_date):
    date_list = []
    for i in range(1,len(dict_with_date)//7):
        date_list.append(i*7)
    date_list.append(len(dict_with_date))
    return date_list





tracker_data = requests.get('https://api.covid19india.org/data.json')
formatted_tracker_data = tracker_data.json()["cases_time_series"]
dict_with_date = {}
for data in formatted_tracker_data:
        current_date=str(data["date"]).strip()
        dict_with_date[current_date] = dict(dailyconfirmed=data["dailyconfirmed"],dailydeceased=data["dailydeceased"],dailyrecovered=data["dailyrecovered"])

print(dict_with_date)
divide_data_into_weeks(dict_with_date)




