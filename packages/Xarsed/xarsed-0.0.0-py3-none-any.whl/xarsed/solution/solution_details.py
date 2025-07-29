from xarsed.solution.warning_recommendation import solar_energy_pv_electricity_battery_warning


def solar_energy_pv_electricity_battery_details(all_schemes, recommendation, plot_list, alarm_list, min_list, zero_list, latitude):

    line1 = '<h1>Solution Details</h1>'
    line2 = '<p>In this section, you can see the details of the average scenario in two paths, high and low. '
    line3 = 'In the figure below, the system components are placed side by side to give you a better understanding of the system state. '
    line4 = 'To be able to use this data to determine the dimensions you want, refer to the example at the end of the report.</p>'
    line5 = '<p>Your report may contain warnings and recommendations under each scenario. In this case, it can be said that sometimes the outputs of the <b>Xarsed</b> algorithm are calculated outside the norm, based on the criteria. '
    line6 = 'Pay attention to the messages to better understand your system and be more productive.</p>'
    part1 = line1 + line2 + line3 + line4 + line5 + line6

    scheme1 = '<h2>Scheme of Average scenarios</h2><div style="width: 100%; height: 0; padding-top: 96%; position: relative;">'+all_schemes[0]+'</div>'
    plot1 = '<h2>Plots of Average scenarios</h2><div>'+plot_list[0]+'</div><br>'    
    alarm1 = solar_energy_pv_electricity_battery_warning(alarm_list[0], "Average", "high")
    alarm2 = solar_energy_pv_electricity_battery_warning(min_list[0], "Average", "high")
    alarm3 = solar_energy_pv_electricity_battery_warning(zero_list[0], "Average", "high")
    plot2 = '<div>'+plot_list[1]+'</div>'
    alarm4 = solar_energy_pv_electricity_battery_warning(alarm_list[1], "Average", "low")
    alarm5 = solar_energy_pv_electricity_battery_warning(min_list[1], "Average", "low")
    alarm6 = solar_energy_pv_electricity_battery_warning(zero_list[1], "Average", "low")
    part2 = scheme1 + plot1 + alarm1 + alarm2 + alarm3 + plot2 + alarm4 + alarm5 + alarm6 
    
    line7 = '<h2>General recommendations</h2>'
    line8 = '<ul><li>Solar panels, need light to produce electricity. As a result, they should be placed in a location that has the most light and the least shade during the day. '
    if latitude > 0:
        line9 = 'To find this location, you should check the shadows of your desired location on the southern solstice, which usually occurs on December 21 or 22, cause you are in the northern hemisphere. ' 
    else:
        line9 = 'To find this location, you should check the shadows of your desired location on the northern solstice, which usually occurs on June 20, 21 or 22, cause you are in the southern hemisphere. '
    line10 = 'On this day, the length of the shadows is the greatest. You can also do this with the help of satellite image archives. '
    line11 = 'The method is simple, just check how far the buildings, trees and other large elements around you cast shadows on this date, within a time range of 2 to 3 hours before and after solar noon. Outside this area, the most suitable place to install panels are.</li>'
    line12 = '<li>Due to their outdoor location, the panels are constantly exposed to dust and air pollution. On the other hand, snow and hail also prevent light from reaching them. ' 
    line13 = 'To maintain their power production, clean their surface preferably every month and also after snow or hail.</li>'
    line14 = '<li>The operating temperature of the panels is typically between -40°C and 85°C. Therefore, to prevent damage, keep them away from excessive heat such as flames. Also, cover them when the temperature drops sharply.</li>'
    line15 = '<li>The ideal operating temperature for batteries is between 20°C and 30°C. Therefore, except for the panels, which should be outdoors, place the rest of the equipment in a room (preferably underground, as the temperature is usually lower) to make it easier to control the temperature. '
    line16 = 'With proper ventilation, it is easy to control the temperature of an enclosed space that is not exposed to direct sunlight.</li></ul>'
    part3 = line7 + line8 + line9 + line10 + line11 + line12 + line13 + line14 + line15 + line16
    
    line17 = '<h2>An example of finding the desired dimensions using data from the Xarsed report</h2>'
    line18 = '<p>If the device you want to purchase has the specifications listed in the details table, your job is simple. Just consider the dimensions specified by the <b>Xarsed</b> to receive the equipment and install your system. '
    line19 = 'However, if you want to purchase a device with different details, the following path will help you.</p>'
    line20 = '<p>Let’s assume that the panel you want to purchase has an efficiency of 15%. <b>Xarsed</b> has calculated the panel area for your high path to be 20 square meters and for low path to be 40 square meters. '
    line21 = 'From the table, the efficiency of the high path panel is 22% and the low path to be 8%. Now calculate the area of your panel with a simple equation as follows:</p>'
    part4 = line17 + line18 + line19 + line20 + line21
    
    equation1 = '<div class="boxes"><div class="form"><p>efficiency<sub>high</sub> - efficiency<sub>yours</sub></p><hr><p>efficiency<sub>high</sub> - efficiency<sub>low</sub></p></div>'
    equation2 = '<div class="form"><p>=</p></div><div class="form"><p>area<sub>high</sub> - area<sub>yours</sub></p><hr><p>area<sub>high</sub> - area<sub>low</sub></p></div></div>'
    equation = equation1 + equation2
    
    line22 = '<p>By putting the values into the equation above, the calculated area value for the desired efficiency will be equal to 30 square meters.</p>'
    line23 = '<p>You can use the same method for each of the other components of the system and achieve the dimensions of the equipment you want.</p>'
    part5 =  line22 + line23
    
    solution_details = part1 + part2 + recommendation + part3 + part4 + equation + part5

    return solution_details 