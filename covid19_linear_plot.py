import numpy as np
import matplotlib.pyplot as plt
import argparse
import datetime
from dateutil.parser import parse
import pandas as pd
import platform
"""

COVID-19 (Coronavirus) Linear Plot Tool With Start and End Dates to Analyze Curve Flattening

Written by Peter C. (https://github.com/map-nerd-peter/covid19_linear_plot)

Special thanks to Valeriu Predoi for sharing statistical calculations and plotting analysis code 
in his Covid-19 Exponential Phase tool - https://github.com/valeriupredoi/COVID-19_LINEAR/.

"""
class Covid19Data:

    def __init__(self, location, url, province_state_selected):
        """Constructor"""

        self._location = location
        self._url = url

        #Load the row that contains for specific state or province and its COVID-19 data
        df = pd.read_csv(url, error_bad_lines=False)

        if province_state_selected:
            self._csv_row_data = df[df['Province/State'] == location]

        #Get country data
        elif not province_state_selected:
            self._csv_row_data = df[df['Country/Region'] == location].groupby('Country/Region').sum()

    @property
    def location(self):
        return self._location

    @property
    def url(self):
        return self._url

    @property 
    def csv_row_data(self):
       return self._csv_row_data

    # Calculate Coefficient of Determination / r-squared. This function is based on Valeriu Predoi's code https://github.com/valeriupredoi/COVID-19_LINEAR
    def coeff_determination(self, ys_orig, ys_line):
        """Compute the line R squared."""
        y_mean_line = [np.mean(ys_orig) for y in ys_orig]
        squared_error_regr = sum((ys_line - ys_orig) * (ys_line - ys_orig))
        squared_error_y_mean = sum((y_mean_line - ys_orig) * \
                                   (y_mean_line - ys_orig))
        return 1 - (squared_error_regr / squared_error_y_mean)

    def set_start_end_dates(self, start, end):
        start_date = None
        end_date = None

        start_end_indices = None
        
        #Allow date in format of mm/dd/YYYY or mm/dd/yy feb/29/20 or feb/29/2020 etc.
        formats=['%m/%d/%Y', '%m/%d/%y', '%b/%d/%y', '%b/%d/%Y', '%B/%d/%Y', '%m-%d-%Y', '%m-%d-%y', '%b-%d-%y', '%b-%d-%Y', '%B-%d-%Y']
        for fmt in formats:
            try:
                start_date = datetime.datetime.strptime(start, fmt)
                end_date = datetime.datetime.strptime(end, fmt)
            except:
                continue

        #Legacy code to determine if Python environment is Linux, Mac or Windows-based, to remove zero-padding from JHU data.
        if platform.system() == 'Windows':
            JHU_CSV_Date_Format = '%m/%d/%y'
            print('Using Python date format for Windows')
        elif platform.system() == 'Darwin' or platform.system() == 'Linux':
            JHU_CSV_Date_Format = '%m/%d/%y'
            print('Using Python date format for MacOS or Linux')

        if start_date is not None and end_date is None:

            start_date_col = start_date.strftime(JHU_CSV_Date_Format)
          
            try:
                print(list(self.csv_row_data).index(start_date_col))
                csv_start_idx = list(self.csv_row_data).index(start_date_col)

                print(self.csv_row_data)
                return (csv_start_idx, None)
            except ValueError as e:
                print ('The value %s, is an invalid start date' %(e))

        elif start_date is not None and end_date is not None:

            start_date_col = start_date.strftime(JHU_CSV_Date_Format)

            try:
                csv_start_idx = list(self.csv_row_data).index(start_date_col)

                end_date_col = end_date.strftime(JHU_CSV_Date_Format)
                csv_end_idx = list(self.csv_row_data).index(end_date_col)
                return (csv_start_idx, csv_end_idx)
            except ValueError as e:
                print ('There was an error with one the dates entered: %s' %(e))

        elif start_date is None and end_date is not None:

            end_date_col = end_date.strftime(JHU_CSV_Date_Format)
            try:
                csv_end_idx = list(self.csv_row_data).index(end_date_col)
                return (None, csv_end_idx)
            except ValueError as e:
                print ('The value %s, is an invalid end date' %(e))

        # User did not provide start date nor end date for plotting.
        else:
            return (None, None)

    def plot_covid19_data(self, start_end_dates):
        """ Plot COVID19 data based on statistical calculations.
            Uses some of Valeriu Predoi's statistical calcuations and plotting code from https://github.com/valeriupredoi/COVID-19_LINEAR
        Parameters:
            start_end_dates
                Tuple containing index position of start date and index position of end date.
        """

        start_idx = None
        end_idx = None

        # Checks if start date and end date are provided. Start date is optional, and End date is also optional.
        if start_end_dates[0] is not None:
            start_idx = start_end_dates[0]

        if start_end_dates[1] is not None:
            end_idx = start_end_dates[1]

        if start_idx is not None and end_idx is None:
            y01_plot_data = self.csv_row_data.iloc[0,start_idx:]
        elif start_idx is not None and end_idx is not None:
            y01_plot_data = self.csv_row_data.iloc[0, start_idx:end_idx]
        elif start_idx is None and end_idx is not None:
            y01_plot_data = self.csv_row_data.iloc[0, :end_idx]
        #No start date and end dates given.    
        else:
            y01_plot_data = self.csv_row_data.iloc[0, 4:]

        #This provides the days on the X axis, e.g. Day 1, 2, 3, 4, 5, etc.
        x1 = [np.float(x) for x in range(1, len(y01_plot_data)+1)]

        #y1 is the natural log of y01_plot_data values/case values
        ln_y1 = np.asarray([y if y<=0  else np.log(y) for y in y01_plot_data])

        print('Abbreviated output of Covid-19 Infection Values')
        print(y01_plot_data)
        print('Natural Log of Covid-19 Infection values')
        print(ln_y1)

        coef = np.polyfit(x1, ln_y1, 1)
        poly1d_fn1 = np.poly1d(coef)

        # statistical parameters first line 
        R = self.coeff_determination(ln_y1, poly1d_fn1(x1))  # R squared
        y_error = poly1d_fn1(x1) - ln_y1  # error
        
        slope = coef[0]  # slope
        d_time = np.log(2.) / slope  # doubling time
        R0 = np.exp(slope) - 1 #daily reproductive number

        plot_title = "Linear Fit of " + \
                        "log cases $N=Ce^{bt}$ with " + \
                        "$b=$%.3f day$^{-1}$ (red, %s)" % (slope, self.location) + "\n" + \
                        "Coefficient of determination (R-Squared)=%.3f" % R + "\n" + \
                        "Population Doubling time: %.2f days" % d_time + "\n" + \
                        "Estimated Daily $R_0 (Reproductive Number)=$%.2f" % R0

        print('Slope value %.3f' %slope)
        print('R Squared Value %.3f' %R)
        print('Doubling time %.2f' %d_time)
        print('R0 Value %.2f' %R0)

        if start_end_dates[0] is None:
            start_date_label = self.csv_row_data.columns[4]
        else:
            start_date_label = self.csv_row_data.columns[start_idx]

        # plotting
        plt.plot(x1, ln_y1, 'yo', x1, poly1d_fn1(x1), '--r', label=self.location)
        plt.errorbar(x1, ln_y1, yerr=y_error, fmt='o', color='r')
        plt.grid()
        plt.yticks(ln_y1, [np.int(y) for y in y01_plot_data])
        plt.xlabel("Days for %s - Day 1 is %s" %(self.location, start_date_label))
        plt.ylabel("Number of reported cases on given day DD")
        plt.title("COVID-19 Epidemic in %s\n%s" %(self.location, plot_title))
        plt.legend(loc="lower left")
        
        #Uncomment these 2 lines to save to an image file
        #plot_name = "COVID-19_LIN_{}.png".format(self.location)
        #plt.savefig(plot_name)
        plt.show()


