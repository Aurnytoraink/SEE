import sys
from adc import ADC
import numpy as np
from scipy.signal import find_peaks
from enum import Enum

from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QWidget, QLabel, QPushButton, QGridLayout
from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSlot
from PyQt5.QtChart import QChart, QChartView
from PyQt5.QtGui import QPixmap

class Emoji(Enum):
    HAPPY = "emoji/smiling-face.png"
    DEAD = "emoji/dead.png"
    HOT = "emoji/hot-face.png"
    SLEEP = "emoji/sleeping-face.png"
    LUNGS = "emoji/lungs.png"

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()

        self.setObjectName("MainWindow")
        self.resize(256, 256)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QSize(256, 256))
        self.setMaximumSize(QSize(256, 256))
        self.centralwidget = QWidget(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setAutoFillBackground(True)
        
        self.grid = QGridLayout()
        
        self.bpm_label = QLabel(self.centralwidget)
        self.bpm_label.setStyleSheet("font: 700 18pt \"Cantarell\";")
        self.bpm_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.bpm_label.setObjectName("bpm_label")
        self.bpm_label.setText("XXX bpm")
        self.grid.addWidget(self.bpm_label,1,2,1,1)

        self.oxygen_label = QLabel(self.centralwidget)
        self.oxygen_label.setStyleSheet("font: 700 18pt \"Cantarell\";")
        self.oxygen_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.oxygen_label.setObjectName("oxyge_label")
        self.oxygen_label.setText("XXX %")
        self.grid.addWidget(self.oxygen_label,2,2,1,1)
        
        self.img_bpm = QPixmap(Emoji.HAPPY.value)
        self.img_bpm_label = QLabel(self.centralwidget)
        self.img_bpm_label.setStyleSheet("font: 700 24pt \"Cantarell\";")
        self.img_bpm_label.setPixmap(self.img_bpm.scaled(110,110,Qt.KeepAspectRatio))
        self.img_bpm_label.setAlignment(Qt.AlignCenter|Qt.AlignTrailing|Qt.AlignVCenter)
        
        self.grid.addWidget(self.img_bpm_label,1,1,1,1)
        
        self.oxygen_img = QPixmap(Emoji.LUNGS.value)
        self.img_oxygen_label = QLabel(self.centralwidget)
        self.img_oxygen_label.setPixmap(self.oxygen_img.scaled(110,110,Qt.KeepAspectRatio))
        self.img_oxygen_label.setAlignment(Qt.AlignCenter|Qt.AlignTrailing|Qt.AlignVCenter)
        
        self.grid.addWidget(self.img_oxygen_label,2,1,1,1)

#         self.pushButton = QPushButton(self.centralwidget)
#         self.pushButton.setObjectName("pushButton")
#         self.pushButton.setText("Afficher le graph")
#         self.grid.addWidget(self.pushButton,3,1,1,2)

        widget = QWidget()
        widget.setLayout(self.grid)
        self.setCentralWidget(widget)

        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.setWindowTitle("BPMmeter")

        self.adc = ADC(0)
        self.value = np.array([])
        
        self.update_value_timer = QTimer()
        self.update_value_timer.setInterval(100)
        self.update_value_timer.timeout.connect(self.acquerir)
        
        self.acquisition_time = QTimer()
        self.acquisition_time.setInterval(5000)
        self.acquisition_time.timeout.connect(self.update_BPM_value)
        
        self.update_value_timer.start()
        self.acquisition_time.start()
        
        self.tries = 0
        
        
        
    @pyqtSlot()
    def acquerir(self):
        value = self.adc.convert_values()
        self.value = np.append(self.value,[value])
        #print("acquisitiooooooooooooooooooooon")
        if self.tries > 5:
            self.bpm_label.setText("T'es mort ?\nPlace ton doigt")
            self.img_bpm.load(Emoji.DEAD.value)
            self.img_bpm_label.setPixmap(self.img_bpm.scaled(110,110,Qt.KeepAspectRatio))
    
    @pyqtSlot()
    def update_BPM_value(self):
        """En gros ici, dès que le timer run out, on procède au calcul
        """
        print("j'update")
        if self.value.size != 0:
            data = self.value.copy()
            
            self.update_value_timer.stop()
            
            print(data)
            
            data = data - np.average(data)
            data = np.correlate(data,data,mode='full')
            data = data[data.size // 2:]
            #Find peaks
            peaks, _ = find_peaks(data, height=0.2, distance=1)
            
            times = np.linspace(0, data.size*0.1, data.size)
                       
            pulse = times[peaks][1:len(peaks)] - times[peaks][0:len(peaks)-1]
            
            print(peaks,times,pulse)
            
            if pulse.size > 1:
                self.tries = 0
                bpm = 60/np.average(pulse)
                txt = str(int(bpm))
                self.bpm_label.setText(txt + "bpm")
                self.change_picture(bpm)
            else:
                self.tries += 1
                
                
            
            
            self.value = np.array([])
            
            self.update_value_timer.start()
            
    def change_picture(self,bpm):
        if bpm < 60:
            self.img_bpm.load(Emoji.SLEEP.value)
        elif bpm >= 60 and bpm <= 100:
            self.img_bpm.load(Emoji.HAPPY.value)
        else:
            self.img_bpm.load(Emoji.HOT.value)
        self.img_bpm_label.setPixmap(self.img_bpm.scaled(110,110,Qt.KeepAspectRatio))
