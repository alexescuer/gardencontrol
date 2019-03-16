import time
import datetime
import requests
import json
import threading
import logging
import RPi.GPIO as GPIO
try:
    import tkinter as tk # Python 3.x
    import tkinter.scrolledtext as ScrolledText
except ImportError:
    import Tkinter as tk # Python 2.x
    import ScrolledText

class TextHandler(logging.Handler):
        # This class allows you to log to a Tkinter Text or ScrolledText widget
        #constructor method for this class
        
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # create the empty text variable that we will use to log the info
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            #take the text variable and we configure the format of the log
            self.text.configure(state='normal')
            #search the end of the log, insert the message and jump to the next line
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)

# Here we create the global variables that will store the user input.
# By default we will use the value 2 days
global WaterDays
WaterDays = 2
# This will store the status of the button "water now" 0 is off 1 means action
global ButtonWaterInput
ButtonWaterInput = 0

class buttons():
    #This class contain the functions triggered with the menu buttons
    
    def LightsOff():
            # lights off please
            loff = GpioAction.LigthsOff()
    
    def LightsOn():
            # lights on please
            # not used
            lon = GpioAction.LigthsOn()

    def WaterNow():
            # water please
            wn = GpioAction.OpenCloseWater()
            
    def Water2Days():
            # change the global variable with 2 days
            global WaterDays
            WaterDays = 2
            # log
            timeStr = time.asctime()
            msg = timeStr + ' - Change the water timing. Water every TWO days'
            logging.info(msg)

    def Water4Days():
            # change the global variable with 4 days
            global WaterDays
            WaterDays = 4
            # log
            timeStr = time.asctime()
            msg = timeStr + ' - Change the water timing. Water every FOUR days'
            logging.info(msg)

    def Water8Days():
            # change the global variable with 8 days
            global WaterDays
            WaterDays = 8
            # log
            timeStr = time.asctime()
            msg = timeStr + ' - Change the water timing. Water every EIGHT days'
            logging.info(msg)
     
