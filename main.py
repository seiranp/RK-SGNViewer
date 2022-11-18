#  TODO    implemented just for check
#  TODO    run_CSF doesn't clean after long records

# import easygui
# for file dialogs see easygui library   http://easygui.sourceforge.net/tutorial.html
# path = easygui.actionFileOpenbox()
# from PyQt5.QtWidgets import *
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# import sys
# import unittest


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QMessageBox, QApplication, \
    QFileDialog, QTabWidget,QStackedLayout,QSlider
from random import uniform , randint
import os
import numpy as np
import pyqtgraph as pg
import time as tm
import sys
from sys import exit as sysExit
import traceback
#import drawnow as dn
#from pyqtgraph import PlotWidget, plot
from StringParser import StringParserClass
from ThermoTables import Regulator,Thermistor
from controls import ALPHA_BETTA,GAINBOX,GAINBOXCOMBO
import subprocess
from subprocess import Popen, PIPE
# from PyQt5.QtCore import QObject,QRunnable,QThreadPool,QTimer,pyqtSignal,pyqtSlot
##################################################
class WorkerKilledException( Exception):
    pass

class WorkerSignals(QObject):
    """ Defines the signals available from a running worker thread.
    Supported signals are:  finished        No data
                            error          `tuple` (exctype, value, traceback.format_exc() )
                            result         `object` data returned from processing, anything"""
    finished=pyqtSignal()
    error=pyqtSignal(tuple)
    result=pyqtSignal(object)
    result1=pyqtSignal()
    result2=pyqtSignal()

class Worker(QRunnable):
    """ Worker thread Inherits from QRunnable
    to handle worker thread setup, signals and wrap-up
    :param callback: The function callback to run on this worker
    :thread. Supplied args and kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """
    def __init__(self,fn,*args,**kwargs):
        super().__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.branch = 0
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.GO = True
        self.mode=0

    @pyqtSlot()
    def run(self):
        """
            Initialize the runner function with passed args, kwargs.
        """
        # Retrieve args/ kwargs here; and fire processing using them

        #print("running")
        if (self.mode == 2):  # Signalling MODE  2 - Infinnite Mode
            while (self.GO):
                self.fn(*self.args,**self.kwargs)   # calls threadloop
                self.signals.result1.emit()         # calls self.signalPlot
            return  # exit from run
        elif (self.mode==1):  # Signalling MODE  1 - CSF loop
            self.fn(*self.args, **self.kwargs)      # calls threadloop
            self.signals.result2.emit()             # calls self.plotSignalsnSave
            return

        else:
            return

#            raise WorkerKilledException

#        except WorkerKilledException:
#            pass

#    def setBranch(self,br):
#        self.branch=br
#        print(br)
# call as self.worker.setBranch(br)

    def kill(self):
        self.GO = False

    def SetMode(self,mode):
        self.mode=mode
        return


#0 #################################################################
#class Ui_MainWindow(object):
class Ui_MainWindow(QWidget):
    convert = Regulator()
    CoolerThermistor = Thermistor()
    parser = StringParserClass()

    MODE = 0  # graf mode
    FourChannelMode = False
    TESTPLOTEN = False
    TESTPLOTmainScopeEN =False
    SignalPLOTEN = False
    SignalPLOTEN2 = False
    TemperaturePLOTEN = False

    timerTick=10
    EnTimer = 0

    font_main=QtGui.QFont()
    font_main.setFamily("Lucida Console")
    font_main.setPointSize(10)
    font_main.setBold(False)


    font_label_13=QtGui.QFont()
    font_label_13.setFamily("Lucida Console")
    font_label_13.setPointSize(13)
    font_label_13.setBold(False)

    font_label_17=QtGui.QFont()
    font_label_17.setFamily("Lucida Console")
    font_label_17.setPointSize(17)
    font_label_17.setBold(False)

    font_BIG=QtGui.QFont()
    font_BIG.setFamily("Lucida Console")
    font_BIG.setPointSize(30)
    font_BIG.setBold(False)


    TEST_RUNNING = False
    defaultScriptName="mainscript"
    scriptName=""
    script_found=False

    echoEnableMode = False

    scriptnames = [
        "--------",
        "--------",
        "--------",
        "--------",
        "--------",
        "--------",
        "--------",
        "--------",
        "--------",
        "--------"
        "--------",
        "--------",
        "--------",
        "--------",
        "--------",
        "--------",
        "--------",
        "--------",
        "--------",
        "--------"
        ]
    arnpu32=np.array(np.zeros([6]),np.uint32)
    anpi32=np.int32(0)
    previousline="get_ver"
    TT = []

    VERSION     = "3.1"
    subversion  = "Subversion 3"
    VTECTEMP2   = .75
    Isense2     = 0.0
    WorkingMode = 0

    WBigscreen  = 2600
    HBigscreen  = 1400

    WSmallscreen  = 1880
    HSmallscreen  = 980


    WScreen = 0
    HScreen = 0



#
#
    ##########################################################
    ScreenWideMode = True
    #ScreenWideMode = False

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        buttonW=90; buttonH=40;
        #  reset Geometry
        if (self.ScreenWideMode):
            self.WScreen = self.WBigscreen;  self.HScreen = self.HBigscreen
            tabX=570;

        else:
            self.WScreen = self.WSmallscreen;  self.HScreen = self.HSmallscreen
            tabX=470;

        tabY=2;
        tabWidth=self.WScreen - tabX;
        tabHight=self.HScreen - buttonH -8 ;

        MainWindow.resize(self.WScreen, self.HScreen)

        buttonfont = QtGui.QFont()
        buttonfont.setPointSize(10)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("color: yellow; background: rgb(20, 40, 30);")
        MainWindow.setCentralWidget(self.centralwidget)

        self.threadpool=QThreadPool()
        ################################################################################################
        font = QtGui.QFont()
        font.setBold(True)
        font = QtGui.QFont()
        font.setPointSize(9)

#        font.setBold(True)
#        font.setWeight(75)#
        font.setPointSize(10)
        #tabwindows
        script_X=10;         script_Y=20;         script_W=165;         script_H=17;         script_Dy=20
        ssboxw=3*script_W+40;
        ssboxh = 6*script_Dy






        self.DYNAMICMODE_BOX=QtWidgets.QGroupBox(self.centralwidget)
        self.DYNAMICMODE_BOX.setGeometry(QtCore.QRect(tabX, tabY, tabWidth, tabHight))
        self.DYNAMICMODE_BOX.setFont(font)
        self.DYNAMICMODE_BOX.setAlignment(QtCore.Qt.AlignCenter)
        self.DYNAMICMODE_BOX.setObjectName("DYNAMICMODE_BOX")
        self.DYNAMICMODE_BOX.setTitle("DYNAMIC SCRIPTING")

        # PLot Mode box ####################################################################
        self.graphModeSelect=QtWidgets.QGroupBox(self.DYNAMICMODE_BOX)
        self.graphModeSelect.setObjectName("graphModeSelect")
        #self.signalSourceBox.setGeometry(QtCore.QRect(scgpbxX+scgpbxW-ssboxw,scgpbxY+scgpbxH+10,ssboxw,ssboxh))
        self.graphModeSelect.setGeometry(QtCore.QRect(2,tabHight-120-2,190,80))
        self.graphModeSelect.setFont(font)
        self.graphModeSelect.setAlignment(QtCore.Qt.AlignCenter)

        # radiobuttons
        self.rBTN_6xCH=QtWidgets.QRadioButton(self.graphModeSelect)
        self.rBTN_6xCH.setFont(self.font_label_13)
        self.rBTN_6xCH.setGeometry(QtCore.QRect(10,int(.95*script_Y),int(1.05*script_W),script_H))
        self.rBTN_6xCH.setObjectName("rBTN_6xCH")
        self.rBTN_6xCH.setChecked(False)
        self.rBTN_6xCH.clicked.connect(self.selectMode)

        self.rBTN_4xCH=QtWidgets.QRadioButton(self.graphModeSelect)
        self.rBTN_4xCH.setFont(self.font_label_13)
        self.rBTN_4xCH.setGeometry(QtCore.QRect(10, int(1.9*script_Y),int(1.05*script_W),script_H))
        self.rBTN_4xCH.setObjectName("rBTN_4xCH")
        self.rBTN_4xCH.setChecked(True)
        self.rBTN_4xCH.clicked.connect(self.selectMode)

        self.rBTN_4_2xCH=QtWidgets.QRadioButton(self.graphModeSelect)
        self.rBTN_4_2xCH.setFont(self.font_label_13)
        self.rBTN_4_2xCH.setGeometry(QtCore.QRect(10, int(2.85*script_Y),int(1.05*script_W),script_H))
        self.rBTN_4_2xCH.setObjectName("rBTN_4_2xCH")
        self.rBTN_4_2xCH.setChecked(False)
        self.rBTN_4_2xCH.clicked.connect(self.selectMode)

        # Variance Preview box ####################################################################
        self.VariancePreview=QtWidgets.QGroupBox(self.DYNAMICMODE_BOX)
        self.VariancePreview.setObjectName("VariancePreview")
        self.VariancePreview.setGeometry(QtCore.QRect(2,tabHight-43 ,190,41))
        self.VariancePreview.setFont(font)
        self.VariancePreview.setAlignment(QtCore.Qt.AlignCenter)

        # radiobuttons
        self.rBTN_Preview=QtWidgets.QRadioButton(self.VariancePreview)
        self.rBTN_Preview.setFont(font)
        self.rBTN_Preview.setGeometry(QtCore.QRect(10, int(.8*script_Y),int(0.5*script_W),script_H))
        self.rBTN_Preview.setObjectName("rBTN_Preview")
        self.rBTN_Preview.setChecked(True)
        self.rBTN_Preview.clicked.connect(self.PreviewButtonClicked)


        self.rBTN_Variance=QtWidgets.QRadioButton(self.VariancePreview)
        self.rBTN_Variance.setFont(font)
        self.rBTN_Variance.setGeometry(QtCore.QRect(100,int(0.8*script_Y),int(.5*script_W),script_H))
        self.rBTN_Variance.setObjectName("rBTN_Variance")
        self.rBTN_Variance.setChecked(False)
        # TODO#self.rBTN_Variance.clicked.connect()
        self.rBTN_Variance.clicked.connect(self.VarianceButtoClicked)

        #------------------------



        # DIGITAL GAIN BOX ####################################################################
        #self.GAIN_sbox=QtWidgets.QGroupBox(self.DYNAMICMODE_BOX)
        #self.GAIN_sbox.setGeometry(QtCore.QRect(222,tabHight-120-2,185,120))
        #self.GAIN_sbox.setFont(font)
        #self.GAIN_sbox.setAlignment(QtCore.Qt.AlignCenter)
        #self.ALPHA_sbox.setAlignment(QtCore.Qt.AlignLeft)
        #self.GAIN_sbox.setObjectName("GAIN_sbox")


        #self.GAIN_CNT1 = GAINBOX(self.GAIN_sbox,15,1)
        #self.GAIN_CNT2 = GAINBOX(self.GAIN_sbox,32,2)
        #self.GAIN_CNT3 = GAINBOX(self.GAIN_sbox,49,3)
        #self.GAIN_CNT4 = GAINBOX(self.GAIN_sbox,66,4)
        #self.GAIN_CNT5 = GAINBOX(self.GAIN_sbox,83,5)
        #self.GAIN_CNT6 = GAINBOX(self.GAIN_sbox,100,6)

        self.DIGITAL_GAIN_BOX=GAINBOXCOMBO(self.DYNAMICMODE_BOX, 194, tabHight-120-2)
        self.DIGITAL_GAIN_BOX.ADCLSBmvminus=self.parser.ADCLSBmvminus;
        self.DIGITAL_GAIN_BOX.resetToDefault(4)



        # ESTIMATOR_box ####################################################################
        self.ESTIMATOR_box=QtWidgets.QGroupBox(self.DYNAMICMODE_BOX)
        self.ESTIMATOR_box.setGeometry(QtCore.QRect(410, tabHight - 120 - 2, 138, 120))
        self.ESTIMATOR_box.setFont(font)
        self.ESTIMATOR_box.setAlignment(QtCore.Qt.AlignCenter)
        #self.ALPHA_sbox.setAlignment(QtCore.Qt.AlignLeft)
        self.ESTIMATOR_box.setObjectName("ESTIMATOR_box")

        self.ALPHA_BETTA_CNT = ALPHA_BETTA(self.ESTIMATOR_box)


        #SignalSourceBox #############################################################
        self.signalSourceBox = QtWidgets.QGroupBox(self.DYNAMICMODE_BOX)
        self.signalSourceBox.setGeometry(QtCore.QRect(550,tabHight-120-2,535 , 120 ))
        self.signalSourceBox.setFont(font)
        self.signalSourceBox.setAlignment(QtCore.Qt.AlignCenter)
        self.signalSourceBox.setObjectName("groupBox_3")
        self.signalSourceBox.setStyleSheet(" background: black")

        # SignalSourceBoxradiobuttons
        self.rBTN_SCRIPT1 = QtWidgets.QRadioButton(self.signalSourceBox)
        self.rBTN_SCRIPT1.setGeometry(QtCore.QRect(script_X,script_Y,script_W,script_H))
        self.rBTN_SCRIPT1.setObjectName("radioButton_SCRIPT1")
        self.rBTN_SCRIPT1.clicked.connect(self.SignalPlotStart_SCRIPT1)

        self.rBTN_SCRIPT2 = QtWidgets.QRadioButton(self.signalSourceBox)
        self.rBTN_SCRIPT2.setGeometry(QtCore.QRect(script_X,script_Y+script_Dy,script_W,script_H))
        self.rBTN_SCRIPT2.setObjectName("radioButton_SCRIPT2")
        self.rBTN_SCRIPT2.clicked.connect(self.SignalPlotStart_SCRIPT2)

        self.rBTN_SCRIPT3 = QtWidgets.QRadioButton(self.signalSourceBox)
        self.rBTN_SCRIPT3.setGeometry(QtCore.QRect(script_X,script_Y+ (2*script_Dy),script_W,script_H))
        self.rBTN_SCRIPT3.setObjectName("radioButton_SCRIPT3")
        self.rBTN_SCRIPT3.clicked.connect(self.SignalPlotStart_SCRIPT3)

        self.rBTN_SCRIPT4 = QtWidgets.QRadioButton(self.signalSourceBox)
        self.rBTN_SCRIPT4.setGeometry(QtCore.QRect(script_X,script_Y + 3*script_Dy,script_W,script_H))
        self.rBTN_SCRIPT4.setObjectName("radioButton_SCRIPT4")
        self.rBTN_SCRIPT4.clicked.connect(self.SignalPlotStart_SCRIPT4)

        self.rBTN_SCRIPT5 = QtWidgets.QRadioButton(self.signalSourceBox)
        self.rBTN_SCRIPT5.setGeometry(QtCore.QRect(script_X + script_W+10,script_Y ,script_W,script_H))
        self.rBTN_SCRIPT5.setObjectName("radioButton_SCRIPT5")
        self.rBTN_SCRIPT5.clicked.connect(self.SignalPlotStart_SCRIPT5)

        self.rBTN_SCRIPT6 = QtWidgets.QRadioButton(self.signalSourceBox)
        self.rBTN_SCRIPT6.setGeometry(QtCore.QRect(script_X + script_W+10, script_Y+1*script_Dy,script_W,script_H))
        self.rBTN_SCRIPT6.setObjectName("radioButton_SCRIPT6")
        self.rBTN_SCRIPT6.clicked.connect(self.SignalPlotStart_SCRIPT6)

        self.rBTN_SCRIPT7 = QtWidgets.QRadioButton(self.signalSourceBox)
        self.rBTN_SCRIPT7.setGeometry(QtCore.QRect(script_X + script_W+10, script_Y+2*script_Dy,script_W,script_H))
        self.rBTN_SCRIPT7.setObjectName("radioButton_SCRIPT7")
        self.rBTN_SCRIPT7.clicked.connect(self.SignalPlotStart_SCRIPT7)

        self.rBTN_SCRIPT8 = QtWidgets.QRadioButton(self.signalSourceBox)
        self.rBTN_SCRIPT8.setGeometry(QtCore.QRect(script_X + script_W+10, script_Y+3*script_Dy,script_W,script_H))
        self.rBTN_SCRIPT8.setObjectName("radioButton_SCRIPT8")
        self.rBTN_SCRIPT8.clicked.connect(self.SignalPlotStart_SCRIPT8)

        self.rBTN_SCRIPT9 = QtWidgets.QRadioButton(self.signalSourceBox)
        self.rBTN_SCRIPT9.setGeometry(QtCore.QRect(script_X + 2*(script_W+10), script_Y+ 0*script_Dy,script_W,script_H))
        self.rBTN_SCRIPT9.setObjectName("radioButton_SCRIPT9")
        self.rBTN_SCRIPT9.clicked.connect(self.SignalPlotStart_SCRIPT9)

        self.rBTN_SCRIPT10 = QtWidgets.QRadioButton(self.signalSourceBox)
        self.rBTN_SCRIPT10.setGeometry(QtCore.QRect(script_X + 2*(script_W+10), script_Y+ 1*script_Dy,script_W,script_H))
        self.rBTN_SCRIPT10.setObjectName("radioButton_SCRIPT10")
        self.rBTN_SCRIPT10.clicked.connect(self.SignalPlotStart_SCRIPT10)

        self.rBTN_SIMULATOR = QtWidgets.QRadioButton(self.signalSourceBox)
        self.rBTN_SIMULATOR.setGeometry(QtCore.QRect(script_X + 2*(script_W+10), script_Y+ 2*script_Dy,script_W,script_H))
        self.rBTN_SIMULATOR.setObjectName("radioButton_SIMULATOR")
        self.rBTN_SIMULATOR.setChecked(False)
        self.rBTN_SIMULATOR.clicked.connect(self.TestPlotStart)

        self.rBTN_IDLE = QtWidgets.QRadioButton(self.signalSourceBox)
        self.rBTN_IDLE.setGeometry(QtCore.QRect(script_X + 2*(script_W+10), script_Y+ 3*script_Dy,script_W,script_H))
        self.rBTN_IDLE.setObjectName("radioButton_IDLEMODE")
        self.rBTN_IDLE.setChecked(True)
        self.rBTN_IDLE.clicked.connect(self.IdleMode)

        # Refresh Names
        self.pBTN_ScriptNmUpdate=QtWidgets.QPushButton(self.signalSourceBox)
        self.pBTN_ScriptNmUpdate.setGeometry(QtCore.QRect(400,100,int(1.4*buttonW),int(0.35*buttonH)))
        self.pBTN_ScriptNmUpdate.setObjectName("pBTN_SCR")
        self.pBTN_ScriptNmUpdate.setStyleSheet("color: yellow;  border-radius: 5px; background: blue")
        self.pBTN_ScriptNmUpdate.setToolTip('Runs current script\n in editor')
        self.pBTN_ScriptNmUpdate.clicked.connect(self.getScripList)
        self.pBTN_ScriptNmUpdate.setFont(buttonfont)
        ################################################################################################
        scgpbxX=570;  scgpbxY=2;
        scgpbxW=1080; scgpbxH=800;

        lbX=scgpbxX+5; lbY=scgpbxY+5; lbW=scgpbxW-10; lbH=22;

        #mScopeX=2;   mScopeY=previewY+previewh+5;   mScopeW=previewW;  mScopeH=scgpbxH - previewh-35;
        mScopeX=2;    mScopeY=lbY+lbH+10;            mScopeW=scgpbxW-10;  mScopeH=scgpbxH-125;

        #previewX=2; previewY=lbY+lbH+10;            previewW=scgpbxW-10;        previewh=80;
        previewX=2;  previewY = mScopeY+mScopeH ;             previewW=mScopeW;           previewh=93;

        #reviewX = mScopeX;   reviewY = mScopeY + mScopeH + 2;    reviewW=previewW;      reviewH=50

        btSTOPX=scgpbxX+scgpbxW-buttonW-5;
        #        btSTOPY=scgpbxY+scgpbxH-buttonH-5;
        btSTOPY=scgpbxY+7
        btSTARTX=btSTOPX-buttonW-5
        btINFX=btSTARTX-buttonW-5
        btSAVEX=btINFX-buttonW-5

        # mainSignalLbBeamNames ###########################################################
        self.mainSignalLbBeamNames=QtWidgets.QLabel(self.DYNAMICMODE_BOX)
        self.mainSignalLbBeamNames.setGeometry(QtCore.QRect(2,lbY+10,lbW,lbH))
        self.mainSignalLbBeamNames.setFont(self.font_label_13)
        self.mainSignalLbBeamNames.setText("RAW SIGNALS: ADC 1-Y,2-B,3-G,4-R)    YSCALE UNITS [V] ")

        # mainSignalPreview ##############################################################
        self.ScopeVariance = pg.PlotWidget(self.DYNAMICMODE_BOX)
        self.ScopeVariance.setGeometry(QtCore.QRect(previewX,previewY,previewW,previewh))
        self.ScopeVariance.setObjectName("graphicsVariance")
        self.ScopeVariance.setBackground(((0,55,0)))
        self.ScopeVariance.hideAxis('bottom')
        self.ScopeVariance.setMouseEnabled(x=True,y=True)
        self.ScopeVariance.hide()
        # mainSignalPreview ##############################################################
        self.ScopePreview = pg.PlotWidget(self.DYNAMICMODE_BOX)
        self.ScopePreview.setGeometry(QtCore.QRect(previewX,previewY,previewW,previewh))
        self.ScopePreview.setObjectName("graphicspreView")
        self.ScopePreview.setBackground(((0,55,0)))
        self.ScopePreview.hideAxis('bottom')
        #self.ScopePreview.setMouseEnabled(x=False,y=False)
        self.ScopePreview.setYRange(-50,300,padding=0)  # padding is offset from up and down

        # mScope #########################################################################
        self.mScopeSignal = pg.PlotWidget(self.DYNAMICMODE_BOX)
        self.mScopeSignal.setGeometry(QtCore.QRect(mScopeX, mScopeY, mScopeW, mScopeH))
        self.mScopeSignal.setObjectName("SignalView")
        self.mScopeSignal.setBackground((00, 40, 00))
        self.mScopeSignal.showGrid(x=True, y=True, alpha=0.95)
        self.mScopeSignal.setMouseEnabled(x=True, y=True)
        ####################################################
        self.editor = QtWidgets.QPlainTextEdit(self.DYNAMICMODE_BOX)
        #self.editor.setGeometry(QtCore.QRect(1555, 30, 320, 944))
        self.editor.setGeometry(QtCore.QRect(1085, 40, tabWidth-1085, tabHight-42))
        self.editor.setObjectName("EditScript")
        self.editor.setStyleSheet("color: yellow; background: black;")
        self.editor.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)

        fixedfont = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixedfont.setPointSize(12)
        self.editor.setFont(fixedfont)
        self.path = None
        self.status = QtWidgets.QStatusBar(self.centralwidget)
        # setting stats bar to the window
        # self.status.setStatusBar(self.status)
        #####################################################################
        #####################################################################
        # CALLIBRATIONMODEBOX
        self.CALIBRATIONMODE_BOX=QtWidgets.QGroupBox(self.centralwidget)
        self.CALIBRATIONMODE_BOX.setGeometry(QtCore.QRect(tabX, tabY, tabWidth, tabHight))
        self.CALIBRATIONMODE_BOX.setFont(font)
        self.CALIBRATIONMODE_BOX.setAlignment(QtCore.Qt.AlignCenter)
        self.CALIBRATIONMODE_BOX.setObjectName("CALIBRATIONMODE_BOX")
        self.CALIBRATIONMODE_BOX.setTitle("CALIBRATION MODE")
        #self.CALIBRATIONMODE_BOX.setStyleSheet("background-image: url(background1.png)")
        self.scgpbx = QtWidgets.QGroupBox(self.CALIBRATIONMODE_BOX)
        #self.scgpbx.setGeometry(QtCore.QRect(scgpbxX, scgpbxY, scgpbxW,scgpbxH))
        self.scgpbx.setGeometry(QtCore.QRect(2, 15, scgpbxW,scgpbxH))
        self.scgpbx.setObjectName("scgpbxl")
        self.scgpbx.setStyleSheet("background-image: url(background1.png)")
        #self.scgpbx.hide()


        #self.CALIBRATIONMODE_BOX.hide()

