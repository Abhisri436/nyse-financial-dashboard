import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

app = dash.Dash(__name__)

df = pd.read_csv("clean-data/nyse_clean_2015.csv")
df_prices = pd.read_csv("clean-data/prices_split_adjusted_clean_2015.csv")

# Metric options for Chart 1 dropdown
metric_options = [
    {'label': 'Net Income',       'value': 'Net Income'},
    {'label': 'Total Revenue',    'value': 'Total Revenue'},
    {'label': 'Gross Profit',     'value': 'Gross Profit'},
    {'label': 'Operating Income', 'value': 'Operating Income'},
]

ticker_options = [{'label': sym, 'value': sym} for sym in sorted(df_prices['symbol'].unique())]

numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
numerical_cols.remove('For Year')
numerical_cols.remove('CIK')

# Options for Chart 4 dropdowns
sector_options = [
    {'label': sector, 'value': sector}
    for sector in sorted(df['GICS Sector'].dropna().unique())
]

ranking_metric_options = [
    {'label': 'Net Income', 'value': 'Net Income'},
    {'label': 'Total Revenue', 'value': 'Total Revenue'},
    {'label': 'Gross Profit', 'value': 'Gross Profit'},
    {'label': 'Operating Income', 'value': 'Operating Income'},
    {'label': 'Profit Margin', 'value': 'Profit Margin'},
    {'label': 'Operating Margin', 'value': 'Operating Margin'},
    {'label': 'Gross Margin', 'value': 'Gross Margin'},
]

rank_order_options = [
    {'label': 'Top 10', 'value': 'top'},
    {'label': 'Bottom 10', 'value': 'bottom'},
]


