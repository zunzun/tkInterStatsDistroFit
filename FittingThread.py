import os, sys, time, threading, warnings
import scipy.stats
import pyeq3


class FittingThread(threading.Thread):
    
    def __init__(self, notify_window, inRawData, inSelectedDistributions, inSortOrderString):
        threading.Thread.__init__(self)
        self.notify_window = notify_window
        self.rawData = inRawData
        self.selectedDistributions = inSelectedDistributions
        self.sortOrderString = inSortOrderString
        
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()


    def run(self):
        resultList = []
        for distroString in self.selectedDistributions:            
            # get the scipy.stats distribution name
            distributionName = distroString.split('[')[1].split()[0]

            statusString = 'Fitting ' + distroString
            self.notify_window.queue.put(statusString)
            self.notify_window.event_generate('<<status_update>>')
            
            # ignore warnings like underflow during fitting
            with warnings.catch_warnings(record=True):
            # pyeq3 returns zero here if any errors or exceptions
                result = pyeq3.Services.SolverService.SolverService().SolveStatisticalDistribution(distributionName, self.rawData, self.sortOrderString)
                if result:
                    resultList.append(result)

        statusString = 'Fitting complete, creating graphs and reports...'
        self.notify_window.queue.put(statusString)
        self.notify_window.event_generate('<<status_update>>')
        time.sleep(0.5) # allow users a moment to see the update
        
        # the fitted equation is now the queue's event data, rather than
        # a status update string.  The event handler checks the data type
        self.notify_window.queue.put(resultList)
        self.notify_window.event_generate('<<status_update>>')