# Calibration Spinbox
        self.lasers = 30
        self.CALIBRATION_QSpinBox_lbl = ["0650", "0675", "0700", "0725", "0750", "0775", "0800", "0825", "0850", "0875",
                                         "0900", "0925", "0950", "0975", "1000", "1025", "1050", "1075", "1100", "1125",
                                         "1150", "1175", "1200", "1225", "1250", "1275", "1300", "1325", "1350", "1375",
                                         "1400", "1425", "1450", "1475", "1500", "1525", "1550", "1575", "1600", "1625",
                                         "1650", "1675", "1700", "1725", "1750", "1775", "1800", "1825", "1850", "1875",
                                         "1900", "1925", "1950", "1975", "2000", "2025", "2050", "2075", "2100", "2125",
                                         "2150", "2175", "2200", "2225", "2250", "2275", "2300", "2325", "2350", "2375",
                                         "2400", "2425", "2450", "2475", "2500", "2525", "2550", "2575", "2600", "2625"]

        self.CALIBRATION_CURRENT      = [123.36, 128.93, 126.81, 129.75, 128.21, 124.56, 127.68, 127.69, 126.52, 130.54,
                                         126.65, 125.89, 129.39, 128.16, 128.68, 124.85, 123.62, 129.80, 130.57, 127.91,
                                         125.05, 127.28, 123.70, 130.95, 126.25, 130.73, 126.52, 126.71, 129.20, 125.84,
                                         131.49, 132.64, 123.83, 130.11, 130.31, 130.38, 128.01, 124.13, 130.40, 127.99,
                                         124.74, 124.54, 131.14, 126.54, 129.90, 125.98, 126.17, 127.65, 130.35, 128.12,
                                         132.88, 125.77, 125.13, 125.56, 129.72, 131.46, 131.21, 131.86, 127.94, 129.78,
                                         131.82, 127.32, 123.82, 131.81, 126.62, 124.63, 126.34, 125.26, 125.62, 123.89,
                                         126.86, 127.25, 128.64, 131.22, 130.32, 127.31, 129.87, 128.36, 125.69, 124.01]

        self.CALIBRATION_QSpinBox = QtWidgets.QSpinBox(self.scgpbx)
        self.CALIBRATION_QSpinBox.setGeometry(QtCore.QRect(10, 300, 250, 60))
        self.CALIBRATION_QSpinBox.setObjectName("CALIBRATION_QSpinBox")
        self.CALIBRATION_QSpinBox.setStyleSheet("color: yellow;  border-radius: 3px; background: darkblue")

        self.CALIBRATION_QSpinBox.setRange(0, 79)
        self.CALIBRATION_QSpinBox.setSingleStep(1)
        #font.setBold(True)
        self.CALIBRATION_QSpinBox.setFont(self.font_BIG)
        self.CALIBRATION_QSpinBox.setPrefix(self.CALIBRATION_QSpinBox_lbl[0] + "  " )
        self.CALIBRATION_QSpinBox.valueChanged.connect(self.CALIBRATION_QSpinBoxvalue_changed)
        #self.CALIBRATION_QSpinBox.hide()


        self.CALIBCURRENT_QSpinBox = QtWidgets.QDoubleSpinBox(self.scgpbx)
        self.CALIBCURRENT_QSpinBox.setGeometry(QtCore.QRect(290, 300, 200, 60))
        self.CALIBCURRENT_QSpinBox.setObjectName("CALIBCURRENT_QSpinBox")
        self.CALIBCURRENT_QSpinBox.setStyleSheet("color: yellow;  border-radius: 3px; background: darkblue")
        self.CALIBCURRENT_QSpinBox.setRange(0.0, 299.00);
        self.CALIBCURRENT_QSpinBox.setSingleStep(.01)
        self.CALIBCURRENT_QSpinBox.setFont(self.font_BIG)
        #self.CALIBCURRENT_QSpinBox.setPrefix(self.CALIBRATION_QSpinBox_lbl[0] + "   ")
        self.CALIBCURRENT_QSpinBox.setValue(self.CALIBRATION_CURRENT[0])
        self.CALIBCURRENT_QSpinBox.valueChanged.connect(self.CALIBCURRENT_QSpinBoxvalue_changed)
        #self.CALIBCURRENT_QSpinBox.hide()

        self.CALIBRATION_label1=QtWidgets.QLabel(self.scgpbx)
        self.CALIBRATION_label1.setGeometry(QtCore.QRect(10, 250, 400, 40))
        self.CALIBRATION_label1.setFont(self.font_label_17)
        self.CALIBRATION_label1.setText("LAMBDA   LASER       CURRENT\n (nm)      #          (ma)")
        #self.CALIBRATION_label1.hide()

        # Callibration buttons
        self.pBTN_CALLIB_SAVE=QtWidgets.QPushButton(self.CALIBRATIONMODE_BOX)
        self.pBTN_CALLIB_SAVE.setGeometry(QtCore.QRect(80, tabHight-70, 200, 60))
        self.pBTN_CALLIB_SAVE.setObjectName("pBTN_CALLIB_SAVE")
        self.pBTN_CALLIB_SAVE.setStyleSheet("color: black;  border-radius: 20px; background: cyan")
        self.pBTN_CALLIB_SAVE.setToolTip('Runs AUTOCALIBRATION\n Starts from LASER0 to last laser\n each step takes 200ms')
        #self.pBTN_CALLIB_SAVE.clicked.connect(self.getScripList)
        self.pBTN_CALLIB_SAVE.setFont(self.font_label_17)
        #self.pBTN_CALLIB_SAVE.hide()


        self.pBTN_CALLIB_AUTO=QtWidgets.QPushButton(self.CALIBRATIONMODE_BOX)
        self.pBTN_CALLIB_AUTO.setGeometry(QtCore.QRect(310, tabHight-70, 200, 60))
        self.pBTN_CALLIB_AUTO.setObjectName("pBTN_CALLIB_AUTO")
        self.pBTN_CALLIB_AUTO.setStyleSheet("color: black;  border-radius: 20px; background: cyan")
        self.pBTN_CALLIB_AUTO.setToolTip('Saves table in\nBinary file')
        #self.pBTN_CALLIB_AUTO.clicked.connect(self.getScripList)
        self.pBTN_CALLIB_AUTO.setFont(self.font_label_17)
        #self.pBTN_CALLIB_AUTO.hide()

        self.pBTN_CALLIB_PROGRAM=QtWidgets.QPushButton(self.CALIBRATIONMODE_BOX)
        self.pBTN_CALLIB_PROGRAM.setGeometry(QtCore.QRect(540, tabHight-70, 200, 60))
        self.pBTN_CALLIB_PROGRAM.setObjectName("pBTN_CALLIB_PROGRAM")
        self.pBTN_CALLIB_PROGRAM.setStyleSheet("color: black;  border-radius: 20px; background: cyan")
        self.pBTN_CALLIB_PROGRAM.setToolTip('Saves table in\nonboard FLASH')
        #self.pBTN_CALLIB_AUTO.clicked.connect(self.getScripList)
        self.pBTN_CALLIB_PROGRAM.setFont(self.font_label_17)
        #self.pBTN_CALLIB_PROGRAM.hide()


        self.pBTN_CALLIB_RELOAD=QtWidgets.QPushButton(self.CALIBRATIONMODE_BOX)
        self.pBTN_CALLIB_RELOAD.setGeometry(QtCore.QRect(770, tabHight-70, 200, 60))
        self.pBTN_CALLIB_RELOAD.setObjectName("pBTN_CALLIB_RELOAD")
        self.pBTN_CALLIB_RELOAD.setStyleSheet("color: black;  border-radius: 20px; background: cyan")
        self.pBTN_CALLIB_RELOAD.setToolTip('Reload from\nonboard FLASH')
        #self.pBTN_CALLIB_AUTO.clicked.connect(self.getScripList)
        self.pBTN_CALLIB_RELOAD.setFont(self.font_label_17)

        self.calibration_editor = QtWidgets.QPlainTextEdit(self.CALIBRATIONMODE_BOX)
        self.calibration_editor.setGeometry(QtCore.QRect(1085,40,320,tabHight-42))
        self.calibration_editor.setObjectName("EditScript")
        self.calibration_editor.setStyleSheet("color: yellow; background: black;")
        self.calibration_editor.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.calibration_editor.setFont(fixedfont)
       # self.calibration_editor.appendPlainText("Hello World")
        for x in range(self.lasers) :  self.calibration_editor.appendPlainText (self.CALIBRATION_QSpinBox_lbl[x] + '   ' +  str('{:03d}   {:03.2f}'.format(x,self.CALIBRATION_CURRENT[x]) ) )
        #self.calibration_editor.

        self.CALIBRATIONMODE_BOX.hide()

#####################################################################
        ####     HISTORY  MODEL




        histgpbxX=2; histgpbxY=615 ; histgpbxW=tabX-3 ; histgpbxH=360
        buttonXstart=tabX + 2
        buttonYstart=tabHight +2 ;  buttonDX =buttonW +6; buttonDY= buttonH+10# (buttonYstart + (1 * buttonDY))
        #buttonYstart=histgpbxY+histgpbxH - buttonH+2 ;  buttonDX =buttonW +6; buttonDY= buttonH+10# (buttonYstart + (1 * buttonDY))
        lstHist_W=histgpbxW -10 ; lstHist_H=histgpbxH-45
        lstEdit_W=lstHist_W -buttonW ; lstEdit_H=25



        # _HISTORY groupbox
        self.groupboxlHistory = QtWidgets.QGroupBox(self.centralwidget)
        self.groupboxlHistory.setGeometry(QtCore.QRect(histgpbxX, histgpbxY, histgpbxW,histgpbxH))


        self.groupboxlHistory.setObjectName("groupboxlHistory")
        self.groupboxlHistory.setFont(buttonfont)
        # _Message_List widget
        #self.listWidgetMSG = QtWidgets.QListWidget(self.centralwidget)
        #self.listWidgetMSG.setGeometry(QtCore.QRect(lstWmsgX, lstWmsgY, lstWmsgW, lstWmsgH))
        #self.listWidgetMSG.setObjectName("listWidgetMSG")
        #self.listWidgetMSG.setStyleSheet("color: cyan; background: black;  border:1px solid rgb(255, 255, 255);")
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        font.setPointSize(14)
        font.setFamily("Courier")
        #self.listWidgetMSG.setFont(font)
        # self.listHistory.setStyleSheet("background-color:grey")
        # _HISTORY List widget
        #self.listHistory = QtWidgets.QListWidget(self.centralwidget)
        self.listHistory = QtWidgets.QListWidget(self.groupboxlHistory)
        self.listHistory.setGeometry(QtCore.QRect(4, 15, lstHist_W, lstHist_H))
        font.setPointSize(10)
        self.listHistory.setFont(font)
        self.listHistory.setObjectName("listHistory")
        self.listHistory.setStyleSheet("color: cyan; background: black;  border:1px solid rgb(255, 255, 255);")
        #self.listHistory.addItem("ROCKLEY Photonics Signal Viewer")
        # _LineEdit input
        self.lEdit1 = QtWidgets.QLineEdit(self.groupboxlHistory)
        self.lEdit1.setGeometry(QtCore.QRect(4, lstHist_H+16, lstEdit_W, lstEdit_H))
        self.lEdit1.setObjectName("lEdit1")
        self.lEdit1.setFont(font)
        self.lEdit1.setStyleSheet("color: cyan; background: black;  border:1px solid rgb(255, 255, 255);")
        self.lEdit1.installEventFilter(self)

        # _Clear History Button
        self.pBTN_CLEAR_W1 = QtWidgets.QPushButton(self.groupboxlHistory)
        self.pBTN_CLEAR_W1.setGeometry(QtCore.QRect(lstEdit_W+8, lstHist_H+20, int(0.9*buttonW), int(0.5*buttonH)))
        self.pBTN_CLEAR_W1.setObjectName("pBTN_CLEAR_W1")
        self.pBTN_CLEAR_W1.clicked.connect(self.clearHistory)
        self.pBTN_CLEAR_W1.setStyleSheet("color: yellow;  border-radius: 5px; background: blue")
        self.pBTN_CLEAR_W1.setFont(buttonfont)

        # _UpdateRegisters button
        self.pBTN_UpdateRegisters = QtWidgets.QPushButton(self.centralwidget)
        self.pBTN_UpdateRegisters.setGeometry(QtCore.QRect(buttonXstart , buttonYstart, buttonW, buttonH))
        self.pBTN_UpdateRegisters.setObjectName("pBTN_UpdateRegisters")
        self.pBTN_UpdateRegisters.clicked.connect(self.fupdateRegisters)
        self.pBTN_UpdateRegisters.setStyleSheet("color: yellow; border-radius: 5px;  background: blue")
        self.pBTN_UpdateRegisters.setFont(buttonfont)

        # _CONNECT USB BUTTON
        self.pBTN_CONNECT=QtWidgets.QPushButton(self.centralwidget)
        self.pBTN_CONNECT.setGeometry(QtCore.QRect(buttonXstart + buttonDX, buttonYstart, buttonW, buttonH))
        self.pBTN_CONNECT.setObjectName("pBTN_CONNECT")
        self.pBTN_CONNECT.setStyleSheet("color: yellow; border-radius: 5px;  background: blue")
        self.pBTN_CONNECT.setFont(buttonfont)
        #  self.pBTN_CONNECT.setStyleSheet("foreground-color: grey")
        self.pBTN_CONNECT.clicked.connect(self.connectUSB)
        #  self.pBTN_CONNECT.setIcon(QIcon('32x32.png'))

        # _FPGA RESET BUTTON
        self.pBTN_ResetFpga=QtWidgets.QPushButton(self.centralwidget)
        self.pBTN_ResetFpga.setGeometry(QtCore.QRect(buttonXstart + 2*buttonDX, buttonYstart, buttonW, buttonH))
        self.pBTN_ResetFpga.setObjectName("pBTN_ResetFpga")
        self.pBTN_ResetFpga.setStyleSheet("color: yellow;  border-radius: 5px; background: blue")
        self.pBTN_ResetFpga.clicked.connect(self.onRSTnUpdateFpga)
        self.pBTN_ResetFpga.setFont(buttonfont)

        # Save Signals Button
        self.pBTN_SaveSamples = QtWidgets.QPushButton(self.centralwidget)
        self.pBTN_SaveSamples.setGeometry(QtCore.QRect(buttonXstart+3*buttonDX,buttonYstart,buttonW,buttonH))
        self.pBTN_SaveSamples.setObjectName("pBTN_SAVESignals")
        self.pBTN_SaveSamples.setStyleSheet("color: yellow; border-radius: 5px;  background: blue")
        self.pBTN_SaveSamples.setFont(buttonfont)
        self.pBTN_SaveSamples.clicked.connect(self.saveFileDialog)


        self.pBTN_SaveMeanAndVar = QtWidgets.QPushButton(self.centralwidget)
        self.pBTN_SaveMeanAndVar.setGeometry(QtCore.QRect(buttonXstart+4*buttonDX,buttonYstart,buttonW,buttonH))
        self.pBTN_SaveMeanAndVar.setObjectName("pBTN_SAVESignals")
        self.pBTN_SaveMeanAndVar.setStyleSheet("color: yellow; border-radius: 5px;  background: blue")
        self.pBTN_SaveMeanAndVar.setFont(buttonfont)
        self.pBTN_SaveMeanAndVar.clicked.connect(self.saveMeanAndVarianceFileDialog)


        #self.pBTN_AddHBeat=QtWidgets.QPushButton(self.centralwidget)
        #self.pBTN_AddHBeat.setGeometry(QtCore.QRect(buttonXstart + 4*buttonDX, buttonYstart, buttonW, buttonH))
        #self.pBTN_AddHBeat.setObjectName("pBTN_AddHBeat")
        #self.pBTN_AddHBeat.setStyleSheet("color: yellow; border-radius: 5px;  background: blue")
        #self.pBTN_AddHBeat.setFont(buttonfont)
        #self.pBTN_AddHBeat.setToolTip('AADDING SYNTHETIC Heartbeat to DAC')
        #self.pBTN_AddHBeat.clicked.connect(self.fAddHBeat)

        # REgisterMap ###############################################
        self.pBTN_REgisterMap = QtWidgets.QPushButton(self.centralwidget)
        self.pBTN_REgisterMap.setGeometry(QtCore.QRect(buttonXstart+5*buttonDX,buttonYstart,buttonW,buttonH))
        self.pBTN_REgisterMap.setObjectName("pBTN_StopTest")
        self.pBTN_REgisterMap.setStyleSheet("color: yellow;   border-radius: 5px; background: blue")
        self.pBTN_REgisterMap.setFont(buttonfont)
        self.pBTN_REgisterMap.clicked.connect(self.OpenRegisterMap)
        #        self.pBTN_StopTest.setText(_translate("MainWindow", "STOP\nTest"))
        # _RunTest button
        self.pBTN_RunTest = QtWidgets.QPushButton(self.centralwidget)
        self.pBTN_RunTest.setGeometry(QtCore.QRect(buttonXstart + 6*buttonDX, buttonYstart, buttonW, buttonH))
        self.pBTN_RunTest.setObjectName("pBTN_RunTest")
        self.pBTN_RunTest.setStyleSheet("color: yellow;  border-radius: 5px; background: blue")
        self.pBTN_RunTest.setFont(buttonfont)
        self.pBTN_RunTest.clicked.connect(self.onRunTest)

        regboxX=histgpbxX + histgpbxW + 5; regboxY=histgpbxY ; regboxW=390 ; regboxH=histgpbxH

