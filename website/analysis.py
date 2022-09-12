import datetime
import numpy as np

class AnalysisStateError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class Analysis:
    def __init__(self, datapoints):
        self.aggregated_data = {}
        self.aggregate_data(datapoints)
        self.check_ready_state()
    def check_ready_state(self):
        if len(self.aggregated_data) == 0:
            raise AnalysisStateError('Data not aggregated yet! Cannot be plotted.')
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
            self.aggregated_data['usage'].append(int(np.median(usage)))
            self.aggregated_data['peak'].append(int(np.median(peak)))
            self.aggregated_data['xlabels'].append(inc.strftime('%H:%M'))