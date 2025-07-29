
def solar_energy_pv_electricity_battery_overview(panel_position):
    
    line1 = '<h1>Solution Overview</h1>'
    line2 = '<h2>The Xarsed solution for designing the triple PV-Battery-Electricity system</h2>'
    line3 = '<p>PV panels need sunlight to generate electricity. As a result, their position must be adjusted to their surface faces the sun. ' 
    line4 = 'There are mainly six methods of orientation towards the sun, which are shown below, based on the lowest to highest efficiency:</p>'
    line5 = '<ul><li>Vertical plane (wall)</li><li>Horizontal plane (roof)</li><li><b>Tilted fixed (one optimal angle)</b></li>'
    line6 = '<li>Tilted fixed (two optimal angles for summer and winter)</li><li>One-axis tracker</li><li><b>Two-axis tracker</b></li></ul>'
    line7 = '<p><b>Xarsed</b> considers the low cost and efficiency Tilted fixed (one optimal angle) method as the minimum option and the high cost efficiency Two-axis tracker method as the maximum option for calculations.</p>'
    part1 = line1 + line2 + line3 + line4 + line5 + line6 + line7

    line8 = '<p>To date, three generations of PV panels have been developed, which are listed below:</p>'
    line9 = '<ul><li><b>First generation</b></li><li>Mono-crystalline silicon</li><li>Poly-crystalline silicon</li>'
    line10 = '<li><b>Second generation</b></li><li>Amorphous silicon</li><li>Cadmium telluride</li><li>Copper indium gallium diselenide</li>'
    line11 = '<li><b>Third generation</b></li><li>Perovskite</li><li>Dye-sensitised</li><li>Organic</li></ul>'
    line12 = '<p>Currently, based on the panels available on the market, the overall efficiency of the panels can be considered between 5 and 25 percent. '
    line13 = 'As a result, <b>Xarsed</b> combines the panel with higher technical characteristics with the Two-axis tracker system and the panel with lower specifications with the Tilted fixed system in the calculations.</p>'
    part2 = line8 + line9 + line10 + line11 + line12 + line13

    line14 = '<p>As for batteries, two types of batteries, lead-acid and lithium-ion, are usually associated with solar systems. ' 
    line15 = 'Based on market data, the cost and efficiency of the lead-acid are lower than the lithium-ion, so to complete the calculation process, lead-acid batteries were coupled with the tilted system and lithium-ion batteries were coupled with the tracker system. '
    line16 = 'Also, the inverter and converter were also included in <b>Xarsed</b> calculations, with typical market efficiency. Details of all equipment calculated in the PV-Battery-Electricity section are given in the table below.</p>'
    part3 = line14 + line15 + line16

    row1 = '<table><tr><th><b>Tracking System</b></th><th><b>High</b></th><th><b>Low</b></th></tr>'
    row2 = '<tr><td><b>Type</b></td><td>Two-axis tracker</td><td>Tilted fixed</td></tr>'
    row3 = '<tr><td><b>Angle [°]</b></td><td>Solar Azimuth and Zenith</td><td><a href="#AZ">Look here</a></td></tr>'
    row4 = '<tr><th><b>PV Panel</b></th><th><b>High</b></th><th><b>Low</b></th></tr>'
    row5 = '<tr><td><b>Efficiency [%]</b></td><td>22.0</td><td>8.0</td></tr>'
    row6 = '<tr><td><b>PV power flux [W/m^2]</b></td><td>220.0</td><td>180.0</td></tr>'
    row7 = '<tr><td><b>Power temperature coefficient [%/°C]</b></td><td>-0.3</td><td>-0.5</td></tr>'
    row8 = '<tr><td><b>Nominal operating cell temperature (NOCT) [°C]</b></td><td>45.0</td><td>57.0</td></tr>'
    row9 = '<tr><th><b>Battery</b></th><th><b>High</b></th><th><b>Low</b></th></tr>'
    row10 = '<tr><td><b>Efficiency [%]</b></td><td>85.0</td><td>75.0</td></tr>'
    row11 = '<tr><td><b>Maximum state of charge [%]</b></td><td>95.0</td><td>80.0</td></tr>'
    row12 = '<tr><td><b>Minimum state of charge [%]</b></td><td>15.0</td><td>20.0</td></tr>'
    row13 = '<tr><td><b>Self discharge factor [%/month]</b></td><td>2.5</td><td>5.0</td></tr>'
    row14 = '<tr><th><b>Inverter/Converter</b></th><th colspan="2"><b>Efficiency [%]</b></th></tr>'
    row15 = '<tr><td><b>DC-DC converter (PV to DC bus)</b></td><td colspan="2">95.0</td></tr>'
    row16 = '<tr><td><b>DC-DC converter (Battery to DC bus)</b></td><td colspan="2">95.0</td></tr>'
    row17 = '<tr><td><b>DC-AC inverter (DC bus to load)</b></td><td colspan="2">95.0</td></tr></table>'
    table = row1 + row2 + row3 + row4 + row5 + row6 + row7 + row8 + row9 + row10 + row11 + row12 + row13 + row14 + row15 + row16 + row17 
    
    scheme = '<h2>The panel position for your location</h2><div id="AZ" style="width: 100%; height: 0; padding-top: 64%; position: relative;">'+panel_position+'</div>'            
    
    line17 = '<p>Now that the system components have been described, let’s take a look at the scenario that governs the calculations. '
    line18 = '<b>Xarsed</b> defines an average scenario to establish the relationship between production, consumption, and storage, the three basic components of the system. '
    line19 = 'In this scenario, as the name suggests, your average daily consumption over a year is the design criterion for the triple system. '
    line20 = 'You can see the full details of this design for both the high and low paths in the section below.</p>'
    part4 = line17 + line18 + line19 + line20
    
    solution_overview = part1 + part2 + part3 + table + scheme + part4 

    return solution_overview
                    