'''
Created on Oct 17, 2020

@author: shanti
'''

from utils.decorators import Singleton
from mainprogram.constants import ECG_waveform_file
import pandas as pd
import numpy as np
import ast

@Singleton
class ECG(object):
    '''
        ECG device that stores the measurement readings as waverform
    '''

    def __init__(self):
        '''Constructor: Initialize the ECG instance here.'''
        self.initialize()
    
    def initialize(self, ecg_file = ECG_waveform_file):
        ''' Read file '''
        try:
            self._readings = pd.read_json(ecg_file, dtype={"values":"int"})
        except Exception as e:
            self._readings = pd.read_json(ecg_file, lines=True, dtype={"values":"int"})
        ''' compute seconds '''
        pos = self._readings.columns.get_loc('time')
        self._readings['delta'] = (self._readings.iloc[1:, pos] - self._readings.iat[0,pos]) / 1000
        ''' Set the first entry of Nan to zero '''
        self._readings.loc[0,'delta'] = 0
        ''' compute timedelta: gives value in days:minutes:seconds '''
        self._readings['delta'] = self._readings['delta'].astype('timedelta64[s]')
        ''' Validating entire file takes too long '''
        self._readings = self._validate(window = self._readings)
    
    @property
    def readings(self):
        return self._readings
    
    @property 
    def hours(self):
        ''' how many hours' worth of data is there in the ECG dataset '''
        hours = self._readings.iloc[-1][ 'delta'] / pd.Timedelta('1 hour')
        return round(hours)
    
    def _validate(self, window):
        df = window.copy()
        #df['check'] = df['values'].apply(self._validate_values)
        ''' validate the readings: check length of chunk and data type '''
        try:
            df.loc[:,'values'] = df['values'].apply(self._validate_values)
        except Exception as e:
            print(e)
        ''' assign group numbers for consecutive groups of non-null values '''
        mask = df['values'].astype(str).str.contains("nan")
        df['group'] = mask.cumsum()
        
        return df
    
    def _validate_values(self, values):
        ''' check that there are 240 values in chunk '''
        ''' and if there is any element that is not a signed integer '''
        ''' return an array of invalid values '''
        if len(values) != 240 or any(not isinstance(x, int) for x in values):            
            return [np.nan] * 240
        else:
            return values
        
    def __str__(self):
        return 'ECG device'
    
    def get_dataframe(self, offset_hours, interval_minutes, gaps = "Yes"):
        if gaps == "Yes":
            df = self.get_window_with_gaps(offset_hours = offset_hours, interval_minutes = interval_minutes)
        elif gaps == 'No':
            df = self.get_window_without_gaps(offset_hours = offset_hours, interval_minutes = interval_minutes)
        data = df.explode('values').reset_index()
        
        return data, df
        
    def get_window_with_gaps(self, offset_hours, interval_minutes):

        start_td = pd.Timedelta(hours = offset_hours)
        end_td = pd.Timedelta(hours = offset_hours, minutes = float(interval_minutes))
        source_window = self._readings.loc[(self._readings['delta'] >= start_td) & (self._readings['delta'] < end_td) ]
        ''' all rows are in the same group '''
        source_window.loc[:,'group'] = 1
        return source_window

    
    def get_window_without_gaps(self, offset_hours, interval_minutes):
        start_td = pd.Timedelta(hours = offset_hours)
        ''' determine the end time in milliseconds. Subtract '1' due to zero-indexing '''
        nrows = round(interval_minutes * 60)
        source_window = self._readings.loc[(self._readings['delta'] >= start_td)].copy()
        source_window = source_window.head(nrows)
        source_start_index = source_window.index[0]
        source_end_index = source_window.index[-1]
        source_window = source_window[~source_window['values'].astype(str).str.contains("nan")]
        ''' get valid rows as needed to fill up requested interval_minutes, as we are dropping invalid rows'''
        while (len(source_window) < nrows) :
            needed = nrows - len(source_window)
            source_start_index = source_end_index
            source_end_index = source_end_index + needed
            
            window = self._readings.loc[source_start_index:source_end_index].copy()
            window = self._validate(window = window)
            window = window[~window['values'].astype(str).str.contains("nan")]
            source_window = pd.concat([source_window, window], ignore_index = True)
        return source_window
            
        
    def inject_reading(self, offset_hours, interval_minutes, values_list):
        ''' method specifically only to inject invalid data for testing validation scenarios '''
        ''' reading is appended at the end of the specified offset_hours and interval_minutes '''
        window = self.get_window_with_gaps(offset_hours, interval_minutes)

        new_row = pd.DataFrame(window[-1:].values, columns=window.columns)
        new_row['values'] = str(values_list)
        try:
            window = pd.concat([window, new_row], ignore_index = True)
        except Exception as e:
            print(e)
        return window
    

    
    
