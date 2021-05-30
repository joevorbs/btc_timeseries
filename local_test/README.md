## Multivariate Timeseries Forecasting on BTC Price
This repo focuses on a machine-learning approach to timeseries forecasting. This differs from the traditional univariate method as this method allows for multiple features. Using a multivariate approach can also help explain causality and give strong insights into the actual forecast. That is, as long as your data is good! 

A few different methods are included (cross-correlation, univariate) to develop forecasts on the price of bitcoin. This is also a way to experiment with Facebook's Prophet timeseries library. Prophet can develop strong univariate forecasts as well as pre-whiten the data for the multivariate approach.

Forecasts will be plotted and stored in the Visualizations folder.

Datasources: 
  1) blockchain.com - Blockchain metrics
  2) coindesk.com - Bitcoin Price (Historical - To Date)