#        self.gpBx_FPGA_REGISTERS.setGeometry(QtCore.QRect(regboxX,regboxY,regboxW,regboxH))
        font.setPointSize(8)
#        font.setBold(True)
        #font.setWeight(75)
################################################################################################
        font.setBold(True)
        font = QtGui.QFont()
        font.setPointSize(9)

        self.cmnXpadding = 0.00
        self.signal_bims = 6

        self.signal_pen=[ pg.mkPen(color=(255, 0, 0),     width=2),     #   RED   #FF0000
                          pg.mkPen(color=(0, 255, 0),     width=2),     #   GRN   #00FF00
                          pg.mkPen(color=(255, 0, 255),   width=2),   #   MAG   #FF00FF
                          pg.mkPen(color=(255, 255, 0),   width=2),   #   CYA   #00FFFF
                          pg.mkPen(color=(140, 100, 255),  width=2),   #   YEL   #FFFF00
                          pg.mkPen(color=(0, 255, 255),   width=2),
                          pg.mkPen(color=(0, 255, 255),   width=1),
                          pg.mkPen(color=(255, 255, 0),   width=1),
                          pg.mkPen(color=(0, 255, 255),   width=1)
                          ]

        self.pen_BLU  = pg.mkPen(color=(255, 200, 200), width=2)

        self.tickTextOffset= -5
        self.tickLength=20
        self.ScopeVariance.getAxis('left').setWidth(55)

        #axis.setTickSpacing(5,1)
        self.ScopeVariance.getAxis('left').setStyle(tickLength=self.tickLength,tickTextOffset=self.tickTextOffset)


        self.mScopeSignal.getAxis('left').setWidth(55)

        #self.mScope.getAxis('left').setTickSpacing(200000,50000)
        self.mScopeSignal.getAxis('left').setStyle(tickLength=self.tickLength, tickTextOffset=self.tickTextOffset)
        self.xrange=np.linspace(0,10,11)



        self.SamplingPeriodus = 2
        self.SignalTickPeriod = 1  # 20ms refresh period
        self.bufferLengthmax = 32768
        self.recordsamples   = 20000
        self.showsamples     = 2000
        self.allBuffer       = np.array(np.zeros([5,self.bufferLengthmax]),np.uint32)
        self.showbuffer      = np.array(np.zeros([5,self.showsamples]))
        self.showStartPoint  = 0

        self.showTime_us   = self.SamplingPeriodus * self.showsamples
        self.allBufferTime = self.SamplingPeriodus * self.bufferLengthmax


        #self.axis=self.mScope.getAxis('left')
        #self.axis.setStyle(tickLength=5, tickTextOffset=self.tickTextOffset, showValues=True , autoExpandTextSpace = False, tickAlpha=255)



        #self.graphWidget1.setXRange(0, self.showsamples - 1,  padding=.0)  # padding is offset from left and right
        self.SY_OFFSET=[5,2.5,0,-2.5,-5]

        self.msGain=np.array([1.0,1.0,1.0,1.0,1.0,1.0])
        self.msMult     = (self.parser.ADCLSBmvminus) * self.msGain
        self.msOffset   = np.array([0.0,0.0,0.0,0.0,0.0,0.0])
        self.mscurrent  = self.msOffset
        self.msError    = np.array([0.0,0.0,0.0,0.0,0.0,0.0])
        self.msErrorsqr = np.array([0.0,0.0,0.0,0.0,0.0,0.0])

        self.offstp6=6.600/6  # offset step
        self.SB_OFFSET6 = np.array([2*self.offstp6,self.offstp6,0,-self.offstp6,-2*self.offstp6,-3*self.offstp6])   #6chmode

        self.offstp4=6.600/4  # offset step
        self.SB_OFFSET4=np.array([1*self.offstp4,0,-self.offstp4,-2*self.offstp4])

        self.SB_OFFSET=self.SB_OFFSET6 ; #FourChannelMode

#        self.initSignalPlot()
        self.TestsignalTickPeriod=5
        ################################################################################################
##  TODO     PARAMS  hbeatGRAPH #########################################################################
        self.HB_Box = QtWidgets.QGroupBox(self.centralwidget)
        self.HB_Box.setGeometry(QtCore.QRect(2, 10, tabX-3, 210))
        self.HB_Box.setStyleSheet("color: yellow; background: black;")
        font = QtGui.QFont();  font.setPointSize(9); font.setBold(True)

        self.HB_Box.setFont(self.font_label_13)
        self.HB_Box.setAlignment(QtCore.Qt.AlignLeft)
        self.HB_Box.setObjectName("HB_Box")
        self.HB_Box.setTitle("HEARTBEAT SAMPLES : ")


        self.HB_TickPeriod = np.uint32(1)  # each tic is 50ms
        self.HB_SamplePeriodms = 50*self.HB_TickPeriod
        self.HB_ScLengSmp = 128
        self.HB_RecLength  = 5120 # depth of buffer in samples
        self.HB_CurrentPoint=0  # This variable show where is the ploting start point
        self.HB_Viewsection=0;  self.hbPointsToDraw=0         # viewsection number  and points to plot, rest are 0.

        self.hbeat_Time_ms   =self.HB_RecLength*self.HB_SamplePeriodms  # Total bufffer record length in ms
        self.hbeat_Screen_ms =self.HB_ScLengSmp*self.HB_SamplePeriodms   # Length of screen in ms

        self.hbeat_timeScale  = np.linspace(0,self.hbeat_Screen_ms-self.HB_SamplePeriodms,self.HB_ScLengSmp)  # defining scale values
        self.hbeat_timeAngles = np.linspace(0,self.hbeat_Time_ms-self.HB_SamplePeriodms,self.HB_RecLength)  # defining scale values
        self.hbsc_buffer      = np.zeros(self.HB_ScLengSmp)
        self.hbeatRec_buffer  = np.zeros(self.HB_RecLength,np.int16)

        self.hbeatScope=pg.PlotWidget(self.HB_Box)
        self.hbeatScope.setGeometry(QtCore.QRect(5,20,450,188)) #5,20,390,315
        self.hbeatScope.setObjectName("heartbeat_View1")
        #self.hbeat_View.setTitle("HEARTBEAT")
        self.hbeatScope.showGrid(x=True,y=True,alpha=.8)

        self.hbeatPEN=pg.mkPen(color=(255,0,0),width=2)
        #self.hbeatScope.showGrid(x=True,y=True,alpha=.8)

        #self.hbInitTestPlot()
        #self.hbeat_line=self.hbeat_View.plot(self.hbeat_timeScale[self.hBstart: self.hBEnd],self.hbsc_buffer[self.hBstart: self.hBEnd],pen=self.hbeat_PEN)
        ################################################################################################
        ########## THERMOGRAPH #########################################################################
        # Termostructure
        self.tempCurrentValueBox = QtWidgets.QGroupBox(self.centralwidget)
        srect=QtCore.QRect(2, 222, tabX-3, 275);  self.tempCurrentValueBox.setGeometry(srect)
        self.tempCurrentValueBox.setStyleSheet("color: yellow; background: black;")
        self.tempCurrentValueBox.setFont(self.font_label_13)
        self.tempCurrentValueBox.setAlignment(QtCore.Qt.AlignLeft)
        self.tempCurrentValueBox.setObjectName("tempCurrentValueBox")
        self.tempCurrentValueBox.setTitle("TEMPERATURE PLOT:    5SMPS ºC ")

        self.ThermoTickPeriod=np.uint32(20)  # replot each 300ms
        self.TemperaturePLOTPeriod=np.uint32(20)
        self.thermo_recordLengthmax = 6000   # number of samples in thermobuffer
        self.thermo_graphmax=2*self.thermo_recordLengthmax
        self.tmp=[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        self.bims=6
        self.thermoGraph_MXBF    = np.array(25.0*np.ones([self.bims,self.thermo_graphmax]))
        self.thermo_SMPPeriod = 0.1  # period of ssmpling in sec

        self.thermo_rdptr = int(0)  # Current offset in buffer
        self.thermoGraph_wrptr = int(0)  # Current offset in buffer
        self.thermoGraph_xrange_d = int(300)
        self.thermoGraph_wrptr = self.thermoGraph_xrange_d  # Current offset in buffer
        self.thermoGraph_wrptr2 = self.thermoGraph_wrptr

        self.thermoGrapg_xrange = np.linspace(0,self.thermoGraph_xrange_d-1,self.thermoGraph_xrange_d)
        self.thermoGraph_plotstart = self.thermoGraph_wrptr-self.thermoGraph_xrange_d
        self.thermoGraph_plotend = int(0)
        self.thermo_xrange_s       =(self.thermoGraph_wrptr-self.thermoGraph_xrange_d)%self.thermo_recordLengthmax

        self.thermoGraph_pen=[ pg.mkPen(color=(255,0,0),width=2),     #   RED   #FF0000
                               pg.mkPen(color=(0,255,0),width=2),     #   GRN   #00FF00
                               pg.mkPen(color=(255,0,255),width=2),   #   MAG   #FF00FF
                               pg.mkPen(color=(255,255,0),width=1),   #   YEL   #FFFF00
                               pg.mkPen(color=(0,255,255),width=1),   #   CYA   #00FFFF
                               pg.mkPen(color=(0,127 ,255),width=2)]
        self.thermoGraph_firstTime=True
        self.thermoGraph_Scope = pg.PlotWidget(self.tempCurrentValueBox)
        #self.thermoScope.setGeometry(QtCore.QRect(10, 293, 455, 300))
        self.thermoGraph_Scope.setGeometry(QtCore.QRect(5,20,390,252))
        self.thermoGraph_Scope.setObjectName("thermoView1")
        self.thermoGraph_Scope.showGrid(x=True,y=True,alpha=.8)
        # Temperature Labels
        self.tmp1Label = QtWidgets.QLabel(self.tempCurrentValueBox)
        self.tmp1Label.setGeometry(QtCore.QRect(405, 20, 50, 20)); self.tmp1Label.setFont(self.font_label_13);
        self.tmp1Label.setToolTip("Sensor at J5 TERM1A1/TERM1B1")
        self.tmp1Label.setStyleSheet("color: #FF0000") ;  self.tmp1Label.setText("00.00")

        self.tmp2Label = QtWidgets.QLabel(self.tempCurrentValueBox)
        self.tmp2Label.setGeometry(QtCore.QRect(405, 55, 50, 20)) ; self.tmp2Label.setFont(self.font_label_13);
        self.tmp2Label.setStyleSheet("color: #00FF00");  self.tmp2Label.setText("00.00")
        self.tmp2Label.setToolTip("Sensor at J5 TERM2A1/TERM2B1")

        self.tmp3Label = QtWidgets.QLabel(self.tempCurrentValueBox)
        self.tmp3Label.setGeometry(QtCore.QRect(405, 90, 50, 20));  self.tmp3Label.setFont(self.font_label_13);
        self.tmp3Label.setStyleSheet("color: #FF00FF");         self.tmp3Label.setText("00.00")
        self.tmp3Label.setToolTip("Sensor at J5 TERM1A2/TERM1B2")

        self.tmp4Label = QtWidgets.QLabel(self.tempCurrentValueBox)
        self.tmp4Label.setGeometry(QtCore.QRect(405, 125, 50, 20)) ;     self.tmp4Label.setFont(self.font_label_13)
        self.tmp4Label.setStyleSheet("color: #FFFF00") ;   self.tmp4Label.setText("00.00")
        self.tmp4Label.setToolTip("Sensor at J5 TERM2A2/TERM2B2")

        self.tmp5Label = QtWidgets.QLabel(self.tempCurrentValueBox)
        self.tmp5Label.setGeometry(QtCore.QRect(405, 160, 50, 20)) ; self.tmp5Label.setFont(self.font_label_13)
        self.tmp5Label.setStyleSheet("color: #00FFFF") ;        self.tmp5Label.setText("00.00")
        self.tmp5Label.setToolTip("Temperature of sensor at J5 TERM1A3/TERM1B3")

        self.tmp6Label = QtWidgets.QLabel(self.tempCurrentValueBox)
        self.tmp6Label.setGeometry(QtCore.QRect(405, 195, 50, 20));        self.tmp6Label.setFont(self.font_label_13)
        self.tmp6Label.setStyleSheet("color: #0080FF");        self.tmp6Label.setText("00.00")
        self.tmp6Label.setToolTip("Sensor at J3 TERM2A3/TERM2B3")

        self.rBTN_enThermoFilter = QtWidgets.QCheckBox(self.tempCurrentValueBox)
        self.rBTN_enThermoFilter.setGeometry(QtCore.QRect(410, 225, 50, 20));
        self.rBTN_enThermoFilter.setObjectName("FEN");   self.rBTN_enThermoFilter.setFont(self.font_label_13);
        self.rBTN_enThermoFilter.setText("Fen")
        self.rBTN_enThermoFilter.setStyleSheet("color: #808000;  border-radius: 3px; background: #202020")
        #self.rBTN_enThermoFilter.clicked.connect(self.EnableThermoFilter)

        self.rBTN_enThermomeasurement = QtWidgets.QCheckBox(self.tempCurrentValueBox)
        self.rBTN_enThermomeasurement.setGeometry(QtCore.QRect(410, 248, 50, 20));        self.rBTN_enThermomeasurement.setObjectName("Enscan")
        self.rBTN_enThermomeasurement.setFont(self.font_label_13);        self.rBTN_enThermomeasurement.setText("EN")
        self.rBTN_enThermomeasurement.setStyleSheet("color: #808000;  border-radius: 3px; background: #202020")

        self.rBTN_enThermomeasurement.clicked.connect(self.EnableThermomeasurement)

        #
        self.thermoScopeGrpboxQSpin = QtWidgets.QGroupBox(self.tempCurrentValueBox)
        self.thermoScopeGrpboxQSpin.setGeometry(QtCore.QRect(338, 325, 92, 27))
        self.thermoScopeGrpboxQSpin.setStyleSheet("color: red; border-radius: 4px;  background: white")
        self.thermoScopeGrpboxQSpin.hide()

        # Spinbox
        self.thermoGraph_SelectorTime = np.array([.5,1.0,3.0,10.0,100.0,200.0,600.0])
        self.thermoGraph_SelectorTimeindex = int(3)  # Current time range

        self.thermoScope_QSpinSFX = ["      1sec", "      2sec", "      5sec", "     10sec", "     20sec",
                                     "     50sec", "    100sec", "    200sec", "    500sec",  "   1000sec"]
        self.thermo_QSpinBox = QtWidgets.QSpinBox(self.tempCurrentValueBox)
        self.thermo_QSpinBox.setGeometry(QtCore.QRect(300, 250, 90, 25))
        self.thermo_QSpinBox.setObjectName("thermo_QSpinBox")
        self.thermo_QSpinBox.setStyleSheet("color: yellow;  border-radius: 3px; background: darkblue")

        self.thermo_QSpinBox.setRange(0, 9);  self.thermo_QSpinBox.setSingleStep(1)
        #font.setBold(True)
        font.setPointSize(10);         self.thermo_QSpinBox.setFont(font)
        self.thermo_QSpinBox.setSuffix(self.thermoScope_QSpinSFX[0])
        self.thermo_QSpinBox.valueChanged.connect(self.thermo_QSpinBoxvalue_changed)
        self.thermo_QSpinBox.hide()
        #########################################################################
        # TEC ###################################################################################
        self.TEC_Box = QtWidgets.QGroupBox(self.centralwidget)
        self.TEC_Box.setGeometry(QtCore.QRect(2, 497, tabX-3, 120))
        self.TEC_Box.setStyleSheet("color: yellow; background: black;")
        self.TEC_Box.setFont(self.font_label_13)
        self.TEC_Box.setAlignment(QtCore.Qt.AlignLeft)
        self.TEC_Box.setObjectName("TEC_Box")
        self.TEC_Box.setTitle("TEC PLOT: 1SMPS ºC")
        # TEC Plot
        self.TEC_Scope = pg.PlotWidget(self.TEC_Box)
        self.TEC_Scope.setGeometry(QtCore.QRect(5,20,250,97))
        self.TEC_Scope.setObjectName("thermoView1")
        self.TEC_Scope.showGrid(x=True,y=True,alpha=.8)

        # Temperature Labels
        self.TEC_Label1 = QtWidgets.QLabel(self.TEC_Box)
        self.TEC_Label1.setGeometry(QtCore.QRect(262, 20, 170, 20)); self.TEC_Label1.setFont(self.font_label_13)
        self.TEC_Label1.setStyleSheet("color: #FF0000") ;  self.TEC_Label1.setText("SET----TºC")

        self.TEC_Label2 = QtWidgets.QLabel(self.TEC_Box)
        self.TEC_Label2.setGeometry(QtCore.QRect(262, 45, 170, 20)) ; self.TEC_Label2.setFont(self.font_label_13)
        self.TEC_Label2.setStyleSheet("color: #00FF00");   self.TEC_Label2.setText("ACTUAL-TºC  00.00")
        self.TEC_Label2.setToolTip("  PELTIER COOLLER\n ACTUAL TEMPERATURE")

        self.TEC_Label3 = QtWidgets.QLabel(self.TEC_Box)
        self.TEC_Label3.setGeometry(QtCore.QRect(262, 70, 170, 20)) ; self.TEC_Label3.setFont(self.font_label_13)
        self.TEC_Label3.setStyleSheet("color: #00FF00");   self.TEC_Label3.setText("I (Amp)      0.35")
        # Start Button
        self.TEC_btnEn = QtWidgets.QCheckBox(self.TEC_Box)
        self.TEC_btnEn.setGeometry(QtCore.QRect(262, 95, 50, 20));        self.TEC_btnEn.setObjectName("Enscan")
        self.TEC_btnEn.setFont(self.font_label_13);        self.TEC_btnEn.setText("TECon")
        self.TEC_btnEn.setStyleSheet("color: #808000;  border-radius: 3px; background: #202020")
        self.TEC_btnEn.clicked.connect(self.TEC_ENABLE)
        # Spinbox
        self.TEC_QSpinBox = QtWidgets.QDoubleSpinBox(self.TEC_Box)
        self.TEC_QSpinBox.setGeometry(QtCore.QRect(380, 18, 80, 24))
        self.TEC_QSpinBox.setObjectName("TEC_QSpinBox")
        self.TEC_QSpinBox.setStyleSheet("color: #FF0000;  border-radius: 3px; background: #202020")


        self.TEC_QSpinBox.setRange(10.0, 49.9);  self.TEC_QSpinBox.setSingleStep(.1)
        self.TEC_QSpinBox.setFont(self.font_label_13)
        #self.TEC_QSpinBox.setSuffix(self.thermoScope_QSpinSFX[0])
        self.TEC_QSpinBox.valueChanged.connect(self.TEC_QSpinBox_valuechanged)
        self.TEC_QSpinBox.setValue(25.00)
        self.TEC_QSpinBox.setToolTip("SENSOR's TEMPERATURE\n SETTING")
        #self.thermo_QSpinBox.hide()

    ###############################################################
        #MainWindow.setCentralWidget(self.centralwidget)
        #self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar = QtWidgets.QMenuBar(self.DYNAMICMODE_BOX)
        self.menubar.setGeometry(QtCore.QRect(1085, 10, 290, 30))  # 1560, 30, 285 , 944
        self.menubar.setObjectName("menubar")

        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")

        self.NotepadMenu = QtWidgets.QMenu(self.menubar)
        self.NotepadMenu.setObjectName("NotepadMenu")

        self.actionrunNotepad = QtWidgets.QAction(MainWindow)
        self.actionrunNotepad.setObjectName("actionRunNotepad")
        self.actionrunNotepad.setShortcut("Ctrl+N")
        self.actionrunNotepad.triggered.connect(self.Notepad_pp)

        #self.actionRunScript = QtWidgets.QAction(MainWindow)
        #self.actionRunScript.setObjectName("actionRunScript")
        #self.actionRunScript.triggered.connect(self.onScript_action)

        self.actionFileLoadOther = QtWidgets.QAction(MainWindow)
        self.actionFileLoadOther.setObjectName("actionFileLoad")
        self.actionFileLoadOther.setShortcut("Ctrl+l")
        self.actionFileLoadOther.triggered.connect(self.fileLoadOther)

        self.actionFileSave = QtWidgets.QAction(MainWindow)
        self.actionFileSave.setObjectName("actionFileSave")
        self.actionFileSave.setShortcut("Ctrl+S")
        self.actionFileSave.triggered.connect(self.file_save)

        self.actionFileReload = QtWidgets.QAction(MainWindow)
        self.actionFileReload.setObjectName("actionFileReload")
        self.actionFileReload.setShortcut("Ctrl+R")
        self.actionFileReload.triggered.connect(self.file_reload)

#        self.menu_File.addAction(self.actionRunScript)
        self.menu_File.addAction(self.actionFileSave)
        # self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionFileReload)
        self.menu_File.addAction(self.actionFileLoadOther)

        self.NotepadMenu.addAction(self.actionrunNotepad)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.NotepadMenu.menuAction())

        ############################################################

        # This section creates a temporary test buttons for temporary
        self.ModeSelect = QtWidgets.QGroupBox(self.centralwidget)
        self.ModeSelect.setGeometry(QtCore.QRect(1235, tabHight +2 , 640, 45))
        # font = QtGui.QFont()
        # font.setPointSize(9)
        #       self.signalSourceBox.setFont(font)
        self.ModeSelect.setAlignment(QtCore.Qt.AlignCenter)
        self.ModeSelect.setObjectName("TestBox")
        self.ModeSelect.setFont(font)
        self.ModeSelect.setTitle("MODE SELECT")

        # Dynamic mode button

        self.ModeSelect_RBTN_DYNAMIC = QtWidgets.QRadioButton(self.ModeSelect)
        self.ModeSelect_RBTN_DYNAMIC.setGeometry(QtCore.QRect(5, 14, 148, 24))
        self.ModeSelect_RBTN_DYNAMIC.setObjectName("ModeSelect_RBTN_DYNAMIC")
        self.ModeSelect_RBTN_DYNAMIC.setStyleSheet(
            "color: yellow;  border-radius: 5px; background: rgb(100,0,0)")  # rgb(150,150,15)
        self.ModeSelect_RBTN_DYNAMIC.setChecked(True)
        self.ModeSelect_RBTN_DYNAMIC.setFont(font)
        self.ModeSelect_RBTN_DYNAMIC.setText("SCRIPTING")
        self.ModeSelect_RBTN_DYNAMIC.setToolTip('Run programm in script Mode')
        self.ModeSelect_RBTN_DYNAMIC.clicked.connect(self.DYNAMIC_MODE_Selected)

        # CALIBRATION MODE BUTTON
        self.ModeSelect_RBTN_CALIBRATION = QtWidgets.QRadioButton(self.ModeSelect)
        self.ModeSelect_RBTN_CALIBRATION.setGeometry(QtCore.QRect(165, 14, 148, 24))
        self.ModeSelect_RBTN_CALIBRATION.setObjectName("ModeSelect_RBTN_CALIBRATION")
        self.ModeSelect_RBTN_CALIBRATION.setStyleSheet(
            "color: rgb(150,150,0);  border-radius: 5px; background: darkblue")
        self.ModeSelect_RBTN_CALIBRATION.setToolTip('Run programm in calibration Mode')
        self.ModeSelect_RBTN_CALIBRATION.clicked.connect(self.CALIBRATION_MODE_Selected)
        self.ModeSelect_RBTN_CALIBRATION.setFont(font)
        self.ModeSelect_RBTN_CALIBRATION.setText("CALIBRATION")

        # VI MODE BUTTON
        self.ModeSelect_RBTN_VIMODE = QtWidgets.QRadioButton(self.ModeSelect)
        self.ModeSelect_RBTN_VIMODE.setGeometry(QtCore.QRect(325, 14, 148, 24))
        self.ModeSelect_RBTN_VIMODE.setObjectName("ModeSelect_RBTN_VIMODE")
        self.ModeSelect_RBTN_VIMODE.setStyleSheet("color: rgb(150,150,0);  border-radius: 5px; background: darkblue")
        self.ModeSelect_RBTN_VIMODE.setToolTip('Run programm in VoltagevsCurrent Mode')
        self.ModeSelect_RBTN_VIMODE.clicked.connect(self.VI_MODE_MODE_Selected)
        self.ModeSelect_RBTN_VIMODE.setFont(font)
        self.ModeSelect_RBTN_VIMODE.setText("  VI MODE")

        # Stability Map MODE BUTTON
        self.ModeSelect_RBTN_SMAP = QtWidgets.QRadioButton(self.ModeSelect)
        self.ModeSelect_RBTN_SMAP.setGeometry(QtCore.QRect(485, 14, 148, 24))
        self.ModeSelect_RBTN_SMAP.setObjectName("ModeSelect_RBTN_SMAP")
        self.ModeSelect_RBTN_SMAP.setStyleSheet("color: rgb(150,150,0);  border-radius: 5px; background: darkblue")
        self.ModeSelect_RBTN_SMAP.setToolTip('Run programm in STABILITY MAP Mode')
        self.ModeSelect_RBTN_SMAP.clicked.connect(self.STABILITY_MAP_MODE_Selected)
        self.ModeSelect_RBTN_SMAP.setFont(font)
        self.ModeSelect_RBTN_SMAP.setText(" S-MAP MODE")

        self.retranslateUi(MainWindow)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.lEdit1.returnPressed.connect(self.on_ReturnPressed)

        self.TimerCounter = np.uint32(0)
        self.TimerCMP1 = self.SignalTickPeriod
        self.TimerCMP2 = self.ThermoTickPeriod
        self.TimerCMP3 = self.HB_TickPeriod
        self.TimerCMP4 = self.TestsignalTickPeriod
        self.TimerCMP5 = 50
        self.TimerCMP6Thermoperiod = 1
        self.OneSecCounter = 19


        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.onTimer)

        #self.worker=Worker(self.mythreadexec)
        np.set_printoptions(formatter={'int': hex})
        #self.initSignalPlot()

        app.aboutToQuit.connect(self.terminate)
        #app.aboutToQuit.connect(self.closeEvent)

