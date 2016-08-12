import pickle, io

import scipy, scipy.stats
import pyeq3

import tkinter as tk
from tkinter import ttk as ttk
from tkinter import messagebox as tk_mbox
import tkinter.scrolledtext as tk_stxt

import IndividualReports
import AdditionalInfo


class ResultsFrame(tk.Frame):
    
    def __init__(self, parent, pickledStatsDistroFile):
        tk.Frame.__init__(self, parent)
        
        # first, load the fitted distributions
        resultsFile = open(pickledStatsDistroFile, 'rb')
        rawData, distroList = pickle.load(resultsFile)
        resultsFile.close()
        
        # ensure distribution list is sorted by user criteria
        distroList.sort(key=lambda item: item[0])

        # now dig out "long names" for user select in a combobox, and
        # initialize "parameter names" and and additional scipy onformation
        longnameList = []
        maxWidth = 0
        rank = 1
        for distro in distroList:
            item = eval('scipy.stats.' + distro[1]['distributionName'])
            longName = io.StringIO(item.__doc__).readlines()[0]
            if longName[:2] == 'A ':
                longName = longName[2:]
            if longName[:3] == 'An ':
                longName = longName[3:]
            longname = 'Rank ' + str(rank) + ': ' + longName[:longName.find(' continuous')]
            if len(longName) > maxWidth:
                maxWidth = len(longName)
            longnameList.append(longname)
            distro[1]['longName'] = longName
            rank += 1

            # find the distribution parameter names
            if distro[1]['distributionName'] == 'loggamma' and not item.shapes:
                item.shapes = 'c'
            if item.shapes:
                parameterNames = item.shapes.split(',') + ['location', 'scale']
            else:
                parameterNames = ['location', 'scale']
            distro[1]['parameterNames'] = parameterNames

            # any additional info from scipy?
            try:
                n = item.__doc__.find('Notes\n')
                e = item.__doc__.find('Examples\n')
                
                notes =  item.__doc__[n:e]
                notes = notes[notes.find('-\n') + 2:].replace('::', ':').strip()  
            except:
                notes = ''
                
            if notes:
                distro[1]['scipyInfo'] = notes
            else:
                distro[1]['scipyInfo'] = 'No additional information available from scipy.'

        # a combo box for user selection of fitted distributions
        distroStringVar = tk.StringVar()
        self.comboBox = ttk.Combobox(self, textvariable=distroStringVar, state='readonly', width=maxWidth)
        self.comboBox['values'] = longnameList
        self.comboBox.pack()
        
        topLevelNotebook = ttk.Notebook(self)
        topLevelNotebook.pack()

        # the "graph reports" notebook tab
        nbGraphReports = ttk.Notebook(topLevelNotebook)
        nbGraphReports.pack()
        topLevelNotebook.add(nbGraphReports, text='Graph Reports')

        report = IndividualReports.StatsDistroHistogram(nbGraphReports, rawData, distro)
        nbGraphReports.add(report, text="Statistical Distribution Histogram")

        report = IndividualReports.DataHistogram(nbGraphReports, rawData)
        nbGraphReports.add(report, text="Data Histogram")

        # the "text reports" notebook tab
        nbTextReports = ttk.Notebook(topLevelNotebook)
        nbTextReports.pack()
        topLevelNotebook.add(nbTextReports, text='Text Reports')
                
        report = IndividualReports.ParameterListing(nbTextReports, distroList[0])
        nbTextReports.add(report, text="Fitted Parameters")

        report = IndividualReports.DataArrayStatisticsReport(nbTextReports, "Data Statistics", rawData)
        nbTextReports.add(report, text="Data Statistics")

        report = IndividualReports.ScipyInfoReport(nbTextReports, distroList[0])
        nbTextReports.add(report, text="Scipy Info")



if __name__ == "__main__":
    root = tk.Tk()
    interface = ResultsFrame(root, 'pickledStatsDistroFile')
    
    # I could not get this to work in the interface
    # __init__() method, but it works here
    interface.comboBox.current(0) # initialize to the first item in the combobox
    interface.comboBox.selection_clear()
    interface.pack()
    root.title("Example tkStatsDistroFit -  Fitted Distribitions Results Viewer")
    
    # manually center the application window on the user display
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2) # integer division
    y = (root.winfo_screenheight() // 2) - (height // 2) # integer division
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))        
        
    root.mainloop()
