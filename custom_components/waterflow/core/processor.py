from datetime import datetime
from typing import Any, Dict, List

class SMHIProcessor:
    def __init__(self):
        pass

    @staticmethod
    def merge_series(hindcast: dict, forecast: dict) -> Dict[str, Any]:
        import pandas as pd
        hindcast_data = hindcast.get("data", [])
        forecast_data = forecast.get("data", [])

        combined = hindcast_data + forecast_data

        if not combined:
            return {
                "startindex": None,
                "firstdate": None,
                "lastdate": None,
                "data": []
            }

        timestamps = [entry[0] for entry in combined]
        min_timestamp = min(timestamps)
        max_timestamp = max(timestamps)
        startindex = SMHIProcessor.calculate_start_index(min_timestamp)
        
        # Convert timestamps to datetime objects
        from datetime import datetime
        firstdate = datetime.fromtimestamp(min_timestamp / 1000)
        lastdate = datetime.fromtimestamp(max_timestamp / 1000)

        return {
            "startindex": startindex,
            "firstdate": firstdate,
            "lastdate": lastdate,
            "data": [entry[1] for entry in combined]
        }

    @staticmethod
    def process_background(background: List) -> Dict[str, Any]:
        import pandas as pd
        years = list(range(2022, 1990, -1))
        daily_data = {year: [-1] * 365 for year in years}

        for day_entry in background:
            timestamp, values = day_entry
            date = pd.to_datetime(timestamp, unit="ms")
            day_of_year = date.timetuple().tm_yday

            if date.month == 2 and date.day == 29:
                continue

            if SMHIProcessor.is_leap_year(date.year) and (date.month > 2 or (date.month == 2 and date.day > 28)):
                adjusted_day = day_of_year - 2
            else:
                adjusted_day = day_of_year - 1

            if 0 <= adjusted_day < 365:
                for idx, year in enumerate(years):
                    value = values[idx] if idx < len(values) else -1
                    daily_data[year][adjusted_day] = value

        averages, mins, maxs = [], [], []
        for i in range(365):
            vals = [daily_data[year][i] for year in years if daily_data[year][i] != -1]
            if vals:
                averages.append(sum(vals) / len(vals))
                mins.append(min(vals))
                maxs.append(max(vals))
            else:
                averages.append(-1)
                mins.append(-1)
                maxs.append(-1)

        return {
            "history": daily_data,
            "average": averages,
            "min": mins,
            "max": maxs
        }

    @staticmethod
    def is_leap_year(year: int) -> bool:
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    @staticmethod
    def calculate_start_index(timestamp: int) -> int:
        import pandas as pd
        date = pd.to_datetime(timestamp, unit="ms")
        day_of_year = date.timetuple().tm_yday - 1
        if day_of_year >= 365:
            day_of_year = 364
        return day_of_year

    def process_data(self, chart_data: dict) -> Dict[str, Any]:
        return {
            "waterflow": self.merge_series(
                chart_data.get("coutHindcast", {}),
                chart_data.get("coutForecast", {})
            ),
            "precipitation": self.merge_series(
                chart_data.get("psimHindcast", {}),
                chart_data.get("psimForecast", {})
            ),
            "waterflow_history": self.process_background(chart_data.get("background", [])),
            "mq": chart_data.get("mq", -1),
            "mlq": chart_data.get("mlq", -1),
            "mhq": chart_data.get("mhq", -1)
        }
