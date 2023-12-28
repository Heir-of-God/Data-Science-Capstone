# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

def get_booster_version(booster):
    return booster.split(" ")[1]

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
spacex_df.loc[:, "Booster Version"] = spacex_df["Booster Version"].transform(get_booster_version)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown', value="ALL",
                                             options=[{"label":"All Sites", "value":"ALL"},{"label":"CCAFS LC-40", "value":"CCAFS LC-40"},
                                             {"label":"VAFB SLC-4E", "value":"VAFB SLC-4E"},{"label":"KSC LC-39A", "value":"KSC LC-39A"},
                                             {"label":"CCAFS SLC-40", "value":"CCAFS SLC-40"}],
                                             style={"textAlign":"center"},
                                             placeholder="Select a Launch Site here",
                                             searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(min=min_payload, max=max_payload, step=1000, value=[min_payload, max_payload], id='payload-slider'),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

def is_success(val):
    match val:
        case 0: return "Failure"
        case 1: return "Success"

@app.callback(Output(component_id='success-pie-chart', component_property='figure'), Input(component_id='site-dropdown', component_property='value'))
def get_success_pie(selected_option):
    if selected_option == "ALL":
        data = spacex_df.copy()
        figure = px.pie(data, values="class", names="Launch Site", title="Success launches for all sites")
        return figure
    else:
        data = spacex_df[spacex_df["Launch Site"] == selected_option]
        data.loc[:, "class"] = data["class"].transform(is_success)
        figure = px.pie(data, names="class", title=f"Launches result for {selected_option} launch site")

        return figure
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id="success-payload-scatter-chart", component_property="figure"), Input(component_id='site-dropdown', component_property='value'),
              Input(component_id="payload-slider", component_property="value"))
def do_scatter(selected_site, payload_mass):
    payload_mass = sorted(payload_mass)
    data = spacex_df[spacex_df["Payload Mass (kg)"].between(payload_mass[0], payload_mass[1], inclusive="both")]

    if selected_site == "ALL":
        figure = px.scatter(data, x="Payload Mass (kg)", y="class", color="Booster Version", title="Correlation between Payload and Success for all sites")
        return figure

    else:
        data = data[data["Launch Site"] == selected_site]
        figure = px.scatter(data, x="Payload Mass (kg)", y="class", color="Booster Version", title=f"Correlation between Payload and Success for {selected_site} launch site")
        return figure


# Run the app
if __name__ == '__main__':
    app.run_server()
