# Import required libraries
import pandas as pd
import dash
import app
from dash import Dash, dcc, html, Input, Output
from dash.dependencies import State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update

# Create a Dash app
app = dash.Dash(__name__)

# Read the dataset into a Pandas DataFrame
URL = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/Canada.xlsx'
df_can = pd.read_excel(URL, sheet_name='Canada by Citizenship', skiprows=range(20), skipfooter=2)
df_can.drop(['AREA', 'REG', 'DEV', 'Type', 'Coverage'], axis=1, inplace=True)
df_can.rename(columns={'OdName': 'Country', 'AreaName': 'Continent', 'RegName': 'Region'}, inplace=True)
df_can.columns = list(map(str, df_can.columns))
df_can['Total'] = df_can.iloc[:, 4:-1].sum(axis=1)

# Define the layout of your app
app.layout = html.Div(
    children=[
        html.H1("Canadian Immigration Dashboard",style={'textAlign': 'center', 'color': '#503D36', 'font-size': '24px'}),
        html.Div(
            children=[
                html.Label("Select a country:"),
                dcc.Dropdown(
                    id='dropdown-country',
                    options=[
                        {'label': country, 'value': country} for country in df_can['Country'].unique()
                    ],
                    value=df_can['Country'].unique()[0]
                )
            ],
            style={'width': '30%', 'display': 'inline-block'}
        ),
        dcc.Graph(id='graph-immigration'),
        html.Div(
            children=[
                html.Label("Select a year for the pie chart:"),
                dcc.Dropdown(
                    id='dropdown-pie-chart',
                    options=[
                        {'label': year, 'value': year} for year in df_can.columns[4:-1]
                    ],
                    value=df_can.columns[4]
                )
            ],
            style={'width': '30%', 'display': 'inline-block', 'margin-top': '20px'}
        ),
        dcc.Graph(id='graph-continent')
    ]
)

# Define the callback function for the country graph
@app.callback(
    Output('graph-immigration', 'figure'),
    [Input('dropdown-country', 'value')]
)
def update_graph(selected_country):
    filtered_data = df_can[df_can['Country'] == selected_country]
    years = df_can.columns[4:-1]  # Extract the years from the column names
    immigration_data = filtered_data[years].values.tolist()
    
    fig = go.Figure()
    for i, year in enumerate(years):
        fig.add_trace(go.Bar(
            x=[year],
            y=[immigration_data[0][i]],
            text=[immigration_data[0][i]],
            textposition='auto',
            name=str(year)
        ))
    
    fig.update_layout(
        title=f'Immigration from {selected_country} to Canada (1980-2013)',
        xaxis=dict(title='Year'),
        yaxis=dict(title='Number of Immigrants'),
    )
    
    return fig

# Define the callback function for the continent graph
@app.callback(
    Output('graph-continent', 'figure'),
    [Input('dropdown-pie-chart', 'value')]
)
def update_pie_chart(selected_year):
    continent_data = df_can.groupby('Continent')[selected_year].sum().reset_index()
    fig = px.pie(
        continent_data,
        values=selected_year,
        names='Continent',
        title=f'Immigration to Canada by Continent ({selected_year})'
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
