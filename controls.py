import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QMessageBox, QApplication, QFileDialog, QSlider

#from PyQt5 import QtCore, QtGui, QtWidgets
#from PyQt5.QtCore import Qt

######################################################################################################
######################################################################################################
class ALPHA_BETTA(QtWidgets.QWidget):
    """
    Kalman Gain Control
    """
    def __init__(self, pbox,  *args, **kwargs):
        super(ALPHA_BETTA, self).__init__(*args, **kwargs)

        self.parentbox = pbox
        self.font_label_13=QtGui.QFont()
        self.font_label_13.setFamily("Lucida Console")
        self.font_label_13.setPointSize(13)
        self.font_label_13.setBold(False)


        self.ALPHA_lbl   = ["1(BYPASS)", "0.5      ", "0.1    ","0.05   ", "0.01  ", "0.005 ",
                             "0.001   ", "0.0005   ", "0.00001", "0.000005 ", "0.000001 ", "0.0000005 ","0.0000001 "]
        self.ALPHA_ValueArray = [1.0,0.5,0.1,0.05,0.01,0.005,0.001,0.0005,0.0001,0.00005,0.00001,0.000005,0.000001,]
        self.ALPHA_value=self.ALPHA_ValueArray[0]
        self.ALPHA_SpinBox = QtWidgets.QSpinBox(self.parentbox)
        self.ALPHA_SpinBox.setGeometry(QtCore.QRect(2, 34, 135, 30))
        self.ALPHA_SpinBox.setObjectName("ALPHA_SpinBox")
        self.ALPHA_SpinBox.setStyleSheet("color: yellow;  border-radius: 1px; background: darkblue")
        self.ALPHA_SpinBox.setRange(0, 12)
        self.ALPHA_SpinBox.setSingleStep(1)
        self.ALPHA_SpinBox.setFont(self.font_label_13)
        self.ALPHA_SpinBox.setPrefix(self.ALPHA_lbl[0] + " " )
        self.ALPHA_SpinBox.setValue(0)
        self.ALPHA_SpinBox.valueChanged.connect(self.ALPHA_SpinBox_changed)
        self.ALPHA_SpinBoxTxt = QtWidgets.QLabel(self.parentbox)
        self.ALPHA_SpinBoxTxt.setGeometry(QtCore.QRect(10, 14, 100, 20)) ; self.ALPHA_SpinBoxTxt.setFont(self.font_label_13)
        self.ALPHA_SpinBoxTxt.setStyleSheet("color: #00FF00");   self.ALPHA_SpinBoxTxt.setText("ALPHA")
        self.ALPHA_SpinBoxTxt.setToolTip("ALPHA VAULE of ESTIMATOR")

        # Betta_SpinBox
        self.BETTA_lbl   = ["1(BYPASS)", "0.1     ", "0.01    ","0.001   ","0.0001  ", "0.00001 ", "0.000001"]
        self.BETTA_ValueArray = [1.0,0.1,0.01,0.001,0.0001,0.00001,0.000001]
        self.BETTA_value=self.BETTA_ValueArray[0]
        self.BETTA_SpinBox = QtWidgets.QSpinBox(self.parentbox)
        self.BETTA_SpinBox.setGeometry(QtCore.QRect(2, 86, 135, 30))
        self.BETTA_SpinBox.setObjectName("BETTA_SpinBox")
        self.BETTA_SpinBox.setStyleSheet("color: yellow;  border-radius: 1px; background: darkblue")
        self.BETTA_SpinBox.setRange(0, 6)
        self.BETTA_SpinBox.setSingleStep(1)
        self.BETTA_SpinBox.setFont(self.font_label_13)
        self.BETTA_SpinBox.setPrefix(self.BETTA_lbl[0] + " " )
        self.BETTA_SpinBox.setValue(0)
        self.BETTA_SpinBox.valueChanged.connect(self.BETTA_SpinBox_changed)
        self.BETTA_SpinBoxTxt = QtWidgets.QLabel(self.parentbox)
        self.BETTA_SpinBoxTxt.setGeometry(QtCore.QRect(10, 66, 100, 20)) ; self.BETTA_SpinBoxTxt.setFont(self.font_label_13)
        self.BETTA_SpinBoxTxt.setStyleSheet("color: #00FF00");   self.BETTA_SpinBoxTxt.setText("BETTA")

        self.BETTA_SpinBoxTxt.setToolTip("BETTA VAULE of ESTIMATOR")
        self.BETTA_SpinBoxTxt.hide()
        self.BETTA_SpinBox.hide()

        # ####################################################################

    #ALPHA_SpinBox_changed
    def ALPHA_SpinBox_changed(self,indexValue):
        self.ALPHA_SpinBox.setPrefix(self.ALPHA_lbl[indexValue]+" ")
        self.ALPHA_SpinBox.setValue(indexValue)
        #print("ALPHA = {:f}".format(self.ALPHA_ValueArray[indexValue]))
        self.ALPHA_value=self.ALPHA_ValueArray[indexValue]

    #BETTA_SpinBox_changed
    def BETTA_SpinBox_changed(self,indexValue):
        self.BETTA_SpinBox.setPrefix(self.ALPHA_lbl[indexValue]+" ")
        self.BETTA_SpinBox.setValue(indexValue)
        #self.listHistory.addItem("BETTA = {:f}".format(self.BETTA_ValueArray[indexValue]))
        self.BETTA_value = self.BETTA_ValueArray[indexValue]

