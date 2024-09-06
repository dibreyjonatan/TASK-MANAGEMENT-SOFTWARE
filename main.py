import sys
from PyQt5.QtWidgets import QApplication,QMainWindow
from PyQt5.QtCore import Qt,QTimer,QTime,pyqtSignal, pyqtSlot,QThread
from interface import Ui_MainWindow
import pyqtgraph as pg # type: ignore
import psutil # type: ignore
import numpy as np
from time import sleep


count=0
class ComputerThread(QThread):
    fps=pyqtSignal(np.ndarray)
    def run(self):
        s=0
        while True:
            s+=1
            #s=int(QTime.currentTime().toString('ss'))
            cpu=psutil.cpu_percent()
            ram=psutil.virtual_memory().percent
            fps=[s,cpu,ram]
            self.fps.emit(np.array(fps))
            sleep(0.8)
            
class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        
        self.setupUi(self)
        self.setWindowTitle("Reading Guage Values")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        #connection des buttons
        self.CPU_button_1.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(0))
        self.CPU_button_2.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(0))
        self.RAM_button_1.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(1))
        self.RAM_button_2.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(1))
        self.WIFI_button_1.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(2))
        self.WIFI_button_2.clicked.connect(lambda : self.stackedWidget.setCurrentIndex(2))
        #configurations des guages
        #upload guage
        self.upload_guage.value_min=0
        self.upload_guage.value_max=1024
        self.upload_guage.set_scala_main_count(4)
        self.upload_guage.set_NeedleColor(255,0,0, 255)
        self.upload_guage.set_CenterPointColor(255,0,0, 255)
        self.upload_guage.initial_scale_fontsize = 35
        self.upload_guage.scale_angle_size = 180
        self.upload_guage.needle_scale_factor = 0.6
       
        #download guage
        self.download_guage.value_min=0
        self.download_guage.value_max=1024
        self.download_guage.set_scala_main_count(4)
        self.download_guage.set_NeedleColor(255,0,0, 255)
        self.download_guage.set_CenterPointColor(255,0,0, 255)
        self.download_guage.initial_scale_fontsize = 35
        self.download_guage.scale_angle_size = 180
        self.download_guage.needle_scale_factor = 0.6
       
        #defining max values
        self.maxValue=100
       
        #configurations des graphs
        self.p1=self.cpu_plot.graph.addPlot(title="CPU USAGE GRAPH")
        self.p2=self.ram_plot.graph.addPlot(title="RAM USAGE GRAPH")
        self.p3=self.wifi_plot.graph.addPlot(title="WIFI SPEED GRAPH")
        self.cpu_plot.graph.setBackground('w')
        self.ram_plot.graph.setBackground('w')
        self.wifi_plot.graph.setBackground('w')
        #adding grids to the plots 
        self.p1.showGrid(x=True, y=True)
        self.p2.showGrid(x=True,y=True)
        self.p3.showGrid(x=True,y=True)
      
        styles = {"color": "black", "font-size": "13px","font-weight":"900"}
        self.p1.setLabel('left','CPU percent',units='%',**styles)
        self.p1.setLabel('bottom','Time',units='s',**styles)
        self.p2.setLabel('left','RAM percent',units='%',**styles)
        self.p2.setLabel('bottom','Time',units='s',**styles)
        self.p3.setLabel('left','WIFI',units='B/s',**styles)
        self.p3.setLabel('bottom','Time',units='s',**styles)
    
        self.time_wifi=[]
        self.time=[]
        self.cpu_data=[]
        self.ram_data=[]
        self.upload_data=[]
        self.download_data=[]
        
        self.curve1=self.p1.plot(self.time,self.cpu_data,fillLevel=0.5,brush=((85, 170, 255, 50)), pen=pg.mkPen(color=(0, 0, 255),width=1,style=Qt.SolidLine,))
        self.curve2=self.p2.plot(self.time,self.ram_data,fillLevel=0.5,brush=((255, 0, 127, 50)),pen=pg.mkPen(color=(255,0,127),width=1,style=Qt.SolidLine))
        self.curve3=self.p3.plot(self.time_wifi,self.upload_data, pen=pg.mkPen(color=(255, 0, 0),width=1.5,style=Qt.DashLine))
        self.curve4=self.p3.plot(self.time_wifi,self.download_data,fillLevel=0.5,brush=(200,0,0,70),pen=pg.mkPen(color=(255,0,0),width=1.5, style=Qt.SolidLine))
        #parameters of wifi
        self.UPDATE_DELAY=1
        self.io = psutil.net_io_counters()
        self.bytes_sent, self.bytes_recv = self.io.bytes_sent, self.io.bytes_recv
        
        #creating the threads
        self.thread = ComputerThread()
        # connect its signal to the update_image slot
        self.thread.fps.connect(self.update_data)
        # start the thread
        self.thread.start()
        
        #adding a timer to update wifi and battery and time data
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
       
        
    @pyqtSlot(np.ndarray)
    def update_data(self,fps):
        s=fps[0]
        cpu=fps[1]
        ram=fps[2]
        self.time.append(s)
        self.cpu_data.append(cpu)
        self.ram_data.append(ram)
        self.curve1.setData(self.time,self.cpu_data)
        self.curve2.setData(self.time,self.ram_data)
        self.setValue( ram, self.labelPercentage_RAM,self.circularProgress_RAM, "rgba(255,0, 127, 255)")
        self.setValue( cpu, self.labelPercentage_CPU,self.circularProgress_CPU, "rgba(85, 170, 255, 255)")
        
           
    def get_size(self,bytes):
        for unit in ['', 'K', 'M', 'G', 'T', 'P']:
            if bytes < 1024:
               return (f"{bytes:.2f}",unit)
            bytes /= 1024
       
    def update_plot(self):
        global count
        #updating the time 
        self.time_label.setText(QTime.currentTime().toString('hh:mm:ss'))
        #update battery
        self.Battery_label.setText(str(psutil.sensors_battery().percent)+str("%"))
        #updating ipv4 and ipv6 values
        self.address_v4.setText(str(psutil.net_if_addrs()['Wi-Fi'][1].address))
        self.address_v6.setText(str(psutil.net_if_addrs()['Wi-Fi'][2].address))
        #calculating wifi values
        self.io_2 = psutil.net_io_counters()
        us, ds = self.io_2.bytes_sent - self.bytes_sent, self.io_2.bytes_recv - self.bytes_recv
        self.time_wifi.append(count)
        self.upload_data.append(us/self.UPDATE_DELAY)
        self.download_data.append(ds/self.UPDATE_DELAY)
        #plotting data
        self.curve3.setData(self.time_wifi,self.upload_data)
        self.curve4.setData(self.time_wifi,self.download_data)
        count+=1
        #set texts of data
        (value,unit)=self.get_size(us/self.UPDATE_DELAY)
        self.upload_speed.setText(value+unit+"B/s")
        #guage values 
        self.upload_guage.update_value(float(value))
        (value,unit)=self.get_size(ds/self.UPDATE_DELAY)
        self.download_speed.setText(f"{value}{unit}B/s")
        #guage values
        self.download_guage.update_value(float(value)) 
    
         # update the bytes_sent and bytes_recv for next iteration
        self.bytes_sent, self.bytes_recv = self.io_2.bytes_sent, self.io_2.bytes_recv   
        
        #reset the plot so that it should not exceed
        if count >=60 :
            self.time_wifi=[]
            self.upload_data=[]
            self.download_data=[] 
            count=0
        
    def setValue(self, value, labelPercentage, progressBarName,color):

        sliderValue = (value / self.maxValue)*100

        # HTML TEXT PERCENTAGE
        htmlText = """<p align="center"><span style=" font-size:26pt;">{VALUE}</span><span style=" font-size:20pt; vertical-align:super;">%</span></p>"""
        labelPercentage.setText(htmlText.replace(
            "{VALUE}", f"{sliderValue:.1f}"))

        # CALL DEF progressBarValue
        self.progressBarValue(value, progressBarName,color)
        
    def progressBarValue(self, value, widget,color):

        # PROGRESSBAR STYLESHEET BASE
        styleSheet = """
        QFrame{
        	border-radius: 85px;
        	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} {COLOR});
        }
        """

        # GET PROGRESS BAR VALUE, CONVERT TO FLOAT AND INVERT VALUES
        # stop works of 1.000 to 0.000
        progress = (self.maxValue - value) / self.maxValue
       
        # GET NEW VALUES
        stop_1 = str(progress - 0.001)
        stop_2 = str(progress)
       
        
        # FIX MAX VALUE
        if value == self.maxValue :
            stop_1 = "1.000"
            stop_2 = "1.000"

        # SET VALUES TO NEW STYLESHEET
        newStylesheet = styleSheet.replace("{STOP_1}", stop_1).replace(
            "{STOP_2}", stop_2).replace("{COLOR}", color)

        # APPLY STYLESHEET WITH NEW VALUES
        widget.setStyleSheet(newStylesheet)

        
       
    
   
app=QApplication(sys.argv)
run=MainWindow()
run.show()
app.exec_()
         