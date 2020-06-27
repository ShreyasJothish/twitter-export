import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import timedelta, datetime
import pandas as pd
import plotly.graph_objects as go
from timeloop import Timeloop


from twitter import trigger_follower_processing, get_total_follower_count
from db import get_all_records, get_high_value_followers


tl = Timeloop()


@tl.job(interval=timedelta(minutes=60))  # to be updated to days=1
def start_follower_processing():
    trigger_follower_processing()


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

export_options = ["Export high value followers",
                  "Export all fetched followers",
                  "Export all DM status",
                  "Export all skipped followers"]

app.layout = html.Div(
    html.Div([
        html.H4('Twitter Exporter Dash Board'),
        html.Div(id='live-update-text'),
        dcc.Dropdown(
            id='export-options',
            options=[{'label': i, 'value': i} for i in export_options],
            # value=export_options[0]
        ),
        html.Div(id='export-options-output'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=60*1000,  # in milliseconds # to be updated to 30 mins
            n_intervals=0
        )
    ]
    ),
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


@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    follower_df = get_all_records("follower")
    dm_status_df = get_all_records("dm_status")

    follower_df['created_at'] = pd.to_datetime(follower_df['created_at'])
    today = datetime.now()
    follower_df['years_on_twitter'] = \
        follower_df['created_at'].apply(lambda x: today.year - x.year)

    dm_status_aggr = dm_status_df.groupby('id')['timestamp'].count().reset_index()
    dm_status_aggr.columns = ['id', 'dm_count']
    dm_status_aggr['dm_count'] = \
        dm_status_aggr['dm_count'].apply(lambda x: "DM count: " + str(x))

    # merge dm status aggregation with follower table
    follower_df = follower_df.merge(dm_status_aggr, on='id', how='left')
    follower_df['dm_count'] = follower_df['dm_count'].fillna("DM count: 0")

    verified_follower_df = follower_df[follower_df['verified'] == 1]
    unverified_follower_df = follower_df[follower_df['verified'] == 0]

    fig = go.Figure()

    fig.add_trace(
        go.Scattergl(
            x=verified_follower_df['followers_count'],
            y=verified_follower_df['friends_count'],
            text=verified_follower_df['name'] + "<br>" + verified_follower_df['dm_count'],
            mode='markers',
            marker=dict(
                size=verified_follower_df['years_on_twitter'] * 2,
                colorscale='Viridis',
                line_width=1,
            ),
            name='Verified'
        )
    )

    fig.add_trace(
        go.Scattergl(
            x=unverified_follower_df['followers_count'],
            y=unverified_follower_df['friends_count'],
            text=unverified_follower_df['name'] + "<br>" + unverified_follower_df['dm_count'],
            mode='markers',
            marker=dict(
                size=unverified_follower_df['years_on_twitter'] * 2,
                colorscale='Viridis',
                line_width=1,
            ),
            name='Unverified'
        )
    )

    fig.update_layout(title='Followers vs. Friends of specific Follower',
                      autosize=True,
                      xaxis=dict(
                          title='Followers',
                          gridcolor='white',
                          type='log',
                          gridwidth=2,
                      ),
                      yaxis=dict(
                          title='Friends',
                          gridcolor='white',
                          type='log',
                          gridwidth=2,
                      ),
                      paper_bgcolor='rgb(243, 243, 243)',
                      plot_bgcolor='rgb(243, 243, 243)')

    return fig


@app.callback(
    Output('export-options-output', component_property='children'),
    [Input('export-options', 'value')])
def export_data(export_option):
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Export high value followers
    if export_option == export_options[0]:
        high_value_followers = get_high_value_followers()
        high_value_followers.to_csv(f"high_value_followers_{current_time}.csv", index=False)

        return f"High value followers data exported as high_value_followers_{current_time}.csv"

    # Export all fetched followers
    elif export_option == export_options[1]:
        follower_df = get_all_records("follower")
        follower_df.to_csv(f"followers_{current_time}.csv", index=False)

        return f"Followers data exported as followers_{current_time}.csv"

    # Export all DM status
    elif export_option == export_options[2]:
        dm_status_df = get_all_records("dm_status")
        dm_status_df.to_csv(f"dm_status_{current_time}.csv", index=False)

        return f"DM status data exported as dm_status_{current_time}.csv"

    #  Export all skipped followers
    elif export_option == export_options[3]:
        skip_user_df = get_all_records("skip_user")
        skip_user_df.to_csv(f"skip_followers_{current_time}.csv", index=False)

        return f"Skipped followers data exported as skip_followers_{current_time}.csv"


if __name__ == '__main__':
    trigger_follower_processing()
    tl.start()
    try:
        print(f"Started twitter-export application.")
        app.run_server()
    except KeyboardInterrupt:
        print("Exiting the application.")
        tl.stop()
