import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import argparse
import datetime
from dateutil.parser import parse
import pandas as pd
import platform
import collections
from enum import Enum
"""

COVID-19 (Coronavirus) Linear Plot Tool With Start and End Dates to Analyze Curve Flattening

Written by Peter C. (https://github.com/map-nerd-peter/covid19-linear-plot)

Special thanks to Valeriu Predoi for sharing statistical calculations and plotting analysis code 
in his Covid-19 Exponential Phase tool - https://github.com/valeriupredoi/COVID-19_LINEAR/.

"""

# Define the type of location data based on Johns Hopkins COVID19 data schema
class DataLocation(Enum):
    province_state = 1
    country_region = 2
    world = 3

class Covid19Data:

    def __init__(self, location, url, data_location):
        """Constructor"""
        #index location of world row index, only used when we want world total
        self.world_row_index = -1
        self._location = location
        self._url = url
        self._data_location = data_location
        self._csv_date_format = None

        #Load the row that contains for specific state or province and its COVID-19 data
        df = pd.read_csv(url, error_bad_lines=False)

        if data_location == DataLocation.province_state:
            self._csv_row_data = df[df['Province/State'] == location]

        #Get country data
        elif data_location == DataLocation.country_region:
            self._csv_row_data = df[df['Country/Region'] == location].groupby('Country/Region').sum()
            
        #World data
        elif data_location == DataLocation.world:

            #Add a row at the bottom that has total global value 
            df = df.append(df.sum(numeric_only=True), ignore_index=True)

            self.world_row_index = df.shape[0]-1
            self._csv_row_data = df
        
        # Remove the zero padding from single digit date values so it matches JHU data. e.g. Feb. 9 2020 is shown as 2/9/20 in the csv data.
        if platform.system() == 'Windows':
            self._csv_date_format = '%#m/%#d/%y'
            print('Using Python date format for Windows')
        elif platform.system() == 'Darwin' or platform.system() == 'Linux':
            self._csv_date_format = '%-m/%-d/%y'
            print('Using Python date format for MacOS / Linux')

    @property
    def location(self):
        return self._location
        
    @property
    def data_location(self):
        return self._data_location

    @property
    def url(self):
        return self._url

    @property 
    def csv_row_data(self):
       return self._csv_row_data
    
    @property
    def csv_date_format(self):
        return self._csv_date_format

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
            except:
                continue

        #Try to parse end date separately as it could be different date format than start date.
        for fmt in formats:
            try:
                end_date = datetime.datetime.strptime(end, fmt)
            except:
                continue



        if start_date is not None and end_date is None:

            start_date_col = start_date.strftime(self.csv_date_format)
          
            try:
                print(list(self.csv_row_data).index(start_date_col))
                csv_start_idx = list(self.csv_row_data).index(start_date_col)

                print(self.csv_row_data)
                return (csv_start_idx, None)
            except ValueError as e:
                print ('The value %s, is an invalid start date' %(e))

        elif start_date is not None and end_date is not None:

            start_date_col = start_date.strftime(self.csv_date_format)

            try:
                csv_start_idx = list(self.csv_row_data).index(start_date_col)

                end_date_col = end_date.strftime(self.csv_date_format)
                csv_end_idx = list(self.csv_row_data).index(end_date_col)
                return (csv_start_idx, csv_end_idx)
            except ValueError as e:
                print ('There was an error with one the dates entered: %s' %(e))

        elif start_date is None and end_date is not None:

            end_date_col = end_date.strftime(self.csv_date_format)
            try:
                csv_end_idx = list(self.csv_row_data).index(end_date_col)
                return (None, csv_end_idx)
            except ValueError as e:
                print ('The value %s, is an invalid end date' %(e))

        # User did not provide start date nor end date for plotting.
        else:
            return (None, None)

    # Returns readable date, e.g. Mar/31/2020 instead of 03/31/20
    def get_readable_date(self, csv_date):
        try:
            date_label = datetime.datetime.strptime(csv_date, '%m/%d/%y')
            return datetime.datetime.strftime(date_label, '%b/%d/%Y') 
        except:
            return 'Invalid Date'

    # Get the csv data based on start and end dates, to use for plotting
    def get_covid19_data(self, start_end_dates):
        """ Get the covid19 data for Y and x axes and start dates.

        Parameters:
            start_end_dates
                Tuple containing column index of start date and column index of end date.
        
        Returns:
            X axis data of the dates, Y axis data of the case numbers, and start date column and end date column
                
        """
        start_idx = None
        end_idx = None

        covid19_data = collections.namedtuple('covid19_data',['x01_plot_data', 'y01_plot_data', 'start_date_col', 'end_date_col']) 

        # Checks if start date and end date are provided. Start date is optional, and End date is also optional.
        if start_end_dates[0] is not None:
            start_idx = start_end_dates[0]

        if start_end_dates[1] is not None:
            end_idx = start_end_dates[1]

        if start_idx is not None and end_idx is None and self.data_location == DataLocation.world:
            covid19_data.y01_plot_data = self.csv_row_data.iloc[self.world_row_index, start_idx:]

        elif start_idx is not None and end_idx is not None and self.data_location == DataLocation.world:
            covid19_data.y01_plot_data = self.csv_row_data.iloc[self.world_row_index, start_idx:end_idx+1]

        #works for prov/state or country/region
        elif start_idx is not None and end_idx is None:
            covid19_data.y01_plot_data = self.csv_row_data.iloc[0, start_idx:]

        #works for prov/state or country/region
        elif start_idx is not None and end_idx is not None:
            covid19_data.y01_plot_data = self.csv_row_data.iloc[0, start_idx:end_idx+1]

        elif start_idx is None and end_idx is not None and self.data_location == DataLocation.province_state:
            covid19_data.y01_plot_data = self.csv_row_data.iloc[0,4:end_idx+1]
            start_idx = 4

        elif start_idx is None and end_idx is not None and self.data_location == DataLocation.country_region:
            covid19_data.y01_plot_data = self.csv_row_data.iloc[0,2:end_idx+1]
            start_idx = 2
            
        elif start_idx is None and end_idx is not None and self.data_location == DataLocation.world:
            covid19_data.y01_plot_data = self.csv_row_data.iloc[self.world_row_index,4:end_idx+1]
            start_idx = 4   

        #No start date and end dates given, but start date of dataset still needs to be defined at Jan. 22, 2020           
        elif start_idx is None and end_idx is None and self.data_location == DataLocation.province_state:
            covid19_data.y01_plot_data = self.csv_row_data.iloc[0,4:]
            start_idx = 4

        elif start_idx is None and end_idx is None and self.data_location == DataLocation.country_region:
            covid19_data.y01_plot_data = self.csv_row_data.iloc[0,2:]
            start_idx = 2
        
        elif start_idx is None and end_idx is None and self.data_location == DataLocation.world:
            covid19_data.y01_plot_data = self.csv_row_data.iloc[self.world_row_index,4:]
            start_idx = 4  
            
        #This provides the days on the X axis, e.g. Day 1, 2, 3, 4, 5, etc.
        covid19_data.x01_plot_data = [np.float(x) for x in range(1, len(covid19_data.y01_plot_data)+1)]

        covid19_data.start_date_col = start_idx
        covid19_data.end_date_col = end_idx

        return covid19_data


    #returns double image data for rendering to segmented red, orange, yellow to show the intensity of the virus' doubling time
    #Returns a list of red orange yellow proportions
    def get_doubling_time_cmap(self, doubling_time):
        
        if doubling_time <= 60:
            return [(0.0, '#FF0000'), (0.5, '#FFA500'), (1.0, '#FFFF00')]

        #Show more yellows to indicate less danger
        elif doubling_time > 60 and doubling_time <= 365:
            return [(0.0, '#FF0000'), (0.35, '#FFA500'), (0.75, '#FFFF00'), (1.0, '#FFFF80')]

        #Show mostly yellows as doubling time is more than a year
        elif doubling_time > 365:
            return [(0.0, '#FF0000'), (0.1, '#FFA500'), (0.4, '#FFFF00'), (1.0, '#FFFF80')]
            #return colors.LinearSegmentedColormap.from_list('custom roy', [(0.0, '#FF0000'), (0.2, '#FFA500'), (0.6, '#FFFF00')], N=256)

    def plot(self, covid19_data):

        # Plot data, using some of Valeriu Predoi's statistical calcuations and plotting code from https://github.com/valeriupredoi/COVID-19_LINEAR

        # ln_y1 is the natural log of y01_plot_data. y01_plot_data contains daily case values
        ln_y1 = np.asarray([y if int(y)<=0  else np.log(y) for y in covid19_data.y01_plot_data])

        print('Abbreviated output of Covid-19 Infection Values')
        print(covid19_data.y01_plot_data)
        print('Natural Log of Covid-19 Infection values')
        print(ln_y1)

        coef = np.polyfit(covid19_data.x01_plot_data, ln_y1, 1)
        poly1d_fn1 = np.poly1d(coef)

        # statistical parameters first line 
        R = self.coeff_determination(ln_y1, poly1d_fn1(covid19_data.x01_plot_data))  # R squared
        y_error = poly1d_fn1(covid19_data.x01_plot_data) - ln_y1  # error
        
        slope = coef[0]  # slope
        d_time = np.log(2.) / slope  # doubling time
        R0 = np.exp(slope) - 1 #daily reproductive number

        print('Slope value %.3f' %slope)
        print('R Squared Value %.3f' %R)
        print('Doubling time %.2f' %d_time)
        print('R0 Value %.2f' %R0)

        if covid19_data.start_date_col is None:
            start_date_label = self.get_readable_date(self.csv_row_data.columns[4])
        else:
            start_date_label = self.get_readable_date(self.csv_row_data.columns[covid19_data.start_date_col])

        if covid19_data.end_date_col is None:
            end_date_label = self.get_readable_date(self.csv_row_data.columns[-1])
        else:
            end_date_label = self.get_readable_date(self.csv_row_data.columns[covid19_data.end_date_col])


        gridsize = (2, 2)
        fig = plt.figure(figsize=(10,10)) #width and height
        ax1 = plt.subplot2grid(gridsize, (0, 0), colspan=1, rowspan=3)
        ax2 = plt.subplot2grid(gridsize, (0, 1))
        ax3 = plt.subplot2grid(gridsize, (1, 1))
        
        

        # List Integer values to use build the plotted colou map images
        IMAGE_ROW_VALUES = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190]

        # Build the linear plot
        ax1.plot(covid19_data.x01_plot_data, ln_y1, 'yo', covid19_data.x01_plot_data, poly1d_fn1(covid19_data.x01_plot_data), '--r', label=self.location)
        ax1.errorbar(covid19_data.x01_plot_data, ln_y1, yerr=y_error, fmt='o', color='r')
        ax1.grid()
        ax1.set_yticks(ln_y1)
        ax1.set_yticklabels([np.int(y) for y in covid19_data.y01_plot_data]) 

        ax1.set_xlabel("Days for %s - Day 1 is %s" %(self.location, start_date_label))
        ax1.set_ylabel("Number of reported cases on given day DD")

        ax1_title = "Linear Fit of " + \
                        "log cases $N=Ce^{bt}$ with " + \
                        "$b=$%.3f day$^{-1}$ (red, %s) and $t$ in days\n" % (slope, self.location) + \
                        "Coef. of Determination $R^{2}$=%.2f" % R + " and Est. Daily $R_0$ (Reproductive Number)=%.2f" % R0

        ax1.set_title(ax1_title)
        ax1.title.set_fontsize(11.5)
        ax1.legend(loc="lower right")
        

        #Very steep rise in infections
        if slope > 0.12:
            scale_offset = 0.85
        #Steep curve
        elif slope > 0.09 and slope <= 0.12:
            scale_offset = 0.7
        #Curve is a bit steep 
        elif slope > 0.05 and slope <= 0.09:
            scale_offset = 0.55
        #Most countries are here and flattening their infection rates
        elif slope >= 0.009 and slope < 0.05:
            scale_offset = 0.38
        #Very flat curve
        elif slope > 0 and slope < 0.009:
            scale_offset = 0.14
        #Downward revision of cases
        elif slope <= 0:
            scale_offset = 0

        slope_image = np.array([IMAGE_ROW_VALUES])

        #Show as shades of greys
        slope_cmap = colors.LinearSegmentedColormap.from_list('custom grey', [(0.0, '#FFFFFF'), (0.5, '#C0C0C0'), (1.0 ,'#606060')] , N=256)

        #Build the image showing slope of the curve

        ax2.imshow(slope_image ,interpolation='nearest',  cmap=slope_cmap, aspect='auto')

        ax2.xaxis.axes.annotate('%s:\nSlope of \nthe curve is %.3f' %(self.location, slope), ha="center", xy=(scale_offset+0.001*slope, 0), xycoords='axes fraction',
            xytext=(0.5, 0.5), textcoords='axes fraction', 
            arrowprops=dict(arrowstyle="simple", facecolor='black'), fontsize=9.5, va="bottom")

        ax2.xaxis.axes.annotate('Slope b = 0\nCompletely\nFlat Curve',  xy=(0, 0), xycoords='axes fraction', 
            xytext=(0.1, 0.1), textcoords='axes fraction', arrowprops=dict(arrowstyle="-|>", facecolor='black'), fontsize=9.5, va="bottom")
 
        ax2.xaxis.axes.annotate('Steep\n Curve', xy=(1, 0), xycoords='axes fraction', xytext=(0.9,0.1), #Provide a bit offset for the text, so not to overlap axis boundary 
            textcoords='axes fraction', 
            arrowprops=dict(arrowstyle="-|>", facecolor='black'), 
            fontsize=9.5)

        ax2.xaxis.set_visible(False)
        ax2.yaxis.set_visible(False)
        ax2.set_title('Infection\'s Exponential Curve Slope $b=$%.3f day$^{-1}$:' % (slope))
        ax2.title.set_fontsize(11.5)

        #Build doubling timeimage
        doubling_time_cmap = colors.LinearSegmentedColormap.from_list('custom roy', self.get_doubling_time_cmap(d_time) , N=256)
        dtime_image = np.array([IMAGE_ROW_VALUES])
        ax3.imshow(dtime_image ,interpolation='nearest',  cmap=doubling_time_cmap, aspect='auto')

        #Determine location and label for doubling time at 60 days
        if d_time > 60:
            dtime_60_loc = 60/d_time
            dtime_60_label = dtime_60_loc
            dtime_loc = 1.0
        elif d_time <= 60 and d_time >= 50:
            dtime_60_loc = 1.0
            #Allow for small offset from right boundary of axis.
            dtime_60_label = 0.80
            dtime_loc = d_time/60
        elif d_time < 50 and d_time > 0:
            dtime_60_loc = 1.0
            dtime_60_label = 0.80
            dtime_loc = d_time/60
        elif d_time < 0:
            dtime_60_loc = 1.0
            dtime_60_label = 0.80
            dtime_loc = -0.08


        ax3.xaxis.axes.annotate('%s:\nDoubling Time is %.1f days' %(self.location, d_time), ha="center", xy=(dtime_loc, 0), xytext=(0.5, 0.6), 
            xycoords='axes fraction', textcoords='axes fraction', arrowprops=dict(arrowstyle="simple", facecolor='black'), fontsize=9.5, va="bottom")

        ax3.xaxis.axes.annotate('Doubling Time\n at 1 day\n(Very Fast Virus Growth)',  xy=(0, 0), xycoords='axes fraction', 
            xytext=(0.1, 0.15), textcoords='axes fraction', arrowprops=dict(arrowstyle="-|>", facecolor='black'), fontsize=9.5, va="bottom")
 
        ax3.xaxis.axes.annotate('Doubling Time\n at 60 days', xy=(dtime_60_loc, 0), xycoords='axes fraction', xytext=(dtime_60_label,0.37), #Provide a bit offset for the text  
            textcoords='axes fraction', 
            arrowprops=dict(arrowstyle="-|>", facecolor='black'), fontsize=9.5, va="bottom")
        ax3.xaxis.set_visible(False)
        ax3.yaxis.set_visible(False)

        ax3.set_title('Population Doubling time of Infections:')
        ax3.title.set_fontsize(11.5)
        
        date_info = '%s - %s' %(start_date_label, end_date_label) 
        plt.suptitle('COVID-19 Epidemic in %s \n%s' %(self.location, date_info), fontsize=16)
        #plt.rc('axes', titlesize=7) 
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
        parser.add_argument('-w',
                            '--world',
                            action='store_const',
                            const = 'The World',
                            help='The entire world')
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

        if not (args.province_state or args.country_region or args.world) or not args.url:
            print('Please provide a URL of the data file plus location (province, state, region, or country, or type w for the world,).')
            print('Instructions are available by typing: python covid19_linear_plot.py --help')
            print('Example commands and more info available at https://github.com/map-nerd-peter/covid19-linear-plot')
            return
        start_date = None
        end_date = None
        if args.start_date:
            start_date = args.start_date
        if args.end_date:
            end_date = args.end_date
        if args.province_state and args.url:
            data = Covid19Data(args.province_state, args.url, DataLocation.province_state)
        elif args.country_region and args.url:
            data = Covid19Data(args.country_region, args.url, DataLocation.country_region)
        elif args.world and args.url:
            data = Covid19Data(args.world, args.url, DataLocation.world)

        start_and_end_dates = data.set_start_end_dates(start_date, end_date)
        x_y_dates = data.get_covid19_data(start_and_end_dates)
        data.plot(x_y_dates)

if __name__ == '__main__':
    main()
