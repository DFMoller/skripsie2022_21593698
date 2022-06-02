import pandas as pd
import datetime

def prepare_usage_data(usage_entries):
    usage_listOfLists = []
    for x in usage_entries:
        usage_listOfLists.append([x.datetime, x.usage])
    usage_df = pd.DataFrame(usage_listOfLists, columns=["datetime", "usage"])
    usage_df["datetime"] = pd.to_datetime(usage_df["datetime"])
    usage_df = usage_df.sort_values(by="datetime", ascending=True)
    xlabels = []
    usage_values = []
    today = datetime.datetime.today().date()
    for index, row in usage_df.iterrows():
        if row["datetime"].date() == today:
            xlabels.append(datetime.datetime.strftime(row["datetime"], "%H:%S"))
            usage_values.append(row["usage"])
            print("Usage Row")
    return usage_values, xlabels

def prepare_peak_data(peak_entries):
    peak_listOfLists = []
    for x in peak_entries:
        peak_listOfLists.append([x.datetime, x.peak])
    peak_df = pd.DataFrame(peak_listOfLists, columns=["datetime", "peak"])
    peak_df["datetime"] = pd.to_datetime(peak_df["datetime"])
    peak_df = peak_df.sort_values(by="datetime", ascending=True)
    peak_values = []
    today = datetime.datetime.today().date()
    for index, row in peak_df.iterrows():
        if row["datetime"].date() == today:
            peak_values.append(row["peak"])
            print("Peak Row")
    return peak_values