class myGUI(tk.Frame):
        # This class defines the graphical user interface
        # constructor method for this class
        
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.root = parent
        # call the build GUI method in this class
        self.build_gui()

    def build_gui(self):                    
        # Build GUI with tkinter library. 5 columns to place each button
        self.root.title('Garden Control 1.0')
        self.root.option_add('*tearOff', 'FALSE')
        self.grid(column=0, row=1, sticky='ew', columnspan=5)
        self.grid_columnconfigure(0, weight=1, uniform='a')
        self.grid_columnconfigure(1, weight=1, uniform='a')
        self.grid_columnconfigure(2, weight=1, uniform='a')
        self.grid_columnconfigure(3, weight=1, uniform='a')
        self.grid_columnconfigure(4, weight=1, uniform='a')
 
        #B utton menu. if added any must change columnconfigure and columnspan
        boton1 = tk.Button(text ="Apagar luces")
        boton1.configure(font='TkFixedFont', command=buttons.LightsOff)
        boton1.grid(column=0, row=0, sticky='w')

        boton2 = tk.Button(text ="Regar Ahora")
        boton2.configure(font='TkFixedFont', command=buttons.WaterNow)
        boton2.grid(column=1, row=0, sticky='w')

        boton3 = tk.Button(text ="x2 dias")
        boton3.configure(font='TkFixedFont', command=buttons.Water2Days)
        boton3.grid(column=2, row=0, sticky='w')

        boton4 = tk.Button(text ="x4 dias")
        boton4.configure(font='TkFixedFont', command=buttons.Water4Days)
        boton4.grid(column=3, row=0, sticky='w')

        boton5 = tk.Button(text ="x8 dias")
        boton5.configure(font='TkFixedFont', command=buttons.Water8Days)
        boton5.grid(column=4, row=0, sticky='w')

        # calling Text widget from tkinter to display log info
        st = ScrolledText.ScrolledText(self, state='disabled')
        # define font
        st.configure(font='TkFixedFont')
        # define position of the text widget
        st.grid(column=0, row=2, sticky='w', columnspan=5)
        
        # Here we invoque the TextHandler Class created before
        text_handler = TextHandler(st)

        # Log file configuration. Here we define the file we will store the log
        logging.basicConfig(filename='log_file.log',
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s - %(message)s')        

        # Add the handler to logger
        logger = logging.getLogger()        
        logger.addHandler(text_handler)

class GpioAction():
        # here we have all gpio actions and configurations, we define the pins used
        WaterPin = 11
        LightPin = 7

        def __init__(self):
            self.time = time

        def OpenWater():
            # Maybe it is not the most ortodox way to control GPIO but is rock solid
            # First we define that GPIO will be using BOARD pin numbers
            GPIO.setmode(GPIO.BOARD)
            # We declare the pin we will use as an output
            GPIO.setup(GpioAction.WaterPin,GPIO.OUT)
            # Turn relay ON
            GPIO.output(GpioAction.WaterPin, GPIO.HIGH)
           
            #log
            timeStr = time.asctime()
            msg = timeStr + ' - Open water'
            logging.info(msg)
            
        def CloseWater():    
            # Maybe it is not the most ortodox way to control GPIO but is rock solid
            # First we define that GPIO will be using BOARD pin numbers
            GPIO.setmode(GPIO.BOARD)
            # We declare the pin we will use as an output
            GPIO.setup(GpioAction.WaterPin,GPIO.OUT)
            # Turn relay OFF
            GPIO.output(GpioAction.WaterPin, GPIO.LOW)
            # Lets clean the output used so no voltage is transmited
            # Not sure why but this was the only method to 100% turn off the relay
            GPIO.cleanup(GpioAction.WaterPin)
            
            #log
            timeStr = time.asctime()
            msg = timeStr + ' - Close water'
            logging.info(msg)
        
        def OpenCloseWater():
            # This will perform both actions open-close. We don't rehuse code becasue the closing action is not the same
            # First we define that GPIO will be using BOARD pin numbers
            GPIO.setmode(GPIO.BOARD)
            # We declare the pin we will use as an output
            GPIO.setup(GpioAction.WaterPin,GPIO.OUT)
            # Turn relay ON
            GPIO.output(GpioAction.WaterPin, GPIO.HIGH)

            #log
            timeStr = time.asctime()
            msg = timeStr + ' - Open water'
            logging.info(msg)

            # we will sleep for 1800 seconds (30min) every time to water the plants
            time.sleep(1800)

            # Turn relay OFF
            GPIO.output(GpioAction.WaterPin, GPIO.LOW)
            # Lets clean the output used so no voltage is transmited
            # Not sure why but this was the only method to 100% turn off the relay
            GPIO.cleanup(GpioAction.WaterPin)

            
        def LigthsOn():
            # Maybe it is not the most ortodox way to control GPIO but is rock solid
            # First we define that GPIO will be using BOARD pin numbers
            GPIO.setmode(GPIO.BOARD)
            # We declare the pin we will use as an output
            GPIO.setup(GpioAction.LightPin,GPIO.OUT)
            # Turn relay ON
            GPIO.output(GpioAction.LightPin, GPIO.HIGH)
          
            #log
            timeStr = time.asctime()
            msg = timeStr + ' - Ligths ON'
            logging.info(msg)
            
        def LigthsOff():
            # Maybe it is not the most ortodox way to control GPIO but is rock solid
            # First we define that GPIO will be using BOARD pin numbers
            GPIO.setmode(GPIO.BOARD)
            # We declare the pin we will use as an output
            GPIO.setup(GpioAction.LightPin,GPIO.OUT)
            # Turn relay OFF
            GPIO.output(GpioAction.LightPin, GPIO.LOW)
            # Lets clean the output used so no voltage is transmited
            # Not sure why but this was the only method to 100% turn off the relay
            GPIO.cleanup(GpioAction.LightPin)

            #log
            timeStr = time.asctime()
            msg = timeStr + ' - Ligths OFF'
            logging.info(msg)
            
      
class Sleeping():
            # This class is used for making all calcultions to sleep in the diferent threads used
        def __init__(self, Now, FixedHour, FutureTime, FixedMinute, Days):
            self.FutureTime = FutureTime
            self.Now = Now
            self.FixedHour = FixedHour
            self.FixedMinute = FixedMinute
            self.Days = Days
            
        def FixedSleep(FixedHour,FixedMinute):
            # This method is for sleeping certain amount of hours and minutes
            # First find the time now
            Now = datetime.datetime.today()
            # the future is...
            FutureTime = datetime.datetime(Now.year,Now.month,Now.day,FixedHour,FixedMinute)
            if Now.hour >= FixedHour:
                FutureTime += datetime.timedelta(days=1)
            # Sleep the time between the future and now
            time.sleep((FutureTime-Now).seconds)

        def DaysSleep(Days):
            # This is for those situations that we need to sleep several days
            # one day = 86400 seconds
            DaysToSleep = Days * 86400
            time.sleep(DaysToSleep)
            
class API():
            # This is the class that conects to the API that gives us the sunset time everyday
        def __init__(self, ConectionTime):
            self.ConectionTime = Conection()

        def Conection():
            # log in to the API. This URL icnludes latitude and longitude. please check the api for more info.
            url = 'https://api.sunrise-sunset.org/json?lat=36.7201600&lng=-4.4203400'
            try:
                apidata = requests.get(url).json()
            except requests.exceptions.RequestException as error:  
                # we log this info
                timeStr = time.asctime()
                msg = timeStr + ' - API Error: ' + error
                logging.info(msg)

            # Take te sunset value time
            sunset = apidata['results']['sunset']
            # We clean the format with split to be able to use it for the schedule.
            hours, minutes, seconds = sunset.split(":")
            # we add 12 to have a 24h format not 12h and we make sure it is an int
            hoursint = int(hours) + 12
            # we make sure minutes are also an int
            minutesint = int(minutes)
            # we return a list value
            return SunsetTime = [hoursint, minutesint]
          
# Now we define the diferent threads that we will use.

def WorkerWater():
    # This is the thread that will take care of the water
    # We request de global variable that stores the data input from user. Default will be 2 days
    global WaterDays
    while True:
        # here we will loop the open water and close water tasks.
        # This is the "adjustment" sleep.
        # we use this to be sure that we will always open water at sunset
        # lets request to the API the sunset time and pass it  to the sleeping class
        SunsetTime = API.Conection()
        FirstTask = Sleeping.FixedSleep(SunsetTime[0],SunsetTime[1])
        
        # water please!
        SecondTask = GpioAction.OpenCloseWater()
        
        # sleep for the amount of days desired by the user
        ThirdTask = Sleeping.DaysSleep(WaterDays)   
        
        
def WorkerLigths():
    # This is the thread for the lights
    while True:
        # we will sleep until the time to switch on the ligths
        # lets call the global variable with the sunset time and pass it to the sleeping class
        SunsetTime = API.Conection()

        # we log this info
        timeStr = time.asctime()
        msg = timeStr + ' - API Conected successfully. Sunset: ' + SunsetTime
        logging.info(msg)

        FirstTask = Sleeping.FixedSleep(SunsetTime[0],SunsetTime[1])

        #Lights On please!
        SecondTask = GpioAction.LigthsOn()

        # now we will wait until the time to switch off the ligths at 23 pm
        ThirdTask = Sleeping.FixedSleep(23,00)

        #Lights Off please!
        FourthTask = GpioAction.LigthsOff()  

def main():
      
    # start the Tkinter GUI
    root = tk.Tk()
    myGUI(root)
        
    # start the threads that execute the workers
    # lights worker
    Worker1 = threading.Thread(target=WorkerLigths, args=[])
    Worker1.start()
    # water worker
    Worker2 = threading.Thread(target=WorkerWater, args=[])
    Worker2.start()

    # put in mainloop GUI and worker threads
    root.mainloop()
    Worker1.join()
    Worker2.join()


#here we start the engine
main()
 

