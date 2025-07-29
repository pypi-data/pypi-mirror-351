import math


def photovoltaics_panel_position(zenith_angle, azimuth_angle):
    
    if azimuth_angle == 0:
        direction = "South"
    else:
        direction = "North"
    
    y1 = 320.0 - 120.0 * math.sin(math.radians(zenith_angle))
    x2 = 750.0 + 120.0 * math.cos(math.radians(zenith_angle))

    part1 = '<svg viewBox="0 0 1000 640" xmlns="http://www.w3.org/2000/svg" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">'
    part2 = '<rect width="160" height="50" x="170" y="20" rx="10" ry="10" fill="hsl(187.23, 100%, 16.27%)" />'
    part3 = '<text x="180" y="50" textLength="140" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >Azimuth (optimum) = '+str(azimuth_angle)+' [°]</text>'
    part4 = '<polyline points="70,310 60,320 70,330 60,320 440,320 430,310 440,320 430,330" fill="none" stroke="hsl(355.14, 37%, 39.22%)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
    part5 = '<polyline points="240,140 250,130 260,140 250,130 250,510 240,500 250,510 260,500" fill="none" stroke="hsl(355.14, 37%, 39.22%)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
    part6 = '<rect width="50" height="40" x="225" y="80" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part7 = '<text x="230" y="105" textLength="40" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >North</text>'
    part8 = '<rect width="50" height="40" x="225" y="520" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part9 = '<text x="230" y="545" textLength="40" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >South</text>'
    part10 = '<rect width="50" height="40" x="445" y="300" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part11 = '<text x="450" y="325" textLength="40" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >East</text>'
    part12 = '<rect width="50" height="40" x="5" y="300" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part13 = '<text x="10" y="325" textLength="40" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >West</text>'
    section1 = part1 + part2 + part3 + part4 + part5 + part6 + part7 + part8 + part9 + part10 + part11 + part12 + part13
    
    if azimuth_angle == 0:
        part14 = '<rect width="80" height="120" x="210" y="350" fill="hsl(221.54, 98.11%, 20.78%)" stroke="hsl(219.23, 17.81%, 71.37%)" stroke-width="4" />'
    else:
        part14 = '<rect width="80" height="120" x="210" y="170" fill="hsl(221.54, 98.11%, 20.78%)" stroke="hsl(219.23, 17.81%, 71.37%)" stroke-width="4" />'   

    part15 = '<rect width="160" height="50" x="670" y="20" rx="10" ry="10" fill="hsl(187.23, 100%, 16.27%)" />'
    part16 = '<text x="680" y="50" textLength="140" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >Zenith (optimum) = '+str(round(zenith_angle))+' [°]</text>'
    part17 = '<polyline points="570,310 560,320 570,330 560,320 940,320 930,310 940,320 930,330" fill="none" stroke="hsl(355.14, 37%, 39.22%)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
    part18 = '<polyline points="740,140 750,130 760,140 750,130 750,510 740,500 750,510 760,500" fill="none" stroke="hsl(355.14, 37%, 39.22%)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
    part19 = '<rect width="50" height="40" x="725" y="80" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part20 = '<text x="740" y="105" textLength="20" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >Up</text>'
    part21 = '<rect width="50" height="40" x="725" y="520" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part22 = '<text x="730" y="545" textLength="40" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >Down</text>'
    part23 = '<rect width="50" height="40" x="945" y="300" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part24 = '<text x="950" y="325" textLength="40" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >Front</text>'
    part25 = '<rect width="50" height="40" x="505" y="300" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part26 = '<text x="510" y="325" textLength="40" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >Back</text>'
    part27 = '<line x1="750" y1="'+str(y1)+'" x2="'+str(x2)+'" y2="320" stroke="hsl(219.23, 17.81%, 71.37%)" stroke-width="8" />'           
    section2 = part14 + part15 + part16 + part17 + part18 + part19 + part20 + part21 + part22 + part23 + part24 + part25 + part26 + part27    
    
    part28 = '<line x1="500" y1="80" x2="500" y2="560" stroke="hsl(0, 0%, 2.75%)" stroke-width="2" stroke-linecap="round" stroke-dasharray="10,10" />'
    part29 = '<rect width="600" height="50" x="200" y="570" rx="10" ry="10" fill="hsl(24, 32.61%, 18.04%)" />'
    part30 = '<text x="210" y="600" textLength="580" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >'
    part31 = 'According to the figure above, you should place your panel facing '+direction+', at a '+str(round(zenith_angle))+'-degree angle to the horizontal.</text>'
    part32 = '</svg>'
    section3 = part28 + part29 + part30 + part31 + part32 

    graph = section1 + section2 + section3

    return graph


