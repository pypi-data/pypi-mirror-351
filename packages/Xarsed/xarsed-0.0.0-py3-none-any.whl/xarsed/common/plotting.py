import plotly.graph_objects as go


def production_consumption_plot(consumption, production, unit, module, scenario):

    x_axis = ["00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]

    figure = go.Figure()

    figure.add_trace(go.Scatter(
        x=x_axis,
        y=consumption,
        fill="tozeroy",
        fillcolor="hsla(350.09, 100%, 45.1%, 0.2)", 
        line_color="hsl(350.09, 100%, 45.1%)",
        name="Consumption",    
    ))
    figure.add_trace(go.Scatter(
        x=x_axis,
        y=production,
        fill="tozeroy",
        fillcolor="hsla(180, 100%, 40%, 0.2)", 
        line_color="hsl(180, 100%, 40%)",
        name="Production",
    ))
    figure.update_traces(mode="lines")
    figure.update_layout(
        xaxis_title="Time [Hour]",
        yaxis_title="Value["+unit+"]",
        title=scenario+" Scenario for "+module+"-path",
    )
    
    final_plot = figure.to_html()

    return final_plot