#2  TODO    HEARTBEATGRAPH ####################

#       self.worker=Worker(self.mythreadexec) #mainSignalUpdate
        self.worker=Worker(self.threadloop)   #mainSignalUpdate
        self.worker.kill()
        self.getTemperatureTable()
        self.listHistory.addItem("\n---------------------------\nTEC Thermistor parameters")

        self.listHistory.addItem(self.CoolerThermistor.info())
        # self.listHistory.addItem (str(self.convert.startingCode))
        # Process command line
        self.scrfnm ='script.txt'
        # self.listHistory.addItem("Name of the script      : {:s}".format(sys.argv[0]))
        # if system was started with script name in command line
        if (len(sys.argv) == 2) :
        #     self.listHistory.addItem("Name of the script      : {:s}".format(sys.argv[1]))
            self.scrfnm = sys.argv[1]
        self.file_load()

        self.autorunflag=False
        self.getScripList()
        self.IdleMode()
        if self.autorunflag :
            self.parser.currentScriptName='autorun'
            self.parser.findScriptMode=True
            self.listHistory.addItem("# autorun was found and run")
            if (self.connectUSB()) :
                #self.rBTN_SCRIPT1
                self.IdleMode()
                self.onScript()

        #####################################################################
        self.listHistory.addItem(self.subversion )


        return
        # End of Init
        #sys.exit()

    def DYNAMIC_MODE_Selected(self):
        # self.listHistory.addItem("testboxF1 is unchecked: ")
        self.unhighlightallselections()
        self.ModeSelect_RBTN_DYNAMIC.setStyleSheet("color: yellow;  border-radius: 5px; background: rgb(100,0,0)")


        self.CALIBRATIONMODE_BOX.hide()
        self.DYNAMICMODE_BOX.show()
        self.WorkingMode = 0
        return

    def CALIBRATION_MODE_Selected(self):
        #self.listHistory.addItem("testboxF1 is checked: ")
        self.unhighlightallselections()
        self.ModeSelect_RBTN_CALIBRATION.setStyleSheet("color: yellow;  border-radius: 5px; background: rgb(100,0,0)")

        self.DYNAMICMODE_BOX.hide()
        self.CALIBRATIONMODE_BOX.show()
        self.WorkingMode = 1
        return

    def VI_MODE_MODE_Selected(self):
        self.unhighlightallselections()
        self.ModeSelect_RBTN_VIMODE.setStyleSheet("color: yellow;  border-radius: 5px; background: rgb(100,0,0)")
        return

    def STABILITY_MAP_MODE_Selected(self):
        self.unhighlightallselections()
        self.ModeSelect_RBTN_SMAP.setStyleSheet("color: yellow;  border-radius: 5px; background: rgb(100,0,0)")
        return

    def unhighlightallselections(self):
        self.ModeSelect_RBTN_CALIBRATION.setStyleSheet("color: rgb(150,150,0);  border-radius: 5px; background: darkblue")
        self.ModeSelect_RBTN_DYNAMIC.setStyleSheet("color: rgb(150,150,0);  border-radius: 5px; background: darkblue")
        self.ModeSelect_RBTN_VIMODE.setStyleSheet("color: rgb(150,150,0);  border-radius: 5px; background: darkblue")
        self.ModeSelect_RBTN_SMAP.setStyleSheet("color: rgb(150,150,0);  border-radius: 5px; background: darkblue")
        return
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
    def TEC_QSpinBox_valuechanged(self,f):

        #self.listHistory.addItem("{:02.1F}".format(self.TEC_QSpinBox.value()) )
        #self.listHistory.addItem("{:04d}".format(self.convert.TECcode(f)) )

        return
######################################################################################################################
    def getTemperatureTable(self):
        tempfnm='codeTempTable.txt'
        try:   f = open(tempfnm, "r")
        except IOError:
            self.listHistory.addItem("Could not openCode to temperature file: {:s}".format(tempfnm))
            return
        txt = f.read();  txt1 = txt.splitlines(); i=0
        for x in txt1:  s=x.split(); self.convert.COD2TEMP[i]=float(s[1]); i=i+1
        self.convert.startingCode = int(txt1[0].split()[0]);   self.convert.tablelength = i
        self.listHistory.addItem("Temperature table loaded")
        self.listHistory.addItem("OFFSET code        : {:d} ".format(self.convert.startingCode))
        self.listHistory.addItem("Temperature Range  : {:04.2F}...{:04.2F} ºC".format(self.convert.COD2TEMP[0],self.convert.COD2TEMP[i-1]))
        self.listHistory.addItem("Number of elements : {:d}".format(self.convert.tablelength))
        return


    ######################################################################################################################
    # Select 6x or 4x mode
    def select6xOr4xChannelMode1(self):
        if ( self.rBTN_6xCH.isChecked() or self.rBTN_4_2xCH.isChecked()) :
            self.SB_OFFSET=2*self.SB_OFFSET6
            self.FourChannelMode=False
            self.DIGITAL_GAIN_BOX.resetToDefault(6)
            self.mScopeSignal.setYRange(-6.600, 6.6, padding=.001)


        else:
            self.SB_OFFSET=2*self.SB_OFFSET4
            self.FourChannelMode=True
            self.DIGITAL_GAIN_BOX.resetToDefault(4)
            self.mScopeSignal.setYRange(-6.6, 6.6, padding=.001)



    def selectMode(self):
        self.select6xOr4xChannelMode1()
        if (self.rBTN_SCRIPT1.isChecked()): self.SignalPlotStart_SCRIPT1();   return
        if (self.rBTN_SCRIPT2.isChecked()): self.SignalPlotStart_SCRIPT2();   return
        if (self.rBTN_SCRIPT3.isChecked()): self.SignalPlotStart_SCRIPT3();   return
        if (self.rBTN_SCRIPT4.isChecked()): self.SignalPlotStart_SCRIPT4();   return
        if (self.rBTN_SCRIPT5.isChecked()): self.SignalPlotStart_SCRIPT5();   return
        if (self.rBTN_SCRIPT6.isChecked()): self.SignalPlotStart_SCRIPT6();   return
        if (self.rBTN_SCRIPT7.isChecked()): self.SignalPlotStart_SCRIPT7();   return
        if (self.rBTN_SCRIPT8.isChecked()): self.SignalPlotStart_SCRIPT8();   return
        if (self.rBTN_SCRIPT9.isChecked()): self.SignalPlotStart_SCRIPT9();   return
        if (self.rBTN_SCRIPT10.isChecked()): self.SignalPlotStart_SCRIPT10(); return

    #   MAIN SWITCH ##############################################
    def SignalPlotStart_SCRIPT1(self):  self.IdleMode(); self.parser.currentScriptName=self.scriptnames[0]; self.parser.findScriptMode=True;  self.onScript()  # Run Script to prepare all registers but not CYCLES
    def SignalPlotStart_SCRIPT2(self):  self.IdleMode(); self.parser.currentScriptName=self.scriptnames[1]; self.parser.findScriptMode=True;  self.onScript()
    def SignalPlotStart_SCRIPT3(self):  self.IdleMode(); self.parser.currentScriptName=self.scriptnames[2]; self.parser.findScriptMode=True;  self.onScript()
    def SignalPlotStart_SCRIPT4(self):  self.IdleMode(); self.parser.currentScriptName=self.scriptnames[3]; self.parser.findScriptMode=True;  self.onScript()
    def SignalPlotStart_SCRIPT5(self):  self.IdleMode(); self.parser.currentScriptName=self.scriptnames[4]; self.parser.findScriptMode=True;  self.onScript()
    def SignalPlotStart_SCRIPT6(self):  self.IdleMode(); self.parser.currentScriptName=self.scriptnames[5]; self.parser.findScriptMode=True;  self.onScript()
    def SignalPlotStart_SCRIPT7(self):  self.IdleMode(); self.parser.currentScriptName=self.scriptnames[6]; self.parser.findScriptMode=True;  self.onScript()
    def SignalPlotStart_SCRIPT8(self):  self.IdleMode(); self.parser.currentScriptName=self.scriptnames[7]; self.parser.findScriptMode=True;  self.onScript()
    def SignalPlotStart_SCRIPT9(self):  self.IdleMode(); self.parser.currentScriptName=self.scriptnames[8]; self.parser.findScriptMode=True;  self.onScript()
    def SignalPlotStart_SCRIPT10(self): self.IdleMode(); self.parser.currentScriptName=self.scriptnames[9]; self.parser.findScriptMode=True;  self.onScript()
    def TestPlotStart(self):
        self.IdleMode()
        #self.mScope_initTestPlot()
        self.hbInitTestPlot() # heartbeatinit
        #self.test_Thermoinit()
        #        self.pBTN_EnableTimer.setStyleSheet("color: red; border-radius: 5px; background: rgb(50,15,15);")
        self.EnTimer=1
        self.TESTPLOTEN=True
        self.timer.start(50)   # enable onTimer(self)
        return

#####################################
    def IdleMode(self):
        self.worker.kill()
        self.parser.stopInf()
        self.parser.V2Icontrol(0)
        if (self.parser.ft232h_connected): # keep the sequence of clearfifo and purge
            self.parser.clearfifo()
            self.parser.ft232h.purge(3)

        self.TESTPLOTEN = False
        self.SignalPLOTEN = False
        #self.TemperaturePLOTEN = False
        #self.EnTimer = 0

        self.parser.SETTLING_PASSED = True

        self.initStartRecord()
        self.select6xOr4xChannelMode1()
        self.echoEnableMode = True
        return

    def initStartRecord(self):
        self.parser.nextCycleToRead  = 0      # next reading will be written from this frame
        self.parser.Recordtail=self.parser.nextCycleToRead
        self.parser.nextByteBufferWritePointer = 0 # start loading from this index (offset in bytes)
        self.parser.nextCycleToPlotStart =0

