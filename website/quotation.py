import numpy as np
import datetime, csv
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
        self.minimum_parameters = {}
        self.mode_set(usage_mode=usage_mode, peak_mode=peak_mode)
        # self.aggregate_data(datapoints)
        self.generate_minimum_parameters()
        self.check_ready_state()
    def check_ready_state(self):
        for category in Quotation.mode_options.keys():
            if category not in self.mode:
                raise QuotationStateError('Quotation mode not set!')
        # if len(self.aggregated_data) == 0:
        #     raise QuotationStateError('Data not Aggregated for Quotation!')
        if len(self.minimum_parameters) == 0:
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
    def generate_minimum_parameters(self):
        # Define Data Structure
        self.minimum_parameters = {
            'description': 'This is a description for the quotation results',
            'power': {
                'description': 'Input Parameter Description',
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
                'description': 'Equipment Specification Description',
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
                    'SC': {
                        'description': 'Solar Charger Description',
                        'disp_name': 'Solar Charger Specification',
                        'specs': {
                            'Voltage Rating': {
                                'val': self.battery_voltage,
                                'unit': 'V'
                            },
                            'Current Rating': {
                                'val': 0,
                                'unit': 'A'
                            }
                        }
                    }
                }
            }
        }
        # Power Requirements
        if self.mode['usage'] == 'median':
            self.minimum_parameters['power']['params']['usage']['val'] = np.median(self.aggregated_data['usage'])
        elif self.mode['usage'] == 'maximum':
            self.minimum_parameters['power']['params']['usage']['val'] = np.max(self.aggregated_data['usage'])
        if self.mode['peak'] == 'median':
            self.minimum_parameters['power']['params']['peak']['val'] = np.median(self.aggregated_data['peak'])
        elif self.mode['peak'] == 'maximum':
            self.minimum_parameters['power']['params']['peak']['val'] = np.max(self.aggregated_data['peak'])
        # Battery Parameters
        self.minimum_parameters['equipment']['items']['battery']['specs']['Capacity']['val'] = self.power_hours * self.minimum_parameters['power']['params']['usage']['val'] * 2
        # Inverter Parameters
        self.minimum_parameters['equipment']['items']['inverter']['specs']['Power Rating']['val'] = self.minimum_parameters['power']['params']['peak']['val']
        # PV Panel Parameters
        self.minimum_parameters['equipment']['items']['PV']['specs']['Power Rating']['val'] = round(self.minimum_parameters['equipment']['items']['battery']['specs']['Capacity']['val'] / self.minimum_parameters['power']['params']['chargeHrs']['val'], 0)
        # Solar Charger Parameters
        self.minimum_parameters['equipment']['items']['SC']['specs']['Current Rating']['val'] = round(self.minimum_parameters['equipment']['items']['PV']['specs']['Power Rating']['val'] / self.battery_voltage, 0)

    def generate_cost_estimation(self):
        self.cost_estimation = {
            'description': 'This is a description for the cost estimation section',
            'items': {
                'battery': {
                'disp_name': 'Battery',
                'description': 'This is a description for the Battery\'s cost estimation',
                'cost': 0
            },
            'inverter': {
                'disp_name': 'Hybrid Inverter',
                'description': 'This is a description for the Hybrid Inverter\'s cost estimation',
                'cost': 0
            },
            'PV': {
                'disp_name': 'PV Solar Panels',
                'description': 'This is a description for the PV Solar Panels\' cost estimation',
                'cost': 0
            }}
        }
        bat_df = pd.read_csv("solar_data/battery_export.csv", delimiter=';', encoding='cp1252')
        inv_df = pd.read_csv("solar_data/inverter_export.csv", delimiter=';', encoding='cp1252')
        pv_df = pd.read_csv("solar_data/panels_export.csv", delimiter=';', encoding='cp1252')
        battery_capacity = self.minimum_parameters['equipment']['items']['battery']['specs']['Capacity']['val']
        inverter_rating = self.minimum_parameters['equipment']['items']['inverter']['specs']['Power Rating']['val']
        pv_rating = self.minimum_parameters['equipment']['items']['PV']['specs']['Power Rating']['val']
        self.cost_estimation['items']['battery']['cost'] = self.calculate_cost_single_battery(bat_df, battery_capacity)
        self.cost_estimation['items']['inverter']['cost'] = self.calculate_cost_single_inverter(inv_df, inverter_rating)

    def calculate_cost_single_battery(bat_df, required_capacity):
        potential_matches = []
        for index, row in bat_df.iterrows():
            if row['Max Discharge'] > required_capacity:
                potential_matches.append(row)
        match = min(potential_matches, key=lambda x:x['Max Discharge'])
        cost = match['Cost']
        return cost

    def calculate_cost_single_inverter(inv_df, inv_rating):
        potential_matches = []
        for index, row in inv_df.iterrows():
            if row['Hybrid Inverter Power'] > inv_rating:
                potential_matches.append(row)
        match = min(potential_matches, key=lambda x:x['Max Discharge'])
        cost = match['Cost']
        return cost

    def get_minimum_parameters(self):
        return self.minimum_parameters

    def calculate_cost(self):
        pass
    def display_results(self):
        pass