def main():

        parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.add_argument('-p',
                            '--province_state',
                            type=str,
                            help='Name of province or state to obtain the COVID-19 data')
        parser.add_argument('-c',
                            '--country_region',
                            type=str,
                            help='Name of country or region to obtain the COVID-19 data')
        parser.add_argument('-u',
                            '--url',
                            type=str,
                            help='URL of COVID-19 data file, e.g. https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
        parser.add_argument('-s',
                            '--start_date',
                            type=str,
                            help='Start date in the COVID-19 data, can be entered as M-DD-YY such as 1-22-20 for January 22, 2020')
        parser.add_argument('-e',
                            '--end_date',
                            type=str,
                            help='End date in the COVID-19 data, can be entered as M-DD-YY such as 1-31-20 for January 31, 2020')    
        args = parser.parse_args()

        if not args.province_state and not args.url or not args.country_region and not args.url:
            print('Please provide a URL of the data file plus location (province, state, region, or country).')
            print('Instructions are available by typing: python covid19_linear_plot.py --help')
            return
        if not args.url:
            print('Please provide the URL of the data file.')
            print('Instructions are available by typing: python covid19_linear_plot.py --help')      
            return            
        if not args.province_state and not args.country_region:
            print('Please provide a province/state or country/region.')
            print('Instructions are available by typing: python covid19_linear_plot.py --help')            
            return
        start_date = None
        end_date = None
        if args.start_date:
            start_date = args.start_date
        if args.end_date:
            end_date = args.end_date
        if args.province_state and args.url:
            data = Covid19Data(args.province_state, args.url, province_state_selected = True)
        elif args.country_region and args.url:
            data = Covid19Data(args.country_region, args.url, province_state_selected = False)
        data.plot_covid19_data(data.set_start_end_dates(start_date, end_date))

if __name__ == '__main__':
    main()