def photovoltaics_electricity_battery_scheme(scenario, up_list, down_list):
    
    up = "low"
    down = "high"
    up_word = scenario+"-low"       
    down_word = scenario+"-high"

    more = []
    for i in range(0,len(up_list)):
        if up_list[i] < down_list[i]:
            more.append(True)
        else:
            more.append(False)

    part1 = '<svg viewBox="0 0 1100 1050" xmlns="http://www.w3.org/2000/svg" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">'
    part2 = '<rect width="140" height="50" x="100" y="20" rx="10" ry="10" fill="hsl(13.18, 100%, 50%)" />'
    part3 = '<text x="110" y="50" textLength="120" lengthAdjust="spacingAndGlyphs" fill="hsl(0, 0%, 2.75%)" font-family="Verdana" >P<tspan style="font-size:small">'+up+'</tspan> = '+str(round(up_list[0]/1000.0,2))+' [kW]</text>'
    part4 = '<rect width="140" height="50" x="100" y="80" rx="10" ry="10" fill="hsl(180, 100%, 50%)" />'
    part5 = '<text x="110" y="110" textLength="120" lengthAdjust="spacingAndGlyphs" fill="hsl(0, 0%, 2.75%)" font-family="Verdana" >P<tspan style="font-size:small">'+down+'</tspan> = '+str(round(down_list[0]/1000.0,2))+' [kW]</text>'
    part6 = '<rect width="80" height="50" x="10" y="180" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part7 = '<text x="20" y="210" textLength="60" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >PV Array</text>'
    part8 = '<polygon points="100,140 240,140 240,280 100,280 100,140 170,210 240,140" fill="hsl(39.29, 100%, 50%)" stroke="hsl(219.23, 17.81%, 71.37%)" stroke-width="3" stroke-linejoin="round" />'
    part9 = '<rect width="140" height="50" x="100" y="290" rx="10" ry="10" fill="hsl(13.18, 100%, 50%)" />'
    part10 = '<text x="110" y="320" textLength="120" lengthAdjust="spacingAndGlyphs" fill="hsl(0, 0%, 2.75%)" font-family="Verdana" >A<tspan style="font-size:small">'+up+'</tspan> = '+str(round(up_list[1],2))+' [m^<tspan style="font-size: small">2</tspan>]</text>'
    part11 = '<rect width="140" height="50" x="100" y="350" rx="10" ry="10" fill="hsl(180, 100%, 50%)" />'
    part12 = '<text x="110" y="380" textLength="120" lengthAdjust="spacingAndGlyphs" fill="hsl(0, 0%, 2.75%)" font-family="Verdana" >A<tspan style="font-size:small">'+down+'</tspan> = '+str(round(down_list[1],2))+' [m^<tspan style="font-size: small">2</tspan>]</text>'
    part13 = '<polyline points="240,210 340,210 330,200 340,210 330,220" fill="none" stroke="hsl(355.14, 37%, 39.22%)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
    section1 = part1 + part2 + part3 + part4 + part5 + part6 + part7 + part8 + part9 + part10 + part11 + part12 + part13
    
    part14 = '<rect width="80" height="50" x="130" y="450" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part15 = '<text x="140" y="480" textLength="60" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >Battery</text>'
    part16 = '<polygon points="100,530 150,530 150,510 130,510 130,530 210,530 210,510 190,510 190,530 240,530 240,630 100,630 100,530" fill="hsl(39.29, 100%, 50%)" stroke="hsl(219.23, 17.81%, 71.37%)" stroke-width="3" stroke-linejoin="round" />'
    part17 = '<rect width="140" height="50" x="100" y="660" rx="10" ry="10" fill="hsl(13.18, 100%, 50%)" />'
    part18 = '<text x="110" y="690" textLength="120" lengthAdjust="spacingAndGlyphs" fill="hsl(0, 0%, 2.75%)" font-family="Verdana" >E<tspan style="font-size:small">'+up+'</tspan> = '+str(round(up_list[2]/1000.0,2))+' [kW.h]</text>'
    part19 = '<rect width="140" height="50" x="100" y="720" rx="10" ry="10" fill="hsl(180, 100%, 50%)" />'
    part20 = '<text x="110" y="750" textLength="120" lengthAdjust="spacingAndGlyphs" fill="hsl(0, 0%, 2.75%)" font-family="Verdana" >E<tspan style="font-size:small">'+down+'</tspan> = '+str(round(down_list[2]/1000.0,2))+' [kW.h]</text>'
    part21 = '<polyline points="250,570 240,580 250,590 240,580 340,580 330,570 340,580 330,590" fill="none" stroke="hsl(355.14, 37%, 39.22%)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
    section2 = part14 + part15 + part16 + part17 + part18 + part19 + part20 + part21

    part22 = '<rect width="120" height="50" x="350" y="80" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part23 = '<text x="360" y="110" textLength="100" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >PV Converter</text>'
    part24 = '<polygon points="480,140 480,280 340,280 340,140 480,140 340,280" fill="hsl(39.29, 100%, 50%)" stroke="hsl(219.23, 17.81%, 71.37%)" stroke-width="3" stroke-linejoin="round" />'
    part25 = '<rect width="140" height="50" x="340" y="290" rx="10" ry="10" fill="hsl(13.18, 100%, 50%)" />'
    part26 = '<text x="350" y="320" textLength="120" lengthAdjust="spacingAndGlyphs" fill="hsl(0, 0%, 2.75%)" font-family="Verdana" >P<tspan style="font-size:small">'+up+'</tspan> = '+str(round(up_list[4]/1000.0,2))+' [kW]</text>'
    part27 = '<rect width="140" height="50" x="340" y="350" rx="10" ry="10" fill="hsl(180, 100%, 50%)" />'
    part28 = '<text x="350" y="380" textLength="120" lengthAdjust="spacingAndGlyphs" fill="hsl(0, 0%, 2.75%)" font-family="Verdana" >P<tspan style="font-size:small">'+down+'</tspan> = '+str(round(down_list[4]/1000.0,2))+' [kW]</text>'
    part29 = '<polyline points="480,210 580,210 570,200 580,210 570,220" fill="none" stroke="hsl(355.14, 37%, 39.22%)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
    section3 = part22 + part23 + part24 + part25 + part26 + part27 + part28 + part29
    
    part30 = '<rect width="140" height="50" x="340" y="450" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part31 = '<text x="350" y="480" textLength="120" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >Battery Converter</text>'
    part32 = '<polygon points="480,510 480,650 340,650 340,510 480,510 340,650" fill="hsl(39.29, 100%, 50%)" stroke="hsl(219.23, 17.81%, 71.37%)" stroke-width="3" stroke-linejoin="round" />'
    part33 = '<rect width="140" height="50" x="340" y="660" rx="10" ry="10" fill="hsl(13.18, 100%, 50%)" />'
    part34 = '<text x="350" y="690" textLength="120" lengthAdjust="spacingAndGlyphs" fill="hsl(0, 0%, 2.75%)" font-family="Verdana" >P<tspan style="font-size:small">'+up+'</tspan> = '+str(round(up_list[5]/1000.0,2))+' [kW]</text>'
    part35 = '<rect width="140" height="50" x="340" y="720" rx="10" ry="10" fill="hsl(180, 100%, 50%)" />'
    part36 = '<text x="350" y="750" textLength="120" lengthAdjust="spacingAndGlyphs" fill="hsl(0, 0%, 2.75%)" font-family="Verdana" >P<tspan style="font-size:small">'+down+'</tspan> = '+str(round(down_list[5]/1000.0,2))+' [kW]</text>'
    part37 = '<polyline points="490,570 480,580 490,590 480,580 580,580 570,570 580,580 570,590" fill="none" stroke="hsl(355.14, 37%, 39.22%)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'  
    section4 = part30 + part31 + part32 + part33 + part34 + part35 + part36 + part37     
    
    part38 = '<rect width="80" height="50" x="540" y="80" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part39 = '<text x="550" y="110" textLength="60" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >DC Bus</text>'
    part40 = '<line x1="580" y1="140" x2="580" y2="650" stroke="hsl(355.14, 37%, 39.22%)" stroke-width="3" stroke-linecap="round" />'
    part41 = '<polyline points="580,390 680,390 670,380 680,390 670,400" fill="none" stroke="hsl(355.14, 37%, 39.22%)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
    part42 = '<polyline points="580,210 710,210 700,200 710,210 700,220" fill="none" stroke="hsl(355.14, 37%, 39.22%)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
    part43 = '<rect width="80" height="50" x="710" y="185" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part44 = '<text x="720" y="215" textLength="60" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >DC Load</text>'
    section5 = part38 + part39 + part40 + part41 + part42 + part43 + part44

    part45 = '<rect width="80" height="50" x="710" y="260" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part46 = '<text x="720" y="290" textLength="60" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >Inverter</text>'
    part47 = '<polygon points="820,320 820,460 680,460 680,320 820,320 680,460" fill="hsl(39.29, 100%, 50%)" stroke="hsl(219.23, 17.81%, 71.37%)" stroke-width="3" stroke-linejoin="round" />'
    part48 = '<rect width="140" height="50" x="680" y="470" rx="10" ry="10" fill="hsl(13.18, 100%, 50%)" />'
    part49 = '<text x="690" y="500" textLength="120" lengthAdjust="spacingAndGlyphs" fill="hsl(0, 0%, 2.75%)" font-family="Verdana" >P<tspan style="font-size:small">'+up+'</tspan> = '+str(round(up_list[3]/1000.0,2))+' [kW]</text>'
    part50 = '<rect width="140" height="50" x="680" y="530" rx="10" ry="10" fill="hsl(180, 100%, 50%)" />'
    part51 = '<text x="690" y="560" textLength="120" lengthAdjust="spacingAndGlyphs" fill="hsl(0, 0%, 2.75%)" font-family="Verdana" >P<tspan style="font-size:small">'+down+'</tspan> = '+str(round(down_list[3]/1000.0,2))+' [kW]</text>'
    part52 = '<polyline points="820,390 920,390 910,380 920,390 910,400" fill="none" stroke="hsl(355.14, 37%, 39.22%)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
    section6 = part45 + part46 + part47 + part48 + part49 + part50 + part51 + part52

    part53 = '<rect width="80" height="50" x="880" y="80" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part54 = '<text x="890" y="110" textLength="60" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >AC Bus</text>' 
    part55 = '<line x1="920" y1="140" x2="920" y2="650" stroke="hsl(355.14, 37%, 39.22%)" stroke-width"3" stroke-linecap="round" />'
    part56 = '<polyline points="920,390 1000,390 990,380 1000,390 990,400" fill="none" stroke="hsl(355.14, 37%, 39.22%)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
    part57 = '<rect width="80" height="50" x="1000" y="365" rx="10" ry="10" fill="hsl(258.46, 74.29%, 27.45%)" />'
    part58 = '<text x="1010" y="395" textLength="60" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >AC Load</text>'
    section7 = part53 + part54 + part55 + part56 + part57 + part58 

    part59 = '<rect width="120" height="80" x="960" y="200" rx="10" ry="10" fill="hsl(24, 32.61%, 18.04%)" />'
    part60 = '<text x="970" y="230" textLength="100" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >Scenario</text>'
    part61 = '<text x="980" y="260" textLength="80" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >'+scenario+'</text>'  
    section8 = part59 + part60 + part61

    part62 = '<rect width="1000" height="80" x="50" y="800" rx="10" ry="10" fill="hsl(24, 32.61%, 18.04%)" />'
    part63 = '<text x="60" y="830" textLength="980" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >'
    part64 = 'As can be seen from the figure, for the '+down_word+' scenario, the required power for PV is '+str(round(down_list[0]/1000.0,2))+' kW or the required panel area is '+str(round(down_list[1],2))+' m^2. The amount of energy</text>'
    part65 = '<text x="60" y="860" textLength="980" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >'
    part66 = 'required for storage, or battery capacity, is '+str(round(down_list[2]/1000.0,2))+' kW.h. Also, the power of PV converter, battery converter and inverter are '+str(round(down_list[4]/1000.0,2))+', '+str(round(down_list[5]/1000.0,2))+' and '+str(round(down_list[3]/1000.0,2))+' kW respectively.</text>'
    part67 = '<rect width="1000" height="80" x="50" y="900" rx="10" ry="10" fill="hsl(24, 32.61%, 18.04%)" />'
    part68 = '<text x="60" y="930" textLength="980" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >'
    part69 = 'As can be seen from the figure, for the '+up_word+' scenario, the required power for PV is '+str(round(up_list[0]/1000.0,2))+' kW or the required panel area is '+str(round(up_list[1],2))+' m^2. The amount of energy</text>'
    part70 = '<text x="60" y="960" textLength="980" lengthAdjust="spacingAndGlyphs" fill="hsl(60, 55.56%, 91.18%)" font-family="Verdana" >'
    part71 = 'required for storage, or battery capacity, is '+str(round(up_list[2]/1000.0,2))+' kW.h. Also, the power of PV converter, battery converter and inverter are '+str(round(up_list[4]/1000.0,2))+', '+str(round(up_list[5]/1000.0,2))+' and '+str(round(up_list[3]/1000.0,2))+' kW respectively.</text>'
    
    if more.count(True) > 0:
        part72 = '<rect width="1000" height="40" x="50" y="1000" rx="10" ry="10" fill="hsl(24, 32.61%, 18.04%)" />'
        part73 = '<text x="60" y="1025" textLength="980" lengthAdjust="spacingAndGlyphs" fill="hsl(39.29, 100%, 50%)" font-family="Verdana" >'
        part74 = 'The parameters of the high scenario are more than the low scenario, usually due to its less calculated radiation value (see below plots).</text>'
    else:
        part72 = ''
        part73 = ''
        part74 = ''
    
    part75 = '</svg>'

    section9 = part62 + part63 + part64 + part65 + part66 + part67 + part68 + part69 + part70 + part71 + part72 + part73 + part74 + part75
    
    scheme = section1 + section2 + section3 + section4 + section5 + section6 + section7 + section8 + section9
    
    return scheme 

