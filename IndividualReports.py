import pickle, inspect, re
import pyeq3
import numpy, scipy, scipy.stats

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import tkinter as tk
from tkinter import ttk as ttk
from tkinter import messagebox as tk_mbox
import tkinter.scrolledtext as tk_stxt
import XYscrolledtext as xy_stxt


textboxWidth = 60 # units are characters
textboxHeight = 12 # units are characters

graphWidth = 800 # units are pixels
graphHeight = 600 # units are pixels



def ParameterListing(parent, distro):
    scrolledText = tk_stxt.ScrolledText(parent, width=textboxWidth, height=textboxHeight, wrap=tk.NONE)
    scrolledText.insert(tk.END, 'Parameters:\n')
    
    for parmIndex in range(len(distro[1]['fittedParameters'])):
        scrolledText.insert(tk.END, '    ' + distro[1]['parameterNames'][parmIndex] + ' = %-.16E' % (distro[1]['fittedParameters'][parmIndex]) + '\n')
    return scrolledText


def ScipyInfoReport(parent, distro):
    xyscrolledText = xy_stxt.XYScrolledText(parent, width=textboxWidth, height=textboxHeight, wrap=tk.NONE)
    xyscrolledText.insert(tk.END, distro[1]['scipyInfo'])    
    return xyscrolledText


def DataArrayStatisticsReport(parent, titleString, tempdata):
    scrolledText = tk_stxt.ScrolledText(parent, width=textboxWidth, height=textboxHeight, wrap=tk.NONE)
    scrolledText.insert(tk.END, titleString + '\n\n')
    
    # must at least have max and min
    minData = min(tempdata)
    maxData = max(tempdata)
    
    if maxData == minData:
        scrolledText.insert(tk.END, 'All data has the same value,\n')
        scrolledText.insert(tk.END, "value = %-.16E\n" % (minData))
        scrolledText.insert(tk.END, 'statistics cannot be calculated.')
    else:
        scrolledText.insert(tk.END, "max = %-.16E\n" % (maxData))
        scrolledText.insert(tk.END, "min = %-.16E\n" % (minData))
        
        try:
            temp = scipy.mean(tempdata)
            scrolledText.insert(tk.END, "mean = %-.16E\n" % (temp))
        except:
            scrolledText.insert(tk.END, "mean gave error in calculation\n")

        try:
            temp = scipy.stats.sem(tempdata)
            scrolledText.insert(tk.END, "standard error of mean = %-.16E\n" % (temp))
        except:
            scrolledText.insert(tk.END, "standard error of mean gave error in calculation\n")

        try:
            temp = scipy.median(tempdata)
            scrolledText.insert(tk.END, "median = %-.16E\n" % (temp))
        except:
            scrolledText.insert(tk.END, "median gave error in calculation\n")

        try:
            temp = scipy.var(tempdata)
            scrolledText.insert(tk.END, "variance = %-.16E\n" % (temp))
        except:
            scrolledText.insert(tk.END, "variance gave error in calculation\n")

        try:
            temp = scipy.std(tempdata)
            scrolledText.insert(tk.END, "std. deviation = %-.16E\n" % (temp))
        except:
            scrolledText.insert(tk.END, "std. deviation gave error in calculation\n")

        try:
            temp = scipy.stats.skew(tempdata)
            scrolledText.insert(tk.END, "skew = %-.16E\n" % (temp))
        except:
            scrolledText.insert(tk.END, "skew gave error in calculation\n")

        try:
            temp = scipy.stats.kurtosis(tempdata)
            scrolledText.insert(tk.END, "kurtosis = %-.16E\n" % (temp))
        except:
            scrolledText.insert(tk.END, "kurtosis gave error in calculation\n")
            
    return scrolledText


def Histogram(parent, equation):
    f = plt.figure(figsize=(graphWidth/100.0, graphHeight/100.0), dpi=100)
    canvas = FigureCanvasTkAgg(f, master=parent)
    axes = f.add_subplot(111)
    abs_error = equation.modelAbsoluteError
    bincount = len(abs_error)//2 # integer division
    if bincount < 5:
        bincount = 5
    if bincount > 25:
        bincount = 25
    n, bins, patches = axes.hist(abs_error, bincount, rwidth=0.8)
    
    # some axis space at the top of the graph
    ylim = axes.get_ylim()
    if ylim[1] == max(n):
        axes.set_ylim(0.0, ylim[1] + 1)

    axes.set_title('Absolute Error Histogram') # add a title
    axes.set_xlabel('Absolute Error') # X axis data label
    axes.set_ylabel(" Frequency") # Y axis label is frequency

    canvas.show()
    plt.close('all') # clean up after using pyplot or else thaere can be memory and process problems
    return canvas.get_tk_widget()
