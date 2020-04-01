Python Tool showing a linear fit of logarithmic data of COVID-19 time series data from Johns Hopkins University:
==================================================================================================================================

* The data can be pulled from the GitHub COVID-19 data repository of Johns Hopkins University Center for Systems Science and Engineering (https://github.com/CSSEGISandData/COVID-19). This tool runs in Python command line and it calculates exponent b value to indicate the level of flattening of the curve: N=Ce^(bt) at different time periods, and population doubling time.  Different start and end times can be added to visualize the levels "flattening" of the Covid-19 cases during different time periods.

* Example Commands:

    `python covid19_linear_plot.py --province_state Quebec --url https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv --start_date Feb/29/2020 --end_date Mar/31/2020`

    Abbreviated command format:

    `covid19_linear_plot.py -p Quebec -u https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv -s Feb/29/2020 -e Mar/31/2020`

    For help/instructions:
    
    `python covid19_linear_plot.py -h`

* Start and End date parameters are optional.  If you do enter start and end dates, you must enter start and end dates that fall within the date range of the data, see the time series data at 
https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv
Start and end dates need to be entered in the format of month/day/year or month-day-year.

* Requirements: Python 3 (on Windows, Mac, or Linux) and Python libraries numpy, matplotlib and Pandas. This tool builds on the statistical calculations and plotting analysis of [Valeriu Predoi's Covid-19 Exponential Phase tool] (https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/README.md#Introduction). 

* Example plots of COVID-19 cases in Quebec based on different dates:

* March 1 - 24, 2020 shows exponent b value of 0.29 (a higher value shows sharper exponent curve) and population doubling time of 2.4. Fitted line of logarithmic data and Coefficient of determination (R-Squared) are also shown.

  (https://raw.githubusercontent.com/map-nerd-peter/covid19_linear_plot/master/example_plots/Quebec_March_1_24_2020.png)


* March 25 - 31, 2020 shows exponent b value of  0.19 (this value is lower than the March 1-24 b value so it indicate flattening curve of infection rates), and population doubling time is 3.7. These values show that mitigation efforts (e.g. locking down of communities, encouraging social distancing, etc.) are working to reduce exponential growth of infections.
  
  NOTE: The fitted line in this plot looks "steeper" than the March 1-24 fitted line because this plot has fewer data points. The exponent b value and population doubling time values are better indicators of curve flattening than the graphical reprsentation in this line.  
  
  (https://raw.githubusercontent.com/map-nerd-peter/covid19_linear_plot/master/example_plots/Quebec_March_25_30_2020.png)
