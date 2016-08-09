import os, sys, io, queue, pickle, time, inspect
import scipy, scipy.stats
import pyeq3

import matplotlib # ensure this dependency imports for later use in fitting results

import tkinter as tk
from tkinter import messagebox as tk_mbox
import tkinter.scrolledtext as tk_stxt

import ExampleData
#import FittingThread


class InterfaceFrame(tk.Frame):
    
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        
        self.queue = queue.Queue()

        self.sortOrderStringVar = tk.StringVar()

        # ROW 0 - empty labels as visual buffers
        row, col = (0, 0) # left edge
        l = tk.Label(self, text="   ")
        l.grid(column=col, row=row)
        row, col = (0, 2) # right edge
        l = tk.Label(self, text="     ")
        l.grid(column=col, row=row)
        
        # ROW 1 - text data entry label
        # no "self" needed as no later references exist
        row, col = (1, 1)
        l = tk.Label(self, text="--- Text Data Editor ---", font="-weight bold")
        l.grid(column=col, row=row)
        
        # ROW 2 - text data input, no line wrap
        row, col = (2, 1)
        self.text_1D = tk_stxt.ScrolledText(self, width=40, height=12, wrap=tk.NONE)
        self.text_1D.insert(tk.END, ExampleData.exampleData1D) # inital text data
        self.text_1D.grid(column=col, row=row, sticky=(tk.N, tk.W, tk.E, tk.S))

        # ROW 3 - empty label as visual buffer
        row, col = (3, 0)
        l = tk.Label(self, text=" ")
        l.grid(column=col, row=row)

        # ROW 4 - text data entry label
        # no "self" needed as no later references exist
        row, col = (4, 1)
        l = tk.Label(self, text="--- Multiple-Select Statistical Distributions ---", font="-weight bold")
        l.grid(column=col, row=row)

        # ROW 5 - statistical distribution selection
        row, col = (5, 1)
        f = tk.Frame(self)
        f.grid(column=col, row=row)
        vScrollbar = tk.Scrollbar(f, orient=tk.VERTICAL)
        self.distListBox = tk.Listbox(f, selectmode=tk.EXTENDED, yscrollcommand=vScrollbar.set)
        self.distListBox.config(width=0) # makes width auto-resize to fit nicely
        vScrollbar.config(command=self.distListBox.yview)
        vScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.distListBox.pack(side=tk.LEFT)
        for item in inspect.getmembers(scipy.stats):
            if isinstance(item[1], scipy.stats.rv_continuous):
                # dig out a "long name" for user display
                longName = io.StringIO(item[1].__doc__).readlines()[0]
                if longName[:2] == 'A ':
                    longName = longName[2:]
                if longName[:3] == 'An ':
                    longName = longName[3:]
                longname = longName[:longName.find(' continuous')]
                self.distListBox.insert(tk.END, longname + ' [' + item[0] + ' in scipy.stats]')
        
        # ROW 6 - empty label as visual buffer
        row, col = (6, 0)
        l = tk.Label(self, text=" ")
        l.grid(column=col, row=row)
            
        # ROW 7 - sort order selection label
        # no "self" needed as no later references exist
        row, col = (7, 1)
        l = tk.Label(self, text="--- Results Sort Order ---", font="-weight bold")
        l.grid(column=col, row=row)
        
        # ROW 8 - sort order selection radio buttons
        row, col = (8, 1)
        f = tk.Frame(self)
        f.grid(column=col, row=row)        
        rb = tk.Radiobutton(f, text='Negative Log Likelihood', variable=self.sortOrderStringVar, value='NegLogLikelihood')
        rb.pack(anchor=tk.W)
        rb.select() # default initial selection
        rb = tk.Radiobutton(f, text='Akaike Information Criterion (AIC)', variable=self.sortOrderStringVar, value='AIC')
        rb.pack(anchor=tk.W)
        rb = tk.Radiobutton(f, text='AIC corrected (AICc) - Burnham and Anderson', variable=self.sortOrderStringVar, value='AICc_BA')
        rb.pack(anchor=tk.W)

        # ROW 9 - empty label as visual buffer
        row, col = (9, 0)
        l = tk.Label(self, text=" ")
        l.grid(column=col, row=row)

        # ROW 10 - fitting button
        row, col = (10, 1)
        self.buttonFit_1D = tk.Button(self, text="Fit Statistical Distributions", command=self.OnFitDistributions)
        self.buttonFit_1D.grid(column=col, row=row)
    
        # ROW 11 - empty label as visual buffer
        row, col = (11, 0)
        l = tk.Label(self, text=" ")
        l.grid(column=col, row=row)
        
        # now bind our custom ""status_update"" event to the handler function
        self.bind('<<status_update>>', self.StatusUpdateHandler)


    def OnFitDistributions(self):
        # get a list of the selected statistical distribution names
        selectedDistributions = [self.distListBox.get(idx) for idx in self.distListBox.curselection()]
        if len(selectedDistributions) < 1:
            tk_mbox.showerror("Error", "You have not selected any statistical distributions.")
            return
        
        # convert text to numeric data checking for log of negative numbers, etc.
        textData = self.text_1D.get("1.0", tk.END)
        self.equationBase = pyeq3.IModel.IModel()
        self.equationBase._dimensionality = 1
        pyeq3.dataConvertorService().ConvertAndSortColumnarASCII(textData, self.equationBase, False)
        dataCount = len(self.equationBase.dataCache.allDataCacheDictionary['IndependentData'])
        if dataCount < 2:
            tk_mbox.showerror("Error", "A minimum of two data points is needed, you have supplied " + repr(dataCount) + ".")
            return
                
        # then sort order for results
        sortOrderString = self.sortOrderStringVar.get()
        
        # Now the status dialog is used. Disable fitting buttons until thread completes
        self.buttonFit_1D.config(state=tk.DISABLED)
        
        # create simple top-level text dialog to display status as fitting progresses
        # when the fitting thread completes, it will close the status box
        self.statusBox = tk.Toplevel()
        self.statusBox.title("Fitting Status")
        self.statusBox.text = tk.Text(self.statusBox)
        self.statusBox.text.pack()
        
        # in tkinter the status box must be manually centered
        self.statusBox.update_idletasks()
        width = self.statusBox.winfo_width()
        height = self.statusBox.winfo_height()
        x = (self.statusBox.winfo_screenwidth() // 2) - (width // 2) # integer division
        y = (self.statusBox.winfo_screenheight() // 2) - (height // 2) # integer division
        self.statusBox.geometry('{}x{}+{}+{}'.format(width, height, x, y))        

        # thread will automatically start to run
        # "status update" handler will re-enable buttons
        #self.fittingWorkerThread = FittingThread.FittingThread(self, self.equation)


    # When "status_update" event is generated, get
    # text data from queue and display it to the user.
    # If the queue data is not text, it is the fitted equation.
    def StatusUpdateHandler(self, *args):
        data = self.queue.get_nowait()
        
        if type(data) == type(''): # text is used for status box display to user
            self.statusBox.text.insert(tk.END, data + '\n')
        else: # the queue data is now the fitted equation.
            # write the fitted equation to a pickle file.  This
            # allows the possibility of archiving the fitted equations
            pickledEquationFile = open("pickledEquationFile", "wb")
            pickle.dump(data, pickledEquationFile)
            pickledEquationFile.close()
    
            # view fitting results
            # allow multiple result windows to open for comparisons
            os.popen(sys.executable + ' FittingResultsViewer.py')
            
            # give the system a few seconds to start the reporting application
            time.sleep(5.0)

            # re-enable fitting buttons
            self.buttonFit_1D.config(state=tk.NORMAL)
        
            # destroy the now-unused status box
            self.statusBox.destroy()
            


if __name__ == "__main__":
    root = tk.Tk()
    interface = InterfaceFrame(root)
    interface.pack()
    root.title("tkinterDistributionFit - Fitting Interface")
    
    # manually center the application window on the user display
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2) # integer division
    y = (root.winfo_screenheight() // 2) - (height // 2) # integer division
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))        
    
    root.mainloop()
