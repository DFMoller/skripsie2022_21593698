import numpy as np
import math
import pandas as pd

class QuotationStateError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class Quotation:
    mode_options = {
        'usage': ['median', 'maximum'],
        'peak': ['median', 'maximum']
    }
    def __init__(self, batV, powerHours, chargingHours, usage_mode, peak_mode, aggregated_data):
        self.battery_voltage = batV
        self.power_hours = powerHours
        self.charging_hours = chargingHours
        self.mode = {}
        self.aggregated_data = aggregated_data
        self.quotation_results = {}
        self.mode_set(usage_mode=usage_mode, peak_mode=peak_mode)
        self.generate_equipment_results()
        self.generate_cost_estimation()
        self.check_ready_state()
    def check_ready_state(self):
        for category in Quotation.mode_options.keys():
            if category not in self.mode:
                raise QuotationStateError('Quotation mode not set!')
        # if len(self.aggregated_data) == 0:
        #     raise QuotationStateError('Data not Aggregated for Quotation!')
        if len(self.quotation_results) == 0:
            raise QuotationStateError('Minimum parameters required for Quotation not calculated!')
    def mode_set(self, usage_mode, peak_mode):
        if usage_mode in Quotation.mode_options['usage']:
            self.mode['usage'] = usage_mode
        else:
            raise KeyError('mode_set: usage mode "{}" does not exist'.format(usage_mode))
        if peak_mode in Quotation.mode_options['peak']:
            self.mode['peak'] = peak_mode
        else:
            raise KeyError('mode_set: peak mode "{}" does not exist'.format(peak_mode))
    def generate_equipment_results(self):
        # Define Data Structure
        self.quotation_results = {
            'description': 'Here is your generated quotation for the purchase of solar equipment to power your home during load shedding. The equipment specification shown below describes the recommended ratings for the different solar components your will need based on your load profile shown at the top of this page.',
            'power': {
                'description': 'This section displays the four parameters that are used to generate the quotation.',
                'disp_name': 'Input Parameters',
                'params': {
                    'usage': {
                        'val': 0,
                        'disp_name': 'Median usage per 30 min',
                        'unit': 'Wh',
                        'description': 'Used to size your battery system'
                    },
                    'peak': {
                        'val': 0,
                        'unit': 'W',
                        'disp_name': 'Peak Power Consumption',
                        'description': 'Used to size your inverter'
                    },
                    'pwrHours': {
                        'val': self.power_hours,
                        'unit': 'Hours',
                        'disp_name': 'Hours of Supplementary Power',
                        'description': 'Duration for which Supplementary Power is required per day'
                    },
                    'chargeHrs': {
                        'val': self.charging_hours,
                        'unit': 'Hours',
                        'disp_name': 'Hours of Direct Sunlight',
                        'description': 'Average duration of direct sunlight on your roof per day'
                    }
                }
            },
            'equipment': {
                'description': 'This section lists the important parameters that you need to consider for your solar panels, batteries and inverter(s). It only lists your personal demand from each component type and these numbers will not match the ratings of components on the market exactly. These numbers are minimum requirements.',
                'disp_name': 'Equipment Specification',
                'items': {
                    'battery': {
                        'description': 'Battery Description',
                        'disp_name': 'Battery Specification',
                        'specs': {
                            'Capacity': {
                                'val': 0,
                                'unit': 'Wh'
                            },
                            'Voltage': {
                                'val': self.battery_voltage,
                                'unit': 'V'
                            }
                        }
                    },
                    'inverter': {
                        'description': 'Inverter Description',
                        'disp_name': 'Inverter Specification',
                        'specs': {
                            'Power Rating': {
                                'val': 0,
                                'unit': 'W'
                            },
                            'DC Voltage': {
                                'val': self.battery_voltage,
                                'unit': 'V'
                            },
                            'AC Voltage': {
                                'val': 230,
                                'unit': 'V'
                            }
                        }
                    },
                    'PV': {
                        'description': 'PV Panel Description',
                        'disp_name': 'PV Panel Specification',
                        'specs': {
                            'Power Rating': {
                                'val': 0,
                                'unit': 'W'
                            },
                            'Voltage Rating': {
                                'val': self.battery_voltage,
                                'unit': 'V'
                            }
                        }
                    },
                    # 'SC': {
                    #     'description': 'Solar Charger Description',
                    #     'disp_name': 'Solar Charger Specification',
                    #     'specs': {
                    #         'Voltage Rating': {
                    #             'val': self.battery_voltage,
                    #             'unit': 'V'
                    #         },
                    #         'Current Rating': {
                    #             'val': 0,
                    #             'unit': 'A'
                    #         }
                    #     }
                    # }
                }
            }
        }
        # Power Requirements
        if self.mode['usage'] == 'median':
            self.quotation_results['power']['params']['usage']['val'] = np.median(self.aggregated_data['usage'])
        elif self.mode['usage'] == 'maximum':
            self.quotation_results['power']['params']['usage']['val'] = np.max(self.aggregated_data['usage'])
        if self.mode['peak'] == 'median':
            self.quotation_results['power']['params']['peak']['val'] = np.median(self.aggregated_data['peak'])
        elif self.mode['peak'] == 'maximum':
            self.quotation_results['power']['params']['peak']['val'] = np.max(self.aggregated_data['peak'])
        # Battery Parameters
        self.quotation_results['equipment']['items']['battery']['specs']['Capacity']['val'] = self.power_hours * self.quotation_results['power']['params']['usage']['val'] * 2
        # Inverter Parameters
        self.quotation_results['equipment']['items']['inverter']['specs']['Power Rating']['val'] = self.quotation_results['power']['params']['peak']['val']
        # PV Panel Parameters
        self.quotation_results['equipment']['items']['PV']['specs']['Power Rating']['val'] = round(self.quotation_results['equipment']['items']['battery']['specs']['Capacity']['val'] / self.quotation_results['power']['params']['chargeHrs']['val'], 0)
        # Solar Charger Parameters
        # self.quotation_results['equipment']['items']['SC']['specs']['Current Rating']['val'] = round(self.quotation_results['equipment']['items']['PV']['specs']['Power Rating']['val'] / self.battery_voltage, 0)

    def generate_cost_estimation(self):
        cost_estimation = {
            'disp_name': 'Cost Estimation',
            'description': 'This section displays your cost estimation for each of the components you will need in your solar system. The algorithm considers multiple cases for each type of component. For example, it determines if it will be cheaper for you to purchase one big battery or two smaller batteries to be used together to meet your demand.',
            'items': {
                'battery': {
                    'disp_name': 'Battery',
                    'description': 'Please find here your cost estimation for your solar battery pack. The parameters and cost shown are based on real market research done in 2022.',
                    'unit': 'Wh',
                    'options': []
                },
                'inverter': {
                    'disp_name': 'Hybrid Inverter',
                    'description': 'This is a description for the Hybrid Inverter\'s cost estimation',
                    'unit': 'W',
                    'options': []
                },
                'PV': {
                    'disp_name': 'PV Solar Panels',
                    'description': 'This is a description for the PV Solar Panels\' cost estimation',
                    'unit': 'W',
                    'options': []
                }
            },
            'totals': {
                'bat': 0,
                'inv': 0,
                'pv': 0
            }
        }
        # Read csv into DataFrame and convert stings to floats
        bat_df = pd.read_csv("/home/21593698/skripsie2022_21593698/solar_data/battery_export.csv", delimiter=';', encoding='cp1252')
        inv_df = pd.read_csv("/home/21593698/skripsie2022_21593698/solar_data/inverter_export.csv", delimiter=';', encoding='cp1252')
        pv_df = pd.read_csv("/home/21593698/skripsie2022_21593698/solar_data/panels_export.csv", delimiter=';', encoding='cp1252')
        # Convert strings to floats
        bat_df['Max Discharge'] = bat_df['Max Discharge'].str.replace(',', '.').astype(float)
        bat_df['Battery Capacity'] = bat_df['Battery Capacity'].str.replace(',', '.').astype(float)
        # Scale values to W and Wh
        bat_df['Battery Capacity'] = bat_df['Battery Capacity']*1000
        bat_df['Max Discharge'] = bat_df['Max Discharge']*1000
        inv_df['Hybrid Inverter Power'] = inv_df['Hybrid Inverter Power']*1000
        # Fetch minimum required parameters
        battery_capacity = self.quotation_results['equipment']['items']['battery']['specs']['Capacity']['val']
        inverter_rating = self.quotation_results['equipment']['items']['inverter']['specs']['Power Rating']['val']
        pv_rating = self.quotation_results['equipment']['items']['PV']['specs']['Power Rating']['val']
        # Calculate Cost Estimate
        cost_estimation['items']['battery']['options'] = self.calculate_battery_cost(bat_df, battery_capacity)
        cost_estimation['items']['inverter']['options'] = self.calculate_inverter_cost(inv_df, inverter_rating)
        cost_estimation['items']['PV']['options'] = self.calculate_panels_cost(pv_df, pv_rating)
        # Add totals
        cost_estimation['totals']['bat'] = cost_estimation['items']['battery']['options'][0]['details']['Total Cost'][1]
        cost_estimation['totals']['inv'] = cost_estimation['items']['inverter']['options'][0]['details']['Total Cost'][1]
        cost_estimation['totals']['pv'] = cost_estimation['items']['PV']['options'][0]['details']['Total Cost'][1]
        cost_estimation['totals']['total'] = cost_estimation['totals']['bat'] + cost_estimation['totals']['inv'] + cost_estimation['totals']['pv']
        # Add Cost Estimation to Quotation Results
        self.quotation_results['quotation'] = cost_estimation

    def calculate_battery_cost(self, bat_df, required_capacity):
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
        # print('Length of best_matches:', len(best_matches))
        results = []
        count = 0
        for key in best_matches:
            # print('Number of Units:', key)
            # print('Capacity per unit:', best_matches[key]['Max Discharge'])
            # print('Total Capacity:', best_matches[key]['Max Discharge']*int(key))
            # print('Cost per unit:', best_matches[key]['Cost'])
            # print('Total Cost:', best_matches[key]['Cost']*int(key))
            # print()
            results.append({
                'disp_name': 'Battery Parameters',
                'description': 'The least expensive combination of batteries for your needs consists of {} unit(s).'.format(count+1),
                'details': {
                    'Number of Battery Units': [key, ' Units'],
                    'Unit Capacity': [best_matches[key]['Max Discharge'], ' Wh'],
                    'Unit Cost': ['R', best_matches[key]['Cost']],
                    'Total Capacity': [best_matches[key]['Max Discharge']*int(key), ' Wh'],
                    'Total Cost': ['R', best_matches[key]['Cost']*int(key)]
                }
            })
            # Filter out two more expensive options

            count += 1
        results = [min(results, key=lambda x:x['details']['Total Cost'][1])]
        return results

    def calculate_inverter_cost(self, inv_df, inv_rating):
        one_unit_matches = []
        two_unit_matches = []
        three_unit_matches = []
        for index, row in inv_df.iterrows():
            if row['Hybrid Inverter Power'] > inv_rating:
                one_unit_matches.append(row)
            if row['Hybrid Inverter Power']*2 > inv_rating:
                two_unit_matches.append(row)
            if row['Hybrid Inverter Power']*3 > inv_rating:
                three_unit_matches.append(row)
        best_matches = {}
        if len(one_unit_matches) > 0:
            best_matches['1'] = min(one_unit_matches, key=lambda x:x['Hybrid Inverter Power'])
        if len(two_unit_matches) > 0:
            best_matches['2'] = min(two_unit_matches, key=lambda x:x['Hybrid Inverter Power'])
        if len(three_unit_matches) > 0:
            best_matches['3'] = min(three_unit_matches, key=lambda x:x['Hybrid Inverter Power'])
        results = []
        count = 0
        for key in best_matches:
            results.append({
                'disp_name': 'Inverter Parameters',
                'description': 'The least expensive combination of inverters for your needs consists of {} unit(s).'.format(count+1),
                'details': {
                    'Number of Hybrid Inverter Units': [key, ' Units'],
                    'Unit Capacity': [best_matches[key]['Hybrid Inverter Power'], ' W'],
                    'Unit Cost': ['R', best_matches[key]['Cost']],
                    'Total Capacity': [best_matches[key]['Hybrid Inverter Power']*int(key), ' W'],
                    'Total Cost': ['R', best_matches[key]['Cost']*int(key)]
                }
            })
            count += 1
        results = [min(results, key=lambda x:x['details']['Total Cost'][1])]
        return results

    def calculate_panels_cost(self, pv_df, power_rating):
        pv_df['PV Score'] = pv_df['Cost'] / pv_df['PV Power']
        # Select row with lowest cost per watt (PV Score)
        best_value_row = pv_df[pv_df['PV Score'] == pv_df['PV Score'].min()]
        # Select row with highest power per panel
        # max_power_row = pv_df[pv_df['PV Power'] == pv_df['PV Power'].max()]
        if len(best_value_row) > 1:
            best_value_row = best_value_row.iloc[[0]]
        # if len(max_power_row) > 1:
        #     # If there are more than one with equal power - Select row with lowest cost per watt (PV Score)
        #     max_power_row = max_power_row[max_power_row['PV Score'] == max_power_row['PV Score'].min()]
            # if len(max_power_row) > 1:
            #     max_power_row = max_power_row.iloc[[0]]
        num_panels_value = math.ceil(power_rating / best_value_row['PV Power'].item())
        # num_panels_power = math.ceil(power_rating / max_power_row['PV Power'].item())
        results = [{
            'disp_name': 'PV Panels\' Parameters',
            'description': 'You will need to install at least {} PV Panels to meet you demand.'.format(num_panels_value),
            'details': {
                'Number of PV Panels Required': [num_panels_value, ' Panels'],
                'Power per Panel': [best_value_row['PV Power'].item(), ' W'],
                'Cost Per Panel': ['R', best_value_row['Cost'].item()],
                'Total Power': [num_panels_value * best_value_row['PV Power'].item(), ' W'],
                'Total Cost': ['R', num_panels_value * best_value_row['Cost'].item()]
            }
        },
        # {
        #     'disp_name': 'PV Panels Option {}'.format(2),
        #     'description': 'This is a description for option 2',
        #     'details': {
        #         'Number of PV Panels Required': num_panels_power,
        #         'Power per Panel': max_power_row['PV Power'].item(),
        #         'Cost Per Panel': max_power_row['Cost'].item(),
        #         'Total Power': num_panels_power * max_power_row['PV Power'].item(),
        #         'Total Cost': num_panels_power * max_power_row['Cost'].item()
        #     }
        # }
        ]
        return results

