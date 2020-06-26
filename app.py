import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
from datetime import timedelta, datetime
import pandas as pd
import plotly.express as px
from timeloop import Timeloop
import plotly

from twitter import trigger_follower_processing, get_total_follower_count
from db import get_all_records


tl = Timeloop()


@tl.job(interval=timedelta(minutes=60))  # to be updated to days=1
def start_follower_processing():
    trigger_follower_processing()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('Twitter Export Dash Board'),
        html.Div(id='live-update-text'),
        # dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=60*1000,  # in milliseconds # to be updated to 30 mins
            n_intervals=0
        )
    ])
)


@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    follower_df = get_all_records("follower")
    dm_status_df = get_all_records("dm_status")
    skip_user_df = get_all_records("skip_user")

    total_follower_count = get_total_follower_count()
    fetch_follower_count = follower_df.shape[0]
    dm_count = dm_status_df.shape[0]
    unique_dm_count = dm_status_df.drop_duplicates('id').shape[0]
    skip_user_count = skip_user_df.shape[0]

    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Span(f'Overall Followers: {total_follower_count}', style=style),
        html.Span(f'Fetched Followers: {fetch_follower_count}', style=style),
        html.Span(f'Skipped Followers: {skip_user_count}', style=style),
        html.Span(f'DM Sent: {unique_dm_count}', style=style),
        html.Span(f'Retry DM Sent: {dm_count - unique_dm_count}', style=style),
    ]


if __name__ == '__main__':
    trigger_follower_processing()
    tl.start()
    try:
        print(f"Started twitter-export application.")
        app.run_server()
    except KeyboardInterrupt:
        print("Exiting the application.")
        tl.stop()
