from shiny import App, render, ui
import pandas as pd
import altair as alt

rec_path = 'renewable_energy_china.csv'
rec_data = pd.read_csv(rec_path)

# Filter data for years from 2012 to 2022
filtered_12to22 = rec_data[(rec_data['Year'] >= 2012) & (rec_data['Year'] <= 2022)]

# Calculate renewable energy for each province
province_12to22 = filtered_12to22.groupby(['Province', 'Year']).agg({
    'Electricity production (billion kilowatt-hours)': 'sum',
    'Hydropower (billion kilowatt-hours)': 'sum',
    'Thermal power generation (billion kilowatt-hours)': 'sum'
}).reset_index()

province_12to22['Hydro (%)'] = (
    province_12to22['Hydropower (billion kilowatt-hours)'] / 
    province_12to22['Electricity production (billion kilowatt-hours)']
)
province_12to22['Thermal (%)'] = (
    province_12to22['Thermal power generation (billion kilowatt-hours)'] / 
    province_12to22['Electricity production (billion kilowatt-hours)']
)
province_12to22['Renewable energy (%)'] = (
    (1 - province_12to22['Hydro (%)'] - province_12to22['Thermal (%)']) * 100
)

# Calculate nationwide renewable energy
national_12to22 = filtered_12to22.groupby('Year').agg({
    'Electricity production (billion kilowatt-hours)': 'sum',
    'Hydropower (billion kilowatt-hours)': 'sum',
    'Thermal power generation (billion kilowatt-hours)': 'sum'
}).reset_index()

national_12to22['Hydro (%)'] = (
    national_12to22['Hydropower (billion kilowatt-hours)'] / 
    national_12to22['Electricity production (billion kilowatt-hours)']
)
national_12to22['Thermal (%)'] = (
    national_12to22['Thermal power generation (billion kilowatt-hours)'] / 
    national_12to22['Electricity production (billion kilowatt-hours)']
)
national_12to22['Renewable energy (%)'] = (
    (1 - national_12to22['Hydro (%)'] - national_12to22['Thermal (%)']) * 100
)
national_12to22['Province'] = 'Nationwide'

# Combine nationwide and provincial data
combined_data = pd.concat([province_12to22, national_12to22], ignore_index=True)
# Define UI
app_ui = ui.page_fluid(
    ui.h2("Renewable Energy (%) from 2012 to 2022"),
    ui.input_select(
        id="province_select", 
        label="Select Province", 
        choices=["Nationwide"] + sorted(combined_data['Province'].unique())
    ),
    ui.output_plot("renewable_plot")
)

# Define Server Logic
def server(input, output, session):
    @output
    @render.plot
    def renewable_plot():
        # Get the selected province
        selected_province = input.province_select()

        # Filter data for the selected province
        if selected_province == "Nationwide":
            plot_data = national_12to22  # Use nationwide data
        else:
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
        return chart

# Create App
app = App(app_ui, server)
