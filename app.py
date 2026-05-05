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

# -------------------------------------------------------
# Layout
# -------------------------------------------------------
app.layout = html.Div(children=[

    html.H1("NYSE S&P 500 Financial Dashboard (2015)",
            style={'textAlign': 'center', 'marginBottom': '30px'}),

    # -------------------------------------------------------
    # CHART 1 - Sector Profitability
    # Question: Which sectors generate the most profit/revenue?
    # -------------------------------------------------------
    html.Div(children=[
        html.H2("Sector Profitability Overview"),
        html.P("Select a financial metric to compare average performance across S&P 500 sectors."),

        dcc.Dropdown(
            id='chart1-dropdown',
            options=metric_options,
            value='Net Income',
            style={'width': '300px', 'marginBottom': '10px'}
        ),

        dcc.Graph(id='chart1-graph'),
    ], style={'marginBottom': '50px'}),

    # -------------------------------------------------------
    # CHART 2 
    # Question: How did a stock's price and trading volume move together throughout 2015?
    # -------------------------------------------------------
    
    html.Div(children=[
        html.H2("Stock Price & Volume Trend (2015)"),
        html.P(
            "Select a ticker to view its daily closing price alongside trading volume. "
            "Volume spikes often signal key market events — use this to spot momentum "
            "shifts and regime changes at a glance."
        ),

        #dropdown to filter which stock to select from all the stock options
        dcc.Dropdown(
            id='chart2-dropdown',
            #gets the unique stocks, declared at the top
            options=ticker_options,
            #defaulted to AAPL
            value='AAPL',
            style={'width': '300px', 'marginBottom': '10px'}
        ),
        #graph component to be updated
        dcc.Graph(id='chart2-graph'),
    ], style={'marginBottom': '50px'}),

    # -------------------------------------------------------
    # CHART 3 
    # -------------------------------------------------------

    html.Div(children=[
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
    ], style={'marginBottom': '50px'}),

    # -------------------------------------------------------
    # CHART 4
    # -------------------------------------------------------

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

    fig = px.bar(
        sector_avg,
        x='GICS Sector',
        y=selected_metric,
        title=f"Average {selected_metric} by Sector (2015)",
        labels={'GICS Sector': 'Sector', selected_metric: f'Avg {selected_metric} (USD)'},
        template='simple_white',
        color='GICS Sector',
    )
    fig.update_layout(
        xaxis_tickangle=-30,
        showlegend=False,
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
        title=f"{selected_x} vs. {selected_y}",
        template='simple_white'
    )
    return fig

# -------------------------------------------------------
# CHART 4 Callback 
# -------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)
