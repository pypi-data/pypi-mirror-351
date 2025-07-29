import pandas as pd


def annual_hourly_average(data):

    date_time_index = pd.date_range(start="2025-01-01T00:00:00",end="2025-12-31T23:00:00", freq="1h")
    date_frame = pd.DataFrame(data,date_time_index)
    hourly_average = date_frame.groupby(date_frame.index.hour).mean()
    average_hourly = hourly_average.values.tolist()
    annual_hourly_average = []
    for i in average_hourly:
        annual_hourly_average.append(i[0]) 

    return annual_hourly_average
