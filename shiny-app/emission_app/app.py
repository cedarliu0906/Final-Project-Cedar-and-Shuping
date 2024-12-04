from shiny import App, reactive, render, ui
import pandas as pd 
import pandas as pd
import altair as alt 
import pandas as pd
from datetime import date
import numpy as np
from shinywidgets import render_altair, output_widget
import os


file_path1 = "../../gdp_merged.csv"
file_path2 = "../../carbon_annual.csv"
# Load the CSV file
combined_data = pd.read_csv(file_path1)
annual_nation = pd.read_csv(file_path2)
# Define UI
app_ui = ui.page_fluid(
    ui.h2("Carbon Emissions per GDP from 2012 to 2022"),
    ui.input_select(
        id="province_select", 
        label="Select Province", 
        choices=["Nationwide"] + sorted(combined_data['Province'].unique())
    ),
    ui.input_checkbox("show", "Show Changes", True),
    ui.panel_conditional(
        "input.province_select === 'Nationwide'",
        output_widget("renewable_plot2")
),
    ui.panel_conditional(
        "input.province_select !== 'Nationwide'",
        output_widget("renewable_plot")
),
)

# Define Server Logic
def server(input, output, session):
    @output
    @render.text
    def state_left():
        return f"input.sidebar_left()"
    @render_altair
    def renewable_plot():
        # Get the selected province
        selected_province = input.province_select()

        # Filter data for the selected province

        plot_data = combined_data[combined_data['Province'] == selected_province]

        # Convert plot_data to a proper DataFrame
        plot_data = plot_data.reset_index(drop=True)

        # Create Altair line plot
        chart = alt.Chart(plot_data).mark_line(point=True).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Carbon Emissions per GDP:Q', title='Carbon Emissions per GDP'),
            tooltip=[
                alt.Tooltip('Year:O', title='Year'),
                alt.Tooltip('Carbon Emissions per GDP:Q', title='Carbon Emissions per GDP', format='.2f')
            ]
        ).properties(
            title=f"Carbon Emissions per GDP for {selected_province} (2012-2022)",
            width=800,
            height=400
        )
        
        #renewable_2012 = plot_data.loc[plot_data['Year'] == 2012, 'Carbon Emissions per GDP'].values[0]

        #renewable_2022 = plot_data.loc[plot_data['Year'] == 2022, 'Carbon Emissions per GDP'].values[0]

        #changes_text_12to22 = f"{(renewable_2022 - renewable_2012):.2f}% percentage points increased"

        # Create the horizontal dashed line using a constant y-value for the 2012 renewable energy
        cepg_2012 = plot_data[plot_data['Year'] == 2012]['Carbon Emissions per GDP'].values[0]
        cepg_2022 = plot_data[plot_data['Year'] == 2022]['Carbon Emissions per GDP'].values[0]
        percentage_decrease = ((cepg_2012 - cepg_2022) / cepg_2012) * 100
        percentage_text = f"{percentage_decrease:.2f}% decreased"

        # Create a line chart for Carbon Emissions per GDP from 2012 to 2022
        carbon_per_gdp_chart = alt.Chart(plot_data).mark_line(point=True).encode(
            color=alt.value('#cc0000'),
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Carbon Emissions per GDP:Q', title='Carbon Emissions per GDP (kg)'),
            tooltip=[
                alt.Tooltip('Year:O', title='Year'),
                alt.Tooltip('Carbon Emissions per GDP:Q', title='Carbon Emissions per GDP (kg)', format=',.2f')
            ]
        )

        # Create the horizontal dashed line
        horizontal_cepg = alt.Chart(pd.DataFrame({
            'Year': plot_data['Year'], 
            'y': [cepg_2012]*len(plot_data)  
        })).mark_line(
            strokeDash=[4, 4],
            color='gray'
        ).encode(
            x='Year:O',
            y='y:Q'
        )

        # Create the vertical solid line
        vertical_cepg = alt.Chart(pd.DataFrame({
            'Year': [2022, 2022], 
            'y': [cepg_2012, cepg_2022]  
        })).mark_line(
            color='gray',
            strokeWidth=2
        ).encode(
            x=alt.X('Year:O'),
            y='y:Q'
        )

        # Add text annotation for the percentage decrease
        text_cepg = alt.Chart(pd.DataFrame({
            'Year': ['2012'],
            'y': [(cepg_2012 + cepg_2022) / 2],
            'text': [percentage_text]
        })).mark_text(
            align='right',
            baseline='middle',
            dx=760,
            color='gray'
        ).encode(
            x='Year:O',
            y='y:Q',
            text='text:N'
        )

        # Combine the bar chart with annotations
        cepg_chart_final = alt.layer(
            carbon_per_gdp_chart,  
            horizontal_cepg,           
            vertical_cepg,            
            text_cepg 
        ).properties(
            title='Carbon Emissions per GDP from 2012 to 2022',
            width=800,
            height=400
        )
        

        
        show_diff = input.show()
        if show_diff: 
            return cepg_chart_final
        else:
            return chart
        
    @render_altair   
    def renewable_plot2():

        ceg_2012 = annual_nation[annual_nation['Year'] == 2012]['Carbon Emissions per GDP'].values[0]
        ceg_2022 = annual_nation[annual_nation['Year'] == 2022]['Carbon Emissions per GDP'].values[0]
        percentage_decrease = ((ceg_2012 - ceg_2022) / ceg_2012) * 100
        percentage_text = f"{percentage_decrease:.2f}% decreased"

        carbon_per_gdp_chart1 = alt.Chart(annual_nation).mark_line(point=True).encode(
            color=alt.value('#cc0000'),
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Carbon Emissions per GDP:Q', title='Carbon Emissions per GDP (kg)'),
            tooltip=[
                alt.Tooltip('Year:O', title='Year'),
                alt.Tooltip('Carbon Emissions per GDP:Q', title='Carbon Emissions per GDP (kg)', format=',.2f')
            ]
        ).properties(
            title="Carbon Emissions per GDP (2012-2022)",
            width=800,
            height=400
        )
        # Create the horizontal dashed line
        horizontal_cepg1 = alt.Chart(pd.DataFrame({
            'Year': annual_nation['Year'], 
            'y': [ceg_2012]*len(annual_nation)  
        })).mark_line(
            strokeDash=[4, 4],
            color='gray'
        ).encode(
            x='Year:O',
            y='y:Q'
        )

        # Create the vertical solid line
        vertical_cepg1 = alt.Chart(pd.DataFrame({
            'Year': [2022, 2022], 
            'y': [ceg_2012, ceg_2022]  
        })).mark_line(
            color='gray',
            strokeWidth=2
        ).encode(
            x=alt.X('Year:O', title=None),
            y='y:Q'
        )

        # Add text annotation for the percentage decrease
        text_cepg1 = alt.Chart(pd.DataFrame({
            'Year': ['2012'],
            'y': [(ceg_2012 + ceg_2022) / 2],
            'text': [percentage_text]
        })).mark_text(
            align='right',
            baseline='middle',
            dx=760,
            color='gray'
        ).encode(
            x='Year:O',
            y='y:Q',
            text='text:N'
        )

        # Combine the bar chart with annotations
        cepg_chart_final1 = alt.layer(
            carbon_per_gdp_chart1,  
            horizontal_cepg1,           
            vertical_cepg1,            
            text_cepg1 
        ).properties(
            title='Nationwide Carbon Emissions per GDP from 2012 to 2022',
            width=800,
            height=400
        )
        show_diff = input.show()
        if show_diff: 
            return cepg_chart_final1
        else:
            return carbon_per_gdp_chart1
        
# Create App
app = App(app_ui, server)
