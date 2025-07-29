import math


def modified_radiation(radiation):
    
    solar_constant = 1362.0 # [W/m^2] 
    final_radiation = []
    for i in radiation:
        
        if (solar_constant < i or i < -solar_constant): #current
           
            step = 1
            previous_step = radiation[radiation.index(i) - step] #previous
            next_step = radiation[radiation.index(i) + step] #next
            
            while (solar_constant < previous_step or previous_step < -solar_constant):
                step += 1
                previous_step = radiation[radiation.index(i) - step]
            
            else:
                final_previous_step = previous_step
            
            while (solar_constant < next_step or next_step < -solar_constant):
                step += 1
                next_step = radiation[radiation.index(i) + step]
            
            else:
                final_next_step = next_step
            
            final_radiation.append(abs((final_previous_step + final_next_step) / 2.0)) 
        
        else:
            final_radiation.append(abs(i))
    
    return final_radiation


def radiation_calculation(latitude, global_horizontal_irradiance, diffuse_horizontal_irradiance, surface_albedo, zenith_angle, azimuth_angle):

    optimum_zenith_angle = abs(latitude)
    zenith_optimum_list = []                                                        
    for i in range(0, 8760):
        zenith_optimum_list.append(optimum_zenith_angle)
  
    if latitude < 0:
        optimum_azimuth_angle = 180
    else:
        optimum_azimuth_angle = 0 
    
    optimum_azimuth_list = []
    for i in range(0, 8760):
        optimum_azimuth_list.append(optimum_azimuth_angle)
    
    # the angle between the normal of the tilted surface and that of the beam sunlight
    cosine_incident_angle = []
    for i in range(0, len(zenith_angle)):
        cosine_incident_angle.append(math.cos(math.radians(zenith_angle[i])) * math.cos(math.radians(zenith_optimum_list[i])) 
        + math.sin(math.radians(zenith_angle[i])) * math.sin(math.radians(zenith_optimum_list[i])) * math.cos(math.radians(azimuth_angle[i] - optimum_azimuth_list[i])))

    # the global tilted irradiance (GTdI) 
    tilted_irradiance = [] 
    for i in range(0, len(global_horizontal_irradiance)):
        tilted_irradiance.append((global_horizontal_irradiance[i] - diffuse_horizontal_irradiance[i]) * (cosine_incident_angle[i] / math.cos(math.radians(zenith_angle[i])))
        + diffuse_horizontal_irradiance[i] * ((1 + math.cos(math.radians(zenith_optimum_list[i]))) / 2) 
        + global_horizontal_irradiance[i] * surface_albedo[i] * ((1 - math.cos(math.radians(zenith_optimum_list[i]))) / 2))
    
    global_tilted_irradiance = modified_radiation(tilted_irradiance)

    # the global tracker irradiance (GTrI)
    tracker_irradiance = [] 
    for i in range(0, len(global_horizontal_irradiance)):
        tracker_irradiance.append((global_horizontal_irradiance[i] - diffuse_horizontal_irradiance[i]) / math.cos(math.radians(zenith_angle[i]))
        + diffuse_horizontal_irradiance[i] * ((1 + math.cos(math.radians(zenith_angle[i]))) / 2) 
        + global_horizontal_irradiance[i] * surface_albedo[i] * ((1 - math.cos(math.radians(zenith_angle[i]))) / 2))
 
    global_tracker_irradiance = modified_radiation(tracker_irradiance)
        
    return optimum_zenith_angle, optimum_azimuth_angle, global_tilted_irradiance, global_tracker_irradiance


def photovoltaics_flux(radiation, air_temperature, module):
    
    #The PV module parameters                      #############################################################
    #[T_c,NOCT: is the nominal operating cell temperature (NOCT) [°C],
    # eta_c: is PV efficiency [%], 
    # alfa_p: is the temperature coefficient [%/°C],
    # PV_flux = P_PV,STC / A_PV [W/m^2],
    # track_cons: is the consumption of tracking system  from the total generated power [%]]
    # P_PV,STC: is the PV capacity at standard test conditions (STC) [W]
    # A_PV: is the PV module area [m^2]
    module_parameter = {"high": [45.0, 22.0, -0.3, 220.0, 0.04], "low": [57.0, 8.0, -0.5, 80.0, 0.0]} 
    
    #The cell temperature [°C]
    cell_temperature = (air_temperature - 273.15) + radiation * ((module_parameter[module][0] - 20.0) / 800.0) * (1 - module_parameter[module][1]/90.0)
    if cell_temperature < -40.0:
        alarm_message = "cold"
    elif cell_temperature > 85.0:
        alarm_message = "hot"
    else:
        alarm_message = "ok"

    #The derating factor of temperature []
    derating_factor = 1.0 + module_parameter[module][2] * (cell_temperature - 25.0) / 100.0
    if derating_factor > 1:
        derating_factor = 1.0
    elif derating_factor < 0:
        derating_factor = 0.0

    #The PV output flux [W/m^2]
    photovoltaics_flux = module_parameter[module][3] * 0.9 * derating_factor * (radiation / 1000.0) * (1 - module_parameter[module][4])

    return photovoltaics_flux, alarm_message
    