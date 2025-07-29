import math
from datetime import datetime, timezone


def solar_position(latitude, longitude, time_difference):
    
    base_date = datetime(2000, 1, 1, 12)
    current_time = datetime.now(timezone.utc)
    start_date = datetime(current_time.year, 1, 1, 0)
    difference = str(start_date - base_date)

    if len(difference) == 19:
        date_difference = float(difference[:4]) + 0.5
    elif len(difference) == 20:
        date_difference = float(difference[:5]) + 0.5

    # the number of days of Terrestrial Time (TT) from J2000.0 UT; 
    time_step_number = [] # [day]
    for i in range(0, 8760):
        date_difference += 1/24
        time_step_number.append(date_difference)

    # the mean longitude of the Sun corrected for aberration 
    mean_sun_longitude = [] # [°] or degree
    for i in time_step_number:
        mean_sun_longitude.append((280.466 + 0.9856474 * i) % 360.0)

    # the mean anomaly 
    mean_anomaly = [] # [°] or degree
    for i in time_step_number:
        mean_anomaly.append((357.528 + 0.9856003 * i) % 360.0)

    # the ecliptic longitude 
    ecliptic_longitude = [] # [°] or degree
    for i in range(0, len(mean_sun_longitude)):
        ecliptic_longitude.append((mean_sun_longitude[i] + 1.915 * math.sin(math.radians(mean_anomaly[i])) + 0.020 * math.sin(math.radians(2 * mean_anomaly[i]))) % 360.0)

    # the obliquity of ecliptic 
    obliquity_ecliptic = [] # [°] or degree
    for i in time_step_number:
        obliquity_ecliptic.append(23.440 - 0.0000004 * i)

    # the right ascension 
    right_ascension = [] # [°] or degree
    for i in range(0, len(obliquity_ecliptic)):
        right_ascension.append(math.degrees(math.atan2(math.cos(math.radians(obliquity_ecliptic[i])) * math.tan(math.radians(ecliptic_longitude[i])), math.cos(math.radians(ecliptic_longitude[i])))) % 360.0)

    # the declination of the Sun 
    sun_declination = [] # [°] or degree
    for i in range(0, len(obliquity_ecliptic)):
        sun_declination.append(math.degrees(math.asin(math.sin(math.radians(obliquity_ecliptic[i])) * math.sin(math.radians(ecliptic_longitude[i])))))

    # the equation of time 
    time_equation = [] # [min] or minute
    for i in range(0, len(mean_sun_longitude)):
        time_equation.append((((mean_sun_longitude[i] - right_ascension[i]) + 180.0) % 360.0) - 180.0)

    hour = list(range(0, 24)) # [h] 
    day = list(range(1, 366))
    hour_day = []
    for i in day:
        for j in hour:
            hour_day.append(j)

    # the subsolar point latitude
    subsolar_latitude = sun_declination

    # the subsolar point longitude
    subsolar_longitude = []
    for i in range(0, len(hour_day)):
        subsolar_longitude.append(-15.0 * (hour_day[i] - 12.0 + time_equation[i] * 4 / 60))

    # the observer latitude
    observer_latitude = []
    for i in range(0, 8760):
        observer_latitude.append(latitude)

    # the observer longitude
    observer_longitude = []
    for i in range(0, 8760):
        observer_longitude.append(longitude)

    # the x-, y- and z-components of S

    s_x = []
    for i in range(0, len(subsolar_latitude)):
        s_x.append(math.cos(math.radians(subsolar_latitude[i])) * math.sin(math.radians(subsolar_longitude[i] - observer_longitude[i])))

    s_y = []
    for i in range(0, len(subsolar_latitude)):
        s_y.append(math.cos(math.radians(observer_latitude[i])) * math.sin(math.radians(subsolar_latitude[i])) 
        - math.sin(math.radians(observer_latitude[i])) * math.cos(math.radians(subsolar_latitude[i])) * math.cos(math.radians(subsolar_longitude[i] - observer_longitude[i])))

    s_z = []
    for i in range(0, len(subsolar_latitude)):
        s_z.append(math.sin(math.radians(observer_latitude[i])) * math.sin(math.radians(subsolar_latitude[i])) 
        + math.cos(math.radians(observer_latitude[i])) * math.cos(math.radians(subsolar_latitude[i])) * math.cos(math.radians(subsolar_longitude[i] - observer_longitude[i])))


    # The solar zenith angle

    zenith_angle = [] # [°] or degree
    for i in s_z:
        zenith_angle.append(math.degrees(math.acos(i)))

    # The solar azimuth angle  ## the South-Clockwise convention  >>> The North-Clockwise convention > S_x[i],S_y[i]
    azimuth_angle = [] # [°] or degree
    for i in range(0, len(s_x)):
        azimuth_angle.append(math.degrees(math.atan2(-s_x[i],-s_y[i])))

    zenith_angle =  zenith_angle[time_difference:] + zenith_angle[:time_difference]
    azimuth_angle =  azimuth_angle[time_difference:] + azimuth_angle[:time_difference]

    if longitude > 0:
        final_zenith_angle = zenith_angle[:4105] + zenith_angle[4116:8509] + zenith_angle[8520:] + zenith_angle[8738:]
        final_azimuth_angle = azimuth_angle[:4105] + azimuth_angle[4116:8509] + azimuth_angle[8520:] + azimuth_angle[8738:]
    else:
        final_zenith_angle = zenith_angle[:4093] + zenith_angle[4104:8497] + zenith_angle[8508:] + zenith_angle[8738:]
        final_azimuth_angle = azimuth_angle[:4093] + azimuth_angle[4104:8497] + azimuth_angle[8508:] + azimuth_angle[8738:]

    return final_zenith_angle, final_azimuth_angle