########################################
    def ReviewMode(self):
        self.IdleMode()
        if (self.FourChannelMode):
            self.IdleMode()
            #self.mScope.clear()
            #smps=self.parser.CycleSamples*self.parser.NcyclesinBuffer
            smps=self.parser.SamplesInFrame*32
            sm=4*smps
            self.xrange2=np.linspace(0, smps -1, smps)
            data_R=self.parser.i32arrayRX[0:sm:4]
            data_G=self.parser.i32arrayRX[1:sm:4]
            data_B=self.parser.i32arrayRX[2:sm:4]
            data_Y=self.parser.i32arrayRX[3:sm:4]
            self.signal_line_RED.setData(self.xrange2,(-data_R) + self.SB_OFFSET[0])
            self.signal_line_GRN.setData(self.xrange2,(-data_G) + self.SB_OFFSET[1])
            self.signal_line_CYA.setData(self.xrange2,(-data_B) + self.SB_OFFSET[2])
            self.signal_line_YEL.setData(self.xrange2,(-data_Y) + self.SB_OFFSET[3])
            self.mScopeSignal.setXRange(0, smps, padding=0)
            self.mScopeSignal.setMouseEnabled(x=True, y=True)

    ###############################################
    def SignalPlotInit(self):    # TODO add configuration for TXonlyMode mode
        self.SignalPLOTEN=True
        # update script variables
        self.parser.nextCycleToRead   = 0      # next reading will be written from this frame
        self.parser.nextByteBufferWritePointer  = 0 # start loading from this index (offset in bytes)
        self.parser.nextCycleToPlotStart = 0
        # First validate variables
        self.parser.TotalWords16ToGet=self.parser.SamplesInFrame*self.parser.Words16inSample*((self.parser.rRemainCyclesCNT[1]&0xFFF)+1)
        self.listHistory.addItem("SignalPlotInit: rRemainCyclesTotalWords16ToGet {:d} ".format(self.parser.TotalWords16ToGet))
        if (self.parser.SlotNumbers > 2047):
            self.listHistory.addItem(".-----------------------------------------------.")
            self.listHistory.addItem("| SlotNumbers Should be smaller than 2048 !!!!! |")
            self.listHistory.addItem("`-----------------------------------------------'")
            self.parser.f_resetcmdbuf()
            return
        else:


            self.parser.resetplottedsignals()
            self.ALPHA_BETTA_CNT.ALPHA_SpinBox_changed(0)
            self.PreviewButtonClicked()
            self.ScopeVariance.clear()
            self.ScopeVariance.setYRange(0,0.000003,padding=0)  # padding is offset from up and down
            self.ScopeVariance.setXRange(0,self.parser.SamplesInFrame,padding=self.cmnXpadding)




            self.mScopeSignal.clear()
            self.mScopeSignal.setXRange(0, self.parser.SamplesInFrame, padding=self.cmnXpadding)  # padding is offset from left and right
            self.xrange=np.linspace(0,self.parser.SamplesInFrame-1,self.parser.SamplesInFrame)


            self.signal_line=[self.mScopeSignal.plot(pen = self.signal_pen[0]),
                              self.mScopeSignal.plot(pen = self.signal_pen[1]),
                              self.mScopeSignal.plot(pen = self.signal_pen[2]),
                              self.mScopeSignal.plot(pen = self.signal_pen[3]),
                              self.mScopeSignal.plot(pen = self.signal_pen[4]),
                              self.mScopeSignal.plot(pen = self.signal_pen[5])]


            #self.Error_line    = self.ScopePreviewN_Variance.plot(pen = self.signal_pen[0]),

            self.Variance_line=[self.ScopeVariance.plot(pen = self.signal_pen[0]),
                                self.ScopeVariance.plot(pen = self.signal_pen[1]),
                                self.ScopeVariance.plot(pen = self.signal_pen[2]),
                                self.ScopeVariance.plot(pen = self.signal_pen[3]),
                                self.ScopeVariance.plot(pen = self.signal_pen[4]),
                                self.ScopeVariance.plot(pen = self.signal_pen[5])]


            self.parser.ft232h.purge(3)   # clear buffers

            if (self.parser.SignallingMode == self.parser.TimerMode) :
                self.parser.rRemainCyclesCNTMODE=self.parser.rRemainCyclesFiniteMODE
                self.listHistory.addItem("SignalPlotInit: STARTING IN Timer MODE  {:04x}".format(self.parser.rRemainCyclesCNTMODE))

            elif (self.parser.SignallingMode == self.parser.CSFmode) :
                self.parser.rRemainCyclesCNTMODE=self.parser.rRemainCyclesFiniteMODE   # runCSF mode
                self.parser.rRemainCyclesCNT[1] = self.parser.rRemainCyclesCNTMODE + self.parser.framesPerRead - np.uint16(1)
                self.listHistory.addItem('SignalPlotInit: STARTING IN  runCSF_F MODE ...')

            elif (self.parser.SignallingMode == self.parser.INFmode): # if
                self.parser.rRemainCyclesCNTMODE = self.parser.rRemainCyclesINFMODE   # infinite mode
                self.parser.rRemainCyclesCNT[1] = self.parser.rRemainCyclesCNTMODE + self.parser.framesPerRead - np.uint16(1)
                self.listHistory.addItem("SignalPlotInit: STARTING IN Infinite MODE ...")

            #elif (self.parser.SignallingMode == self.parser.TXonlyMode):
            #    self.listHistory.addItem("SignalPlotInit: STARTING IN TXONLY MODE ...")
            #    self.parser.rRemainCyclesCNTMODE = self.parser.rRemainCyclesINFMODE   # infinite mode
            #    self.parser.rRemainCyclesCNT[1] = self.parser.rRemainCyclesCNTMODE + self.parser.framesPerRead - np.uint16(1)

            else:
                self.listHistory.addItem(" \nSignalPlotInit: Wrong Mode Number")
                return

            # This section for adding initial cycles to keep buffer of TX full of commands
            #if (self.parser.framesPreload):  self.commonrequest(np.uint16(self.parser.framesPerRead))

            # TODO
            # TECDELAY
            if (self.parser.SETTLING_TIME <= 0):  # Settling time is when TEC error become close to 0
                self.onCreateThread()             # if Settling time is not defined then start ! #
            else:                                 #  otherwise wait settling time
            # Now we should set TEC and wait until temperature will be settled
                self.rBTN_enThermomeasurement.setChecked(True)
                self.EnableThermomeasurement()

                self.TEC_QSpinBox.setValue(self.parser.TECTARGET_ºC)
                self.TEC_btnEn.setChecked(True)

                self.TEC_ENABLE()
                self.TimerCounter=0
                self.EnTimer=1
                self.parser.tmrTimetmp = self.parser.SETTLING_TIME
                self.TemperaturePLOTEN=True
                self.timer.start(50)
            #
            #self.timer.start(50)
            return
    #############################################################################################################################
    def onCreateThread(self):
        self.worker=Worker(self.threadloop)
        self.worker.signals.result1.connect(self.signalPlot)        # connects emitted by thread signal "result1" to signalPlot
        self.worker.signals.result2.connect(self.plotSignalsnSave)  # connects emitted by thread signal "result1" to signalPlot
        self.worker.SetMode(self.parser.SignallingMode) # passing the SignallingMode to worker
        self.threadpool.start(self.worker)              # Starts Thread
    ######################################################################################################################
    def threadloop(self):
        self.parser.sc_getFIFOreq(self.parser.TotalWords16ToGet,np.uint16(self.parser.framesPerRead))  # request Data usually 64 frames
        self.parser.getb_rq(self.parser.TEC_TERMO_BUF_Adr,self.parser.TEC_TERMO_BUF_Wlength) # adding request of get temperature command
        self.parser.ftsend()

        self.DIGITAL_GAIN_BOX.refreshGainnOffset()
        self.parser.msGain=self.DIGITAL_GAIN_BOX.msGain
        self.parser.msOffset=self.DIGITAL_GAIN_BOX.msOffset
        self.parser.plotmode4or6 = self.rBTN_4_2xCH.isChecked()
        self.parser.Kalpha = self.ALPHA_BETTA_CNT.ALPHA_value

        self.parser.ftgetNbytesMframes(self.parser.TotalWords16ToGet,self.parser.framesPerRead)  # gets requested data
        self.parser.getTECbuffer()
        #self.signalPlot()
    #############################################################################################################################
    # PLOTSIGNAL signalPlot
    def signalPlot(self): # called by message emitted from Thread
        for i in range(4):
            self.signal_line[i].setData(self.xrange,self.parser.i32arrayRXV[i,:self.parser.SamplesInFrame])
            if (self.rBTN_Variance.isChecked()):
                self.Variance_line[i].setData(self.xrange, self.parser.i32arrayRXV_msqr[i,:self.parser.SamplesInFrame])

        if ( not self.FourChannelMode):
            for i in range(4,self.signal_bims) :
                self.signal_line[i].setData(self.xrange,self.parser.i32arrayRXV[i,:self.parser.SamplesInFrame])
                #self.Variance_line[i].setData(self.xrange, self.parser.i32arrayVAR[i,:self.parser.SamplesInFrame])

        #self.Error_line.setData   (self.xrange, self.parser.i32arrayRXV_err [:self.parser.SamplesInFrame])
        return
    ##############################################################################################################################
    #def unformatFrame(self,startingword,samplesinframe): #
    #    '''
    #    startingword -starting offset in words,
     #   startingword - number of samples in Frame
     #   '''
     #   self.msOffset = self.DIGITAL_GAIN_BOX.msOffset
     #   self.msGN=self.parser.msGain
     #   self.parser.Kalpha   = self.ALPHA_BETTA_CNT.ALPHA_value
#
#        P = startingword
#        for i in range(samplesinframe):
#            self.parser.unformatSample(P)
#            ###################
#            self.parser.PreparePlotFilterData(i)
#            #self.PlotCalc(i)
#            P+=4
    ####################################################################
    def PlotCalc(self,i):        # scaling samples, variance shouldn't be scaled
        for y in range(4):
            self.parser.i32arrayRXV[y,i] = self.msOffset[y] + (self.msGN[y] * self.parser.i32arrayRXV_EST[y,i])
        if (self.rBTN_4_2xCH.isChecked()) :
            self.parser.i32arrayRXV[4,i] = self.msOffset[4] + (self.msGN[4] * (self.parser.i32arrayRXV_EST[0,i] + self.parser.i32arrayRXV_EST[3,i]))
            self.parser.i32arrayRXV[5,i] = self.msOffset[5] + (self.msGN[5] * (self.parser.i32arrayRXV_EST[0,i] - self.parser.i32arrayRXV_EST[3,i]))
        else:
            self.parser.i32arrayRXV[4,i] = self.msOffset[4] + (self.msGN[4] * self.parser.i32arrayRXV_EST[4,i])
            self.parser.i32arrayRXV[5,i] = self.msOffset[5] + (self.msGN[5] * self.parser.i32arrayRXV_EST[5,i])

   ###########################################################################################################################
    def TEC_ENABLE(self):
        if (self.parser.ft232h_connected):
            if (self.TEC_btnEn.isChecked()):
                self.TEC_btnEn.setStyleSheet("color: #FFFF00;  border-radius: 3px; background: #802020")
                f=self.TEC_QSpinBox.value()
                #self.listHistory.addItem("{:04.2F}".format(f) )
                cod=self.convert.TECcode(f) - 2
                #self.listHistory.addItem("{:04d}".format(cod) )
                voltage = cod*1.6/4095
                #self.listHistory.addItem("{:04.2F}".format(voltage) )
                self.parser.txbarrayindex=0; self.parser.add_TEC_setDAC(np.uint16(cod)); self.parser.ftsend()
                self.parser.TEC_OnOFF(1)
                self.EnTimer = 1
                self.timer.start(50)
                return
            else:
                self.TEC_btnEn.setStyleSheet("color: #808000;  border-radius: 3px; background: #202020")
                self.parser.TEC_OnOFF(0); self.EnTimer = 1 ;
                return
        else:
            self.USBNotConnected()
            self.TEC_btnEn.setChecked(False)
            return

    def TEC_PlotInit(self):
        self.TEC_Scope.clear()
        self.TEC_Scope_plotstart =0
        return
#    self.TEC_QSpinBox.setValue()
  ###########################################################################################################################
    def EnableThermomeasurement(self):
        if (self.parser.ft232h_connected):
            if (self.rBTN_enThermomeasurement.isChecked()):
                self.rBTN_enThermomeasurement.setStyleSheet("color: #FFFF00;  border-radius: 3px; background: #802020")
                self.thermoGraph_PlotInit()
                self.TemperaturePLOTEN = True ;  self.TemperaturePLOTPeriod = 4;  self.EnTimer = 1;  self.timer.start(50)
                return
            else:
                self.rBTN_enThermomeasurement.setStyleSheet("color: #808000;  border-radius: 3px; background: #202020")
                self.EnTimer = 1 ;    self.TemperaturePLOTEN= False
                return
        else:
            self.USBNotConnected()
            self.rBTN_enThermomeasurement.setChecked(False)
            return

    def thermoGraph_PlotInit(self):
        self.thermoGraph_Scope.clear()
        self.thermoGraph_Scope.setYRange(23,30,padding=.025)  # padding is offset from up and down
        self.thermoGraph_Scope.setXRange(self.thermo_xrange_s,self.thermoGraph_xrange_d,padding=0.00)  # padding is offset from left and right
        self.thermoGraph_Scope.showGrid(x=True,y=True,alpha=.8)
        self.thermoGraph_plotstart =0
        self.thermoGraph_plotend   = self.thermoGraph_xrange_d
        self.thermoGraph_wrptr     = self.thermoGraph_xrange_d  # Current offset in buffer
        self.thermoGraph_wrptr2    = self.thermoGraph_wrptr

        self.thermoGraph_MXBF[:,:]  = np.array(24.5*np.ones([self.bims,self.thermo_graphmax]))
        self.thermoGraph_line=[self.thermoGraph_Scope.plot(self.thermoGrapg_xrange, self.thermoGraph_MXBF[0,self.thermoGraph_plotstart : self.thermoGraph_plotend],  pen = self.thermoGraph_pen[0]),
                               self.thermoGraph_Scope.plot(self.thermoGrapg_xrange, self.thermoGraph_MXBF[1,self.thermoGraph_plotstart : self.thermoGraph_plotend],  pen = self.thermoGraph_pen[1]),
                               self.thermoGraph_Scope.plot(self.thermoGrapg_xrange, self.thermoGraph_MXBF[2,self.thermoGraph_plotstart : self.thermoGraph_plotend],  pen = self.thermoGraph_pen[2]),
                               self.thermoGraph_Scope.plot(self.thermoGrapg_xrange, self.thermoGraph_MXBF[3,self.thermoGraph_plotstart : self.thermoGraph_plotend],  pen = self.thermoGraph_pen[3]),
                               self.thermoGraph_Scope.plot(self.thermoGrapg_xrange, self.thermoGraph_MXBF[4,self.thermoGraph_plotstart : self.thermoGraph_plotend],  pen = self.thermoGraph_pen[4]),
                               self.thermoGraph_Scope.plot(self.thermoGrapg_xrange, self.thermoGraph_MXBF[5,self.thermoGraph_plotstart : self.thermoGraph_plotend],  pen = self.thermoGraph_pen[5])]

        self.parser.wr_reg(self.parser.rTECT_CNT[0], self.parser.EFM_CMD_GETDATA)

        for i in range(0, 6):   self.tmp[i] =25.0
        self.thermoGraph_firstTime=True
        return

    def thermoGraph_update(self):
        #self.parser.SetEFM(self.parser.EFM_CMD_LED_ON)
        if ( self.rBTN_IDLE.isChecked() or self.rBTN_SIMULATOR.isChecked() or  (not self.parser.SETTLING_PASSED) ):
            self.parser.TTEC_GETDATA(10)

        for x in range(0, 20):  self.parser.uCUDATA_RX8[x]=self.parser.barrayRX[x]
        if (self.thermoGraph_firstTime):
            for i in range(0, 6):   self.tmp[i]=self.convert.GetTempfromCod(int(self.parser.uCUDATA_RX16[i+1]))
            self.thermoGraph_firstTime=False
        else:
            if (self.rBTN_enThermoFilter.isChecked()):
                for i in range(0, 6):   self.tmp[i] += (self.convert.GetTempfromCod(int(self.parser.uCUDATA_RX16[i+1])) - self.tmp[i] ) * 0.1
            else:
                for i in range(0, 6):   self.tmp[i]=self.convert.GetTempfromCod(int(self.parser.uCUDATA_RX16[i+1]))

        #print(self.parser.uCUDATA_RX16[7])
        VITEC= self.parser.EFMADCLSB * int(self.parser.uCUDATA_RX16[7])

        self.tmp[6] =(VITEC-1.52)/0.8
        self.TEC_Label3.setText("I (A)  {:06.4F}".format(self.tmp[6])) # VITEC,

        self.tmp1Label.setText("{:04.2F}".format(self.tmp[0])) ;         self.tmp2Label.setText("{:04.2F}".format(self.tmp[1]))
        self.tmp3Label.setText("{:04.2F}".format(self.tmp[2])) ;         self.tmp4Label.setText("{:04.2F}".format(self.tmp[3]))
        self.tmp5Label.setText("{:04.2F}".format(self.tmp[4])) ;         self.tmp6Label.setText("{:04.2F}".format(self.tmp[5]))

        VTECTEMP=self.parser.EFMADCLSB * int(self.parser.uCUDATA_RX16[8]) # Voltage at divider
        self.VTECTEMP2 += (VTECTEMP- self.VTECTEMP2)/50

        self.Isense2= (1.5 - self.VTECTEMP2 ) /10 #(ma)
        # self.Isense2 += (Isense - self.Isense2)/50

        Rterm = (self.VTECTEMP2/self.Isense2)
        self.TEC_Label2.setText("Rterm {:06.3F} ".format(Rterm))

        self.thermoGraph_MXBF[:,self.thermoGraph_wrptr] = self.tmp[0:6]
        if (self.thermoGraph_wrptr2 < self.thermoGraph_xrange_d) : self.thermoGraph_MXBF[:,self.thermoGraph_wrptr2] = self.tmp[0:6]

        for i in range(self.bims):
            self.thermoGraph_line[i].setData(self.thermoGrapg_xrange,self.thermoGraph_MXBF[i,self.thermoGraph_plotstart: self.thermoGraph_wrptr])  # TODO
        # add plot of TEC temperature here


        self.thermoGraph_plotstart += 1
        self.thermoGraph_plotstart=self.thermoGraph_plotstart%self.thermo_recordLengthmax
        self.thermoGraph_wrptr  = self.thermoGraph_plotstart + self.thermoGraph_xrange_d
        self.thermoGraph_wrptr2 = self.thermoGraph_wrptr % self.thermo_recordLengthmax
        return
    #############################################################################################################################
    def SaveHeadertoFile(self,fileID):
        # writing header if defined
        if self.parser.boolSaveHeaderEn:
            # 1 write board serial number

            fileID.write("BOARD SERIAL NUMBER  :  " + self.parser.dict["serial"].decode("utf-8") + "\n")

            # 2-write script into file
            txt = self.editor.toPlainText()
            txt1 = txt.splitlines()
            # self.linnum=1
            # print(self.parser.currentScriptName)
            namesfound = 0
            for x in txt1:
                mycollapsedstring = ' '.join(x.split())  # removes extra ' ' from the line
                self.TT = mycollapsedstring.split(' ')  # creates array of words
                num_parameters = len(self.TT)  # defines number of words in string
                if (namesfound == 0):  # if scriptname is not found yet
                    if num_parameters == 2:  # check if string is the name of script
                        if (self.TT[0] == '#' and self.TT[1] == self.parser.currentScriptName):
                            namesfound = 1
                            fileID.write(x + "\n")
                            continue
                        else:
                            continue
                    else:
                        continue

                if (namesfound == 1):
                    if self.TT[0] != "end":
                        fileID.write(x + "\n")
                    else:
                        namesfound = 2;
                        fileID.write(x + "\n")
                if (namesfound == 2): break

            if namesfound != 2:
                self.listHistory.addItem("End of Search")
                self.listHistory.addItem(self.parser.currentScriptName + "Not found ")
                self.listHistory.addItem("No file written")
                fileID.close()
                return(False)
        return (True)
    #############################################################################################################################
    def plotSignalsnSave(self):
        #self.listHistory.addItem("plotSignalsnSave")
        if self.parser.ploten :  self.signalPlot()
        if self.parser.savetofile:
            #self.listHistory.addItem("Saving to file ....")
            # define output file name
            fileName = self.parser.SaveFileName
            if self.parser.dateStampEnable:   fileName += tm.strftime("_%Y-%m-%d_at_%H_%M_%S")
            if self.parser.fileNumberEn    :  fileName += "_{:d}".format(self.parser.filenumber)
            fileName += ".txt"
            self.parser.filenumber += 1
            fl1 = open(fileName,'w')
            if self.parser.boolSaveHeaderEn :
                if (not self.SaveHeadertoFile(fl1)): fl1.close(); return(0)


            # Writing  sampled data
            words32inCycle    = self.parser.SamplesInFrame<<2
            for j in range(self.parser.framesPerRead):
                W32PointerinCycle = j*words32inCycle
                self.parser.unformatFrameOnly(W32PointerinCycle,self.parser.SamplesInFrame)
                for i in range(self.parser.SamplesInFrame):
                    fl1.write("{:f}\t{:f}\t{:f}\t{:f}\t{:f}\t{:f}\n".format(self.parser.i32arrayRXV[0,i],self.parser.i32arrayRXV[1,i],
                                                                            self.parser.i32arrayRXV[2,i],self.parser.i32arrayRXV[3,i],
                                                                            self.parser.i32arrayRXV[4,i],self.parser.i32arrayRXV[5,i]))
            fl1.close()
            self.listHistory.addItem("{:s} saved".format(fileName))
            self.listHistory.scrollToBottom()
            self.initStartRecord()
