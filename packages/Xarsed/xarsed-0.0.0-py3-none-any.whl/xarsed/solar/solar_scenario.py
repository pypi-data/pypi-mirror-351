from xarsed.common.statistical_process import annual_hourly_average
from xarsed.common.plotting import production_consumption_plot
from xarsed.solar.photovoltaics import photovoltaics_flux


def photovoltaics_scenario(radiation, air_temperature, electricity, module, scenario):

    electricity_list = annual_hourly_average(electricity) #[W] 
    radiation_list = annual_hourly_average(radiation) #[W/m^2]
    air_temperature_list = annual_hourly_average(air_temperature) #[K]
    
    pv_flux = [] #[W/m^2]
    alarm_list = []
    for i in range(0, len(radiation_list)):
        if radiation_list[i] != 0.0:
            flux, alarm_message = photovoltaics_flux(radiation_list[i], air_temperature_list[i], module)
            pv_flux.append(flux)
            alarm_list.append(alarm_message)
        else:
            pv_flux.append(0.0)

    Hot = alarm_list.count("hot")
    Cold = alarm_list.count("cold")
    if Hot != 0:
        alarm = "Hot"
    elif Cold != 0:
        alarm = "Cold"
    elif (Hot != 0 and Cold != 0):
        alarm = "Both"
    else:
        alarm = "OK" 

    #Inverter/Converter efficiency
    eta_pv_converter = 0.95 # [%] DC-DC converter efficiency for PV to DC bus
    eta_battery_converter = 0.95 # [%] DC-DC converter efficiency for Battery to DC bus
    eta_inverter = 0.95 # [%] DC-AC inverter efficiency for DC bus to load

    # PV area    
    try:
        photovoltaics_area = sum(electricity_list) / (sum(pv_flux) * eta_pv_converter * eta_inverter) #[m^2]
    except ZeroDivisionError:
        photovoltaics_area = 0.0
    
    pv_power = [] #[W]
    for i in pv_flux:
        pv_power.append(i * photovoltaics_area)

    power_difference = [] #[W]
    
    for i in range(0, len(electricity_list)):
        difference = electricity_list[i] - pv_power[i]
        if 0 <= difference:
            power_difference.append(difference)
        else:
            power_difference.append(0)

    ##The Battery parameters                   
    #[eta_c/d: is the battery charge/discharge efficiency [%],
    #SOC_max: is the state of charge for battery at maximum [%], 
    #SOC_min: is the state of charge for battery at minimum [%],    
    #self_discharge: is the self discharge factor for battery [%/month]]
    battery_parameter = {"high": [0.85, 0.95, 0.15, 2.5], "low": [0.75, 0.8, 0.2, 5.0]} 
    
    # Battery capacity
    
    battery_capacity = sum(power_difference) / (battery_parameter[module][0] * (battery_parameter[module][1] - battery_parameter[module][2]) * eta_battery_converter * eta_inverter) #[W]
    discharge_hours = 24 - power_difference.count(0)
    
    final_battery_capacity = battery_capacity * discharge_hours #[W.h]   
    battery_loss = battery_capacity - sum(power_difference)     
    
    try:
        final_pv_area = (sum(electricity_list) + battery_loss) / (sum(pv_flux) * eta_pv_converter * eta_inverter) #[m^2]
    except ZeroDivisionError:
        final_pv_area = 0.0

    ##The PV module parameters                   
    # PV_flux = P_PV,STC / A_PV [W/m^2]]
    module_parameter = {"high": [220], "low": [80]} 
    
    try:
        final_pv_power = module_parameter[module][0] * final_pv_area #[W]
    except ZeroDivisionError:
        final_pv_power = 0.0

    inverter_power = max(electricity_list) * 2.0 / eta_inverter #[W]
    pv_converter_power = max(pv_flux) * final_pv_area * 2.0 / eta_pv_converter #[W]

    battery_power_difference = [] #[W]
    for i in range(0, len(electricity_list)):
        difference = electricity_list[i] - pv_power[i]
        battery_power_difference.append(abs(difference))
    
    battery_converter_power = max(battery_power_difference) * 2.0 / eta_battery_converter #[W]
    
    min_alarm = "Ok"

    consumption = [] #[kW]
    for i in electricity_list:
        consumption.append(i / 1000.0)
    production = [] #[kW]
    for i in pv_flux:
        production.append(i * final_pv_area / 1000.0)

    final_plot = production_consumption_plot(consumption, production, "kW", module, scenario) 
    
    calculated_parameter = [round(final_pv_power/1000.0,2), round(final_pv_area,2), round(final_battery_capacity/1000.0,2), round(inverter_power/1000.0,2), round(pv_converter_power/1000.0,2), round(battery_converter_power/1000.0,2)]
    zero_parameter = calculated_parameter.count(0.0)
    
    if zero_parameter != 0:
        zero_alarm = "Zero"
    else:
        zero_alarm = "OK"
    
    final_list = [final_pv_power, final_pv_area, final_battery_capacity, inverter_power, pv_converter_power, battery_converter_power, final_plot, alarm, min_alarm, zero_alarm]
    
    return final_list