# -------------------------------------------------------
# Layout
# -------------------------------------------------------
app.layout = html.Div(className='dashboard-wrapper', children=[

    html.H1("NYSE S&P 500 Financial Dashboard (2015)", className='dashboard-title'),

    html.Div(className='charts-grid', children=[

        # -------------------------------------------------------
        # CHART 1 - Sector Profitability
        # -------------------------------------------------------
        html.Div(className='chart-card', children=[
            html.H2("Sector Profitability Overview"),
            html.P("Select a financial metric to compare average performance across S&P 500 sectors."),
            dcc.Dropdown(
                id='chart1-dropdown',
                options=metric_options,
                value='Net Income',
                style={'width': '300px', 'marginBottom': '10px'}
            ),
            dcc.Graph(id='chart1-graph'),
        ]),

        # -------------------------------------------------------
        # CHART 2 - Stock Price & Volume
        # -------------------------------------------------------
        html.Div(className='chart-card', children=[
            html.H2("Stock Price & Volume Trend (2015)"),
            html.P(
                "Select a ticker to view its daily closing price alongside trading volume. "
                "Volume spikes often signal key market events — use this to spot momentum "
                "shifts and regime changes at a glance."
            ),
            dcc.Dropdown(
                id='chart2-dropdown',
                options=ticker_options,
                value='AAPL',
                style={'width': '300px', 'marginBottom': '10px'}
            ),
            dcc.Graph(id='chart2-graph'),
        ]),

        # -------------------------------------------------------
        # CHART 3 - Scatter Plot
        # -------------------------------------------------------
        html.Div(className='chart-card', children=[
            html.H2("Stock Metric Relationships (2015)"),
            html.P("Select any two features to view their relationship with each other across all countries."),
            dcc.Dropdown(
                id='chart3-dropdown-x',
                options=[{'label': col, 'value': col} for col in numerical_cols],
                value='Total Revenue',
                style={'width': '300px', 'marginBottom': '10px'}
            ),
            dcc.Dropdown(
                id='chart3-dropdown-y',
                options=[{'label': col, 'value': col} for col in numerical_cols],
                value='Net Income',
                style={'width': '300px', 'marginBottom': '10px'}
            ),
            dcc.Graph(id='chart3-graph'),
        ]),

        # -------------------------------------------------------
        # CHART 4 - Company Ranking
        # -------------------------------------------------------
        html.Div(className='chart-card', children=[
            html.H2("Company Ranking Within Selected Sector (2015)"),
            html.P(
                "Select a sector and metric to rank companies within that sector. "
                "This helps compare which companies lead or lag on key financial measures."
            ),
            html.Div([
                dcc.Dropdown(
                    id='chart4-sector-dropdown',
                    options=sector_options,
                    value=sorted(df['GICS Sector'].dropna().unique())[0],
                    style={'width': '300px', 'marginRight': '15px'}
                ),
                dcc.Dropdown(
                    id='chart4-metric-dropdown',
                    options=ranking_metric_options,
                    value='Net Income',
                    style={'width': '300px', 'marginRight': '15px'}
                ),
                dcc.RadioItems(
                    id='chart4-rank-order',
                    options=rank_order_options,
                    value='top',
                    inline=True,
                    style={'marginTop': '10px'}
                ),
            ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px', 'marginBottom': '15px'}),
            dcc.Graph(id='chart4-graph'),
        ]),

    ]),
])

# -------------------------------------------------------
# CHART 1 Callback
# -------------------------------------------------------
@app.callback(
    Output(component_id='chart1-graph', component_property='figure'),
    Input(component_id='chart1-dropdown', component_property='value'),
)
def update_chart1(selected_metric):
    sector_avg = df.groupby('GICS Sector')[selected_metric].mean().reset_index()
    sector_avg = sector_avg.sort_values(selected_metric, ascending=False)

    median_val = sector_avg[selected_metric].median()
    sector_avg['above_median'] = sector_avg[selected_metric] >= median_val

    fig = px.bar(
        sector_avg,
        x='GICS Sector',
        y=selected_metric,
        color='above_median',
        color_discrete_map={True: '#2563EB', False: '#93c5fd'},
        title=f"Average {selected_metric} by Sector (2015)",
        labels={'GICS Sector': 'Sector', selected_metric: f'Avg {selected_metric} (USD)', 'above_median': 'Above Median'},
        template='simple_white',
    )
    fig.update_layout(
        xaxis_tickangle=-30,
        legend_title_text='Above Median',
    )
    return fig

# -------------------------------------------------------
# CHART 2 Callback 
# -------------------------------------------------------
@app.callback(
    Output('chart2-graph', 'figure'),
    Input('chart2-dropdown', 'value'),
)
def update_chart2(selected_symbol):
    #filter the df for the selected tickers and ensure they are in order
    stock = df_prices[df_prices['symbol'] == selected_symbol].sort_values('date')
 
    #ploty subplot
    #dual-axis subplot: price on top, volume on bottom
    fig = make_subplots(
        rows=2, cols=1,
        #syncs zooming for both graphs
        shared_xaxes=True,
        #equal height for both price and volume
        row_heights=[0.5, 0.5],
        #reduce gap
        vertical_spacing=0.05,
    )
 
    #high-low trading range -- "cloud" in trading terms
    #first trace -- top boundary
    fig.add_trace(
        go.Scatter(
            x=stock['date'],
            y=stock['high'],
            mode='lines',
            #invisible line
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip',
        ),
        row=1, col=1
    )
    #second trace -- bottom boundary
    #filled to the 'next y' --> top boundary
    fig.add_trace(
        go.Scatter(
            x=stock['date'],
            y=stock['low'],
            mode='lines',
            line=dict(width=0),
            #create shaded area
            fill='tonexty',
            #color is light blue
            fillcolor='rgba(99, 162, 222, 0.2)',
            name='High–Low Range',
            hoverinfo='skip',
        ),
        row=1, col=1
    )
    #price chart should show the closing price line
    fig.add_trace(
        go.Scatter(
            x=stock['date'],
            y=stock['close'],
            mode='lines',
            line=dict(color='#2563EB', width=2),
            name='Close Price',
            #show the price on hover
            hovertemplate='%{x|%b %d}<br>Close: $%{y:.2f}<extra></extra>',
        ),
        row=1, col=1
    )
 
    #volume bars
    #green when price closed higher than opened
    #red for lower than opened
    colors = [
        '#16a34a' if c >= o else '#dc2626'
        for c, o in zip(stock['close'], stock['open'])
    ]
    #candlestick chart
    fig.add_trace(
        go.Bar(
            x=stock['date'],
            y=stock['volume'],
            marker_color=colors,
            name='Volume',
            #same hover logic
            hovertemplate='%{x|%b %d}<br>Volume: %{y:,.0f}<extra></extra>',
            opacity=0.75,
        ),
        row=2, col=1
    )
    
    #global adjustment
    fig.update_layout(
        title=f"{selected_symbol} — Daily Close Price & Volume (2015)",
        template='simple_white',
        #all data for a specific date
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=60, r=20, t=60, b=40),
        height=520,
    )
    #label axes
    fig.update_yaxes(title_text='Price (USD)', row=1, col=1)
    fig.update_yaxes(title_text='Volume', row=2, col=1)
    fig.update_xaxes(title_text='Date', row=2, col=1)
 
    return fig

# -------------------------------------------------------
# CHART 3 Callback 
# -------------------------------------------------------
@app.callback(
    Output('chart3-graph', 'figure'),
    [Input('chart3-dropdown-x', 'value'),
     Input('chart3-dropdown-y', 'value')]
)
def update_chart3(selected_x, selected_y):
    fig = px.scatter(
        df,
        x=selected_x,
        y=selected_y,
        color='Country',
        opacity=0.5,
        title=f"{selected_x} vs. {selected_y}",
        template='simple_white'
    )
    return fig

# -------------------------------------------------------
# CHART 4 Callback 
# -------------------------------------------------------
@app.callback(
    Output('chart4-graph', 'figure'),
    [
        Input('chart4-sector-dropdown', 'value'),
        Input('chart4-metric-dropdown', 'value'),
        Input('chart4-rank-order', 'value')
    ]
)
def update_chart4(selected_sector, selected_metric, rank_order):
    # Filter to the selected sector
    filtered_df = df[df['GICS Sector'] == selected_sector].copy()

    # Keep only rows with valid values for the chosen metric and company name
    filtered_df = filtered_df.dropna(subset=[selected_metric, 'Security'])

    # Sort and select top or bottom 10
    if rank_order == 'top':
        ranked_df = filtered_df.sort_values(selected_metric, ascending=False).head(10)
        chart_title = f"Top 10 Companies in {selected_sector} by {selected_metric} (2015)"
    else:
        ranked_df = filtered_df.sort_values(selected_metric, ascending=True).head(10)
        ranked_df = ranked_df.iloc[::-1]
        chart_title = f"Bottom 10 Companies in {selected_sector} by {selected_metric} (2015)"


    median_val = ranked_df[selected_metric].median()
    ranked_df['above_median'] = ranked_df[selected_metric] >= median_val

    fig = px.bar(
        ranked_df,
        x=selected_metric,
        y='Security',
        orientation='h',
        color='above_median',
        color_discrete_map={True: '#2563EB', False: '#93c5fd'},
        title=chart_title,
        template='simple_white',
        labels={
            selected_metric: selected_metric,
            'Security': 'Company',
            'above_median': 'Above Median'
        }
    )

    fig.update_layout(
        legend_title_text='Above Median',
        margin=dict(l=80, r=20, t=60, b=40),
        height=550
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True)
