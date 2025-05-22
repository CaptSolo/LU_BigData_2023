import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go

app = dash.Dash(__name__)
server = app.server

# Constants
DATE_COLUMN = 'date/time'
DATA_URL = 'https://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz'

def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    data.columns = [str(x).lower() for x in data.columns]
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

# Load data
DATA = load_data(10000)

app.layout = html.Div([
    html.H1("Uber pickups in NYC"),

    dcc.Checklist(
        id='show-data-checklist',
        options=[{'label': 'Show raw data', 'value': 'SHOW'}],
        value=[]
    ),

    html.Div(id='data-table'),

    html.H2("Number of pickups by hour"),
    dcc.Graph(id='bar-chart'),

    html.Label("Filter by hour:"),
    dcc.Slider(
        id='hour-slider',
        min=0,
        max=23,
        step=1,
        value=0,
        marks={i: str(i) for i in range(24)}
    ),
    dcc.Graph(id='map-graph')
])

@app.callback(
    Output('data-table', 'children'),
    Input('show-data-checklist', 'value')
)
def update_table(show_data):
    if 'SHOW' in show_data:
        return html.Div([
            html.H4("Raw data"),
            dash_table.DataTable(
                data=DATA.to_dict('records'),
                columns=[{"name": i, "id": i} for i in DATA.columns],
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'}
            )
        ])
    return ""

@app.callback(
    Output('bar-chart', 'figure'),
    Input('show-data-checklist', 'value')
)
def update_bar_chart(_):
    hist_values = np.histogram(DATA[DATE_COLUMN].dt.hour, bins=24, range=(0, 24))[0]
    fig = go.Figure(data=[go.Bar(x=list(range(24)), y=hist_values)])
    fig.update_layout(xaxis_title='Hour', yaxis_title='Pickups')
    return fig

@app.callback(
    Output('map-graph', 'figure'),
    Input('hour-slider', 'value')
)
def update_map(selected_hour):
    filtered_data = DATA[DATA[DATE_COLUMN].dt.hour == selected_hour]
    fig = px.scatter_map(
        filtered_data,
        lat="lat", lon="lon",
        hover_data=[DATE_COLUMN],
        zoom=10,
        height=500
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

if __name__ == '__main__':
    app.run(debug=True)

