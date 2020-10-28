'''
Created on Oct 18, 2020

@author: shanti
'''
from django.views.generic import TemplateView, FormView
from django.contrib.messages.views import SuccessMessageMixin
from mainprogram.forms import ParameterForm, SetupForm
from django.contrib import messages
from django.urls import reverse_lazy
from ECG.views import ECG
import matplotlib.pyplot as plt
from mpld3 import fig_to_html
# use gridspec to partition the figure into subplots
import matplotlib.gridspec as gridspec
import io
import base64
import numpy as np
import pandas as pd


class LandingView(TemplateView):
    template_name = 'mainprogram/welcome.html'
    page_name = "WelcomePage"
        
class InformationView(FormView):
#class ParameterView(FormView):
    template_name = 'mainprogram/parameters.html'
    form_class = ParameterForm
    success_url = reverse_lazy("info")
    success_message = "created successfully for: %(offset_hours)s "
    
    def get_context_data(self, **kwargs):
        context = super(InformationView, self).get_context_data(**kwargs)
        return context
    
    def form_valid(self, form, **kwargs):
        ecg = ECG()
        ''' This option with or without the SuccessMessageMixin also works '''
        offset_hours = float(form.cleaned_data.get('offset_hours'))# zero-index
        interval_minutes = float(form.cleaned_data.get('interval_minutes'))
        gaps = form.cleaned_data.get('gaps')

        self.data, df = ecg.get_dataframe(offset_hours = offset_hours, interval_minutes = interval_minutes, gaps = gaps)
        context = self.get_context_data(**kwargs)
        context['htmldata'] = df.to_html()
        context['html_graph'] = self.get_trends(offset_hours = offset_hours, interval_minutes = interval_minutes, gaps = gaps)
        context['offset_hours'] = offset_hours
        context['interval_minutes'] = interval_minutes
        return self.render_to_response(context)
    
    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)
    
    def get_trends(self, offset_hours = 0, interval_minutes = 0.5, gaps = "Yes"):
        ''' Default = 1/2 minute from start of file'''
        ''' create the plot '''
        ''' offset_hours and gaps are used only for title '''
           
        new = self.data[['time', 'values', 'group', 'delta']]
            
        plt.figure()
        gspec = gridspec.GridSpec(4, 1)

        top_graph = plt.subplot(gspec[0:3, 0:])
        bottom_stats = plt.subplot(gspec[3, 0])
        top_graph.plot(new.index, new['values'])
        top_graph.set_ylabel('Value', fontsize=16)
        plt.xticks(rotation=45)
        
        ''' indicate the breaks in data by vertical lines '''
        '''Determine when the period, "group" Changes '''
        periods = new[new.group.diff(-1)!=0].index.values
        ''' add the first index as well to periods '''
        periods = np.insert(periods, [0], 0)
        # Plot the red vertical lines
        for item in periods[1::]:
            top_graph.axvline(item, ymin=0, ymax=1,color='red')
        # Plot the Period Text.
        for i in periods:
            hours, remainder = divmod(new.loc[i, 'delta'].total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            s = f"{hours}:{minutes}:{seconds}"
            top_graph.text(y=0.8*new['values'].max(), x=i,
                s=s, color='red', fontsize=10, rotation=90)
            
        ''' Set the ticks and labels '''
        ''' if minutes < 0.5, show seconds '''
        if interval_minutes < 1:
            number = round(interval_minutes * 60)
            span = len(new) // number # integer division
            labels = [str(i) for i in  np.linspace(0,number, number + 1)]
            locations = [(span * i) for i in np.linspace(0,number, number + 1)]
            top_graph.set_xlabel('Seconds', fontsize=12)
        else:
            number = round(interval_minutes)
            span = len(new) // number # integer division
            labels = [str(i) for i in range(number + 1)]
            locations = [(span * i) for i in range(number + 1)]
            top_graph.set_xlabel('Minutes', fontsize=12)
        top_graph.set_xticks(locations)
        top_graph.set_xticklabels(labels, rotation = 90)

#         bottom_stats.text(0.25,0.01, new['values'].describe().loc[['min', 'max', 'mean','std']].T.to_string())
        bottom_stats.text(0.25,0.01, new['values'].fillna(value=np.nan).describe().loc[['min', 'max', 'mean','std']].to_frame().T.to_string())
        top_graph.axhline(y = new['values'].mean(), color = 'g', alpha=0.5)
        bottom_stats.set_xticks([])
        bottom_stats.set_yticks([])
        bottom_stats.set_xlabel("Summary Statistics", fontsize=16)
        bottom_stats.axis('off')
        top_graph.set_title(f"Waveform from {offset_hours} hours in for {interval_minutes} minutes; gaps: {gaps}", pad = 40)
        plt.tight_layout()

        img_in_memory = io.BytesIO() # for Python 3
        plt.savefig(img_in_memory, format='png')
        plt.close()
        
        ''' String representation of bytes object using base64encode '''
        html_graph = base64.b64encode(img_in_memory.getvalue()) # load the bytes in the context as base64
        
        # Calling .decode() gets us the right representation of the original image
        html_graph = html_graph.decode('utf8') # this step is necessary.
        
        return html_graph
        
class SetupView(FormView):
#class ParameterView(FormView):
    template_name = 'mainprogram/setup.html'
    form_class = SetupForm
    success_url = reverse_lazy("info")
    
    def form_valid(self, form, **kwargs):
   
        ecg_setup_fp = form.cleaned_data.get('setup_filepath')
        ecg = ECG()
        ecg.initialize(ecg_file = ecg_setup_fp)
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
