import numpy as np
import datetime

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
    def __init__(self, batV, powerHours, chargingHours, datapoints):
        self.battery_voltage = batV
        self.power_hours = powerHours
        self.charging_hours = chargingHours
        self.mode = {}
        self.aggregated_data = {}
        self.minimum_parameters = {}
        self.mode_set('maximum', 'maximum')
        self.aggregate_data(datapoints)
        self.generate_minimum_parameters()
        self.check_ready_state()
    def check_ready_state(self):
        for category in Quotation.mode_options.keys():
            if category not in self.mode:
                raise QuotationStateError('Quotation mode not set!')
        if len(self.aggregated_data) == 0:
            raise QuotationStateError('Data not Aggregated for Quotation!')
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
    def aggregate_data(self, datapoints):
        self.aggregated_data = {
            'usage': [],
            'peak': [],
            'xlabels': []
        }
        delta = datetime.timedelta(minutes=30)
        lookup = [datetime.datetime(year=2022, month=1, day=1, hour=0, minute=30) + x*delta for x in range(48)]
        for inc in lookup:
            usage = []
            peak = []
            for dp in datapoints:
                dt = datetime.datetime.strptime(dp.datetime, "%Y-%m-%d %H:%M")
                if dt.time() == inc.time():
                    usage.append(dp.usage)
                    peak.append(dp.peak)
            self.aggregated_data['usage'].append(np.max(usage))
            self.aggregated_data['peak'].append(np.max(peak))
            self.aggregated_data['xlabels'].append(inc.strftime('%H:%M'))
    def generate_minimum_parameters(self):
        # Define Data Structure
        self.minimum_parameters = {
            'Power': {
                'Usage': 0,
                'Peak': 0,
                'PwrHrs': self.power_hours,
                'ChargeHrs': self.charging_hours
            },
            'Battery': {
                'Wh': 0,
                'V': self.battery_voltage
            },
            'Inverter': {
                'W': 0,
                'VDC': self.battery_voltage,
                'VAC': 230
            },
            'PV': {
                'W': 0,
                'V': self.battery_voltage
            },
            'SC': {
                'V': self.battery_voltage,
                'I': 0
            }
        }
        # Power Requirements
        if self.mode['usage'] == 'median':
            self.minimum_parameters['Power']['Usage'] = np.median(self.aggregated_data['usage'])
        elif self.mode['usage'] == 'maximum':
            self.minimum_parameters['Power']['Usage'] = np.max(self.aggregated_data['usage'])
        if self.mode['peak'] == 'median':
            self.minimum_parameters['Power']['Peak'] = np.median(self.aggregated_data['peak'])
        elif self.mode['peak'] == 'maximum':
            self.minimum_parameters['Power']['Peak'] = np.max(self.aggregated_data['peak'])
        # Battery Parameters
        self.minimum_parameters['Battery']['Wh'] = self.power_hours * self.minimum_parameters['Power']['Usage'] * 2
        # Inverter Parameters
        self.minimum_parameters['Inverter']['W'] = self.minimum_parameters['Power']['Peak']
        self.minimum_parameters['Inverter']['VAC'] = 230
        # PV Panel Parameters
        self.minimum_parameters['PV']['W'] = self.minimum_parameters['Battery']['Wh'] / self.minimum_parameters['Power']['ChargeHrs']
        # Solar Charger Parameters
        self.minimum_parameters['SC']['I'] = self.minimum_parameters['PV']['W'] / self.battery_voltage

    def get_minimum_parameters(self):
        return self.minimum_parameters

    def calculate_cost(self):
        pass
    def display_results(self):
        pass

