'''
Created on Feb 4, 2019

@author: shanti
'''
from django import forms
from decimal import Decimal
from django.core.validators import MinValueValidator
from ECG.views import ECG
import os

ecg = ECG()

class ParameterForm(forms.Form):


    offset_hours = forms.DecimalField(label='Hours from start of file:',max_digits = 3, decimal_places = 1,
                                      validators=[MinValueValidator(Decimal('0.0'))],
                                      max_value = ecg.hours,
                                      min_value = 0.0)
    interval_minutes = forms.DecimalField(label='Interval in minutes', max_digits = 4, decimal_places = 2, 
                                          max_value = 59.0,
                                          validators=[MinValueValidator(Decimal('0.01'))])
    gaps = forms.ChoiceField(label='Would you like gaps in wavwform (Yes/No):', initial = "Yes",
                             choices=(("Yes", 'Yes'), ('No', 'No')))
    
class SetupForm(forms.Form):

    setup_filepath = forms.CharField(label='ECG Waveform filepath',
                            widget=forms.TextInput(attrs={'size':80}))
    
    def clean_setup_filepath(self):
        setup = self.cleaned_data.get('setup_filepath')
        if not os.path.isfile(setup):
            raise forms.ValidationError(f"Error:, {setup} does not exist")
        return setup
        
        
            
            
        