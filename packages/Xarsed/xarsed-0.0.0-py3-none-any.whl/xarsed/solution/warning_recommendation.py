
def solar_energy_pv_electricity_battery_warning(item, scenario, module):

    h1 = '<p>Hot Warning</p>'
    h2 = '<ul><li>According to the data and conditions of the '+scenario+' scenario and '+module+'-path , the panel temperature exceeds the operating temperature of 85°C. '
    h3 = 'As a result, you need to find a way to control its temperature within this time range.</li></ul>'
    Hot = h1 + h2 + h3 
    
    c1 = '<p>Cold Warning</p>'
    c2 = '<ul><li>According to the data and conditions of the '+scenario+' scenario and '+module+'-path, the panel temperature will drop below the operating temperature of -40°C. '
    c3 = 'As a result, you need to find a way to control its temperature during this time range.</li></ul>'
    Cold = c1 + c2 + c3
    
    b1 = '<p>Hot and Cold Warnings</p>'
    b2 = '<ul><li>According to the data and conditions of the '+scenario+' scenario and '+module+'-path, the panel temperature has exceeded the temperature range of -40°C to 85°C. ' 
    b3 = 'As a result, you need to find a way to control its temperature during this time range.</li></ul>'
    Both = b1 + b2 + b3 
    
    o1 = '<p>Out Warning</p>'
    o2 = '<ul><li>According to the data and conditions of the '+scenario+' scenario and '+module+'-path, the number of days without sunlight in your location is more than the energy manitainance ' 
    o3 = 'time of the battery, which is usually 6 months. It is recommended to use batteries with a longer manitainance time.</li></ul>'
    Out = o1 + o2 + o3 

    z1 = '<p>Zero Warning</p>'
    z2 = '<ul><li>According to the data and conditions of the '+scenario+' scenario and '+module+'-path, at least one of the calculated parameters in this scenario is equal to zero. ' 
    z3 = 'This usually happens when the day selected for power generation coincides with a day when there is no consumption, or the amount of solar radiation during this period is continuous, so there is no need for storage.'
    z4 = 'You can easily check this from the production-consumption plots of this scenario.</li></ul>'
    Zero = z1 + z2 + z3 + z4

    if item == "Hot":
        alarm = Hot
    elif item == "Cold":
        alarm = Cold
    elif item == "Both":
        alarm = Both
    elif item == "Out":
        alarm = Out
    elif item == "Zero":
        alarm = Zero
    else:
        alarm = ""
    
    return alarm


def solar_energy_pv_electricity_battery_recommendation(electricity, global_horizontal_irradiance, photovoltaics_power, battery_capacity, hot_list, out_list):

    daily_consumption = sum(electricity) / 365000.0 #[kW.h/day]

    if daily_consumption > 50.0:
        consumption = "High"
    else:
        consumption = "OK"

    photovoltaics_power_average = (photovoltaics_power[0] + photovoltaics_power[1]) / 2000.0

    if photovoltaics_power_average > 10.0: #[kW]
        production = "High"
    else:
        production = "OK"

    battery_capacity_average = (battery_capacity[0] + battery_capacity[1]) / 2000.0

    if battery_capacity_average > 100.0: #[kW.h]
        storage = "High"
    else:
        storage = "OK"

    global_horizontal_irradiance_average = sum(global_horizontal_irradiance) / len(global_horizontal_irradiance)

    if global_horizontal_irradiance_average < 140.0:
        radiation = "Low"
    else:
        radiation = "OK"

    global_horizontal_irradiance_daily = []
    for i in range(1,366): 
        start_index = 24 * i - 24  
        end_index = 24 * i 
        sum_cut_list = sum(global_horizontal_irradiance[start_index:end_index])
        global_horizontal_irradiance_daily.append(sum_cut_list)

    zero_day_count = global_horizontal_irradiance_daily.count(0.0)

    if zero_day_count > 30.0:
        darkness = "High"
    else:
        darkness = "OK"

    hot_count = hot_list.count("Hot")

    if hot_count > 3.0:
        hotness = "High"
    else:
        hotness = "OK"

    out_count = out_list.count("Out")

    if out_count > 1.0:
        outness = "High"
    else:
        outness = "OK"

    if consumption == "High":
       
        c1 = '<p>High Consumption</p>'
        c2 = '<ul><li>Your consumption is higher than the average household consumption. As a result, <b>Xarsed</b> advises you to work on your consumption to reduce it. '
        c3 = ' In this way, with your help, we will have a more pleasant nature.</li></ul>'
        
        consumption_recommendation = c1 + c2 + c3
   
    else:
        consumption_recommendation = ""

    if production == "High":
     
        p1 = '<p>High Production</p>'
        p2 = '<ul><li>The dimensions of your production system are calculated to be larger than the typical household dimensions. This can be for various reasons, including: </li></ul>' 
        if consumption == "High":
            p3 = '<ul><li>Your consumption is higher than the household pattern, as mentioned above. </li></ul>'
        else:
            p3 = ''
        if hotness == "High":
            p4 = '<ul><li>The ambient temperature in your location is high, as mentioned in the scenarios. </li></ul>'
        else:
            p4 = '' 
        if radiation == "Low":
            p5 = '<ul><li>The solar radiation in your location is low value. </li></ul>'
        else:
            p5 = '' 
        if (consumption == "OK" and radiation == "OK" and hotness == "OK"):
            p6 = '<ul><li>Solar panel technology is not suitable for power generation for you. </li></ul>'
        else:
            p6 = ''
      
        production_recommendation = p1 + p2 + p3 + p4 + p5 + p6
    
    else:
        production_recommendation = ""

    if storage == "High":
        
        s1 = '<p>High Storage</p>'
        s2 = '<ul><li>The dimensions of your storage system are calculated to be larger than the typical household dimensions. This can be for various reasons, including: </li></ul>' 
        if consumption == "High":
            s3 = '<ul><li>Your consumption is higher than the household pattern, as mentioned above. </li></ul>'
        else:
            s3 = ''
        if outness == "High":
            s4 = '<ul><li>The battery maintenance period is longer than the typical battery maintenance period, as mentioned in the scenarios. </li></ul>'
        else:
            s4 = '' 
        if darkness == "High":
            s5 = '<ul><li>The number of days without sunlight in your location is high. </li></ul>'
        else:
            s5 = '' 
        if (consumption == "OK" and darkness == "OK" and outness == "OK"):
            s6 = '<ul><li>Chemical battery technology is not suitable for power storage for you. </li></ul>'
        else:
            s6 = ''
        
        storage_recommendation = s1 + s2 + s3 + s4 + s5 + s6
    
    else:
        storage_recommendation = ""
          
    if (consumption_recommendation != "" or production_recommendation != "" or storage_recommendation != ""):
        
        recommendation = '<h2>Your Recommendations</h2>' + consumption_recommendation + production_recommendation + storage_recommendation

    else:
        
        recommendation = ""
    
    return recommendation