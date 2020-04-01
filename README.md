Python Tool showing a linear fit for logarithmic data of time series COVID-19 infection cases data from Johns Hopkins University:
==================================================================================================================================

1.  The data can be pulled from the GitHub COVID-19 data repository of Johns Hopkins University Center for Systems Science and Engineering (https://github.com/CSSEGISandData/COVID-19). This tool also calculates exponent b value to indicate the level of flattening of the curve: N=Ce^(bt) at different time periods, and population doubling time.  Different start and end times can be added to visualize the levels of the Covid-19 case curve flattening.

2.  Example Commands 

python covid19_linear_plot.py --province_state Quebec --url https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv
--start_date Feb/29/2020 --end_date Mar/31/2020

Abbreviated command format:

covid19_linear_plot.py -p Quebec -u https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv
-s Feb/29/2020 -e Mar/31/2020

For help instructions, run python covid19_linear_plot.py -h

3.  Start and End date parameters are optional.  If you do enter start and end dates, you must enter start and end dates that fall within the date range of the data, see the time series data at 
https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv
Start and end dates need to be entered in the format of month/day/year or month-day-year.

4.  Requirements: Python 3 (on Windows, Mac, or Linux) and Python libraries numpy, matplotlib and Pandas. 

Example plots of Quebec for dates:
Ack v



