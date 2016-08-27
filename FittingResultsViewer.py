import pickle, io

import scipy, scipy.stats
import pyeq3

import tkinter as tk
from tkinter import ttk as ttk
from tkinter import messagebox as tk_mbox
import tkinter.scrolledtext as tk_stxt
from tkinter import filedialog as filedialog

import IndividualReports
import AdditionalInfo


class ResultsFrame(tk.Frame):
    
    def __init__(self, parent, pickledStatsDistroFile):
        tk.Frame.__init__(self, parent)

        self.graphReportsListForPDF = []
        self.textReportsListForPDF = []
        self.selectedDistroIndex = 0
        
        # first, load the fitted distributions
        resultsFile = open(pickledStatsDistroFile, 'rb')
        self.rawData, self.distroList = pickle.load(resultsFile)
        resultsFile.close()
        
        # ensure distribution list is sorted by user criteria
        self.distroList.sort(key=lambda item: item[0])

        # now dig out "long names" for user select in a combobox, and
        # then initialize "parameter names" and and additional scipy information
        longnameList = []
        maxWidth = 0
        rank = 1
        for distro in self.distroList:
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
            URL = 'scipy URL is http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.' + distro[1]['distributionName'] + '.html\n\n'
            try:
                distro[1]['scipyInfo'] = URL + item.__doc__
            except:
                distro[1]['scipyInfo'] = URL + 'No additional information available from scipy.'

        # a combo box for user selection of fitted distributions
        distroStringVar = tk.StringVar()
        self.comboBox = ttk.Combobox(self, textvariable=distroStringVar, state='readonly', width=maxWidth)
        self.comboBox['values'] = longnameList
        self.comboBox.bind('<<ComboboxSelected>>', self.onComboBoxSelect)
        self.comboBox.pack()
        
        topLevelNotebook = ttk.Notebook(self)
        topLevelNotebook.pack()

        # the "graph reports" notebook tab
        self.nbGraphReports = ttk.Notebook(topLevelNotebook)
        self.nbGraphReports.pack()
        topLevelNotebook.add(self.nbGraphReports, text='Graph Reports')

        report = IndividualReports.StatsDistroHistogram(self.nbGraphReports, self.rawData, self.distroList[0])
        self.graphReportsListForPDF.append(report[1])
        self.nbGraphReports.add(report[0], text="Statistical Distribution Histogram")
        
        report = IndividualReports.DataHistogram(self.nbGraphReports, self.rawData)
        self.graphReportsListForPDF.append(report[1])
        self.nbGraphReports.add(report[0], text="Data Histogram")

        # the "text reports" notebook tab
        self.nbTextReports = ttk.Notebook(topLevelNotebook)
        self.nbTextReports.pack()
        topLevelNotebook.add(self.nbTextReports, text='Text Reports')
                
        report = IndividualReports.ParametersAndFitStatistics(self.nbTextReports, self.distroList[0])
        reportTitle = "Parameters and Fit Statistics"
        self.nbTextReports.add(report, text=reportTitle)
        self.textReportsListForPDF.append([report.get("1.0", tk.END), reportTitle])

        report = IndividualReports.DataArrayStatisticsReport(self.nbTextReports, "Data Statistics", self.rawData)
        reportTitle = "Data Statistics"
        self.nbTextReports.add(report, text=reportTitle)
        self.textReportsListForPDF.append([report.get("1.0", tk.END), reportTitle])

        report = IndividualReports.ScipyInfoReport(self.nbTextReports, self.distroList[0])
        reportTitle = "Scipy Info"
        self.nbTextReports.add(report, text=reportTitle)
        self.textReportsListForPDF.append([report.get("1.0", tk.END), reportTitle])

        # the "additional information" notebook tab
        nbAdditionalInfo = ttk.Notebook(topLevelNotebook)
        nbAdditionalInfo.pack()
        topLevelNotebook.add(nbAdditionalInfo, text='Additional Information')
                
        scrolledText = tk_stxt.ScrolledText(nbAdditionalInfo, width=IndividualReports.textboxWidth, height=IndividualReports.textboxHeight, wrap=tk.WORD)
        nbAdditionalInfo.add(scrolledText, text="Author History")
        scrolledText.insert(tk.END, AdditionalInfo.author)

        scrolledText = tk_stxt.ScrolledText(nbAdditionalInfo, width=IndividualReports.textboxWidth, height=IndividualReports.textboxHeight, wrap=tk.WORD)
        nbAdditionalInfo.add(scrolledText, text="Web Links")
        scrolledText.insert(tk.END, AdditionalInfo.links)

        # the "Save To PDF" tab
        fsaveFrame = tk.Frame(self)
            
        # this label is only for visual spacing
        l = tk.Label(fsaveFrame, text="\n\n\n")
        l.pack()

        buttonSavePDF = tk.Button(fsaveFrame, text="Save To PDF", command=self.createPDF, height=0, width=0)
        buttonSavePDF.pack()
        topLevelNotebook.add(fsaveFrame, text="Save To PDF File")


    def updateStatisticalDistributionNotebookTabs(self, selectedDistroIndex):
        self.selectedDistroIndex = selectedDistroIndex
        
        # create new graph
        report = IndividualReports.StatsDistroHistogram(self.nbGraphReports, self.rawData, self.distroList[selectedDistroIndex])
        
        # replace the existing graph's tab with the new one
        #use selectedTabIndex to maintain display if currently selected tab
        selectedTabIndex = self.nbGraphReports.index(self.nbGraphReports.select())
        self.nbGraphReports.forget(0)
        self.nbGraphReports.insert(0, report[0], text="Statistical Distribution Histogram")
        
        self.nbGraphReports.select(selectedTabIndex)
        
        # histogram of raw data does not change
        self.graphReportsListForPDF[0] = report[1]

        # replace the existing text info tabs with the new ones
        selectedTabIndex = self.nbTextReports.index(self.nbTextReports.select())
        self.nbTextReports.forget(2)
        self.nbTextReports.forget(0)
        report = IndividualReports.ParametersAndFitStatistics(self.nbTextReports, self.distroList[selectedDistroIndex])
        self.nbTextReports.insert(0, report, text="Parameters and Fit Statistics")
        self.textReportsListForPDF[0][0] = report.get("1.0", tk.END)
        
        # raw data statistics unchanged
        
        report = IndividualReports.ScipyInfoReport(self.nbTextReports, self.distroList[selectedDistroIndex])
        self.nbTextReports.add(report, text="Scipy Info")
        self.textReportsListForPDF[2][0] = report.get("1.0", tk.END)
        
        self.nbTextReports.select(selectedTabIndex)


    def onComboBoxSelect(self, event):
        self.comboBox.selection_clear() # widget appearance only, does not change selection
        self.updateStatisticalDistributionNotebookTabs(self.comboBox.current())


    def createPDF(self):
        try:
            import reportlab
        except:
            tk_mbox.showerror("Error", "\nCould not import reportlab.\n\nPlease install using the command\n\n'pip3 install reportlab'")
            return

        # see https://bugs.python.org/issue22810 for the
        # "alloc: invalid block" error on application close 
        fName = filedialog.asksaveasfilename(
                                filetypes =(("PDF Files", "*.pdf"),("All Files","*.*")),
                                title = "PDF file name"
                                )
        if fName:
            import pdfCode
            pdfCode.CreatePDF(fName,
                              self.distroList[self.selectedDistroIndex][1]['longName'],
                              self.graphReportsListForPDF,
                              self.textReportsListForPDF
                              )
            tk_mbox.showinfo("Success", "\nSuccessfully created PDF file.")
    


if __name__ == "__main__":
    root = tk.Tk()
    interface = ResultsFrame(root, 'pickledStatsDistroFile')
    
    # I could not get this to work in the ResultsFrame class'
    # __init__() method, but it works here
    interface.comboBox.current(0) # initialize to the first item in the combobox
    interface.comboBox.selection_clear() # widget appearance only, does not change selection
    
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
