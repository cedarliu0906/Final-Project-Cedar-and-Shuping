from shiny import App, reactive, render, ui
import pandas as pd 
import pandas as pd
import altair as alt 
import pandas as pd
from datetime import date
import numpy as np
from shinywidgets import render_altair, output_widget
import os


file_path = "../../combined_data.csv"

# Load the CSV file
combined_data = pd.read_csv(file_path)
# Define UI
app_ui = ui.page_fluid(
    ui.h2("Renewable Energy (%) from 2012 to 2022"),
    ui.input_select(
        id="province_select", 
        label="Select Province", 
        choices=["Nationwide"] + sorted(combined_data['Province'].unique())
    ),
    ui.input_checkbox("show", "Show Changes", True),

    output_widget("renewable_plot")
)

# Define Server Logic
def server(input, output, session):
    @output
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
            y=alt.Y('Renewable energy (%):Q', title='Renewable Energy (%)'),
            tooltip=[
                alt.Tooltip('Year:O', title='Year'),
                alt.Tooltip('Renewable energy (%):Q', title='Renewable Energy (%)', format='.2f')
            ]
        ).properties(
            title=f"Renewable Energy (%) for {selected_province} (2012-2022)",
            width=800,
            height=400
        )
        
        line_rec_12to22 = alt.Chart(plot_data).mark_line(point=True).encode(
            color=alt.value('#238b45'),
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Renewable energy (%):Q', title='Renewable Energy (%)', axis=alt.Axis(format='')),
            tooltip=[
                alt.Tooltip('Year:O', title='Year'),
                alt.Tooltip('Renewable energy (%):Q', title='Renewable Energy (%)', format='')
            ]
        )
        renewable_2012 = plot_data.loc[plot_data['Year'] == 2012, 'Renewable energy (%)'].values[0]

        renewable_2022 = plot_data.loc[plot_data['Year'] == 2022, 'Renewable energy (%)'].values[0]

        changes_text_12to22 = f"{(renewable_2022 - renewable_2012):.2f}% percentage points increased"

        # Create the horizontal dashed line using a constant y-value for the 2012 renewable energy
        horizontal_line_12 = alt.Chart(pd.DataFrame({
            'Year': plot_data['Year'],
            'y': [renewable_2012] * len(plot_data)  
        })).mark_line(
            strokeDash=[4, 4],
            color='gray'
        ).encode(
            x='Year:O',
            y='y:Q'
        )

        # Create the vertical line explicitly tied to the 2022 data point
        vertical_under_22 = alt.Chart(pd.DataFrame({
            'Year': [2022, 2022],  
            'y': [renewable_2012, renewable_2022]  
        })).mark_line( 
            color='gray',
            strokeWidth=2
        ).encode(
            x=alt.X('Year:O'),  
            y='y:Q' 
        )


        vertical_text_22 = alt.Chart(pd.DataFrame({
            'x': ['2022'],
            'y': [(renewable_2012 + renewable_2022) / 2],
            'text': [changes_text_12to22]
        })).mark_text(align='right', baseline='middle', dx=760, color='gray').encode(
            x='x:N',
            y='y:Q',
            text='text:N'
        )

        line_rec_12to22_final = alt.layer(
            vertical_under_22,
            line_rec_12to22,
            horizontal_line_12, 
            vertical_text_22
        ).properties(
            title='Renewable Energy (%) from 2012 to 2022', 
            width=800,
            height=400
        ).configure_axis(
            grid=True  
        ).configure_axisY(
            format='',  
            title='Renewable Energy (%)'  
        )
        show_diff = input.show()
        if show_diff: 
            return line_rec_12to22_final
        else:
            return chart
        

# Create App
app = App(app_ui, server)
