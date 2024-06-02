import sys
from adc import ADC
import numpy as np
from scipy.signal import find_peaks
from enum import Enum

from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QWidget, QLabel, QPushButton, QGridLayout
from PyQt5.QtCore import QSize, Qt, QTimer, pyqtSlot
from PyQt5.QtChart import QChart, QChartView
from PyQt5.QtGui import QPixmap
from qtwidgets import AnimatedToggle

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
        self.img_bpm_label.setPixmap(self.img_bpm.scaled(100,100,Qt.KeepAspectRatio))
        self.img_bpm_label.setAlignment(Qt.AlignCenter|Qt.AlignTrailing|Qt.AlignVCenter)
        
        self.grid.addWidget(self.img_bpm_label,1,1,1,1)
        
        self.oxygen_img = QPixmap(Emoji.LUNGS.value)
        self.img_oxygen_label = QLabel(self.centralwidget)
        self.img_oxygen_label.setPixmap(self.oxygen_img.scaled(100,100,Qt.KeepAspectRatio))
        self.img_oxygen_label.setAlignment(Qt.AlignCenter|Qt.AlignTrailing|Qt.AlignVCenter)
        self.grid.addWidget(self.img_oxygen_label,2,1,1,1)
        
        self.toggle = AnimatedToggle(
            checked_color="#FF5733",
            pulse_checked_color="#2ECC71"
        )
        self.toggle.stateChanged.connect(self.on_button_clicked)
        self.grid.addWidget(self.toggle,3,1,1,1)
        
        label = QLabel(self.centralwidget)
        label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        label.setText("Oxymétrie")
        self.grid.addWidget(label,3,2,1,1)

        widget = QWidget()
        widget.setLayout(self.grid)
        self.setCentralWidget(widget)

        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.setWindowTitle("BPMmeter")

        self.adc = ADC(0)
        self.bpm_value = np.array([])
        self.oxy_value = np.array([])
        self._is_oxy = False
        
        self.update_value_timer = QTimer()
        self.update_value_timer.setInterval(125)
        self.update_value_timer.timeout.connect(self.acquerir)
        
        self.acquisition_time = QTimer()
        self.acquisition_time.setInterval(5000)
        self.acquisition_time.timeout.connect(self.update_labels)
        
        self.update_value_timer.start()
        self.acquisition_time.start()
        
        self.tries = 0
    
    @pyqtSlot()
    def on_button_clicked(self):
        if self.toggle.isChecked():
            self._is_oxy = True
        else:
            self._is_oxy = False
        
    @pyqtSlot()
    def acquerir(self):       
        if self._is_oxy:
            self.update_value_timer.setInterval(250)
            QTimer.singleShot(125, self.acquerir_bpm)
            self.acquerir_oxy()
        else:
            self.update_value_timer.setInterval(125)
            self.acquerir_bpm()
            self.oxygen_label.setText("XXX %")
        
        if self.tries > 3:
            self.bpm_label.setText("T'es mort ?\nPlace\nton doigt")
            self.img_bpm.load(Emoji.DEAD.value)
            self.img_bpm_label.setPixmap(self.img_bpm.scaled(100,100,Qt.KeepAspectRatio))
        
        
    
    def acquerir_bpm(self):
        self.adc.set_LED(False)
        self.bpm_value = np.append(self.bpm_value,[self.adc.convert_values()])

        
    def acquerir_oxy(self):
        self.adc.set_LED(True)
        self.oxy_value = np.append(self.oxy_value,[self.adc.convert_values()])


    @pyqtSlot()
    def update_labels(self):
        """En gros ici, dès que le timer run out, on procède au calcul
        """
        print("j'update")
        if self.bpm_value.size != 0:
            data_bpm = self.bpm_value.copy()
            data_oxy = self.oxy_value.copy()
            
            self.update_value_timer.stop()
            
            print(data_oxy)
            
            try:
                oxy = np.average((data_oxy/np.average(data_oxy))/(data_bpm/np.average(data_bpm)))*100
                txt = str(int(oxy))
                self.oxygen_label.setText(txt + "%")
            except:
                pass
            
            data_bpm = data_bpm - np.average(data_bpm)
            data_bpm = np.correlate(data_bpm,data_bpm,mode='full')
            data_bpm = data_bpm[data_bpm.size // 2:]
            
            #Find peaks
            peaks, _ = find_peaks(data_bpm, height=0.2, distance=1)
            times = np.linspace(0, data_bpm.size*0.1, data_bpm.size)
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
                
            self.bpm_value = np.array([])
            self.oxy_value = np.array([])
            self.update_value_timer.start()
            
    def change_picture(self,bpm):
        if bpm < 60:
            self.img_bpm.load(Emoji.SLEEP.value)
        elif bpm >= 60 and bpm <= 100:
            self.img_bpm.load(Emoji.HAPPY.value)
        else:
            self.img_bpm.load(Emoji.HOT.value)
        self.img_bpm_label.setPixmap(self.img_bpm.scaled(100,100,Qt.KeepAspectRatio))
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
