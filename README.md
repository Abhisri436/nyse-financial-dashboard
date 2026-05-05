# nyse-financial-dashboard

A Dash web app for exploring company fundamentals, sector comparisons, and stock trends in the New York Stock Exchange dataset.

## Group Members
- Potri Abhisri Barama
- Saanvi Elaty
- Lohitha Kalepu
- Nahreg Rastguelenian

## Project Overview
This dashboard analyzes financial and stock market data from the New York Stock Exchange dataset. It combines company fundamentals, sector classifications, and stock price trends to help users explore financial performance, compare sectors, and examine company-level patterns in 2015.

## Charts
### 1. Sector Profitability Overview
This chart compares the average value of a selected financial metric across sectors. Users can switch between metrics such as Net Income, Total Revenue, Gross Profit, and Operating Income to see which sectors perform better on average.

### 2. Stock Price & Volume Trend
This chart shows the daily closing price and trading volume for a selected stock in 2015. It helps users identify changes in price movement, volatility, and volume spikes over time.

### 3. Stock Metric Relationships
This scatterplot allows users to compare any two numerical financial variables from the dataset. It helps reveal relationships, clusters, and outliers across companies.

### 4. Company Ranking Within Selected Sector
This chart ranks companies within a selected sector based on a chosen financial metric. Users can view either the top 10 or bottom 10 companies, making it easier to compare leaders and lagging companies within the same industry group.

## Dataset
The dashboard primarily uses a cleaned dataset created by merging company fundamentals with sector and company information. It also uses cleaned split-adjusted stock price data for time-series analysis.

## Tools Used
- Python
- Dash
- Plotly
- Pandas