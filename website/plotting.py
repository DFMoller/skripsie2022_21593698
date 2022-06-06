from time import strftime
import pandas as pd
import datetime

def prepare_chart_data(data_entries, key):
    if key == "24h":
        hours = 24
        bars = 48
        return get_hours(data_entries, hours, bars)
    elif key == "72h":
        hours = 72
        bars = 24
        return get_hours(data_entries, hours, bars)
    elif key == "week":
        return get_week(data_entries)

def get_hours(data_entries, hours, bars):
    now = datetime.datetime.today()
    timediff = datetime.timedelta(minutes=30)
    if now.minute > 30: last_interval = now.replace(minute=30, second=0)
    else: last_interval = now.replace(minute=0, second=0)
    start = last_interval - datetime.timedelta(hours=hours)
    halfhours = hours*2
    data_list = []
    for x in data_entries:
        dt = datetime.datetime.strptime(x.datetime, "%Y-%m-%d %H:%M")
        data_list.append([dt, x.usage, x.peak])
    data_list = sorted(data_list, key = lambda x: x[0])
    if len(data_list) > 0:
        if data_list[0][0] > start: data_list.insert(0, [start, 0, 0])
        if data_list[-1][0] > last_interval: data_list.pop()
        if data_list[-1][0] < last_interval: data_list.append([last_interval, 0, 0])
    filled_list = []
    last_dt = start - timediff
    for item in data_list:
        if item[0] >= start:
            diff = item[0] - last_dt
            num_missing = int((diff - timediff)/timediff)
            if num_missing > 0:
                for i in range(num_missing):
                    filled_list.append([last_dt + timediff*(i+1), 0, 0])
            filled_list.append(item)
            last_dt = item[0]
    accum = 0
    max_peak = 0
    accum_counter = 0
    halfhours_per_bar = int(halfhours/bars)
    aggregated_list = []
    for x in filled_list:
        accum += x[1]
        if x[2] > max_peak: max_peak = x[2]
        accum_counter += 1
        if accum_counter >= halfhours_per_bar:
            aggregated_list.append([x[0],accum, max_peak])
            accum = 0
            accum_counter = 0
            max_peak = 0
    usage_values = []
    peak_values = []
    xlabels = []
    for x in aggregated_list:
        usage_values.append(x[1])
        peak_values.append(x[2])
        if hours == 24: xlabels.append(x[0].strftime("%H:%M"))
        elif hours == 72: xlabels.append(x[0].strftime("%a %H:%M"))
    return usage_values, peak_values, xlabels

def get_week(data_entries):
    data_list = []
    today = datetime.datetime.today().date()
    days = []
    for day in range(7):
        days.append([today - datetime.timedelta(days=(6 - day)), 0, 0])
    accum = 0
    max_peak = 0
    for day in days:
        for x in data_entries:
            dt = datetime.datetime.strptime(x.datetime, "%Y-%m-%d %H:%M")
            if dt.date() == day:
                day[1] += x.usage
                if x.peak > day[2]: day[2] = x.peak
    usage_values = []
    peak_values = []
    xlabels = []
    for day in days:
        usage_values.append(day[1])
        peak_values.append(day[2])
        xlabels.append(day[0].strftime("%a, %d %b"))
    return usage_values, peak_values, xlabels