#####################################################################################################
####################################################################################################
class GAINBOX(QtWidgets.QWidget):
    """
    Custom Qt Widget to show a power bar and dial.
    Demonstrating compound and custom-drawn widget.
    """
    def __init__(self, pbox, posy, chn,  *args, **kwargs):
        super(GAINBOX, self).__init__(*args, **kwargs)

        self.parentbox = pbox
        self.font_label_13=QtGui.QFont()
        self.font_label_13.setFamily("Lucida Console")
        self.font_label_13.setPointSize(10)
        self.font_label_13.setBold(True)

        self.GAIN_lbl   = ["00.1 ","00.2 ", "00.5 ", "01.0 ","02.0 ","05.0 ", "10.0 ", "20.0 "]
        self.GAIN_ValueArray = [0.1,0.2,0.5,1.0,2.0,5.0,10.0,20.0]

        self.CHNUMBERSTR= str('CH{:1d} x'.format(chn))
        self.GAIN_SpinBox = QtWidgets.QSpinBox(self.parentbox)
        self.GAIN_SpinBox.setFont(self.font_label_13)
        self.GAIN_SpinBox.setGeometry(QtCore.QRect(2, posy, 115, 17))
        self.GAIN_SpinBox.setObjectName("GAIN1_SpinBox")
        self.GAIN_SpinBox.setStyleSheet("color: yellow;  border-radius: 1px; background: darkblue")
        self.GAIN_SpinBox.setRange(0, 7)
        self.GAIN_SpinBox.setSingleStep(1)
        self.GAIN_SpinBox.setValue(3)
        self.GAIN_SpinBox.setPrefix(self.CHNUMBERSTR + self.GAIN_lbl[3] + "")
        self.GAIN_SpinBox.valueChanged.connect(self.GAIN_SpinBox_changed)
        # ####################################################################
        self.GainValue = self.GAIN_ValueArray[self.GAIN_SpinBox.value()]

    #ALPHA_SpinBox_changed
    def GAIN_SpinBox_changed(self,indexValue):
        self.GAIN_SpinBox.setPrefix(self.CHNUMBERSTR + self.GAIN_lbl[indexValue]+"")
        self.GainValue=self.GAIN_ValueArray[indexValue]
        #self.ALPHA_SpinBox.setValue(indexValue)
        #print("ALPHA = {:f}".format(self.ALPHA_ValueArray[indexValue]))
        #self.GAIN1_value=self.GAIN_ValueArray[indexValue]

    #BETTA_SpinBox_changed
    def GET_GAIN(self):  return self.GAIN_ValueArray[self.GAIN_SpinBox.value()]


#####################################################################################################
#####################################################################################################

