import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

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
    # -------------------------------------------------------


    # -------------------------------------------------------
    # CHART 3 
    # -------------------------------------------------------


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


# -------------------------------------------------------
# CHART 3 Callback 
# -------------------------------------------------------


# -------------------------------------------------------
# CHART 4 Callback 
# -------------------------------------------------------


if __name__ == '__main__':
    app.run(debug=True)
