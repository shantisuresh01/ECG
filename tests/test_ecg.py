'''
Created on Oct 17, 2020

@author: shanti
'''
import unittest
from ECG.views import ECG
import numpy as np

class ECGTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """ getting ECG object once as as to avoid calling it for each test
            and storing the result as class variable
        """
        super(ECGTest, cls).setUpClass()
        cls.ecg = ECG()

    def test_ecg_device_is_created(self):
        self.assertEqual(self.__class__.ecg.readings.empty, False, "Oops!  there are no readings")
    
    def test_second_ecg_instance_is_same_as_first(self):
        ecg1 = ECG()
        ecg2 = ECG()
        self.assertEqual(id(ecg1), id(ecg2), "Oops!  the two ECG instances are not the same")
         
    def test_1_second_interval_returns_1_chunk(self):
        hour_offset = 0
        ''' one second = 1/60 minute '''
        one_second = 1 / 60
        window = self.ecg.get_window_with_gaps(offset_hours = hour_offset, interval_minutes = one_second)
        self.assertEqual(len(window), 1, "Oops! one chunk not returned")
         
    def test_1_second_interval_returns_2_chunks_after_list_of_values_is_added(self):
        hour_offset = 0
        ''' one second = 1/60 minute '''
        one_second = 1 / 60
        values_list = [1, 2, 3]
        window = self.ecg.inject_reading(offset_hours = hour_offset, interval_minutes = one_second,
                                     values_list = values_list)
        self.assertEqual(len(window), 2, "Oops! two chunks are not returned")
     
    def test_2_second_interval_returns_3_chunks_after_list_of_values_is_added(self):
        hour_offset = 0
        ''' one second = 1/60 minute '''
        two_seconds = 2 / 60
        values_list = [1, 2, 3]
        window = self.ecg.inject_reading(offset_hours = hour_offset, interval_minutes = two_seconds,
                                     values_list = values_list)
        self.assertEqual(len(window), 3, "Oops! three chunks are not returned")
         
    def test_chunk_retrieved_matches_values_injected(self):
        ''' add invalid data - less than 240 values '''
        hour_offset = 0
        ''' one second = 1/60 minute '''
        two_seconds = 2 / 60
        values_list = [1, 2, 3]
        window = self.ecg.inject_reading(offset_hours = hour_offset, interval_minutes = two_seconds,
                                     values_list = values_list)
        #
        injected_values = np.safe_eval(window.iloc[-1]['values'])
        self.assertEqual(injected_values, values_list, "Oops! injected values do not match retrieved values")
 
    def test_validation_nullifies_invalid_chunk(self):
        ''' add invalid data - less than 240 values '''
        hour_offset = 0
        ''' one second = 1/60 minute '''
        one_second = 1 / 60
        values_list = [1, 2, 3]
        window = self.ecg.inject_reading(offset_hours = hour_offset, interval_minutes = one_second,
                                     values_list = values_list)
        window = self.__class__.ecg._validate(window = window)
        values = str(window.loc[1,'values'])
        self.assertTrue("nan" in values, "Oops! null not returned for invalid chunk")
    
    def test_hours_property_returns_nonzero_hours(self):
        self.assertTrue(self.__class__.ecg.hours is not None, "Oops! hours is None")
        
# if __name__ == "__main__":
#     #import sys;sys.argv = ['', 'Test.testName']
#     unittest.main()