class GAINBOXCOMBO(QtWidgets.QWidget):
    """
    Custom Qt Widget to show a power bar and dial.
    Demonstrating compound and custom-drawn widget.
    """

    def __init__(self, pbox, posx, posy,  *args, **kwargs):
        super(GAINBOXCOMBO, self).__init__(*args, **kwargs)

        font = QtGui.QFont()
        font.setPointSize(10)

        self.offsetMAXVoltage=3.3
        self.beamChannels = 4



        self.parentbox = pbox
        self.GAIN_sbox=QtWidgets.QGroupBox(self.parentbox)
        self.GAIN_sbox.setGeometry(QtCore.QRect(posx, posy,215,120))
        self.GAIN_sbox.setFont(font)
        self.GAIN_sbox.setAlignment(QtCore.Qt.AlignCenter)
        #self.ALPHA_sbox.setAlignment(QtCore.Qt.AlignLeft)
        self.GAIN_sbox.setObjectName("GAIN_sbox")
        self.GAIN_sbox.setTitle("DIGITAL GAIN")

        self.GAIN_CNT1 = GAINBOX(self.GAIN_sbox,15,1)
        self.GAIN_CNT1.GAIN_SpinBox.setStyleSheet("color: red;  border-radius: 1px; background: black") # rgb(20, 40, 30)

        self.GAIN_CNT2 = GAINBOX(self.GAIN_sbox,32,2)
        self.GAIN_CNT2.GAIN_SpinBox.setStyleSheet("color: green;  border-radius: 1px; background: black")

        self.GAIN_CNT3 = GAINBOX(self.GAIN_sbox,49,3)
        self.GAIN_CNT3.GAIN_SpinBox.setStyleSheet("color: magenta;  border-radius: 1px; background: black")

        self.GAIN_CNT4 = GAINBOX(self.GAIN_sbox,66,4)
        self.GAIN_CNT4.GAIN_SpinBox.setStyleSheet("color: yellow;  border-radius: 1px; background: black")

        self.GAIN_CNT5 = GAINBOX(self.GAIN_sbox,83,5)
        self.GAIN_CNT5.GAIN_SpinBox.setStyleSheet("color: #B030B0;  border-radius: 1px; background: black")

        self.GAIN_CNT6 = GAINBOX(self.GAIN_sbox,100,6)
        self.GAIN_CNT6.GAIN_SpinBox.setStyleSheet("color: cyan;  border-radius: 1px; background: black")


        self.Resetbtn=QtWidgets.QPushButton(self.GAIN_sbox)
        self.Resetbtn.setGeometry(QtCore.QRect(120,50,22,25))
        self.Resetbtn.setObjectName("pBTN_SCR")
        self.Resetbtn.setStyleSheet("color: yellow;  border-radius: 5px; background: blue")
        self.Resetbtn.setToolTip('Runs current script\n in editor')
        self.Resetbtn.setText("EQ")
        self.Resetbtn.clicked.connect(self.EQUsliders)

        self.EQUbtn=QtWidgets.QPushButton(self.GAIN_sbox)
        self.EQUbtn.setGeometry(QtCore.QRect(120,88,22,25))
        self.EQUbtn.setObjectName("pBTN_SCR")
        self.EQUbtn.setStyleSheet("color: yellow;  border-radius: 5px; background: blue")
        self.EQUbtn.setToolTip('Runs current script\n in editor')
        self.EQUbtn.setText("RST")
        self.EQUbtn.clicked.connect(self.setsliders)




        self.Qslider1 = QSlider(self.GAIN_sbox)
        self.Qslider1.setRange(-1000,+1000)
        self.Qslider1.setSingleStep(1)
        self.Qslider1.setGeometry(144,15,10,100)
        self.Qslider1.setStyleSheet("background: black")

        self.Qslider2 = QSlider(self.GAIN_sbox)
        self.Qslider2.setRange(-1000,+1000)
        self.Qslider2.setSingleStep(1)
        self.Qslider2.setGeometry(156,15,10,100)
        self.Qslider2.setStyleSheet("background: black")

        self.Qslider3 = QSlider(self.GAIN_sbox)
        self.Qslider3.setRange(-1000,+1000)
        self.Qslider3.setSingleStep(1)
        self.Qslider3.setGeometry(168,15,10,100)
        self.Qslider3.setStyleSheet("background: black")

        self.Qslider4 = QSlider(self.GAIN_sbox)
        self.Qslider4.setRange(-1000,+1000)
        self.Qslider4.setSingleStep(1)
        self.Qslider4.setGeometry(180,15,10,100)
        self.Qslider4.setStyleSheet("background: black")

        self.Qslider5 = QSlider(self.GAIN_sbox)
        self.Qslider5.setRange(-1000,+1000)
        self.Qslider5.setSingleStep(1)
        self.Qslider5.setGeometry(192,15,10,100)
        self.Qslider5.setStyleSheet("background: black")

        self.Qslider6 = QSlider(self.GAIN_sbox)
        self.Qslider6.setRange(-1000,+1000)
        self.Qslider6.setSingleStep(1)
        self.Qslider6.setGeometry(204,15,10,100)
        self.Qslider6.setStyleSheet("background: black")



        self.ADCLSBmvminus = 0.0
        self.msGain=np.array([1.0,1.0,1.0,1.0,1.0,1.0])
        self.msMult     = (self.ADCLSBmvminus) * self.msGain



        self.Sliderindex = 6.6/self.Qslider1.maximum()

        self.slidersets0 = np.array([0.0,0.0,0.0,0.0,0.0,0.0])
        # initial slider position at mode4
        self.offstpf = self.offsetMAXVoltage/4.0
        self.offstpi = self.offstpf
        self.offstpi =  (self.Qslider1.maximum()) /2.0
        self.slidersets4 = np.array([(self.offstpi) , 0,(-self.offstpi), (-2 * self.offstpi),0.0,0.0])

        # initial slider position at mode6
        self.offstpf = self.offsetMAXVoltage/6
        self.offstpi = self.Qslider1.maximum()/3
        self.slidersets6 = np.array([(2*self.offstpi) ,(self.offstpi), 0, (-self.offstpi), (-2 * self.offstpi), (-3 * self.offstpi)])

        self.msOffset = np.array(6)
        self.setsliders()

    ################# GAIN Spinboxes control
    def resetGainToDefault(self):
        self.GAIN_CNT1.GAIN_SpinBox.setValue(3)
        self.GAIN_CNT2.GAIN_SpinBox.setValue(3)
        self.GAIN_CNT3.GAIN_SpinBox.setValue(3)
        self.GAIN_CNT4.GAIN_SpinBox.setValue(3)
        self.GAIN_CNT5.GAIN_SpinBox.setValue(3)
        self.GAIN_CNT6.GAIN_SpinBox.setValue(3)
        self.GAIN_CNT1.GAIN_SpinBox_changed(3)
        self.GAIN_CNT2.GAIN_SpinBox_changed(3)
        self.GAIN_CNT3.GAIN_SpinBox_changed(3)
        self.GAIN_CNT4.GAIN_SpinBox_changed(3)
        self.GAIN_CNT5.GAIN_SpinBox_changed(3)
        self.GAIN_CNT6.GAIN_SpinBox_changed(3)
        self.msGain = np.array([1.0,1.0,1.0,1.0,1.0,1.0])
        self.msMult = (self.ADCLSBmvminus) * self.msGain

   ################# SLIDERS control ###
    def setsliders(self):
        '''
        sets sliders to defaults for 3 modes 6beam,4beam,6beam to 0 offset
        '''
        if (self.beamChannels == 4):
            self.Qslider1.setValue(self.slidersets4[0])
            self.Qslider2.setValue(self.slidersets4[1])
            self.Qslider3.setValue(self.slidersets4[2])
            self.Qslider4.setValue(self.slidersets4[3])
            self.Qslider5.setValue(self.slidersets4[4])
            self.Qslider6.setValue(self.slidersets4[5])
            self.msOffset = self.slidersets4 * self.Sliderindex
        else:
            self.Qslider1.setValue(self.slidersets6[0])
            self.Qslider2.setValue(self.slidersets6[1])
            self.Qslider3.setValue(self.slidersets6[2])
            self.Qslider4.setValue(self.slidersets6[3])
            self.Qslider5.setValue(self.slidersets6[4])
            self.Qslider6.setValue(self.slidersets6[5])
            self.msOffset = self.slidersets6 * self.Sliderindex
            return

    def EQUsliders(self):
            self.Qslider1.setValue(0)
            self.Qslider2.setValue(0)
            self.Qslider3.setValue(0)
            self.Qslider4.setValue(0)
            self.Qslider5.setValue(0)
            self.Qslider6.setValue(0)
            self.msOffset = self.slidersets0 * self.Sliderindex


    # COMMON CONTROL #########################################################
    def resetToDefault(self,beams):
        self.beamChannels=beams
        self.setsliders()
        self.resetGainToDefault()

    def refreshGainnOffset(self):
        self.msGain[0] = self.GAIN_CNT1.GainValue
        self.msGain[1] = self.GAIN_CNT2.GainValue
        self.msGain[2] = self.GAIN_CNT3.GainValue
        self.msGain[3] = self.GAIN_CNT4.GainValue
        self.msGain[4] = self.GAIN_CNT5.GainValue
        self.msGain[5] = self.GAIN_CNT6.GainValue
        self.msMult    = self.ADCLSBmvminus * self.msGain
        # Build actual voltage offsets
        self.msOffset[0] = self.Sliderindex * self.Qslider1.value()
        self.msOffset[1] = self.Sliderindex * self.Qslider2.value()
        self.msOffset[2] = self.Sliderindex * self.Qslider3.value()
        self.msOffset[3] = self.Sliderindex * self.Qslider4.value()
        self.msOffset[4] = self.Sliderindex * self.Qslider5.value()
        self.msOffset[5] = self.Sliderindex * self.Qslider6.value()




















