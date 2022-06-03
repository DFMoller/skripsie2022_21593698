from time import strftime
import pandas as pd
import datetime

def prepare_usage_data(usage_entries, hours, bars):
    now = datetime.datetime.today()
    timediff = datetime.timedelta(minutes=30)
    last_interval = now.replace(minute=0, second=0)
    start = last_interval - datetime.timedelta(hours=hours)
    halfhours = hours*2
    usage_list = []
    print("Start: ",start.strftime("%Y-%m-%d %H:%M"))
    for x in usage_entries:
        dt = datetime.datetime.strptime(x.datetime, "%Y-%m-%d %H:%M")
        usage_list.append([dt, x.usage])
    usage_list = sorted(usage_list, key = lambda x: x[0])
    if usage_list[0][0] > start: usage_list.insert(0, [start, 0])
    if usage_list[-1][0] > last_interval: usage_list.pop()
    if usage_list[-1][0] < last_interval: usage_list.append([last_interval, 0])
    last_dt = start - timediff
    filled_usage_list = []
    for item in usage_list:
        if item[0] >= start:
            diff = item[0] - last_dt
            num_missing = int((diff - timediff)/timediff)
            if num_missing > 0:
                for i in range(num_missing):
                    filled_usage_list.append([last_dt + timediff*(i+1), 0])
            filled_usage_list.append(item)
            last_dt = item[0]
    accum = 0
    accum_counter = 0
    halfhours_per_bar = int(halfhours/bars)
    aggregated_list = []
    for x in filled_usage_list:
        accum += x[1]
        accum_counter += 1
        if accum_counter >= halfhours_per_bar:
            aggregated_list.append([x[0],accum])
            accum = 0
            accum_counter = 0
    usage_values = []
    xlabels = []
    for x in aggregated_list:
        usage_values.append(x[1])
        if hours == 24: xlabels.append(x[0].strftime("%H:%M"))
        elif hours == 72: xlabels.append(x[0].strftime("%a %H:%M"))
        elif hours == 168: xlabels.append(x[0].strftime("%Y/%m/%d"))

    return usage_values, xlabels

def prepare_peak_data(peak_entries, hours, bars):
    now = datetime.datetime.today()
    timediff = datetime.timedelta(minutes=30)
    last_interval = now.replace(minute=0, second=0)
    start = last_interval - datetime.timedelta(hours=hours)
    halfhours = hours*2
    peak_list = []
    print("Start: ",start.strftime("%Y-%m-%d %H:%M"))
    for x in peak_entries:
        dt = datetime.datetime.strptime(x.datetime, "%Y-%m-%d %H:%M")
        peak_list.append([dt, x.peak])
    peak_list = sorted(peak_list, key = lambda x: x[0])
    if peak_list[0][0] > start: peak_list.insert(0, [start, 0])
    if peak_list[-1][0] > last_interval: peak_list.pop()
    if peak_list[-1][0] < last_interval: peak_list.append([last_interval, 0])
    last_dt = start - timediff
    filled_peak_list = []
    for item in peak_list:
        if item[0] >= start:
            diff = item[0] - last_dt
            num_missing = int((diff - timediff)/timediff)
            if num_missing > 0:
                for i in range(num_missing):
                    filled_peak_list.append([last_dt + timediff*(i+1), 0])
            filled_peak_list.append(item)
            last_dt = item[0]
    max = 0
    accum_counter = 0
    halfhours_per_bar = int(halfhours/bars)
    aggregated_list = []
    for x in filled_peak_list:
        if x[1] > max: max = x[1]
        accum_counter += 1
        if accum_counter >= halfhours_per_bar:
            aggregated_list.append([x[0],max])
            max = 0
            accum_counter = 0
    peak_values = []
    for x in aggregated_list:
        peak_values.append(x[1])
    return peak_values