#                       #os.system("start " + self.parser.startExeFName + " " + self.SaveFileName)
            # see also
            # subprocess.check_output(["echo", "Hello World!"])
            if self.parser.startExeEn :
                # os.system("start " + self.parser.startExeFName)
                #subprocess.call(["ls", "-1"])
                #prc = Popen(["ls", "-1", "*.txt"], stdout=PIPE)
                #prc = Popen(["ls", "-1", "*.txt"])
                #output = subprocess.check_output(["ls","-1","*.txt"],universal_newlines=True)
                self.listHistory.addItem("\n\n" + self.parser.startExeFName)
                if (self.parser.execmdaddfn) :
                    outputstr = subprocess.check_output(self.parser.startExeFName + " " + fileName, shell=True, universal_newlines=True)
                else:
                    outputstr = subprocess.check_output(self.parser.startExeFName, shell=True, universal_newlines=True)
                txt1=outputstr.splitlines()
                for x in txt1:
                    self.listHistory.addItem(x)

            #self.IdleMode()
            # exit by run or end of run
        if (self.parser.SignallingMode == self.parser.INFmode) :
            self.listHistory.addItem("End of INFmode ")
            self.listHistory.addItem("--------")
            #self.parser.runinfflag=False
            self.IdleMode()
            self.rBTN_IDLE.setChecked(True)
            if (self.parser.boolexit): sys.exit()

            # exit by run_Cycles_Sec or looping
        if ( self.parser.SignallingMode == self.parser.CSFmode):
            self.parser.tmrcycles -= 1
            if (self.parser.tmrcycles == 0):
                self.parser.run_Cycles_Flag=False
                self.listHistory.addItem("... end of CSFmode")

                self.IdleMode()
                self.rBTN_IDLE.setChecked(True)
                if (self.parser.boolexit): sys.exit()

        if (self.parser.SignallingMode == self.parser.Timer_CSFmode):
            self.parser.tmrcycles -= 1
            if (self.parser.tmrcycles == 0):
                self.parser.run_Cycles_Flag = False
                self.listHistory.addItem("... end of Timer_CSFmode")
                self.IdleMode()
                self.rBTN_IDLE.setChecked(True)
                if (self.parser.boolexit): sys.exit()

        if (self.parser.SignallingMode == self.parser.TEC_CSFmode):
            self.parser.tmrcycles -= 1
            if (self.parser.tmrcycles == 0):
                self.parser.run_Cycles_Flag = False
                self.listHistory.addItem("... end of TC_CSFmode")
                self.IdleMode()
                self.rBTN_IDLE.setChecked(True)
                if (self.parser.boolexit): sys.exit()


            else:
               # restart timer
                self.TimerCounter=0
                self.parser.tmrTimetmp=self.parser.tmrTime
                self.EnTimer=1
                #self.listHistory.addItem("restart Timer")
                self.timer.start(50)
        self.listHistory.scrollToBottom()

        return
