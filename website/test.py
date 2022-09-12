import pandas as pd
import math
# mylist = [{
#     'val': 5
# },
# {
#     'val': 6
# },
# {
#     'val': 5
# }]

# min_dict = min(mylist, key=lambda x:x['val'])
# print(min_dict)

# print("Battery DF:")
# bat_df = pd.read_csv("solar_data/battery_export.csv", delimiter=';', encoding='cp1252')
# bat_df['Max Discharge'] = bat_df['Max Discharge'].str.replace(',', '.').astype(float)*1000
# bat_df['Battery Capacity'] = bat_df['Battery Capacity'].str.replace(',', '.').astype(float)*1000
# for index, row in bat_df.iterrows():
#     print('Battery Capacity Column Type', type(row['Battery Capacity']))
#     print(row['Battery Capacity'])
#     print('Max Discharge Column Type', type(row['Max Discharge']))
#     print(row['Max Discharge'])
#     print('Cost Column Type', type(row['Cost']))
#     print(row['Cost'])
#     print()

# print()
# print("Inverter DF:")
# inv_df = pd.read_csv("solar_data/inverter_export.csv", delimiter=';', encoding='cp1252')
# # inv_df['Hybrid Inverter Power']
# for index, row in inv_df.iterrows():
#     print('Power Column Type', type(row['Hybrid Inverter Power']))
#     print(row['Hybrid Inverter Power'])
#     print('Cost Column Type', type(row['Cost']))
#     print(row['Cost'])
#     print()

# print()
# print("PV Panels DF:")
# pv_df = pd.read_csv("solar_data/panels_export.csv", delimiter=';', encoding='cp1252')
# # inv_df['Hybrid Inverter Power']
# for index, row in pv_df.iterrows():
#     print('Power Column Type:', type(row['PV Power']))
#     print(row['PV Power'])
#     print('Cost Column Type:', type(row['Cost']))
#     print(row['Cost'])
#     print()



def calculate_battery_cost(bat_df, required_capacity):
    one_unit_matches = []
    two_unit_matches = []
    three_unit_matches = []
    for index, row in bat_df.iterrows():
        if row['Max Discharge'] > required_capacity:
            one_unit_matches.append(row)
        if row['Max Discharge'] * 2 > required_capacity:
            two_unit_matches.append(row)
        if row['Max Discharge'] * 3 > required_capacity:
            three_unit_matches.append(row)
    best_matches = {}
    if len(one_unit_matches) > 0:
        best_matches['1'] = min(one_unit_matches, key=lambda x:x['Max Discharge'])
    if len(two_unit_matches) > 0:
        best_matches['2'] = min(two_unit_matches, key=lambda x:x['Max Discharge'])
    if len(three_unit_matches) > 0:
        best_matches['3'] = min(three_unit_matches, key=lambda x:x['Max Discharge'])
    print('Length of best_matches:', len(best_matches))
    for key in best_matches:
        print('Number of Units:', key)
        print('Capacity per unit:', best_matches[key]['Max Discharge'])
        print('Total Capacity:', best_matches[key]['Max Discharge']*int(key))
        print('Cost per unit:', best_matches[key]['Cost'])
        print('Total Cost:', best_matches[key]['Cost']*int(key))
        print()

def calculate_panels_cost(pv_df, power_rating):
        pv_df['PV Score'] = pv_df['Cost'] / pv_df['PV Power']
        # Select row with lowest cost per watt (PV Score)
        best_value_row = pv_df[pv_df['PV Score'] == pv_df['PV Score'].min()]
        # Select row with highest power per panel
        max_power_row = pv_df[pv_df['PV Power'] == pv_df['PV Power'].max()]
        # print(max_power_row.to_string())
        # print('Length of Max Power Row:', len(max_power_row))
        if len(best_value_row) > 1:
            best_value_row = best_value_row.iloc[[0]]
        if len(max_power_row) > 1:
            # If there are more than one with equal power - Select row with lowest cost per watt (PV Score)
            max_power_row = max_power_row[max_power_row['PV Score'] == max_power_row['PV Score'].min()]
            # print(max_power_row.to_string())
            # print('Length of Max Power Row:', len(max_power_row))
            if len(max_power_row) > 1:
                max_power_row = max_power_row.iloc[[0]]
        # print('Best Value Row:', best_value_row.to_string())
        # print('Max Power Row:', max_power_row.to_string())
        num_panels_value = math.ceil(power_rating / best_value_row['PV Power'])
        num_panels_power = math.ceil(power_rating / max_power_row['PV Power'])
        # print("num_panels_value type:", type(num_panels_value))
        # print("num_panels_power type:", type(num_panels_power))
        # print("best_value['PV Power'] Type:", type(best_value_row['PV Power'].item()))
        results = [{
            'Number of PV Panels Required': num_panels_value,
            'Power per Panel': best_value_row['PV Power'],
            'Cost Per Panel': best_value_row['Cost'],
            'Total Power': num_panels_value * best_value_row['PV Power'],
            'Total Cost': num_panels_value * best_value_row['Cost']
        },
        {
           'Number of PV Panels Required': num_panels_power,
            'Power per Panel': max_power_row['PV Power'],
            'Cost Per Panel': max_power_row['Cost'],
            'Total Power': num_panels_power * max_power_row['PV Power'],
            'Total Cost': num_panels_power * max_power_row['Cost'] 
        }]
        print("Results Type:", type(results))


bat_df = pd.read_csv("solar_data/battery_export.csv", delimiter=';', encoding='cp1252')
bat_df['Max Discharge'] = bat_df['Max Discharge'].str.replace(',', '.').astype(float)*1000
bat_df['Battery Capacity'] = bat_df['Battery Capacity'].str.replace(',', '.').astype(float)*1000
pv_df = pd.read_csv("solar_data/panels_export.csv", delimiter=';', encoding='cp1252')

# calculate_battery_cost(bat_df, 23000)
calculate_panels_cost(pv_df, 4331)