#############################################
###################################################################################
###################################################################################
    def hbInitTestPlot(self):
        self.hbeatScope.clear()
        self.hbeatRec_buffer=np.zeros(self.HB_RecLength,np.int16)  # record buffer
        self.hbsc_buffer=np.zeros(self.HB_ScLengSmp)  # buffer for screen
        self.HB_CurrentPoint=0
        self.hbeatScope.setXRange(0,self.hbeat_Screen_ms-self.HB_SamplePeriodms,padding=.02)
        self.hbeatScope.setYRange(2,-2,padding=.025)  # padding is offset from up and down
        self.hBstart=0;
        self.hBEnd=self.hBstart+1
        self.hbeat_line=self.hbeatScope.plot(self.hbeat_timeScale,self.hbsc_buffer,pen=self.hbeatPEN)  # draws 0 - line
        return
    def hbScope_RefreshTestPlot(self):
        #update data first
        angle=self.hbeat_timeAngles[self.HB_CurrentPoint]  # Find new value for angle
        # Find new value for Sample
        self.hbeatRec_buffer[self.HB_CurrentPoint]=np.int16(-1000*(np.sin(1.5*angle)+0.52*np.sin(3*angle)+0.45*np.sin(4.5*angle)))
        # define which section to plot
        self.HB_Viewsection=((self.HB_CurrentPoint//self.HB_ScLengSmp)*self.HB_ScLengSmp)
        self.hbPointsToDraw=self.HB_CurrentPoint%self.HB_ScLengSmp
        # Concatenate and normalize
        self.hbsc_buffer=0.001*(np.concatenate((self.hbeatRec_buffer[self.HB_Viewsection: self.HB_CurrentPoint],np.zeros(self.HB_ScLengSmp-self.hbPointsToDraw,np.int32))))
        self.HB_CurrentPoint=(self.HB_CurrentPoint+1)%self.HB_RecLength  # update increment pointer
        self.HB_Box.setTitle(str("HEARTBEAT SAMPLES : {:04d} - {:04d} ".format(self.HB_Viewsection,self.HB_Viewsection+self.HB_ScLengSmp-1)))
        #self.hbeat_line.setData(self.hbeat_timeScale[20:50],self.hbsc_buffer[20:50],)        # Plot it
        self.hbeat_line.setData(self.hbeat_timeScale,self.hbsc_buffer)  # Plot it
        return
###################################################################################################
######################################################################################################################
######################################################################################################################
############################################################

    #################################################################################

    def getGainnOffset(self):
        self.DIGITAL_GAIN_BOX.refreshGainnOffset()
        self.msMult     = self.DIGITAL_GAIN_BOX.msMult
        self.msOffset   = self.DIGITAL_GAIN_BOX.msOffset

    def onRunTest(self): self.onRunTest3FPGALEDTEST()

    def onRunTest3FPGALEDTEST(self):
        self.parser.SN74HCS594ControlByte = self.parser.SN74HCS594ControlByte ^ 0x80
        self.parser.V2_SN74HCS594_set()

    def onRunTest2(self):
        self.DIGITAL_GAIN_BOX.refreshGainnOffset()
        self.msMult     = self.DIGITAL_GAIN_BOX.msMult
        self.msOffset   = self.DIGITAL_GAIN_BOX.msOffset

        print(self.DIGITAL_GAIN_BOX.msGain)
        print(self.DIGITAL_GAIN_BOX.msMult)
        print(self.msMult)
        print(self.msOffset)


    def onRunTest1(self):
        for x in range(6):
            self.listHistory.addItem(str('[{:03d}] {:04X} {:04X}'. format(x, self.parser.LaserSlotTable[x,0], self.parser.LaserSlotTable[x,1])))
        self.listHistory.addItem('---------------')
        self.listHistory.scrollToBottom()
    #################################################################################
    #################################################################################
    def onRunTest0(self):
        print("onRunTest:",self.parser.txbarrayindex)
        self.listHistory.addItem('--- SlotTableArray--')
        self.listHistory.addItem(' Number of lines {:03d}'.format(self.parser.SlotNumbers))
        for x in range(self.parser.SlotNumbers):
            self.listHistory.addItem(str('[{:03d}] {:04X} {:04X} {:04X} {:04X}'.format(x, self.parser.LaserSlotTable[x,0],
                                                                          self.parser.LaserSlotTable[x,1],
                                                                          self.parser.LaserSlotTable[x,2],
                                                                          self.parser.LaserSlotTable[x,3])))
        self.listHistory.addItem('---------------')
# Dump TX Buffer
        self.listHistory.addItem('--- barrayTX dump ---')
        print("onRunTest:",self.parser.txbarrayindex)
        self.listHistory.addItem('Number of BYTES {:03d} '.format(self.parser.txbarrayindex))
        self.dumparray(self.parser.barrayTX,self.parser.txbarrayindex)
        self.listHistory.addItem('---------------')
#       Dump RX Buffer
        self.listHistory.addItem('barrayRX[0:28] dump')
        self.dumparray(self.parser.barrayRXA,self.parser.TotalWords16ToGet<<1)

        self.listHistory.addItem('---------------')
#        self.parser.getTTEC() ;
        self.listHistory.scrollToBottom()
    #################################################################################

    def dumparray(self,ar,num):
        for x in range(0,num):
            # self.listHistory.addItem(str('{:02x}'.format(ar[x])))
            print("dump_array:  ", str('adr {:02d} {:02x}'.format(x, ar[x])))
        return
    def dumparray2(self,ar,nlines):
        for x in range(0,nlines):
            y=20*x
            print("dump_array2 : ",str('{:02x}{:02x}_{:02x}{:02x}   {:02x}{:02x}_{:02x}{:02x}   {:02x}{:02x}_{:02x}{:02x}   '
                      '{:02x}{:02x}_{:02x}{:02x}   {:02x}{:02x}_{:02x}{:02x}'.format(
                ar[y],ar[y+1],ar[y+2],ar[y+3],ar[y+4],ar[y+5],ar[y+6],ar[y+7],ar[y+8],ar[y+9],
                ar[y+10],ar[y+11],ar[y+12],ar[y+13],ar[y+14],ar[y+15],ar[y+16],ar[y+17],ar[y+18],ar[y+19])))
        return

    def dumpslots(self):
        self.listHistory.addItem('\n---------------- SLOT PARAMETERS ------------')
        if (self.parser.FPGAVer==7 or self.parser.FPGAVer == 6): #     LaserSlotTable
            for x in range(self.parser.SlotNumbers):
                self.listHistory.addItem('{:02d}  {:04x} {:04x} {:04x} {:04x}'.format(x,self.parser.LaserSlotTable[x, 0],
                                                                                self.parser.LaserSlotTable[x, 1],
                                                                                self.parser.LaserSlotTable[x, 2],
                                                                                self.parser.LaserSlotTable[x, 3]))


        if (self.parser.FPGAVer==8): #     LaserSlotTable
            for x in range(self.parser.SlotNumbers):
                self.listHistory.addItem('{:02d}  {:04x} {:04x} {:04x} {:04x}  {:04x} {:04x} {:04x} {:04x}'.format(x,
                                                                                self.parser.LaserSlotTableV2_0[x, 0],
                                                                                self.parser.LaserSlotTableV2_0[x, 1],
                                                                                self.parser.LaserSlotTableV2_0[x, 2],
                                                                                self.parser.LaserSlotTableV2_0[x, 3],
                                                                                self.parser.LaserSlotTableV2_0[x, 4],
                                                                                self.parser.LaserSlotTableV2_0[x, 5],
                                                                                self.parser.LaserSlotTableV2_0[x, 6],
                                                                                self.parser.LaserSlotTableV2_0[x, 7]))
                self.listHistory.addItem('    {:04x} {:04x} {:04x} {:04x}  {:04x} {:04x} {:04x} {:04x}'.format(
                                                                                self.parser.LaserSlotTableV2_0[x, 8],
                                                                                self.parser.LaserSlotTableV2_0[x, 9],
                                                                                self.parser.LaserSlotTableV2_0[x, 10],
                                                                                self.parser.LaserSlotTableV2_0[x, 11],
                                                                                self.parser.LaserSlotTableV2_0[x, 12],
                                                                                self.parser.LaserSlotTableV2_0[x, 13],
                                                                                self.parser.LaserSlotTableV2_0[x, 14],
                                                                                self.parser.LaserSlotTableV2_0[x, 15]))
                self.listHistory.addItem('    {:04x} {:04x} {:04x} {:04x}'.format( self.parser.LaserSlotTableV2_1[x, 0],
                                                                                   self.parser.LaserSlotTableV2_1[x, 1],
                                                                                   self.parser.LaserSlotTableV2_1[x, 2],
                                                                                   self.parser.LaserSlotTableV2_1[x, 3]))
        self.listHistory.addItem('------------ END of SLOT PARAMETERS ---------\n')


    # self.LaserSlotTableV2_0[self.SlotNumbers, 0]
        return


    #################################################################################

    def on_ReturnPressed(self):
#        self.listWidgetMSG.clear()
        self.parser.returnmessage = ""
        rtc = 0
        if self.lEdit1.text() != '':
            if self.lEdit1.text() != 'r': self.previousline = self.lEdit1.text()
            rtc = self.parser.cmdstringex(self.lEdit1.text())
            #print("rtc=",rtc)
            if rtc == self.parser.ok:
                if self.parser.enableResultShow:
                    if (self.echoEnableMode):
                        #self.listWidgetMSG.clear()
                        self.listHistory.addItem(self.lEdit1.text()+self.parser.returnmessage)
                    #else:
                    #    self.listHistory.addItem(self.lEdit1.text())
                else: self.parser.enableResultShow = False
                if (self.echoEnableMode): self.listHistory.scrollToBottom()
            elif rtc==self.parser.hlp:
                #self.listWidgetMSG.clear()
                for x in self.parser.helpmessage: self.listHistory.addItem(x)
                rtc=0
            elif rtc == self.parser.refresh:
                self.fupdateRegisters(); #self.listWidgetMSG.clear()
                if (self.echoEnableMode):
                    self.listHistory.addItem(self.parser.message[rtc]); rtc = 0

            #elif rtc == self.parser.outofrange :  return rtc

            elif rtc == self.parser.commentLine: rtc = 0
            elif rtc == self.parser.clrhist: self.clearHistory(); rtc = 0
            elif rtc == self.parser.repeat_cmd:  self.lEdit1.setText(self.previousline); return rtc
            elif rtc == self.parser.report: self.freport(); rtc=0;
            elif rtc == self.parser.rtn_dumpSlots: self.dumpslots(); return 0
            elif rtc == self.parser.f_getadc: self.dumpadc(); rtc=0;
            elif rtc == self.parser.v_average: self.average(); rtc=0;
            elif rtc == self.parser.v_rpv: self.reportVariables(); rtc=0;
            elif rtc == self.parser.v_clearfifo: self.parser.clearfifo(); rtc = 0;
            elif rtc == self.parser.v_scriptFound:  rtc = 0; return rtc;
            elif rtc == self.parser.v_echoen:        self.echoEnableMode=True;    rtc=0;  return rtc
            elif rtc == self.parser.v_echodis:       self.echoEnableMode=False;   rtc=0;  return rtc
            elif rtc == self.parser.v_signalplotinit:     rtc=0;  return rtc     ; 'run' 'runshort'
            #elif rtc == self.parser.v_signalplotinit2:    rtc=0;  return rtc     ; 'run2'
             # elif rtc == self.parser.runCycles:            rtc=0;  return rtc
            elif (rtc == self.parser.outofrange
                  or  rtc==self.parser.rtn_notSupported
                  or rtc==self.parser.too_many_slots) :
                self.listHistory.addItem("Err: ln{:d} ".format(self.linnum) + self.parser.message[rtc])

            elif rtc==self.parser.clearplot :
                self.mScopeSignal.clear()
                self.ScopeVariance.clear()
                rtc=0
            elif rtc==self.parser.sleepcommand :
                if self.parser.sleepen :
                    tm.sleep(self.parser.sleeptime)
                rtc=0

            # elif rtc == self.parser.timercmd :   #   'repeatByTimer'
            #    #self.clearHistory()
            #    self.listHistory.addItem("")
            #    self.listHistory.addItem("")
            #    self.listHistory.addItem("{:s} will work {:d} times  each {:d} sec".format(self.parser.tmrcmdline,self.parser.tmrcycles,self.parser.tmrTime))
            #    self.listHistory.addItem("-----------------------")
            #    #cself.runByTimer()
            #    self.EnTimer = 1
            #    self.TimerCounter=0
            #     self.timer.start(1000)  # calls runByTimer()
            #     rtc=0

            elif rtc == self.parser.exit :        rtc = 0; return rtc
            elif rtc == self.parser.saveheader :  rtc = 0; return rtc
            elif rtc == self.parser.systemconfig :
                self.listHistory.addItem(self.lEdit1.text()+self.parser.returnmessage)
                self.listHistory.addItem('FPGA SUBVERSION: {:03d}'.format( self.parser.TEST[1] >> 8 ) )
                if (self.parser.TEST[1]  & np.uint16(0x0001)) : self.listHistory.addItem("Clock is inverted")
                else: self.listHistory.addItem("Clock is straight (nonverted)")
                rtc = 0; return rtc
            elif rtc ==  self.parser.hint : self.hinteditor(); rtc = 0; return rtc
            elif rtc ==  self.parser.hlphtml : self.helphtml(); rtc = 0; return rtc


            # If command was entered manually but with error
            elif self.linnum == 0:
                self.listHistory.addItem(self.parser.message[rtc])
                self.listHistory.addItem(self.lEdit1.text())
            else:   # if error
                #print(rtc)
                #if (self.echoEnableMode):
                #    self.listHistory.addItem(self.parser.message[rtc] + ' in line ' + str(self.linnum) + ':')
                #self.listHistory.addItem(self.previousline)
                self.listHistory.scrollToBottom()
            # remove these lines
            self.lEdit1.clear()
            self.listHistory.scrollToBottom()
            return rtc
    ###############################
    def onScript(self):
        # add reset of some parameters
        self.parser.ResetInits()
        self.echoEnableMode=False

        txt=self.editor.toPlainText()
        self.txt1=txt.splitlines()
        self.linnum=1
        # self.listHistory.clear()
        rtc=0
        for x in self.txt1:
            self.lEdit1.setText(x)
            rtc=self.on_ReturnPressed()
            #print("rtc=",rtc)
            if (rtc == self.parser.runScript):
                self.listHistory.addItem("Line {:d} passed, no errors".format(self.linnum))
                self.onEnd()  # Script passed successfully, start implementation
                self.linnum = 0
                return
            if (rtc == self.parser.stopScript):
                self.listHistory.addItem("Line {:d} passed, no errors, exit from script by stop".format(self.linnum))
                self.linnum = 0
                return
            if (rtc == self.parser.outofrange):
                self.listHistory.addItem("Parameter is out of range in line{:d}".format(self.linnum))
                break
            if rtc:
                self.listHistory.addItem("Exit by error: return code is not 0 but {:d}  at line {:d}".format(rtc,self.linnum))
                break # break if returns nonzero

            self.linnum += 1
            #self.listHistory.addItem("Script was not found")


        if (rtc==0): self.listHistory.addItem("End of file, No end of script found, {:d} lines processed".format(self.linnum));
        self.linnum=0
        return
################################################################
    def onEnd(self):
        self.freport()
        #if (( self.parser.SignallingMode == self.parser.INFmode) or self.parser.run_Cycles_Flag):
        if ( self.parser.SignallingMode == self.parser.CSFmode): self.listHistory.addItem('onEnd: Starting the CSFmode....')
        if ( self.parser.SignallingMode == self.parser.INFmode): self.listHistory.addItem('onEnd: Starting the INFmode....')
        if ( self.parser.SignallingMode == self.parser.TEC_CSFmode): self.listHistory.addItem('onEnd: Starting the TEC_CSFmode....')
        if ( self.parser.SignallingMode == self.parser.Timer_CSFmode): self.listHistory.addItem('onEnd: Starting the TimerCSFmode....')
        if ( self.parser.SignallingMode == self.parser.TXonlyMode): self.listHistory.addItem('onEnd: TXonlyModeSTARTING')

        self.parser.slotTableToTXbuffer()
        self.listHistory.addItem("onEnd: Bytes to send {:d} ".format(self.parser.txbarrayindex))
        if ( self.parser.SignallingMode == self.parser.TXonlyMode):
                self.parser.RunInTXonlyMode()
                self.parser.ftsend()
                self.parser.V2Icontrol(1)  # enables current source
                self.listHistory.addItem('onEnd: TXonlyMode RUNNING ....')
                self.PreviewButtonClicked()
                return

        else:
            if (self.parser.ftsend()) :
                self.parser.V2Icontrol(1)  # enables current source
                self.SignalPlotInit()
            else : self.listHistory.addItem("onEnd: Device is not connected")
        return

   ################################################################
    # prints script names
    def getScripList(self):
        txt=self.editor.toPlainText()
        self.txt1=txt.splitlines()
        self.linnum=1
        namesfound=0
        for x in range(len(self.scriptnames)):
            self.scriptnames[x] = "- - nu - -"
        for x in self.txt1:
            mycollapsedstring=' '.join(x.split())  # removes extra ' ' from the line
            TT=mycollapsedstring.split(' ')  # creates array of words
            num_parameters=len(TT)
#            if num_parameters!=2: return self.wnp
            if TT[0]=='#':
                if num_parameters!=2:
                    self.listHistory.addItem("Script name should be 1 word only!")
                    self.listHistory.addItem("Error in line: " + str(self.linnum))
                    #return self.wnp
                else:
                    if TT[1] == 'autorun' : self.autorunflag=True
                    self.scriptnames[namesfound]=TT[1]
                    #self.listHistory.addItem("Added {:s} script from {:02d} line".format(TT[1],self.linnum ))
                    #self.listHistory.addItem("{:s} ".format(TT[1]))
                    namesfound = namesfound+1
            self.linnum += 1
        self.renamescripts()
        #self.listHistory.addItem("Total Names Found {:d}".format(namesfound))
        #self.listHistory.addItem("--------------------------------")
        self.linnum = 0
        return

    def renamescripts(self):
        self.rBTN_SCRIPT1.setText(self.scriptnames[0])
        self.rBTN_SCRIPT2.setText(self.scriptnames[1])
        self.rBTN_SCRIPT3.setText(self.scriptnames[2])
        self.rBTN_SCRIPT4.setText(self.scriptnames[3])
        self.rBTN_SCRIPT5.setText(self.scriptnames[4])
        self.rBTN_SCRIPT6.setText(self.scriptnames[5])
        self.rBTN_SCRIPT7.setText(self.scriptnames[6])
        self.rBTN_SCRIPT8.setText(self.scriptnames[7])
        self.rBTN_SCRIPT9.setText(self.scriptnames[8])
        self.rBTN_SCRIPT10.setText(self.scriptnames[9])
        return
###############################
    def runScript(self,currentScriptName):
        txt=self.editor.toPlainText()
        self.txt1=txt.splitlines()
        self.linnum=1
        namesfound=0
        for x in self.txt1:
            mycollapsedstring=' '.join(x.split())  # removes extra ' ' from the line
            TT=mycollapsedstring.split(' ')  # creates array of words
            num_parameters=len(TT)
            #            if num_parameters!=2: return self.wnp
            if TT[0]=='#':
                if num_parameters!=2:
                    self.listHistory.addItem("Wrong number of parameters for script name in line "+str(self.linnum))
                    return self.wnp
                else:
                    if (TT[1] == currentScriptName):
                        self.listHistory.addItem("# {:s}".format(TT[1]))
            self.linnum+=1
        self.listHistory.addItem("Total Names Found {:d}".format(namesfound))
        self.listHistory.addItem("--------------------------------")

        return
   ###############################
    def average(self):
        avg0 = 0.0
        avg1 = 0.0
        avg2 = 0.0
        avg3 = 0.0
        avg4 = 0.0
        m=1000
        for x in range(1000):
            self.parser.getadc6()
            avg0 = avg0 + float(((np.uint32(self.parser.ADC0MD[1])<<16)+np.uint32(self.parser.ADC0LD[1])).astype(np.int32))
            avg1 = avg1 + float(((np.uint32(self.parser.ADC1MD[1])<<16)+np.uint32(self.parser.ADC1LD[1])).astype(np.int32))
            avg2 = avg2 + float(((np.uint32(self.parser.ADC2MD[1])<<16)+np.uint32(self.parser.ADC2LD[1])).astype(np.int32))
            avg3 = avg3 + float(((np.uint32(self.parser.ADC3MD[1])<<16)+np.uint32(self.parser.ADC3LD[1])).astype(np.int32))
            avg4 = avg4 + float(((np.uint32(self.parser.ADC4MD[1])<<16)+np.uint32(self.parser.ADC4LD[1])).astype(np.int32))
        m=-m
        self.listHistory.addItem('------------------------')
        fvolt = ( avg0/m ) * self.parser.ADCLSBmv
        self.listHistory.addItem(str('ADC1 voltage average {}'.format(fvolt)))
        fvolt = ( avg1/m ) * self.parser.ADCLSBmv
        self.listHistory.addItem(str('ADC2 voltage average {}'.format(fvolt)))
        fvolt = ( avg2/m ) * self.parser.ADCLSBmv
        self.listHistory.addItem(str('ADC3 voltage average {}'.format(fvolt)))
        fvolt = ( avg3/m ) * self.parser.ADCLSBmv
        self.listHistory.addItem(str('ADC4 voltage average {}'.format(fvolt)))
        fvolt = ( avg4/m ) * self.parser.ADCLSBmv
        self.listHistory.addItem(str('ADC5 voltage average {}'.format(fvolt)))

    def freport(self):
        '''Reports status of LookupTable'''
        self.clearHistory()
        smpperiod = (self.parser.rSample_Period[1] + 1) * 2
        smpFreq = 1000 / smpperiod
        cyPeriod =self.parser.SamplesInFrame*smpperiod
        cyFREQ = 1000 / cyPeriod
        slots = self.parser.SlotNumbers
        rensmp = (self.parser.rRemainCyclesCNT[1] & np.uint16(0xFFF)) + np.uint16(1)

        if (self.parser.SignallingMode==self.parser.INFmode) or ( self.parser.SignallingMode==self.parser.TXonlyMode) :
            self.listHistory.addItem('-------------  SCRIPT REPORT -----------------------')
            self.listHistory.addItem("- SYSTEM parameters for " + self.parser.currentScriptName)
            self.listHistory.addItem("Dedicated Buffer parameters")
            self.listHistory.addItem('Capacity of buffer in bytes           : {:d}'.format(self.parser.bytesmax))
            self.listHistory.addItem('Capacity of buffer in samples/channel : {:d}'.format(self.parser.bytesmax>>4))
            self.listHistory.addItem('Number of Samples per 1 cycle         : {:d}'.format(self.parser.SamplesInFrame))
            self.listHistory.addItem("Words16 inSample                      : {:d}".format(self.parser.Words16inSample))
            self.listHistory.addItem('MAX Number of cycles in  buffer       : {:d}'.format(self.parser.NcyclesinBuffer))
            self.listHistory.addItem('Number of samples in buffer/chanell   : {:d}'.format(self.parser.SamplesInBuffer))
            self.listHistory.addItem('Timeslots (add* commands)             : {:d}/{:d}'.format(slots,self.parser.LUTMAX))
            self.listHistory.addItem("rRemainCyclesCNT                      : {:d} ".format(self.parser.rRemainCyclesCNT[1] & 0xFFF +1))
            self.listHistory.addItem("")
            self.listHistory.addItem('Sampling Period (Frequency) : {:06d}us ({:f}KHz)'.format(smpperiod,smpFreq))
            self.listHistory.addItem('Cycle Period (Frequency)    : {:06d}us ({:f}KHz)'.format(cyPeriod,cyFREQ))
            self.listHistory.addItem('Buffer filling time         : {:3.3f}ms'.format((cyPeriod * (self.parser.NcyclesinBuffer))/1000))
#           self.listHistory.addItem("--- REPORT of Script statistics ---")
        if  self.parser.SignallingMode == self.parser.CSFmode:
            self.listHistory.addItem('- SYSTEM parameters for runCSF')
            self.listHistory.addItem('Sampling Period/Frequency       : {:d}us/{:f}KHz'.format(smpperiod, smpFreq))
            self.listHistory.addItem('Number of Samples per 1 cycle   : {:d}'.format(self.parser.SamplesInFrame))
            self.listHistory.addItem('Frames per read (frames/Record) : {:d}'.format(self.parser.framesPerRead) )
            tmp=self.parser.SamplesInFrame*self.parser.framesPerRead
            self.listHistory.addItem('Number of samples in Record     : {:d}'.format(tmp))
            self.listHistory.addItem('One record time (us)            : {:d}'.format(tmp * smpperiod))
        self.listHistory.addItem    ('------------ END OF SCRIPT REPORT -------------------')
        return
#############################################################
    # TODO SignalPreviewUpdate
    def PreviewButtonClicked(self):
        self.rBTN_Preview.setChecked(True)
        self.ScopePreview.show()
        self.ScopePreview.clear()
        self.ScopePreview.setXRange(0,self.parser.pInd1,padding=self.cmnXpadding)  # padding is offset from left and right
        self.ScopePreview.plot(self.parser.pSTbl[0:self.parser.pInd,2],self.parser.pSTbl[:self.parser.pInd,1],pen=self.signal_pen[7],symbol='o')
        if (self.parser.FPGAVer < 8):
            self.ScopePreview.plot(self.parser.pSTbl[0:self.parser.pInd,2],self.parser.pSTbl[:self.parser.pInd,0],pen = self.signal_pen[3])
        return

    def VarianceButtoClicked(self):
        self.ScopePreview.hide()
        self.ScopeVariance.show()
        return
#########################################
    def dumpadc(self):
        self.parser.getadc6()
        self.listHistory.addItem(str('{:04x}{:04x}'.format(self.parser.ADC0MD[1],self.parser.ADC0LD[1])))
        self.listHistory.addItem(str('{:04x}{:04x}'.format(self.parser.ADC1MD[1],self.parser.ADC1LD[1])))
        self.listHistory.addItem(str('{:04x}{:04x}'.format(self.parser.ADC1MD[1],self.parser.ADC2LD[1])))
        self.listHistory.addItem(str('{:04x}{:04x}'.format(self.parser.ADC3MD[1],self.parser.ADC3LD[1])))
        self.listHistory.addItem(str('{:04x}{:04x}'.format(self.parser.ADC4MD[1],self.parser.ADC4LD[1])))
        self.listHistory.addItem("----------")
        fz=float(((np.uint32(self.parser.ADC0MD[1]) <<16) + np.uint32(self.parser.ADC0LD[1])).astype(np.int32))
        self.listHistory.addItem(str('{:f} mv '.format(self.parser.ADCLSBmv * fz)))
        fz=float(((np.uint32(self.parser.ADC1MD[1]) <<16) + np.uint32(self.parser.ADC1LD[1])).astype(np.int32))
        self.listHistory.addItem(str('{:f} mv '.format(self.parser.ADCLSBmv * fz)))
        fz=float(((np.uint32(self.parser.ADC2MD[1]) <<16) + np.uint32(self.parser.ADC2LD[1])).astype(np.int32))
        self.listHistory.addItem(str('{:f} mv '.format(self.parser.ADCLSBmv * fz)))
        fz=float(((np.uint32(self.parser.ADC3MD[1]) <<16) + np.uint32(self.parser.ADC3LD[1])).astype(np.int32))
        self.listHistory.addItem(str('{:f} mv '.format(self.parser.ADCLSBmv * fz)))
        fz=float(((np.uint32(self.parser.ADC4MD[1]) <<16) + np.uint32(self.parser.ADC4LD[1])).astype(np.int32))
        self.listHistory.addItem(str('{:f} mv '.format(self.parser.ADCLSBmv * fz)))
        self.listHistory.addItem("----------")
        return
    #########################################
    def reportVariables(self):
        self.listHistory.addItem("----  Variables ------")
        self.listHistory.addItem(str("txbarrayindex          : {:d}".format(self.parser.txbarrayindex)))
        self.listHistory.addItem(str("rxbarrayindex          : {:d}".format(self.parser.rxbarrayindex)))
        self.listHistory.addItem(str("getbytescnt            : {:d}".format(self.parser.getbytescntRX)))
        self.listHistory.addItem(str("rNumberOfTSlots        : {:d}".format(self.parser.rNumberOfTSlots[1])))
        self.listHistory.addItem(str("SlotNumbers            : {:d}".format(self.parser.SlotNumbers)))
        self.listHistory.addItem(str("rRemainCyclesCNT       : {:04X}".format(self.parser.rRemainCyclesCNT[1])))
        self.listHistory.addItem("=====================================")
    ###########################################################################################################################
    ###########################################################################################################################
    def update_TEC_Kalman(self):
        return

    def fupdateRegisters(self):
        if (self.SignalPLOTEN):
            self.listHistory.addItem("FPGA is busy in infinite read routine.")
            self.listHistory.addItem("Push it into IdleMode first")
        else:
            self.parser.getAllRegisters()
            #self.parser.getTTEC()
            self.listHistory.clear()
#        self.Registers_ListBox.addItem('{:04X}    {:016b}'.format(self.parser.VER[1], self.parser.VER[1]))
            stp = " "
        #self.listHistory.addItem(" HEX         BINARY")
        # for x in self.parser.REGNMS:
        #    self.RegNames_ListBox.addItem;

            self.listHistory.addItem(stp + self.parser.REGNMS[0] + stp  + self.parser.hexprint(self.parser.VER[1]))
            self.listHistory.addItem(stp + self.parser.REGNMS[1] + stp  + self.parser.hexprint(self.parser.TEST[1]))
            self.listHistory.addItem(stp + self.parser.REGNMS[2] + stp  + self.parser.hexprint(self.parser.MASK[1]))
            self.listHistory.addItem(stp + self.parser.REGNMS[3] + stp  + self.parser.hexprint(self.parser.BUF_lngH[1]))
            self.listHistory.addItem(stp + self.parser.REGNMS[4] + stp  + self.parser.hexprint(self.parser.BUF_pnt[1]))
            self.listHistory.addItem(stp + self.parser.REGNMS[5] + stp  + self.parser.hexprint(self.parser.BUF_lng[1]))
            self.listHistory.addItem(stp + self.parser.REGNMS[6] + stp  + self.parser.hexprint(self.parser.CNTreg[1]))
            self.listHistory.addItem(stp + self.parser.REGNMS[7] + stp  + self.parser.hexprint(self.parser.TIMER[1]))
            self.listHistory.addItem(stp + self.parser.REGNMS[8] + stp  + self.parser.hexprint(self.parser.rAD5541TX[1]))
            self.listHistory.addItem(stp + self.parser.REGNMS[9] + stp  + self.parser.hexprint(self.parser.rSPInSELECT[1]))
            self.listHistory.addItem(stp + self.parser.REGNMS[10] + stp  + self.parser.hexprint(self.parser.rTECT_CNT[1]))
            self.listHistory.addItem(stp + self.parser.REGNMS[11] + stp  + self.parser.hexprint(self.parser.rNumberOfTSlots[1]))
            self.listHistory.addItem(stp + self.parser.REGNMS[12] + stp  + self.parser.hexprint(self.parser.rRemainCyclesCNT[1]))
            self.listHistory.addItem(stp + self.parser.REGNMS[13] + stp  + self.parser.hexprint(self.parser.rSample_Period[1]))

            #self.listHistory.addItem(stp + self.parser.REGNMS[14] + stp  + self.parser.hexprint(self.parser.ADC0MD[1]))
            #self.listHistory.addItem(stp + self.parser.REGNMS[15] + stp  + self.parser.hexprint(self.parser.ADC0LD[1]))
            #self.listHistory.addItem(stp + self.parser.REGNMS[16] + stp  + self.parser.hexprint(self.parser.ADC1MD[1]))
            #self.listHistory.addItem(stp + self.parser.REGNMS[17] + stp  + self.parser.hexprint(self.parser.ADC1LD[1]))
            #self.listHistory.addItem(stp + self.parser.REGNMS[18] + stp  + self.parser.hexprint(self.parser.ADC2MD[1]))
            #self.listHistory.addItem(stp + self.parser.REGNMS[19] + stp  + self.parser.hexprint(self.parser.ADC2LD[1]))
            #self.listHistory.addItem(stp + self.parser.REGNMS[20] + stp  + self.parser.hexprint(self.parser.ADC3MD[1]))
            #self.listHistory.addItem(stp + self.parser.REGNMS[21] + stp  + self.parser.hexprint(self.parser.ADC3LD[1]))
            #self.listHistory.addItem(stp + self.parser.REGNMS[22] + stp  + self.parser.hexprint(self.parser.ADC4MD[1]))
            #self.listHistory.addItem(stp + self.parser.REGNMS[23] + stp  + self.parser.hexprint(self.parser.ADC4LD[1]))

            if (self.parser.FPGAVer==8):
                self.listHistory.addItem(stp + self.parser.REGNMS[27] + stp  + self.parser.hexprint(self.parser.DDScontrol[1]))
                self.listHistory.addItem(stp + self.parser.REGNMS[28] + stp  + self.parser.hexprint(self.parser.DDSdeltha[1]))



            #self.update_TEC()
            #self.updateLaserTable()

        return

     #########################################################
    # Update LaserSlotTable by reading script
    def updateLaserTable(self):
       # self.listHistory.clear()
        self.listHistory.addItem('SLOT LED  ATT   I    TIME  SDAC')
        self.listHistory.addItem(' #    #    #    ma   us    cod')
        for x in range(self.parser.SlotNumbers):
            self.listHistory.addItem(str(' {:03d}  {:03d}  {:02X}  {:06.2f} {:05d} {:05d}'.format(x, self.parser.LaserSlotTable[x,0] & 0x00FF, self.parser.LaserSlotTable[x,0] >> 8,
                                                               (self.parser.LaserSlotTable[x,1])*self.parser.DACLSBma, self.parser.LaserSlotTable[x,2],self.parser.LaserSlotTable[x,3])))
        return None
    ###############################################################
#   TODO     fAddHBeat   #####################
    def fAddHBeat(self):
                  return

#### TIMER RELATED FUNCTIONS ######################################
    # Timer does 10ms period interrupt
    #HBeatTickPeriod = np.uint32(5)  # Replot each 50ms
    ###############################################################
    def onTimer(self):
        #i= range(2)
        if (self.EnTimer) :
            self.TimerCounter += 1
            self.OneSecCounter=self.OneSecCounter-1;
            if (self.OneSecCounter == 0) :
                self.OneSecCounter = 19
                if (self.parser.SETTLING_PASSED and (self.parser.SignallingMode == self.parser.CSFmode)) :
                    self.parser.tmrTimetmp=self.parser.tmrTimetmp-1
                    self.lEdit1.setText("Cycles left = {:d}, wait {:d} sec".format(self.parser.tmrcycles, self.parser.tmrTimetmp ))
                    if self.parser.tmrTimetmp == 0 :
                        self.EnTimer=0
                        self.timer.stop()
                        self.lEdit1.setText("")
                        self.onCreateThread()
                        return
                if (self.parser.SETTLING_PASSED == False) :
                    self.parser.tmrTimetmp=self.parser.tmrTimetmp-1
                    self.lEdit1.setText("Wait {:d} sec".format(self.parser.tmrTimetmp ))

                    if self.parser.tmrTimetmp == 0 :
                        #self.EnTimer=0
                        #self.timer.stop()
                        #self.lEdit1.setText("")
                        self.parser.SETTLING_PASSED=True
                        self.onCreateThread()
                        return
        # Heartbit graph update
            if self.TimerCounter == self.TimerCMP2 :

                self.TimerCMP2 += self.HB_TickPeriod
                if self.TESTPLOTEN: self.hbScope_RefreshTestPlot()
        # TermoGraph
            if self.TimerCounter == self.TimerCMP6Thermoperiod :
                self.TimerCMP6Thermoperiod += self.TemperaturePLOTPeriod
                if self.TemperaturePLOTEN: self.thermoGraph_update()
            return
        else:
            self.timer.stop()
    ###############################################################




###############################################################
    #     TimerEn   Setting to global SamplePeriod
    def TemerEn(self):
        if self.EnTimer == 1:
            self.EnTimer=0; self.timer.stop()
#            self.pBTN_EnableTimer.setStyleSheet("color: yellow; border-radius: 5px; background: blue")
        else:
            self.EnTimer = 1; self.timer.start(10)
#            self.pBTN_EnableTimer.setStyleSheet("color: red; border-radius: 5px; background: rgb(50,15,15);")
    ###################################################################################################
    ################ Reset FPGA ################
    def onRSTnUpdateFpga(self):
        if (self.SignalPLOTEN):
            self.listHistory.addItem("FPGA is busy in infinite read routine.")
            self.listHistory.addItem("Push it into IdleMode first")
        else:
            self.parser.ResetFpga()
        #self.fupdateRegisters()
        return
    def on_clearScr(self): self.mScopeSignal.clear()
    def clearHistory(self): self.listHistory.clear()
    #def OpenRegisterMap(self):  os.system('start excel ..\R_RPS_DOCS\XC7SMODULE.xlsx')
    def OpenRegisterMap(self):  os.system('start excel FPGA_V7p9_REGMAP.xlsx')
    def thermo_QSpinBoxvalue_changed(self, value):  self.thermo_QSpinBox.setSuffix(self.thermoScope_QSpinSFX[value])


    def CALIBRATION_QSpinBoxvalue_changed(self, value):
        self.CALIBRATION_QSpinBox.setPrefix(self.CALIBRATION_QSpinBox_lbl[value] + "  " )
        self.CALIBCURRENT_QSpinBox.setValue(self.CALIBRATION_CURRENT[value])
        return

    def CALIBCURRENT_QSpinBoxvalue_changed(self, value):
        self.CALIBRATION_CURRENT[self.CALIBRATION_QSpinBox.value()] = self.CALIBCURRENT_QSpinBox.value()
        return


    # + str("{:03.2F}".format(self.CALIBRATION_CURRENT[value])) + "  "
    # Editor menu commands##############################
    def file_reload(self):
        self.listHistory.addItem("---------------")
        self.listHistory.addItem("File Reloaded")
        self.editor.clear(); self.file_load()

    def file_load(self):
        try:
            f = open(self.scrfnm, "r")
        except IOError:
            self.listHistory.addItem("Could not open file {:s}".format(self.scrfnm))
            return
        self.editor.setPlainText(f.read())
        f.close()

    def file_save(self):
        f = open(self.scrfnm, "w") ; f.write(self.editor.toPlainText()) ; f.close()
        self.listHistory.addItem("File Saved")

    def fileLoadOther(self):
        optionsa = QFileDialog.Options()|QFileDialog.DontUseNativeDialog
        fileName,_=QFileDialog.getOpenFileName(self,"Select your script file","","Text Files (*.txt)",options=optionsa)
        # fileName = os.path.dirname(fileName) + "/" + os.path.basename(fileName)
        self.scrfnm = os.path.basename(fileName)
        self.listHistory.addItem("File Loaded:   " + self.scrfnm)
        self.file_load()
        self.getScripList()
        self.listHistory.addItem("File Script List processed")

    ######################################################################################################################
    def saveMeanAndVarianceFileDialog(self):
        self.listHistory.addItem("Not Implemented Yet");
        return
        if (not (self.rBTN_IDLE.isChecked())):
            self.IdleMode()

        options = QFileDialog.Options()|QFileDialog.DontUseNativeDialog
        fileName,_=QFileDialog.getSaveFileName(self,"Select your script","","All Files (*);;Text Files (*.txt)",options=options)

        # adding data stamp to filename
        fileName = os.path.dirname(fileName) + tm.strftime("/%Y-%m-%d_at_%H_%M_%S_") + os.path.basename(fileName)

        if fileName:
            fl  = open(fileName,'w')

            # Writing  Mean and variances for 4 channels
            for j in range(0, self.parser.NcyclesinBuffer):
                for i in range(self.parser.SamplesInFrame):
                    fl.write("{:f}\t{:f}\t{:f}\t{:f}\t{:f}\t{:f}\n".format(self.parser.i32arrayRXV[0,i],self.parser.i32arrayRXV[1,i],
                                                                           self.parser.i32arrayRXV[2,i],self.parser.i32arrayRXV[3,i],
                                                                           self.parser.i32arrayRXV[4,i],self.parser.i32arrayRXV[5,i]))
                saveframeNumber  = (saveframeNumber+1) % self.parser.NcyclesinBuffer
                W32PointerinCycle=saveframeNumber*words32inCycle
            fl.close()

        self.listHistory.addItem("Number of cycles in Buffer = {:d}".format(self.parser.NcyclesinBuffer))
        self.listHistory.addItem("Samples in Cycle   = {:d}".format(self.parser.SamplesInFrame))

        return
######################################################################################################################
    ######################################################################################################################
    def saveFileDialog(self):
        if (not (self.rBTN_IDLE.isChecked())):
            self.IdleMode()

        optionsa = QFileDialog.Options()|QFileDialog.DontUseNativeDialog
        fileName,_=QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);Text Files (*.txt)",options=optionsa)
        # adding data stamp to filename
        fileName = os.path.dirname(fileName) + tm.strftime("/%Y-%m-%d_at_%H_%M_%S_") + os.path.basename(fileName)


        words32inCycle    = self.parser.SamplesInFrame<<2
        if fileName:
            fl  = open(fileName,'w')

            if (not self.SaveHeadertoFile(fl)): return(0)

            # Writing  sampled data
            for j in range(0, self.parser.NcyclesinBuffer):
                self.parser.unformatFrameOnly(W32PointerinCycle,self.parser.SamplesInFrame)
                for i in range(self.parser.SamplesInFrame):
                    fl.write("{:f}\t{:f}\t{:f}\t{:f}\t{:f}\t{:f}\n".format(self.parser.i32arrayRXV[0,i],self.parser.i32arrayRXV[1,i],
                                                                           self.parser.i32arrayRXV[2,i],self.parser.i32arrayRXV[3,i],
                                                                           self.parser.i32arrayRXV[4,i],self.parser.i32arrayRXV[5,i]))
                saveframeNumber  = (saveframeNumber+1) % self.parser.NcyclesinBuffer
                W32PointerinCycle=saveframeNumber*words32inCycle
            fl.close()

        self.listHistory.addItem("Number of cyclesin Buffer = {:d}".format(self.parser.NcyclesinBuffer))
        self.listHistory.addItem("Samples in Cycle   = {:d}".format(self.parser.SamplesInFrame))

        #self.selectMode()
        #self.listHistory.addItem("Hello")
        return
######################################################################################################################
    def Notepad_pp(self):
        self.listHistory.clear()
        self.listHistory.addItem("Notepad++ started")
        os.system('start notepad++ script.txt')

    # def onScript_action(self):  self.onScript()
    def helphtml(self): os.system('start QandA.html')
    def hinteditor(self): os.system('start hint.txt')
    #########################################################################
    def eventFilter(self, source, event):
        if (event.type() == QEvent.KeyPress and event.key() == Qt.Key_Up):
            self.lEdit1.setText(self.previousline)
            return True
        else: return False
    ##########################################################
    def connectUSB(self):
        if self.parser.ft232h_connected:
            self.IdleMode()
        self.rBTN_IDLE.setChecked(True)

        stat = self.parser.connectUSB() # connect and reset
        #self.dumparray(self.parser.uCUDATA_STATEX8,20)

        self.clearHistory()
        if stat == 0:
            self.pBTN_CONNECT.setStyleSheet("color: yellow")
            self.listHistory.addItem("DEVICE DISCONNECTED")
            self.pBTN_CONNECT.setStyleSheet("color: yellow; border-radius: 5px;  background: blue")
            return False
        elif stat == 1:
            self.clearHistory()
            self.parser.BUFMODE  = False
            self.parser.CMD_MODE = True
            #self.clearHistory()
            #print(stat)
            self.pBTN_CONNECT.setStyleSheet("color: red; border-radius: 5px; background: rgb(100,15,15);")


            self.parser.dict=self.parser.ft232h.getDeviceInfo()
            self.listHistory.addItem("")

            # Is any ROCKLEY part connected?
            self.listHistory.addItem("DEVICE CONNECTED     :     " + self.parser.dict["description"].decode("utf-8"))
            self.listHistory.addItem("----------------------------------")
            #   connected system name :
            #   Examples Version for V1 : RPS_V1R2_30 Board RPS, version 1, rev 2, Serial number 30
            #   Examples Version for V2 : RPS_V2R2_30 Board RPS, version 2, rev 2, Serial number 30
            Namestring=self.parser.dict["serial"].decode("utf-8")
            self.listHistory.addItem("SYSTEM NAME _ SERIAL#:  " + Namestring )

            self.parser.connectFPGA()
            if (self.parser.connectFPGA() == 0) :
                    self.listHistory.addItem("Wrong or nonsupported FPGA Version")
                    self.parser.closeUSB()
                    self.listHistory.addItem("Board disconnected")
                    return (False)

            self.parser.TEST[1]=self.parser.getshortcmd(self.parser.gtst_cmd)
            self.listHistory.addItem("FPGA_V{:d}_R{:d}   SUBVERSION {:03d} connected".format(self.parser.FPGAVer,self.parser.FPGARev,  self.parser.TEST[1] >> 1 ))
            if (self.parser.TEST[1]  & np.uint16(0x0001)) : self.listHistory.addItem("Clock is inverted")
            else: self.listHistory.addItem("Clock is nonverted")
            #self.lEdit1.setText("rd 16")
            #self.on_ReturnPressed()
            # get EFM Version
            self.parser.getTTECSTATUS()
            rvn = np.uint8(self.parser.uCUDATA_STATEX8[1])
            msg1= '{:d}.{:d}'.format(  ((rvn  & 0xf0) >> 4), (rvn & 0x0F))
            self.listHistory.addItem("EFMuCU FIRM VERSION  :       " + msg1)

            #revidst=""
            if self.parser.uCUDATA_STATEX8[4] == 0 : revidst="A"
            else :
                if self.parser.uCUDATA_STATEX8[4] == 1 :  revidst="B"
                else : revidst ="C"

            idstr= "uCU DevID 0x{:x}, DerivID 0x{:x}, RevID 0x{:x} : ".format(self.parser.uCUDATA_STATEX8[2],self.parser.uCUDATA_STATEX8[3],self.parser.uCUDATA_STATEX8[4])
            self.listHistory.addItem(idstr)
            self.listHistory.addItem("uCU PN " + str(self.parser.uCUIDdict.get(0x50)[0]) + revidst + str(self.parser.uCUIDdict.get(0x50)[1]))
            self.listHistory.addItem("----------------------------------")
            return (True)


        else:
            self.listHistory.addItem("DEVICE NOT PLUGGED")
            self.listHistory.scrollToBottom()
        return False


    def USBNotConnected(self):
        self.listHistory.addItem("Device is not connected, check USB connection")
        self.listHistory.scrollToBottom()

    def terminate(self):
        #print("exit over X button")
        self.worker.kill()
        self.IdleMode()
        self.parser.closeUSB()
        tm.sleep(.1)
        self.timer.stop()
        #sys.exit()
        #sys.exit(app.exec_())

  ##################################################################
  #########################################################################
  #########    END OF USER INTERFACE   ####################################
  #################################################################################
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ROCKLEY PHOTONICS SIGNALVIEW " + self.VERSION ))
        self.pBTN_CONNECT.setText(_translate("MainWindow", "CONNECT\nUSB"))
        self.pBTN_ResetFpga.setText(_translate("MainWindow", "RESET\nFPGA"))
        self.pBTN_ScriptNmUpdate.setText(_translate("MainWindow","REFRESH NAMES"))
#       self.gpBx_FPGA_REGISTERS.setTitle(_translate("MainWindow","FPGA REGISTERS"))
        self.groupboxlHistory.setTitle(_translate("MainWindow", "HISTORY"))


        #self.tempCurrentValueBox.setTitle(_translate("MainWindow", "TºC"))


        self.pBTN_CLEAR_W1.setText(_translate("MainWindow", "CLEAR"))
        self.pBTN_UpdateRegisters.setText(_translate("MainWindow", "UPDATE\nREGS"))
#       self.pBTN_AddHBeat.setText(_translate("MainWindow","ADD SYNTH\nHEARTBEAT"))
#       self.pBTN_EnableTimer.setText(_translate("MainWindow", "ENABLE\nTIMER"))
        #self.pBTN_STOP.setText(_translate("MainWindow",   "STOP"))
        #self.pBTN_START.setText(_translate("MainWindow",  "START"))
        #self.pBTN_SINGLE.setText(_translate("MainWindow", "SINGLE"))
        self.pBTN_SaveSamples.setText(_translate("MainWindow","SAVE\nSAMPLES"))
        self.pBTN_SaveMeanAndVar.setText(_translate("MainWindow","SAVE MEAN\nand VARIANCE"))



        self.pBTN_RunTest.setText(_translate("MainWindow", "RUN\nTEST"))
        self.pBTN_REgisterMap.setText(_translate("MainWindow","REGISTER\nMAP/XLS"))
        self.signalSourceBox.setTitle(_translate("MainWindow","SIGNAL SOURCE"))

        self.rBTN_SCRIPT1.setText(_translate("MainWindow",self.scriptnames[0]))
        self.rBTN_SCRIPT2.setText(_translate("MainWindow",self.scriptnames[1]))
        self.rBTN_SCRIPT3.setText(_translate("MainWindow",self.scriptnames[2]))
        self.rBTN_SCRIPT4.setText(_translate("MainWindow",self.scriptnames[3]))
        self.rBTN_SCRIPT5.setText(_translate("MainWindow",self.scriptnames[4]))
        self.rBTN_SCRIPT6.setText(_translate("MainWindow",self.scriptnames[5]))
        self.rBTN_SCRIPT7.setText(_translate("MainWindow",self.scriptnames[6]))
        self.rBTN_SCRIPT8.setText(_translate("MainWindow",self.scriptnames[7]))
        self.rBTN_SCRIPT9.setText(_translate("MainWindow",self.scriptnames[8]))
        self.rBTN_SCRIPT10.setText(_translate("MainWindow",self.scriptnames[9]))
        self.rBTN_SIMULATOR.setText(_translate("MainWindow", "SIMULATOR"))
        self.rBTN_IDLE.setText(_translate("MainWindow", "IDLE"))
        #self.rBTN_REVIEW.setText(_translate("MainWindow", "REVIEW"))


        self.graphModeSelect.setTitle(_translate("MainWindow"," PLOT 1  MODE "))
        self.rBTN_6xCH.setText(_translate("MainWindow","1,2,3,4,5,6"))
        self.rBTN_4xCH.setText(_translate("MainWindow","1,2,3,4,-,-"))
        self.rBTN_4_2xCH.setText(_translate("MainWindow","1,2,3,4,1+4,1-4"))

        self.VariancePreview.setTitle(_translate("MainWindow"," PLOT 2  MODE "))
        self.rBTN_Variance.setText(_translate("MainWindow","VARIANCE"))
        self.rBTN_Preview.setText(_translate("MainWindow","PREVIEW"))

        self.ESTIMATOR_box.setTitle(_translate("MainWindow", "ESTIMATOR"))
#        self.GAIN_sbox.setTitle(_translate("MainWindow","DIGITAL GAIN"))


        #self.groupBox_SEQUENCE.setTitle(_translate("MainWindow", "LASERS / LEDS TBL"))
        self.menu_File.setTitle(_translate("MainWindow", "&SCRIPT:"))
        self.actionFileLoadOther.setText(_translate("MainWindow", "&Load"))
        self.actionFileSave.setText(_translate("MainWindow",   "&Save"))
        self.actionFileReload.setText(_translate("MainWindow", "&Reload "))

        self.NotepadMenu.setTitle(_translate("MainWindow", "NOTEPAD++"))
        self.actionrunNotepad.setText(_translate("MainWindow", "Notepad++"))
        self.pBTN_CALLIB_SAVE.setText(_translate("MainWindow", "AUTO\nCALIBRATION"))
        self.pBTN_CALLIB_AUTO.setText(_translate("MainWindow", "SAVE\nTO FILE"))
        self.pBTN_CALLIB_PROGRAM.setText(_translate("MainWindow", "WRITE\nTO FLASH"))
        self.pBTN_CALLIB_RELOAD.setText(_translate("MainWindow",  "LOAD\nFROM FLASH"))

###################################################################################################
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    #QtWidgets.QWidget(MainWindow)


    MainWindow.show()
    sys.exit(app.exec_())

###################################################################################################
###################################################################################################
###################################################################################################
# PyQt5 uiControls
#   QCheckbox           A checkbox
#   QComboBox           A dropdown list box
#   QDateEdit           For editing dates
#   QDateTimeEdit       For editing dates and datetimes
#   QDial               Rotatable dial
#   QDoubleSpinbox      A number spinner for floats
#   QFontComboBox       A list of fonts
#   QLCDNumber          A quite ugly LCD display
#   QLabel              Just a label, not interactive
#   QLineEdit           Enter a line of text
#   QProgressBar        A progress bar
#   QPushButton         A button
#   QRadioButton        A group with only one active choice
#   QSlider             A slider
#   QSpinBox            An integer spinner
#   QTimeEdit           For editing times
###################################################################################################
#        self.frame1 = QtWidgets.QFrame(self.centralwidget)
#        self.frame1.setGeometry(QtCore.QRect(1550, 60, 331, 321))
#        self.frame1.setFrameShape(QtWidgets.QFrame.StyledPanel)
#        self.frame1.setFrameShape(QtWidgets.QFrame.WinPanel)
#        self.frame1.setFrameShadow(QtWidgets.QFrame.Raised)
#        self.frame1.setObjectName("frame1")
#        self.pushButtonF = QtWidgets.QPushButton(self.frame1)
#        self.pushButtonF.setGeometry(QtCore.QRect(30, 20, 75, 23))
#        self.pushButtonF.setObjectName("pushButtonF")

#        self.pushButtonF.setText(_translate("MainWindow", "FFFFF"))
###################################################################################################
    ###################################################################################################
    ###################################################################################################
    ###################################################################################################
#    def PlotRAWSignal(self):
#        self.data_line_RED.setData(self.sc_time, signalBuffer[0, :])
    ###################################################################################################


