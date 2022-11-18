# Using FT set
# Hardware Specific -->port A --> Hardware -> FT245
# Hardware Specific -->port A --> Driver -> VCP
# IO-Control ACBUS 8 ACBUS 9 in IO mode
# IO pins in 16ma
#
#
##########################################################################
import numpy as np
import time
import ftd2xx as ftd
import time as tm
##########################################################################
class StringParserClass(object):
    def __init__(self):
        self.REGNMS = [" VER -----------",
                       " TEST ----------",
                       " MASK ----------",
                       " BUF_lngh ------",
                       " BUF_pnt -------",
                       " BUF_lng -------",
                       " CNTreg --------",
                       " TIMER ---------",
                       " AD5541TX    h10",
                       " SPInSELECT  h11",
                       " TECT_CNT    h16",
                       " N SLOTS     h18",
                       " RMN_CYCLES  h19",
                       " SMP_PERIOD  h1A",
                       " ADC0MD      h20",
                       " ADC0LD      h21",
                       " ADC1MD      h22",
                       " ADC1LD      h23",
                       " ADC2MD      h24",
                       " ADC2LD      h25",
                       " ADC3MD      h26",
                       " ADC3LD      h27",
                       " ADC4MD      h28",
                       " ADC4LD      h29",
                       " ",
                       " TECT_T[0:3]",
                       " TECT_T[4:6]",
                       " DDS_CNT     h0C",
                       " DDS_DLT     h0D"
                       ]
        ############################################################################
        # command code statics
        self.rd_cmd       = np.uint8(0b0000_0000)  # 0b00****** read register, 6 lsb bits is an address of register
        self.wr_cmd       = np.uint8(0b1000_0000)  # 0b00****** write register, 6 lsb bits is an address of register
                                                   #  next two bytes are the data for target register

        self.getfifo_cmd  = np.uint8(0b0111_0001)  # 0x71 get FIFO
        self.ldfifo_cmd   = np.uint8(0b1111_0001)  # 0xF1 load FIFO
        self.rdbuf_cmd    = np.uint8(0b0111_0010)  # 0x72 rd buffer, each next 2 bytes FPGA send to PC increments pointer
        self.wrbuf_cmd    = np.uint8(0b1111_0010)  # 0xF2 wr buffer, each next 2 bytes FPGA gets from PC increments pointer

        self.ver_cmd      = np.uint8(0b0110_0000)  # 0x60 Get version , read only command
        self.gtst_cmd     = np.uint8(0b0110_0001)  # 0x61 Get version , read only command
        self.gmask_cmd    = np.uint8(0b0110_0010)  # 0x62 get mask
        self.glengthH_cmd = np.uint8(0b0110_0011)  # 0x63 upper 16 bits of  length of buffer
        self.gpointer_cmd = np.uint8(0b0110_0100)  # 0x64 get pointer
        self.glength_cmd  = np.uint8(0b0110_0101)  # 0x65 get buffer length
        self.gcnt_cmd     = np.uint8(0b0110_0110)  # 0x66 get counter
        self.gtimer_cmd   = np.uint8(0b0110_0111)  # 0x67 get timer
        self.ldwdog_cmd   = np.uint8(0b1110_0000)  # watchdog
        self.ltst_cmd     = np.uint8(0b1110_0001)  # 0xE1 load mask
        self.lmask_cmd    = np.uint8(0b1110_0010)  # 0xE2 load mask
        self.llengthH_cmd = np.uint8(0b1110_0011)  # 0xE5 Load buffer length
        self.lpointer_cmd = np.uint8(0b1110_0100)  # 0xE4 load pointer
        self.llength_cmd  = np.uint8(0b1110_0101)  # 0xE5 Load buffer length
        self.lcnt_cmd     = np.uint8(0b1110_0110)  # 0xE6 Load counter
        self.ltimer_cmd   = np.uint8(0b1110_0111)  # 0xE7 Load us timer

        self.pktend_cmd   = np.uint8(0b1111_0011)  # 0xF3 Packet end command
        self.waitus_cmd   = np.uint8(0b1111_0100)  # 0xF4 wait us time (us is a content of timer +1) write into delay timer in us
        self.waitst_cmd   = np.uint8(0b1111_0110)  # 0xF6 wait Masked status,
        self.nop_cmd      = np.uint8(0b1111_1111)  # 0xFF No operation just 1 clock delay
########################################################################################
        self.FPGAVersion = np.uint16(0xFF)
        self.FPGAVer     = np.uint16(0xFF)
        self.FPGARev     = np.uint16(0xFF)
        self.LUTMAX      = np.uint16(16)
        # Memory map
        self.Program_BUF_Adr   = np.uint16(0xC000)
        self.LASER_LUT_Adr     = np.uint16(0x8800)
        self.LASER_LUT2_Adr    = np.uint16(0x8800)
        self.TEC_TERMO_BUF_Adr = np.uint16(0x8000)
        self.TEC_TERMO_BUF_Wlength = np.int(10)
        self.TEC_TERMO_BUF_Blength =self.TEC_TERMO_BUF_Wlength*2
        self.slotparams0 = 4
        self.slotparams1 = 0


        self.FIFO_Adr          = np.uint16(0x8F00)
        self.DDSPAGE_ADD       = np.uint16(0x8E00)

        # system Control Registers
        self.VER     = np.uint16([0x60,0x0000])
        self.TEST    = np.uint16([0x61,0x0000])
        self.MASK    = np.uint16([0x62,0x0000])
        self.BUF_lngH= np.uint16([0x63,0x0000])
        self.BUF_pnt = np.uint16([0x64,0x0000])
        self.BUF_lng = np.uint16([0x65,0x0000])
        self.CNTreg  = np.uint16([0x66,0xC000])
        self.TIMER   = np.uint16([0x67,0x0000])

        # Bits of CNT register
        # 0-
        # 1-
        # 8 - logic0 - V2I  disabled; logic1 - V2I enabled
        # 9 - logic0 - uCU enabled, logic1 disabled


        # FPGA Registers map
        # AD5541TX writing into this register passing the value to DAC AD5541
        # Writing should be enable by bit 10 in SPInSELECT register
        self.rAD5541TX=np.uint16([0x10,0x0000])

        # SPInSELECT bits
        # [14:13] SPI_RATE actualRATE = 30MHZ/(SPI_RATE+1)
        # [10]    LaserSelectOvr - default 0 , if 0 then data of DAC taken from FPGA otherwise from AD5541TX
        # [7:0]   LaserSel  [6:0] selects Laser, bit 7 selects Test cable LEDS
        self.rSPInSELECT=np.uint16([0x11,0x0000])

        # TECT - thermoelectric cooller and Themperature reading
        # Writing bits
        # [15] Enables 1ms period Pulse to request EFM  Data (Hardware request)
        # [14] if writing 1 then bits 7:0 will be send to EFM8 over serial port
        #      This should set control temperature and TEC target
        # [12] if 1 then generate 1 (only) pulse to request EFM  Data (Software  request)
        # Reading returns whatever was written  wih exclusion of bit 8 which is status
        # [8]   returns the status. If serial port is active then it is  1. if Idle then it is 0
        # Transition from 1 to 0 could be catched by software or  hardware in MASK[0] bit
        # Data from EFM could be read from TECT BUFFER (see buffer address below
        self.rTECT_CNT=np.uint16([0x16,0x0000])

        # NumberOfTSlots
        # 8 bits of LSB defines the last address of timeslots need to be used
        # So Total number of Slots in Cycle = NumberOfTSlots +1 (Address counter start from 0)
        self.rNumberOfTSlots=np.uint16([0x18,0x0000])

        #  RemainCyclesCNT control register of cycle counter
        #  controller has remain counter which
        #  counts backward and shows how many full cycles still need to be done
        #  the content of that counter could be
        #   - loaded with value from bus bits [11:0]
        #   - added  with value from bus bits [11:0]
        #   - at the end of each cycle the value will be decremented
        # [12] if 0 then data bits [11:0] will be loaded into 12 bit  remain counter and cycling started
        #      cycling will stop when
        #      if 1 Then data bits [11:0] will be just  added to    12 bit  remain counter
        # [11:0]  bits to load into or add to remain counter
        self.rRemainCyclesCNT=np.uint16([0x19,0x0000])

        # Sample_Period defines sampling period in us. LSB is 2us, So minimal period is 2us and increments by 2 us as wel
        # Maximal Sample_Period value is 65535 what correspond to 65536x2us=131072us ~130ms
        self.rSample_Period=np.uint16([0x1a,0x0000]) # Sample_Period[0] address, Sample_Period[1] data

        self.ADC0MD    = np.uint16([0x20,0x0000])
        self.ADC0LD    = np.uint16([0x21,0x0000])
        self.ADC1MD    = np.uint16([0x22,0x0000])
        self.ADC1LD    = np.uint16([0x23,0x0000])
        self.ADC2MD    = np.uint16([0x24,0x0000])
        self.ADC2LD    = np.uint16([0x25,0x0000])
        self.ADC3MD    = np.uint16([0x26,0x0000])
        self.ADC3LD    = np.uint16([0x27,0x0000])
        self.ADC4MD    = np.uint16([0x28,0x0000])
        self.ADC4LD    = np.uint16([0x29,0x0000])

        self.DDScontrol =np.uint16([0x0C,0x0000]) # Sample_Period[0] address, Sample_Period[1] data
        self.DDSdeltha  =np.uint16([0x0D,0x0000]) # Sample_Period[0] address, Sample_Period[1] data

        self.SN74HCS594ControlByte = np.uint8(0)
    # structure of FPGA control Byte
    # Bit ACBUS9 is serial clock
    # Bit ACBUS8 is Data  In
    # SN74HCS594 Bit definitions
    # Bit[0] - STATE0
    # Bit[1] - STATE1
    # Bit[2] - PROGRAM_B_0
    # Bit[3] - SOFT_RST
    # Bit[4] - M1_2 FPGA MODE  bits 1 & 2 connected  M0 = ~ M1_2
    # Bit[5] - SPARE0
    # Bit[6] - SPARE1
    # Bit[7] - LED3


        ############################################################################
        # uCU EFM8LB11F16
        self.EFM_CMD_NOP              = np.uint16(0xC000)
        self.EFM_CMD_GETID            = np.uint16(0xC001)
        self.EFM_CMD_TEC_ON           = np.uint16(0xC002)
        self.EFM_CMD_TEC_OFF          = np.uint16(0xC003)
        self.EFM_CMD_INC_TEC          = np.uint16(0xC004)
        self.EFM_CMD_DEC_TEC          = np.uint16(0xC005)
        self.EFM_CMD_RESETSEQUENCE    = np.uint16(0xC006)
        self.EFM_CMD_GETVERSION       = np.uint16(0xC007)
        self.EFM_CMD_LED_ON           = np.uint16(0xC008)
        self.EFM_CMD_LED_OFF          = np.uint16(0xC009)
        self.EFM_CMD_GETDATA          = np.uint16(0xC00a)
        self.EFM_CMD_IDSTRING         = np.uint16(0xC00b)

        self.EFM_CMD_SETDACL          = np.uint16(0xC040)
        self.EFM_CMD_SETDACH          = np.uint16(0xC080)
        # uCU EFM8LB11F16
        self.uCUDATA_STATEX8          = bytearray(np.uint8(np.zeros(128)))
        self.uCUDATA_RX8              = bytearray(np.uint8(np.zeros(128)))
        self.uCUDATA_RX16             = np.frombuffer(self.uCUDATA_RX8,dtype=np.uint16,count = -1)
        self.EFMADCLSB=0.000146493   # 2.4v/16383
        self.uCUIDdict={
        	0x41 : ["EFM8LB12F64E-","-QFN32 "]   ,
			0x42 : ["EFM8LB12F64E-","-QFP32 "]   ,
			0x43 : ["EFM8LB12F64E-","-QSOP24"]   ,
			0x44 : ["EFM8LB12F64E-","-QFN24 "]   ,
			0x45 : ["EFM8LB12F32E-","-QFN32 "]   ,
			0x46 : ["EFM8LB12F32E-","-QFP32 "]   ,
			0x47 : ["EFM8LB12F32E-","-QSOP24"]   ,
			0x48 : ["EFM8LB12F32E-","-QFN24 "]   ,
			0x49 : ["EFM8LB11F32E-","-QFN32 "]   ,
			0x4A : ["EFM8LB11F32E-","-QFP32 "]   ,
			0x4B : ["EFM8LB11F32E-","-QSOP24"]   ,
			0x4C : ["EFM8LB11F32E-","-QFN24 "]   ,
			0x4D : ["EFM8LB11F16E-","-QFN32 "]   ,
			0x4E : ["EFM8LB11F16E-","-QFP32 "]   ,
			0x4F : ["EFM8LB11F16E-","-QSOP24"]   ,
			0x50 : ["EFM8LB11F16E-","-QFN24 "]   ,
			0x51 : ["EFM8LB10F16E-","-QFN32 "]   ,
			0x52 : ["EFM8LB10F16E-","-QFP32 "]   ,
			0x53 : ["EFM8LB10F16E-","-QSOP24"]   ,
			0x54 : ["EFM8LB10F16E-","-QFN24 "]   ,
			0x61 : ["EFM8LB12F64ES0-","-QFN32"]  ,
			0x64 : ["EFM8LB12F64ES0-","-QFN24"]  ,
			0x65 : ["EFM8LB12F32ES0-","-QFN32"]  ,
			0x68 : ["EFM8LB12F32ES0-","-QFN24"]  ,
			0x69 : ["EFM8LB11F32ES0-","-QFN32"]  ,
			0x6C : ["EFM8LB11F32ES0-","-QFN24"]  ,
			0x6D : ["EFM8LB11F16ES0-","-QFN32"]  ,
			0x70 : ["EFM8LB11F16ES0-","-QFN24"]  ,
			0x71 : ["EFM8LB10F16ES0-","-QFN32"]  ,
			0x74 : ["EFM8LB10F16ES0-","-QFN24"]  ,
			0x81 : ["EFM8LB12F64ES1-","-QFN32"]  ,
			0x84 : ["EFM8LB12F64ES1-","-QFN24"]  ,
			0x85 : ["EFM8LB12F32ES1-","-QFN32"]  ,
			0x88 : ["EFM8LB12F32ES1-","-QFN24"]  ,
			0x89 : ["EFM8LB11F32ES1-","-QFN32"]  ,
			0x8C : ["EFM8LB11F32ES1-","-QFN24"]  ,
			0x8D : ["EFM8LB11F16ES1-","-QFN32"]  ,
			0x90 : ["EFM8LB11F16ES1-","-QFN24"]  ,
			0x91 : ["EFM8LB10F16ES1-","-QFN32"]  ,
			0x94 : ["EFM8LB10F16ES1-","-QFN24"]
        }

############################################################################
        # Related variables
        self.rRemainCyclesINFMODE    = np.uint16( 0xA000 ) # Bit13=1 defines infinite Mode
        self.rRemainCyclesFiniteMODE = np.uint16( 0x8000)  # Bit13=0 defines counted sycles mode
        self.rRemainCyclesCNTMODE = self.rRemainCyclesFiniteMODE

        self.rRemainCyclesCNTMODE=np.uint16(0x8000)
        self.SignallingMode = 2 # current signalling mode
        self.TimerMode = 0
        self.CSFmode=1
        self.INFmode = 2
        self.Timer_CSFmode = 3
        self.TEC_CSFmode = 4
        self.TXonlyMode  = 5 # Test mode to check if TX path is working, receiveris off

        self.TsamplingReg  = 0
        self.SlotNumbers   = 0
        self.Words16inSample = 8 # We have 4 channels, 2 words per channel
        self.TotalWords16ToGet = np.uint32(0)  # Number of words in 1 FRAME

        self.DACLSBma   =  330   / 65535
        self.ADCLSBmv   =  3.300 / 524288 # 0.00000629425048828125 v/lsb (6.294uV/LSB)
        self.ADCLSBmvsqr   = self.ADCLSBmv * self.ADCLSBmv  # =39.617 10**-12 v**2
        self.ADCLSBmvminus = -1*self.ADCLSBmv

        # self.ADCfullscaleRangemv = 6.6V


        ##########
        # LSER LOOKUPTABLE organized as 128 rows, 4 coolumns of 16bit words
        #
        ###############################################################################
        # |0              15|16             31|32             47|48             63|
        # +--------+--------+--------+--------+--------+--------+--------+--------+
        # |LASER # | ATTRIB | LASER CURRENT   |   SLOT TIME us  |  SECOND  DAC    |
        # +--------+--------+--------+--------+--------+--------+--------+--------+
        #  0 - Y1 index EnableSwitch Signal, 1-SIGNAL, 2-X value of current and logic
        self.pSTbl=np.zeros([131072,6])
        # pSTbl column [0] -
        self.pInd=0
        self.pInd1=0

        self.LaserSlotTable = np.array(np.zeros([2048, 4]), np.uint16) # 2048 rows 4 colums    # Variable_Parameter
        self.LaserSlotTableV2_0 = np.array(np.zeros([1024, 16]), np.uint16) # 1024 rows 16 colums    # Variable_Parameter
        self.LaserSlotTableV2_1 = np.array(np.zeros([1024, 4]), np.uint16) # 1024 rows 16 colums    # Variable_Parameter
        # for 2048 timeslots we need to transfer
        self.barrayTX       = bytearray(np.uint8(np.zeros([65536])))                          # Variable Parameter
        self.txbarrayindex  = 0
        self.barrayRX       = bytearray(np.uint8(np.zeros(8192)))

        ################################################################
        self.NcyclesinBuffer      = 0 # maximal number of frames
        self.nextByteBufferWritePointer = 0
        self.nextCycleToRead=0  # frames.cycles numerated from 0 to k
        self.nextCycleToPlotStart=0  # index for plottig the last sampled cycle
        self.DataReadyFlag=False
        self.SamplesInBuffer=0 # number samples in buffer per channel
        ################################################################
        self.SamplesInFrame   = 1024                    # Cycle Samples  per channel
        self.CycleBytes       = self.SamplesInFrame << 4  # Cycle Bytes for all 4 channel (16X above)

        self.byteshugemax       = 20971520  # 1,310,720 samples
        self.bytesmax           =  1048576  #    65,536 samples
        self.MAXSAMPLESdefault  = 16*65,536
        self.barrayRXA          = bytearray(np.uint8(np.zeros([self.byteshugemax])))

        self.i32arrayRX     = np.frombuffer(self.barrayRXA,dtype=np.uint32,count = -1)
        self.mscurrent   = np.array([0.0,0.0,0.0,0.0,0.0,0.0])
        self.msError     = np.array([0.0,0.0,0.0,0.0,0.0,0.0])
        self.msErrorsqr  = np.array([0.0,0.0,0.0,0.0,0.0,0.0])
        self.msGain      = np.array([1.0,1.0,1.0,1.0,1.0,1.0])
        self.msOffset    = np.array([1.0,1.0,1.0,1.0,1.0,1.0])
        self.plotmode4or6=False
        self.Kalpha      = 0
        #videobuffer
        self.i32arrayRXV      = np.array(np.zeros([6, 65536]))
        self.i32arrayRXV_EST  = np.array(np.zeros([6, 65536]))
        self.i32arrayRXV_err  = np.array(np.zeros([6, 65536]))
        self.i32arrayRXV_msqr = np.array(np.zeros([6, 65536]))

        self.i32arrayErr      = np.array(np.zeros([4, 65536]))
        self.i32arrayVAR      = np.array(np.zeros([4, 65536]))



        self.Recordtail         = self.nextCycleToRead
        self.lastCyclesinBuffer = self.NcyclesinBuffer
        self.lastSamplesInCycle = self.SamplesInFrame

        self.rxbarrayindex  = 0
        self.getbytescntRX    = 0
        ######################################################
        #self.framesToRepeat = 0
        ######################################################
        self.hexadr         = np.uint8(0)

        self.rtn            = np.uint16(0)

        self.TTECTable   = np.array(np.zeros([7]), np.uint16)  # Table of Thermoregister contents

        #       Buffer Data Command
        self.fw2_cmd  = np.uint16(256)  # next  word will be written into buffer
        self.fw4_cmd  = np.uint16(257)  # next  4 words will be written into buffer
        self.fw16_cmd = np.uint16(258)  # next  4 words will be written into buffer

        #   Directives to ft232 layer
        #   Non FPGA commands
        self.mode_buf_on  = np.uint16(512)  # Disable Buffer collection
        self.mode_buf_off = np.uint16(513)  # Enable Buffer Collection
        self.sdo_cmd      = np.uint16(514)  # execute collected commands
        #   Other commands
        #       self.mdtgl_cmd     = np.uint16(1024)     #
        self.comment_cmd  = np.uint16(1026)  # skip line, it's just comment
        self.end_cmd      = np.uint16(1027)  # end of script
        self.help_cmd     = np.uint16(1028)  # help
        self.rfresh_cmd   = np.uint16(1029)  # refresh registers
        self.mode_cmd_on  = np.uint16(1030)  #
        self.mode_cmd_off = np.uint16(1031)

        # return codes
        self.ok = 0
        self.wnp = 1  # Wrong number of parameters
        self.iha = 2  # "Invalid Hex address/value"
        self.ihd = 3  # invalid Hex Data
        self.wcc = 4  # Wrong command code
        self.ifv = 5  # Invalid Float Value
        self.hlp = 6  # helpstring
        self.cmdoff = 7  # Disable implementation of commands
        self.cmdon = 8  # Enable implementation of commands
        self.bufoff = 9
        self.bufon = 10
        self.notConnected = 11
        self.refresh = 12
        self.clrhist = 13
        self.comment = 14
        self.inl = 15
        self.runScript =16
        self.commentLine =17
        self.outofrange =18
        self.sleepcommand=19
        self.clearplot = 20
        self.timercmd =21
        self.runCycles = 22
        self.exit      = 23
        self.saveheader = 24
        self.too_many_slots = 25
        self.iiv = 26
        self.ibv = 27
        self.valueoutoflimits = 28
        self.systemconfig = 29
        self.hint = 30
        self.hlphtml = 31
        self.stopScript = 32
        self.rtn_dumpSlots =33
        self.rtn_notSupported =34
        #self.wrongFPGAVersion = 32

        self.repeat_cmd         = 100
        self.report             = 101
        self.f_getadc           = 102
        self.v_average          = 103
        self.v_rpv              = 104
        self.v_getfifo          = 105
        self.v_clearfifo        = 106
        self.v_scriptFound      = 200
        self.v_echoen           = 201
        self.v_echodis          = 202
        self.v_signalplotinit   = 203
        self.v_signalplotinit2  = 204



        self.message=["OK",
                      "Wrong number of parameters",
                      "Invalid Hex Address",
                      "Invalid Hex Data",
                      "Wrong Command Code",
                      "Invalid Float Value",
                      " ",
                      "CMD_MODE Disabled",
                      "CMD_MODE Enabled",
                      "BUFFERING of commands DISABLED",
                      "Buffering of commands Enabled",
                      "Device not connected",
                      "Refresh Done",
                      "history cleared",
                      "NOT IMPLEMENTED YET",
                      "invalid number of lines",
                      "End of script",
                      " ",
                      "Parameter is out of range",
                      "",
                      "",
                      "",
                      "",
                      "",
                      "",
                      "too_many_slots_defined",
                      "Invalid Integer value",
                      "Invalid Boolean or Integer value",
                      "Value out off limits",
                      "",
                      "",
                      "",
                      "",
                      "",
                      "Command is NOT SUPPORTED in this FPGA version"
                      ]

        self.helpmessage =[
                      "\nAvailable command formats\n",
                      "FPGA commands:",
                      "---------------",
                      "wr hexadress hexdata- writes hexdata into register",
					  "rd hexaddress   - returns content of  register\n",
                      "ld_msk hexvalue - Loads hexvalue into MSK register",
                      "ld_ptr hexvalue - Loads hexvalue into PTR register",
                      "ld_len hexvalue - Loads hexvalue into LENGTH register",
                      "ld_cnt hexvalue - Loads hexvalue into CNT register",
                      "ld_tmr hexvalue - Loads hexvalue into TIMER register\n",
                      "get_msk         - returns MSK register value",
                      "get_ptr         - returns PTR register value",
                      "get_len         - returns LENGTH register value",
                      "get_cnt         - returns CNT register value",
                      "get_tmr         - returns TIMER register value",
                      "get_ver         - returns VER register value\n",
                      "nop             - no command, just skip one clock\n",
                      "CMDBUF (Command Buffer ) append directives:",
                      "-------------------------------------------",
                      "b_wr hexadress hexdata - appends wr comand to CMDBUF ",
                      "b_ld_msk hexvalue - appends ld_msk to CMDBUF",
                      "b_ld_ptr hexvalue - appends ld_ptr to CMDBUF",
                      "b_ld_len hexvalue - appends ld_len to CMDBUF",
                      "b_ld_cnt hexvalue - appends ld_cnt to CMDBUF",
                      "b_ld_tmr hexvalue - appends ld_tmr to CMDBUF",
                      "b_nop             - appends nop    to CMDBUF",
                      "b_waitst          - appends waitst to CMDBUF",
					  "b_waitus          - appends waitus to CMDBUF",
					  "b_pktend          - appends pktend to CMDBUF",
                      "TsamplingReg value- appends wr 1A value to CMDBUF",
                      "CyclesHex value   - appends wr 19 value to CMDBUF ",
                      "addslot L_Num On/Off  Ima  SMPLS  TST - appends\n                    timeslot to CMDBUF",

                      "CMDBUF handling directives:",
                      "---------------------------",
                      "resetCmdBuf      - clears CMDBUF",
                      "resetSlotNumbers - resets Slotcounter variable to 0",
                      "send             - sends CMDBUF to FPGA",
                      "\n\nOther commands",
                      "----------------------------------------------------",
                      "MAXSamplesPerChannel Value - limits number of samples\n                             in receive buffer\n                             the max is 1310720",
                      "clr                        - clear history screen",
                      "rpv                        - report variables",
                      #"refresh " ,
                      #"buf_on  - BUF_MODE ON",
                      #"buf_off - BUF_MODE OFF",
                      #"runbuf  - run BUFFERED commands",
                      #"cmd_mode_off - CMD_MODE OFF",
                      #"cmd_mode_on  - CMD_MODE ON",
                      #"refresh updates all windows",
                      #"refresh - refresh registers from FPGA",
                      "savefilename <filename> define filename and\n                   enable save to  file",
                      "dateStampDisable -  save file datastamp disable",
                      "dateStampEnable  -  save file data stamp enable",
                      "fileNumberDisable",
                      "fileNumberEn -      sav file name numeration en",

                      "end          -      end of script"]

        self.returnmessage = ""
        ##############################################
        self.TECONOFF = False  #   TEC is off by default
        self.TECTARGET_ºC = 25.00
        self.SETTLING_TIME = np.uint32(0)
        self.SETTLING_PASSED = True

        #####################################
        # SaveFileName attributes
        self.SaveFileName = ""
        self.dateStampEnable = True    # controls enable/Disable dateStamp
        self.filenumber      = 1       # output file name postfix index
        self.fileNumberEn    = True
        self.savetofile      = False   # controls output to File.  If Filename shown
                                       # in scriptthen become True and result will be written to file

        # External execution filename and attributes
        self.startExeFName = ""        # external command line
        self.startExeEn  = False       # enables external exe if  execmd+fn  or execmd issued in script
        self.execmdaddfn = False       # Enables adding save file name as argument for external executable
        self.boolSaveHeaderEn = False
        # exit control
        self.boolexit = False  # allows exit if "exit command met
        self.runinfflag = False
        self.run2flag =False
        #####################################
        # Plot control
        self.ploten      = True        # controlled by plotEnable/plotDisable,  if disable then in SignallingMode1 it will not plot signall
        #####################################

        # currently not used
        self.sleeptime = 0.0
        self.sleepen   = False
        ######################
        self.run_Cycles_Flag =False


        # cyclic command control under the timer
        self.tmrCMP=int(-1)
        self.tmrTime      = np.uint32(1000)
        self.tmrTimetmp   = np.uint32(1000)
        self.tmrcycles    = np.uint32(20)
        self.tmrcmdline   = ""  # defines what command need to repeat , used for run_Cycles_Sec/repeatByTimer
       ###################################################
        self.TT = []
        ###################################################
        # FT232 controls
        self.ft232h_connected = False
        self.enableResultShow = False


        self.currentScriptName=""
        self.findScriptMode=False
        self.ScriptNameFound=False
        #self.tmenable=False
        # parameters of USB channel for read
        self.framesPerRead = np.uint16(64)
        self.framesPreload = np.uint16(64)

        self.dict ={}
    #########################################################################
    def resetplottedsignals(self):
        self.i32arrayRXV      = np.array(np.zeros([6, 65536]))
        self.i32arrayRXV_EST  = np.array(np.zeros([6, 65536]))
        self.i32arrayRXV_err  = np.array(np.zeros([6, 65536]))
        self.i32arrayRXV_msqr = np.array(np.zeros([6, 65536]))
        self.i32arrayErr      = np.array(np.zeros([4, 65536]))
        self.i32arrayVAR      = np.array(np.zeros([4, 65536]))
    #########################################################################
    #########################################################################
    #########################################################################
    #   ParserStart #########################################################
    #   ###############
    def cmdstringex(self, text):
        #print(text)
        mycollapsedstring = ' '.join(text.split())  # removes extra ' ' from the line
        self.TT = mycollapsedstring.split(' ')  # creates array of words
        num_parameters = len(self.TT)
        if (self.findScriptMode):
            #print("findScriptMode")
            if (self.TT[0] == "#"):
                if num_parameters != 2: return self.wnp
                if (self.TT[1] == self.currentScriptName):
                    self.findScriptMode=False
                    return self.v_scriptFound
                else:
                    return self.ok
            else:
                return  self.ok    #self.commentLine

        if self.TT[0] == 'end':
            if num_parameters!=1: return self.wnp
            return self.runScript
        if self.TT[0] == 'stop':
            if num_parameters!=1: return self.wnp
            return self.stopScript

        ##########################################################
        elif self.TT[0] == 'wr':
            if num_parameters != 3:   return self.wnp
            try:     self.hexadr = int(self.TT[1], 16)
            except:  return self.iha
            try:     self.hexdata = int(self.TT[2], 16)
            except:  return self.iha

            self.barrayTX[self.txbarrayindex] = np.uint8(self.wr_cmd|(self.hexadr ))
            self.txbarrayindex += 1
            self.addhexdata()
            if (self.ftsend()):  return self.ok
            else: return self.notConnected

        elif self.TT[0] == 'b_wr':
            if num_parameters != 3:   return self.wnp
            try:     self.hexadr = int(self.TT[1], 16)
            except:  return self.iha
            try:     self.hexdata = int(self.TT[2], 16)
            except:  return self.iha

            self.barrayTX[self.txbarrayindex] = np.uint8(self.wr_cmd|(self.hexadr ))
            self.txbarrayindex += 1
            self.addhexdata()
            return self.ok

        ##########################################################
        elif self.TT[0] == 'ld_ver':
            if num_parameters != 2: return self.wnp
            try:    self.hexdata = int(self.TT[1], 16)
            except: return self.iha
            self.barrayTX[self.txbarrayindex] = self.ldwdog_cmd
            self.txbarrayindex += 1;    self.addhexdata()
            if (self.ftsend()) :  return self.ok
            else: return self.notConnected

        elif self.TT[0] == 'b_ld_ver':
            if num_parameters != 2: return self.wnp
            try:    self.hexdata = int(self.TT[1], 16)
            except: return self.iha
            self.barrayTX[self.txbarrayindex] = self.ldwdog_cmd
            self.txbarrayindex += 1;    self.addhexdata()
            return self.ok
        ##########################################################
        elif self.TT[0] == 'ld_tst':
            if num_parameters != 2: return self.wnp
            try:    self.hexdata = int(self.TT[1], 16)
            except: return self.iha
            self.barrayTX[self.txbarrayindex] = self.ltst_cmd
            self.txbarrayindex += 1
            self.addhexdata()
            if (self.ftsend()) :  return self.ok
            else: return self.notConnected

        elif self.TT[0] == 'b_ld_tst':
            if num_parameters != 2: return self.wnp
            try:    self.hexdata = int(self.TT[1], 16)
            except: return self.iha
            self.barrayTX[self.txbarrayindex] = self.ltst_cmd
            self.txbarrayindex += 1
            self.addhexdata()
            return self.ok
        ##########################################################
        elif self.TT[0] == 'ld_msk':
            if num_parameters != 2: return self.wnp
            try:    self.hexdata = int(self.TT[1], 16)
            except: return self.iha
            self.barrayTX[self.txbarrayindex] = self.lmask_cmd
            self.txbarrayindex += 1
            self.addhexdata()
            if (self.ftsend()) :  return self.ok
            else: return self.notConnected

        elif self.TT[0] == 'b_ld_msk':
            if num_parameters != 2: return self.wnp
            try:    self.hexdata = int(self.TT[1], 16)
            except: return self.iha
            self.barrayTX[self.txbarrayindex] = self.lmask_cmd
            self.txbarrayindex += 1
            self.addhexdata()
            return self.ok

        ##########################################################
        elif self.TT[0] == 'ld_ptr':
            if num_parameters != 2: return self.wnp
            try:    self.hexdata = int(self.TT[1], 16)
            except: return self.iha
            self.barrayTX[self.txbarrayindex] = self.lpointer_cmd
            self.txbarrayindex += 1
            self.addhexdata()
            if (self.ftsend()) :  return self.ok
            else: return self.notConnected

        elif self.TT[0] == 'b_ld_ptr':
            if num_parameters != 2: return self.wnp
            try:    self.hexdata = int(self.TT[1], 16)
            except: return self.iha
            self.barrayTX[self.txbarrayindex] = self.lpointer_cmd
            self.txbarrayindex += 1
            self.addhexdata()
            return self.ok

        ##########################################################
        elif self.TT[0] == 'ld_len':
            if num_parameters != 2: return self.wnp
            try:    self.hexdata = int(self.TT[1], 16)
            except: return self.iha
            self.barrayTX[self.txbarrayindex] = self.llength_cmd
            self.txbarrayindex += 1
            self.addhexdata()
            if (self.ftsend()): return self.ok
            else: return self.notConnected

        elif self.TT[0] == 'ld_lenh':
            if num_parameters != 2: return self.wnp
            try:    self.hexdata = int(self.TT[1], 16)
            except: return self.iha
            self.barrayTX[self.txbarrayindex] = self.llengthH_cmd
            self.txbarrayindex += 1
            self.addhexdata()
            if (self.ftsend()): return self.ok
            else: return self.notConnected

        elif self.TT[0] == 'b_ld_len':
            if num_parameters != 2: return self.wnp
            try:    self.hexdata = int(self.TT[1], 16)
            except: return self.iha
            self.barrayTX[self.txbarrayindex] = self.llength_cmd
            self.txbarrayindex += 1
            self.addhexdata()
            return self.ok

        ##########################################################
        elif self.TT[0] == 'ld_cnt':
            if num_parameters != 2:  return self.wnp
            try:      self.hexdata = int(self.TT[1], 16)
            except:   return self.iha
            self.barrayTX[self.txbarrayindex] = self.lcnt_cmd
            self.txbarrayindex += 1
            self.addhexdata()
            if (self.ftsend()): return self.ok
            else: return self.notConnected

        elif self.TT[0] == 'b_ld_cnt':
            if num_parameters != 2:  return self.wnp
            try:      self.hexdata = int(self.TT[1], 16)
            except:   return self.iha
            self.barrayTX[self.txbarrayindex] = self.lcnt_cmd
            self.txbarrayindex += 1
            self.addhexdata()
            if (self.ftsend()): return self.ok

        ##########################################################
        elif self.TT[0] == 'ld_tmr':
            if num_parameters != 2:  return self.wnp
            try:     self.hexdata = int(self.TT[1], 16)
            except:  return self.iha
            self.barrayTX[self.txbarrayindex] = np.uint8(self.ltimer_cmd)
            self.txbarrayindex += 1
            self.addhexdata()
            if (self.ftsend()): return self.ok
            else: return self.notConnected

        elif self.TT[0] == 'b_ld_tmr':
            if num_parameters != 2:  return self.wnp
            try:     self.hexdata = int(self.TT[1], 16)
            except:  return self.iha
            self.barrayTX[self.txbarrayindex] = np.uint8(self.ltimer_cmd)
            self.txbarrayindex += 1
            self.addhexdata()
            return self.ok


        elif self.TT[0] == 'b_waitst':
            if num_parameters != 1: return self.wnp
            self.barrayTX[self.txbarrayindex] = np.uint8(self.waitst_cmd)
            self.txbarrayindex += 1
            return self.ok

        elif self.TT[0] == 'b_waitus':
            if num_parameters != 1: return self.wnp
            self.barrayTX[self.txbarrayindex] = np.uint8(self.waitus_cmd)
            self.txbarrayindex += 1
            return self.ok
        elif self.TT[0] == 'b_nop':
            if num_parameters != 1: return self.wnp
            self.barrayTX[self.txbarrayindex] = np.uint8(self.nop_cmd)
            self.txbarrayindex += 1
            return self.ok

        ##########################################################
        elif self.TT[0] == 'rd':
            if num_parameters != 2: return self.wnp
            try:       self.hexadr = np.uint8(int(self.TT[1], 16)) # gets uint8 from hex
            except:    return self.iha
            rtnv = self.getshortcmd(self.rd_cmd | (self.hexadr & 0x3f))
            self.returnmessage = ' ---> ' + self.hexprint(rtnv)
            return self.ok
        #########################################################################
        # C_GETVERSION      = 8'b0110_0000,  //  60    Get Version
        elif self.TT[0]=='get_ver':
            if num_parameters!=1:  return self.wnp
            self.VER[1]=self.getshortcmd(self.ver_cmd)
            self.returnmessage=' ---> '+self.hexprint(self.VER[1])
            self.returnmessage=self.returnmessage+' ( Ver {:02d}.{:02d} )'.format((((self.VER[1])>>4) & 0xF ),
                                                                           ((self.VER[1])&0xF))
            #print(self.returnmessage)
            return self.ok

        elif self.TT[0]=='get_tst':
            if num_parameters!=1:  return self.wnp
            self.TEST[1]=self.getshortcmd(self.gtst_cmd)
            self.returnmessage=' ---> '+ self.hexprint(self.TEST[1])
            return self.systemconfig

        #########################################################################
        elif self.TT[0] == 'get_msk':
            if num_parameters != 1:   return self.wnp
            self.MASK[1] = self.getshortcmd(self.gmask_cmd)
            self.returnmessage = ' ---> ' + self.hexprint(self.MASK[1])
            return self.ok
        #########################################################################
        elif self.TT[0] == 'get_ptr':
            if num_parameters != 1:   return self.wnp
            self.BUF_pnt[1] = self.getshortcmd(self.gpointer_cmd)
            self.returnmessage = ' ---> ' + self.hexprint(self.BUF_pnt[1])
            return self.ok
        #########################################################################
        elif self.TT[0] == 'get_len':
            if num_parameters != 1:  return self.wnp
            self.BUF_lng[1] = self.getshortcmd(self.glength_cmd)
            self.BUF_lngH[1] = self.getshortcmd(self.glengthH_cmd)
            self.returnmessage = ' ---> ' + self.hexprint(self.BUF_lng[1]) + '   ' + self.hexprint(self.BUF_lngH[1])
            return self.ok
        #########################################################################
        elif self.TT[0] == 'get_cnt':
            if num_parameters != 1: return self.wnp
            self.CNTreg[1] = self.getshortcmd(self.gcnt_cmd)
            self.returnmessage = ' ---> ' + self.hexprint(self.CNTreg[1])
            return self.ok
        #########################################################################
        elif self.TT[0] == 'get_tmr':
            if num_parameters != 1: return self.wnp
            self.TIMER[1] = self.getshortcmd(self.gtimer_cmd)
            self.returnmessage = ' ---> ' + self.hexprint(self.TIMER[1])
            return self.ok
        #########################################################################
        elif self.TT[0] == 'nop':
            if num_parameters != 1: return self.wnp
            self.barrayTX[self.txbarrayindex] = self.nop_cmd
            self.txbarrayindex += 1
            if (self.ftsend()): return self.ok
            else: return self.notConnected
        #########################################################################
        # USB Traffic control
        elif self.TT[0] == 'framesPerRead':
            if num_parameters!=2: return self.wnp
            try:
                self.framesPerRead = int(self.TT[1])
                if (self.framesPerRead < 1): return self.outofrange
                else:  return self.ok
            except:
                return self.iha
            else:
               return self.ok


        elif self.TT[0] == 'framesPreload':
            if num_parameters != 2: return self.wnp
            try:    self.framesPreload = np.uint16(int(self.TT[1]))
            except: return self.ifv
            else: return self.ok

        elif self.TT[0] == 'plotEnable':
            if num_parameters != 1: return self.wnp
            else:
                self.ploten = True
            return self.ok

        elif self.TT[0] == 'plotDisable':
            if num_parameters != 1: return self.wnp
            else:
                self.ploten = False
            return self.ok


        # Frames to repeat
        elif self.TT[0] == 'framesToRepeat':
            if num_parameters != 2: return self.wnp
            try:
                self.framesToRepeat = np.uint16(int(self.TT[1]))
                self.framesPerRead = self.framesToRepeat
            except:
                return self.ifv
            else:
                return self.ok



        elif self.TT[0] == 'savefilename':
            if num_parameters != 2: return self.wnp
            self.SaveFileName = self.TT[1]
            self.savetofile = True
            self.filenumber = 1
            return self.ok


        elif self.TT[0] == 'dateStampDisable':
            if num_parameters != 1: return self.wnp
            self.dateStampEnable = False
            return self.ok

        elif self.TT[0] == 'dateStampEnable':
            if num_parameters != 1: return self.wnp
            self.dateStampEnable = True
            return self.ok


        elif self.TT[0] == 'fileNumberEn':
            if num_parameters != 1: return self.wnp
            self.fileNumberEn = True
            return self.ok

        elif self.TT[0] == 'fileNumberDisable':
            if num_parameters != 1: return self.wnp
            self.fileNumberEn = False
            return self.ok

        #########################################################################
        #########################################################################
        elif self.TT[0] == 'help':
            if num_parameters != 1:
                #print("HELP")
                return self.wnp
            return self.hlp
        # comment sign
        elif self.TT[0][0] == ';':
            return self.commentLine
        # End of script, evrething below this line will be ignored

        elif self.TT[0] == 'refresh': return self.refresh   # Update all listboxes
        elif self.TT[0] == 'clr': return self.clrhist       # Clear History
        elif self.TT[0] == 'r': return self.repeat_cmd      # run previouse line
        elif self.TT[0] == 'rpv': return self.v_rpv         # report variables

        ##################################################################
        elif self.TT[0] == 'resetSlotNumbers':
            if num_parameters != 1: return self.wnp
            self.rNumberOfTSlots[1] = 0
            self.SlotNumbers=0
            self.pInd=0
            self.pInd1=0
            self.pSTbl[0,2] = 0
            return self.ok
        ###########################################################################
        # |0              15|16             31|32             47|48             63|
        # +--------+--------+--------+--------+--------+--------+--------+--------+
        # |LASER # | ATTRIB | LASER CURRENT   |   SLOT TIME us  |  SECOND  DAC    |
        # +--------+--------+--------+--------+--------+--------+--------+--------+
        elif (self.TT[0] == 'addslot'):
            if num_parameters != 6:
                return self.wnp
            try : ln = np.uint16(self.TT[1]) #Laser Number
            except: return self.iha
            try: currentATTRIB = np.uint16(round((float(self.TT[2])))) # Laser Attributes
            except:   return self.iha
            try:  LaserCurrentStartValue = float(self.TT[3])
            except: return self.iha
            StartCurrentCode=np.uint16(round(LaserCurrentStartValue/self.DACLSBma))  # Laser Current code = I/lsb = (I/300)*65535
                                                                 # This assume that currentsource does Iout= Vin *(1K/10K)*1ohm =0.1*Vin
            try:  SlotSamples = np.int16(round((float(self.TT[4])))) # Laser Samples
            except:   return self.iha

            LaserCurentEndValue = np.int16(0)  # SecondDac

            # print(ln, currentCode)
            if (self.SlotNumbers > 2047):
                return self.too_many_slots
            self.LaserSlotTable[self.SlotNumbers, 0] = ln + (currentATTRIB << 8)
            self.LaserSlotTable[self.SlotNumbers, 1] = StartCurrentCode
            self.LaserSlotTable[self.SlotNumbers, 2] =SlotSamples-np.uint16(1)
            self.LaserSlotTable[self.SlotNumbers, 3] = LaserCurentEndValue
            self.SlotNumbers +=1
            self.rNumberOfTSlots[1]+=1
            # print(self.SlotNumbers, self.rNumberOfTSlots)
            self.SamplesInFrame =self.SamplesInFrame+SlotSamples
            self.CycleBytes     = self.SamplesInFrame<<4

            # How many sycles could be fit in dedicated buffer if 1 sample requiring 16 bytes
            self.NcyclesinBuffer=(self.bytesmax>>4)//self.SamplesInFrame # 1 sample is 128 bits

            #How many Samples in buffer ?
            self.SamplesInBuffer=self.NcyclesinBuffer * self.SamplesInFrame

            # prepare plot preview
            enableSignals = (currentATTRIB & np.int16(1))

            for x in range(SlotSamples):
                self.pSTbl[self.pInd,0] = (enableSignals * 35) - 49  # EnableSwitch Signal
                self.pSTbl[self.pInd,1] =  (LaserCurrentStartValue) * enableSignals      # Signal
                self.pSTbl[self.pInd,2] = self.pInd1     #  Xtimecoordinates
                self.pInd  += 1
                self.pInd1 += 1

            #self.pSTbl[self.pInd,0] = enableSignals
            #self.pSTbl[self.pInd,1] = currentx
            #self.pSTbl[self.pInd,2] = self.pInd1
            #self.pInd += 1

            return self.ok
#  --------------------------------------------
        elif self.TT[0] == 'addrumpf' :
            if num_parameters != 6:
                return self.wnp
            try : ln = np.uint16(self.TT[1]) #Laser Number
            except: return self.iha
            try: currentATTRIB = np.uint16(round((float(self.TT[2])))) # Laser Attributes
            except: return self.iha

            try:  LaserCurrentStartValue = float(self.TT[3])
            except: return self.iha

            try:  SlotSamples = np.int16(round((float(self.TT[4])))) # Laser Samples
            except:   return self.iha

            try: LaserCurrentEndValue = float(self.TT[5])
            except: return self.iha

            LaserCurrentDeltaValue = (LaserCurrentEndValue-LaserCurrentStartValue)/SlotSamples
            LaserCurrentStartCode  = np.uint16(round(LaserCurrentStartValue/self.DACLSBma))  # Laser Current code = I/lsb = (I/300)*65535
            LaserCurentDelthaCode  = np.int16(round(LaserCurrentDeltaValue/self.DACLSBma))
            LaserCurrentEndCode    = np.uint16(round(LaserCurrentEndValue/self.DACLSBma))

            # print(ln, currentCode)
            if (self.SlotNumbers > 2047):
                return self.too_many_slots
            self.LaserSlotTable[self.SlotNumbers, 0] = ln + (currentATTRIB<<8)
            self.LaserSlotTable[self.SlotNumbers, 1] = LaserCurrentStartCode
            self.LaserSlotTable[self.SlotNumbers, 2] = SlotSamples-np.uint16(1)
            self.LaserSlotTable[self.SlotNumbers, 3] = LaserCurentDelthaCode
            self.SlotNumbers += 1
            self.rNumberOfTSlots[1] += 1
            # print(self.SlotNumbers, self.rNumberOfTSlots)
            self.SamplesInFrame = self.SamplesInFrame + SlotSamples
            self.CycleBytes     = self.SamplesInFrame << 4

            self.NcyclesinBuffer = (self.bytesmax >> 4)//self.SamplesInFrame
            self.SamplesInBuffer = self.NcyclesinBuffer * self.SamplesInFrame

            # prepare plot preview
            enableSignals = (currentATTRIB & np.int16(1))

            for x in range(SlotSamples):
                self.pSTbl[self.pInd,0] = (enableSignals * 35) - 49  # EnableSwitch Signal
                self.pSTbl[self.pInd,1] = ((LaserCurrentDeltaValue * x) + LaserCurrentStartValue) * enableSignals      # Signal
                self.pSTbl[self.pInd,2] = self.pInd1     #  Xtimecoordinates
                self.pInd  += 1
                self.pInd1 += 1

            #self.pSTbl[self.pInd,0] = enableSignals
            #self.pSTbl[self.pInd,1] = LaserCurrentEndCode
            #self.pSTbl[self.pInd,2] = self.pInd1
            #self.pInd += 1

            return self.ok
#  --------------------------------------------
        elif self.TT[0] == 'addrump2f' :
            '''
; addrump2f          ln  ATT LC  LCT LCE OPA1 OPA2 OPA3 OPA4 WIM1 WIM2 WIM3 WIM4 WIM5 WIM6 WIM7 WIM8 HN  HC  HASV1   SV2
;  1 - ln   :       laser Number : 1-st 4 bits Row Select , selects group of anodes
;                                : 2-d  4 bits Column Select, selects column for cathodes 
;  2 - ATT  :     8 bits currently not used , for future use of attributes, assign them to 0
;  3 - LCS  :     Laser Current Start Value(float) in ma will be converted in 16-bit DAC value in range 0..300ma
;  4 - LT   :     Timeslot Time in number of samples. Actual time is (Sampling Period)*(Number of Samples in slot)      
;  5 - LCE  :     Laser current End value (float in ma in range 0 .. 300ma)
;  6 - OPA1 :     OPA1 current in ma in range 0..300ma 
;  7 - OPA2 :     OPA2 current in ma in range 0..300ma
;  8 - OPA3 :     OPA3 current in ma in range 0..300ma
;  9 - OPA4 :     OPA4 current in ma in range 0..300ma
; 10 - WIM1 :     WIM1 current in ma in range 0..300ma
; 11 - WIM2 :     WIM2 current in ma in range 0..300ma
; 12 - WIM3 :     WIM3 current in ma in range 0..300ma
; 13 - WIM4 :     WIM4 current in ma in range 0..300ma
; 14 - WIM5 :     WIM5 current in ma in range 0..300ma
; 15 - WIM6 :     WIM6 current in ma in range 0..300ma
; 16 - WIM7 :     WIM7 current in ma in range 0..300ma
; 17 - WIM8 :     WIM8 current in ma in range 0..300ma

; 18 - HN   :     Heater Number : 1-st 3 bits Row Select ,   selects group of anodes
;                               : next  5 bits Column Select, selects column for cathodes
;                               : last 8 bits not used 
; 19 - HC   :     Heater current in float (ma) in range 0..300ma
; 20 - PAR1 :     Currently 0, Could be Laser processing First  parameter
; 21 - PAR2 :     Currently 0, Could be Laser processing Second parameter
# addrump2f   EPI_LN  ATT LCS LCT   LCE   OPA1  OPA2   OPA3   OPA4  WIM1  WIM2  WIM3  WIM4  WIM5  WIM6  WIM7  WIM8    HN   HATT  HC     PAR1  PAR2
# addrump2f    3_5     0   20  10  35.7  12.0  77.35  102.35 12.0  11.23  0     0     0     0     210   0     0    2_17  0    215.3   0     0             
'''

            if (self.FPGAVer < 8):
                return self.rtn_notSupported

            if num_parameters != 23: return self.wnp
            self.ss = self.TT[1].split('_')


            try : epi= np.uint16(self.ss[0]) #Laser Number
            except: return self.iha

            try : ln= np.uint16(self.ss[1]) #Laser Number
            except: return self.iha


            try: ATTRIB = np.uint16(round((float(self.TT[2])))) # Laser Attributes
            except:   return self.iha

            try:  LaserCurrentStartValue = float(self.TT[3])
            except: return self.iha

            StartCurrentCode=np.uint16(round(LaserCurrentStartValue/self.DACLSBma))  # Laser Current code = I/lsb = (I/300)*65535
                                                                 # This assume that currentsource does Iout= Vin *(1K/10K)*1ohm =0.1*Vin
            try:  SlotSamples = np.uint16(round((float(self.TT[4])))) # Laser Samples
            except:   return self.iha

            try:
                LaserCurrentEndValue   = float(self.TT[5])
                LaserCurrentDeltaValue = (LaserCurrentEndValue-LaserCurrentStartValue)/SlotSamples
                LaserCurentDelthaCode  = np.int16(round(LaserCurrentDeltaValue/(self.DACLSBma)))
            except: return self.iha

            try:  OPA1Value = float(self.TT[6])
            except: return self.iha

            try:  OPA2Value = float(self.TT[7])
            except: return self.iha

            try:  OPA3Value = float(self.TT[8])
            except: return self.iha

            try:  OPA4Value = float(self.TT[9])
            except: return self.iha


            try:  WIM1Value = float(self.TT[10])
            except: return self.iha
            try:  WIM2Value = float(self.TT[11])
            except: return self.iha
            try:  WIM3Value = float(self.TT[12])
            except: return self.iha
            try:  WIM4Value = float(self.TT[13])
            except: return self.iha
            try:  WIM5Value = float(self.TT[14])
            except: return self.iha
            try:  WIM6Value = float(self.TT[15])
            except: return self.iha
            try:  WIM7Value = float(self.TT[16])
            except: return self.iha
            try:  WIM8Value = float(self.TT[17])
            except: return self.iha

            self.st = self.TT[18].split('_')

            try : epiH= np.uint16(self.st[0])
            except: return self.iha

            try : lnH= np.uint16(self.st[1])
            except: return self.iha
            try: HATTRIB = np.uint16(round((float(self.TT[19])))) # Laser Attributes
            except:   return self.iha

            try:  HeaterCurrent = float(self.TT[20])
            except: return self.iha
            try:  PAR1 = float(self.TT[21])
            except: return self.iha
            try:  PAR2 = float(self.TT[22])
            except: return self.iha



            # print(ln, currentCode)
            if (self.SlotNumbers > 1023):
                return self.too_many_slots
            #filling arrays

            self.LaserSlotTableV2_0[self.SlotNumbers, 0] = (epi<<4) + ln+(ATTRIB<<8)
            self.LaserSlotTableV2_0[self.SlotNumbers, 1] = StartCurrentCode
            self.LaserSlotTableV2_0[self.SlotNumbers, 2] = SlotSamples - 1
            self.LaserSlotTableV2_0[self.SlotNumbers, 3] = LaserCurentDelthaCode
            self.LaserSlotTableV2_0[self.SlotNumbers, 4] = np.uint16(round(OPA1Value/self.DACLSBma))
            self.LaserSlotTableV2_0[self.SlotNumbers, 5] = np.uint16(round(OPA2Value/self.DACLSBma))
            self.LaserSlotTableV2_0[self.SlotNumbers, 6] = np.uint16(round(OPA3Value/self.DACLSBma))
            self.LaserSlotTableV2_0[self.SlotNumbers, 7] = np.uint16(round(OPA4Value/self.DACLSBma))
            self.LaserSlotTableV2_0[self.SlotNumbers, 8] = np.uint16(round(WIM1Value/self.DACLSBma))
            self.LaserSlotTableV2_0[self.SlotNumbers, 9] = np.uint16(round(WIM2Value/self.DACLSBma))
            self.LaserSlotTableV2_0[self.SlotNumbers,10] = np.uint16(round(WIM3Value/self.DACLSBma))
            self.LaserSlotTableV2_0[self.SlotNumbers,11] = np.uint16(round(WIM4Value/self.DACLSBma))
            self.LaserSlotTableV2_0[self.SlotNumbers,12] = np.uint16(round(WIM5Value/self.DACLSBma))
            self.LaserSlotTableV2_0[self.SlotNumbers,13] = np.uint16(round(WIM6Value/self.DACLSBma))
            self.LaserSlotTableV2_0[self.SlotNumbers,14] = np.uint16(round(WIM7Value/self.DACLSBma))
            self.LaserSlotTableV2_0[self.SlotNumbers,15] = np.uint16(round(WIM8Value/self.DACLSBma))

            self.LaserSlotTableV2_1[self.SlotNumbers, 0] = (epiH<<4)+(lnH>>1) + ((lnH & 0x1)<<3) + (HATTRIB<<8)
            self.LaserSlotTableV2_1[self.SlotNumbers, 1] = np.uint16(round(HeaterCurrent/self.DACLSBma))
            # Filters parameters
            self.LaserSlotTableV2_1[self.SlotNumbers, 2] = np.uint16(PAR1)
            self.LaserSlotTableV2_1[self.SlotNumbers, 3] = np.uint16(PAR2)


            self.SlotNumbers +=1
            self.rNumberOfTSlots[1]+=1
            # print(self.SlotNumbers, self.rNumberOfTSlots)
            # TODO FIRST

            self.SamplesInFrame = self.SamplesInFrame+SlotSamples # Total Samples in script
            self.CycleBytes     = self.SamplesInFrame<<4          # Total bytes in script

            # 1 sample requires 16 bytes (120bits in case of 6 channnels)
            #
            self.NcyclesinBuffer = (self.bytesmax>>4)//self.SamplesInFrame
            self.SamplesInBuffer = self.NcyclesinBuffer * self.SamplesInFrame

            # prepare plot preview
            enableSignals = (ATTRIB & np.int16(1))
            currentxStart = LaserCurrentStartValue * enableSignals



            # TODO add interpolation
            for x in range(SlotSamples):
                self.pSTbl[self.pInd,0] = enableSignals  # EnableSwitch Signal
                self.pSTbl[self.pInd,1] = ( LaserCurrentDeltaValue * x ) + LaserCurrentStartValue
                self.pSTbl[self.pInd,2] = self.pInd1     #  Xtimecoordinates
                self.pInd  += 1
                self.pInd1 += 1

            #self.pSTbl[self.pInd,0] = enableSignals
            #self.pSTbl[self.pInd,1] = LaserCurrentStartValue * enableSignals
            #self.pSTbl[self.pInd,2] = self.pInd1
            #self.pInd1 += 1
            #self.pInd += 1

            return self.ok
#  --------------------------------------------

        elif self.TT[0] == 'slotTableToTXbuffer':
            if num_parameters != 1: return self.wnp
            self.slotTableToTXbuffer()
            return self.ok

        elif self.TT[0] == 'SetSamplesInTxBuf':
            if num_parameters != 1: return self.wnp
            self.slotTableToTXbuffer()
            return self.ok

        ##################################################################
        # Set sampling period in us 0 nly even number
        elif self.TT[0] == 'TsamplingReg':
            if num_parameters != 2 : return self.wnp
            try: self.TsamplingReg = int(self.TT[1])
            except: return self.inl
            self.rSample_Period[1] = np.uint16(self.TsamplingReg)
            self.addWrReg(self.rSample_Period[0],self.rSample_Period[1])
            return self.ok

        elif self.TT[0] == 'MAXSamplesPerChannel':
            if num_parameters != 2 : return self.wnp
            try: self.bytesmax = int(16*int(self.TT[1]))
            except: return self.inl
            return self.ok


        elif self.TT[0] == 'resetCmdBuf':
            if num_parameters  != 1 : return self.wnp
            self.txbarrayindex  = 0
            self.rxbarrayindex  =0
            self.SamplesInFrame = 0
            return self.ok

        elif self.TT[0] == 'CyclesHex':
            # setting remain cycles  register
            if num_parameters != 2 : return self.wnp
            try: self.rRemainCyclesCNT[1] = np.uint16(int(self.TT[1],16))
            except: return self.inl
            self.addWrReg(self.rRemainCyclesCNT[0],self.rRemainCyclesCNT[1])
            return self.ok

        elif self.TT[0]=='send' :
            if num_parameters!=1: return self.wnp
            if (self.ftsend()) :  return self.ok
            else: return self.notConnected

        elif  self.TT[0]=='report' :
            if num_parameters!=1:
                return self.wnp
            else:
                self.TotalWords16ToGet=self.SamplesInFrame*self.Words16inSample*((self.rRemainCyclesCNT[1]&0xFFF)+1) # Samples in cycle * 8
                return self.report

        elif  self.TT[0]=='echoenable' :
            if num_parameters!=1:
                return self.wnp
            else:
                return self.v_echoen

        elif  self.TT[0]=='echodisable' :
            if num_parameters!=1:
                return self.wnp
            else:
                return self.v_echodis

        elif self.TT[0]=='average':
            if num_parameters!=1:
                return self.wnp
            else:
                return self.v_average

        elif self.TT[0]=='signalplot':
            if num_parameters!=1:
                return self.wnp
            else:
                return self.v_signalplotinit


        # ; run cycles intervales frames per cycle
        # runCSF <Cycles> <TimetoWait> <FramesPerRead>
        elif self.TT[0] == 'runCSF':
            if num_parameters != 4: return self.wnp
            try: self.tmrcycles = int(self.TT[1])
            except:  return self.inl
            try:  self.tmrTime = np.uint32(int(self.TT[2]))
            except: return self.inl
            try: self.framesPerRead = int(self.TT[3])
            except: return self.inl
            self.SignallingMode = self.CSFmode
            self.tmrCMP = 1
            self.run_Cycles_Flag = True
            self.runinfflag = False
            return self.v_signalplotinit

        elif self.TT[0] == 'TXonlyMode':
            if num_parameters != 1: return self.wnp
            self.SignallingMode=self.TXonlyMode
            return self.ok


        elif self.TT[0] == 'dumpSlots':
            if num_parameters != 1: return self.wnp
            return self.rtn_dumpSlots


        # ; run in infinit mode
        # runInf_F <FramesPerRead>
        elif self.TT[0] == 'runInf_F':
            if num_parameters != 2:  return self.wnp
            try: self.framesPerRead = int(self.TT[1])
            except:  return self.inl
            self.SignallingMode = self.INFmode
            self.runinfflag = True
            self.run_Cycles_Flag =False
            return self.v_signalplotinit

        # wait thermostabilisation and run in CSF mode
        elif self.TT[0] == 'runWaitTimeCSF':
            if num_parameters != 4: return self.wnp
            try: self.tmrcycles = int(self.TT[1])
            except: return self.inl
            try: self.tmrTime = np.uint32(int(self.TT[2]))
            except: return self.inl
            try: self.framesPerRead = int(self.TT[3])
            except: return self.inl
            self.SignallingMode = self.Timer_CSFmode
            self.tmrCMP = 1
            self.run_Cycles_Flag = True
            self.runinfflag = False
            return self.v_signalplotinit

        elif self.TT[0] == 'runWaitTECCSF':
            if num_parameters != 4: return self.wnp
            try: self.tmrcycles = int(self.TT[1])
            except: return self.inl
            try: self.tmrTime = np.uint32(int(self.TT[2]))
            except: return self.inl
            try: self.framesPerRead = int(self.TT[3])
            except: return self.inl
            self.SignallingMode =self.TEC_CSFmode
            self.tmrCMP = 1
            self.run_Cycles_Flag = True
            self.runinfflag = False
            return self.v_signalplotinit

        # Tec ON/OFF/ Set target
        # Format  setTEC 0/1  TECTARGET_ºC SETTLING TIME
        # example
        # setTEC 1 23.2  30.5
        elif self.TT[0] == 'setTEC':
            if num_parameters != 4: return self.wnp
            try:  tmp=int(self.TT[1])
            except:   return self.iiv
            try:   tmp1 = float(self.TT[2])
            except: return self.ifv
            try:   tmp2 = np.uint32(self.TT[3])
            except: return self.ifv

            if (tmp==0):  self.TECONOFF = False;   return self.ok
            else:
                if (tmp==1):  self.TECONOFF = True
                else:         return self.ibv

            if (tmp1<40.0 and tmp1>18.0) :
                self.TECTARGET_ºC = tmp1
            else:
                return self.valueoutoflimits
            if (tmp2<200 and tmp2>0) :
                self.SETTLING_TIME = tmp2
            else:
                return self.outofrange
            self.SETTLING_PASSED = False
            return self.ok

        #############################
        #  Gets 7x16bit values from TTEC buffer into barrayRX
        elif self.TT[0] == 'get_TTEC':
            if num_parameters != 1:  return self.wnp
            if self.TTEC_GETDATA(10): return self.ok
            else: return self.notConnected
        ##################################################
        elif self.TT[0]=='get_adc':
            if num_parameters!=1:  return self.wnp
            return self.f_getadc

        elif self.TT[0]=='get_fifo':
            if num_parameters!=1:  return self.wnp
            return self.v_getfifo

        elif self.TT[0]=='clear_fifo':
            if num_parameters!=1:  return self.wnp
            return self.v_clearfifo

        #sleep() tm.sleep(ss)
        elif self.TT[0] == 'sleep':
            if num_parameters != 2 : return self.wnp
            try: self.sleeptime = (float(self.TT[1]))
            except: return self.inl
            if(self.sleeptime > 0.0) :
                self.sleepen=True
            else: self.sleepen=False
            return self.sleepcommand

        elif self.TT[0]=='execmd':
            if num_parameters==1:  return self.wnp
            for i in range(1 , num_parameters):
                self.startExeFName  += self.TT[i]
                self.startExeFName  += " "
            self.startExeEn = True


        elif self.TT[0]=='execmd+fn':
            if num_parameters==1:  return self.wnp
            for i in range(1 , num_parameters):
                self.startExeFName  += self.TT[i]
                self.startExeFName  += " "
                self.execmdaddfn = True
            self.startExeEn = True


        elif self.TT[0]=='clearplot':
            if num_parameters!=1:  return self.wnp
            return self.clearplot


        elif self.TT[0] == 'addheader':
            if num_parameters != 1:  return self.wnp
            self.boolSaveHeaderEn = True
            return self.saveheader


        elif self.TT[0]=='exiten':
            if num_parameters!=1:  return self.wnp
            self.boolexit= True
            return self.exit


        elif self.TT[0]=='hint':
            if num_parameters!=1:  return self.wnp
            return self.hint

        elif self.TT[0]=='html':
            if num_parameters!=1:  return self.wnp
            return self.hlphtml

        else:
            # self.listWidgetMSG.addItem("Wrong command code")
            # print(self.cmdCode)
            return self.wcc

        return self.ok
## Parser End #######################################################
#########################################################################
#########################################################################
    def ResetInits(self):

        self.ploten         = True
        self.SignallingMode = 2
        self.SaveFileName   = "samples"
        self.framesPerRead  = 64
        self.bytesmax       = self.MAXSAMPLESdefault
        self.savetofile     = False
        self.dateStampEnable   = True
        self.fileNumberEn      = True
        self.startExeFName = ""
        self.startExeEn = False
        self.execmdaddfn = False
        self.boolSaveHeaderEn = False

        self.rNumberOfTSlots[1] = 0
        self.SlotNumbers=0
        self.pInd=0
        self.pInd1=0
        self.pSTbl[0,2] = 0
        self.txbarrayindex  = 0
        self.rxbarrayindex  = 0
        self.SamplesInFrame = 0
        self.resetFIFO()
        return

    def resetFIFO(self):
        self.txbarrayindex=3
        self.barrayTX[0] = self.lcnt_cmd
        self.barrayTX[1] =  0x00
        self.barrayTX[2] =  0xC0
        self.txbarrayindex=3
        if ( not self.ftsend()): return False
        self.barrayTX[2] =  0xC8
        self.txbarrayindex=3
        if ( not self.ftsend()): return False
        self.barrayTX[2] =  0xC0
        self.txbarrayindex=3
        if ( not self.ftsend()): return False
        return True

    def clearfifo(self):
        self.CNTreg[1] ^= 0x0800
        self.wr_reg(self.CNTreg[0], self.CNTreg[1])
        time.sleep(.03)
        self.CNTreg[1] ^= 0x0800
        self.wr_reg(self.CNTreg[0], self.CNTreg[1])
        return

    # current
    def V2Icontrol(self,OnOFF):
        if OnOFF == 0:
            self.CNTreg[1] &= 0xFEFF  # bit 8 set to 0
        else:
            self.CNTreg[1] |= 0x0100  # bit 8 set to 1
        self.wr_reg(self.CNTreg[0], self.CNTreg[1])
        return
#########################################################################
    def RunInTXonlyMode(self):
        self.rRemainCyclesCNT[1] = self.rRemainCyclesINFMODE
        self.addWrReg(self.rRemainCyclesCNT[0],self.rRemainCyclesCNT[1])
#########################################################################
#########################################################################
#########################################################################
    def hexprint(self, inv):
        return str('{:04x}  {:04b}_{:04b}_{:04b}_{:04b}'.format(inv, inv >> 12, (inv >> 8) & 0xf, (inv >> 4) & 0xf, (inv & 0xf)))
    #########################################################################
    def addhexdata(self):
        self.barrayTX[self.txbarrayindex] = np.uint8(self.hexdata& 0xff);    self.txbarrayindex += 1
        self.barrayTX[self.txbarrayindex] = np.uint8(self.hexdata>>8)  ;    self.txbarrayindex += 1
        return

    def f_resetcmdbuf(self):
        self.txbarrayindex=0
        self.rxbarrayindex=0
        self.SamplesInFrame=0
        return

    #########################################################################
    def getAllRegisters(self):
        self.VER[1]      = self.getshortcmd(self.ver_cmd)
        self.TEST[1]     = self.getshortcmd(self.gtst_cmd)
        self.MASK[1]     = self.getshortcmd(self.gmask_cmd)
        self.BUF_lngH[1] = self.getshortcmd(self.glengthH_cmd)
        self.BUF_pnt[1]  = self.getshortcmd(self.gpointer_cmd)
        self.BUF_lng[1]  = self.getshortcmd(self.glength_cmd)
        self.CNTreg[1]   = self.getshortcmd(self.gcnt_cmd)
        self.TIMER[1]    = self.getshortcmd(self.gtimer_cmd)
#
        self.rAD5541TX[1]       =self.getshortcmd(self.rd_cmd|(np.uint8(self.rAD5541TX[0]) ))
        self.rSPInSELECT[1]     =self.getshortcmd(self.rd_cmd|(np.uint8(self.rSPInSELECT[0]) ))
        self.rTECT_CNT[1]       =self.getshortcmd(self.rd_cmd|(np.uint8(self.rTECT_CNT[0]) ))
        self.rNumberOfTSlots[1] =self.getshortcmd(self.rd_cmd|(np.uint8(self.rNumberOfTSlots[0]) ))
        self.rRemainCyclesCNT[1]=self.getshortcmd(self.rd_cmd|(np.uint8(self.rRemainCyclesCNT[0]) ))
        self.rSample_Period[1]  =self.getshortcmd(self.rd_cmd|(np.uint8(self.rSample_Period[0]) ))

        if (self.FPGAVer==8):
            self.DDScontrol[1]  = self.getshortcmd(self.rd_cmd | (np.uint8(self.DDScontrol[0]) ))
            self.DDSdeltha[1]   = self.getshortcmd(self.rd_cmd | (np.uint8(self.DDSdeltha[0]) ))
         #self.DDScontrol[1]  = self.getshortcmd(self.rd_cmd | (np.uint8(self.DDScontrol[0]) ))
#        self.getadc6()
#        self.ft232h.purge(3)
        return
    #########################################################################
    # add write register command to TX buffer
    def addWrReg(self,hexadr,hexdata):
        self.barrayTX[self.txbarrayindex] = np.uint8(self.wr_cmd|(hexadr)) ;  self.txbarrayindex += 1
        self.barrayTX[self.txbarrayindex] = np.uint8(hexdata&0x00ff) ;        self.txbarrayindex += 1
        self.barrayTX[self.txbarrayindex] = np.uint8(hexdata>>8) ;            self.txbarrayindex += 1
        return

    def setSmpNumreg(self): # sets rNumberOfTSlots rSample_Period rRemainCyclesCNT
        self.addWrReg(self.rSample_Period[0],  self.rSample_Period[1]  )  # writing sampling Period
        self.addWrReg(self.rNumberOfTSlots[0], self.rNumberOfTSlots[1] )  # 16 bits but only 7:0 used
        return

############################################################################################
    def slotTableToTXbuffer(self):  # LSB first, MSB second
        if (self.FPGAVer == 8):
            self.slotTableToTXbufferV1(self.slotparams0,self.LaserSlotTableV2_0,self.LASER_LUT_Adr)
            self.slotTableToTXbufferV1(self.slotparams1,self.LaserSlotTableV2_1,self.LASER_LUT2_Adr)
        else:
            self.slotTableToTXbufferV1(self.slotparams0,self.LaserSlotTable,self.LASER_LUT_Adr)
        self.rNumberOfTSlots[1]=np.uint16(self.SlotNumbers-1)
        self.addWrReg(self.rNumberOfTSlots[0], self.rNumberOfTSlots[1] )  # 16 bits but only 7:0 used

    def slotTableToTXbufferV1(self,slotparams0,LUTable,LUT_Adr ):  # LSB first, MSB se cond
        ''' converts LaserSlotTable into sequence of commands '''
        #set pointer
        self.barrayTX[self.txbarrayindex] = self.lpointer_cmd             ; self.txbarrayindex += 1  # loadpointercmd
        self.barrayTX[self.txbarrayindex] = np.uint8(LUT_Adr&0xff)        ; self.txbarrayindex += 1  # lower byte of pointer
        self.barrayTX[self.txbarrayindex] = np.uint8(LUT_Adr>>8)          ; self.txbarrayindex += 1  # Upper byte of pointer
        # set length to qtySlots*4 -1
        wordqty_n= np.uint16(self.SlotNumbers * slotparams0 )- 1
        self.barrayTX[self.txbarrayindex] = self.llength_cmd          ; self.txbarrayindex += 1    # loadLengthReg cmd
        self.barrayTX[self.txbarrayindex] = np.uint8(wordqty_n&0xff)  ; self.txbarrayindex += 1    # LoadLengthReg lowerbyte
        self.barrayTX[self.txbarrayindex] = np.uint8(wordqty_n>>8)    ; self.txbarrayindex += 1    # LoadUpperLengthReg byte
        # add write buffer cmd
        self.barrayTX[self.txbarrayindex] = self.wrbuf_cmd    ;  self.txbarrayindex += 1           # wrbuf command
        # move LaserSlotTable into barrayTX
        for x in range(self.SlotNumbers):
            for y in range(slotparams0):
                self.barrayTX[self.txbarrayindex] = np.uint8(LUTable[x,y]&0x00ff) ; self.txbarrayindex += 1
                self.barrayTX[self.txbarrayindex] = np.uint8(LUTable[x,y]>>8)     ; self.txbarrayindex += 1
        return

    ############################################################################################
    def validateVariables(self):
        self.TotalWords16ToGet=self.SamplesInFrame*self.Words16inSample*((self.rRemainCyclesCNT[1]&0xFFF)+1)
        if (self.TotalWords16ToGet>65535): return False
        else: return True
    #########################################################################
    def getadc6(self):
        self.ADC0MD[1]  = self.getshortcmd(self.rd_cmd|np.uint8(self.ADC0MD[0] ))
        self.ADC0LD[1]  = self.getshortcmd(self.rd_cmd|np.uint8(self.ADC0LD[0] ))
        self.ADC1MD[1]  = self.getshortcmd(self.rd_cmd|np.uint8(self.ADC1MD[0] ))
        self.ADC1LD[1]  = self.getshortcmd(self.rd_cmd|np.uint8(self.ADC1LD[0] ))
        self.ADC2MD[1]  = self.getshortcmd(self.rd_cmd|np.uint8(self.ADC2MD[0] ))
        self.ADC2LD[1]  = self.getshortcmd(self.rd_cmd|np.uint8(self.ADC2LD[0] ))
        self.ADC3MD[1]  = self.getshortcmd(self.rd_cmd|np.uint8(self.ADC3MD[0] ))
        self.ADC3LD[1]  = self.getshortcmd(self.rd_cmd|np.uint8(self.ADC3LD[0] ))
        self.ADC4MD[1]  = self.getshortcmd(self.rd_cmd|np.uint8(self.ADC4MD[0] ))
        self.ADC4LD[1]  = self.getshortcmd(self.rd_cmd|np.uint8(self.ADC4LD[0] ))
        return
        #########################################################################
    def SetEFM(self,MODE):
        self.wr_reg(np.uint8(self.rTECT_CNT[0]),MODE )
        time.sleep(.1)
    #########################################################################
    # - - - - - -  TRANSPORT LAYER  - - - - - -
    # see https://eblot.github.io/pyftdi/api/ftdi.html
    #########################################################################
    ##### Thermo ElectricCooller control Functions      ###########################################
    #  getTTEC gets TEC buffer content 7 16bit words
    #define CMD_NOP              0x00

    def TTEC_GETDATA(self,wrds):   self.txbarrayindex=0;  self.getb(self.TEC_TERMO_BUF_Adr,wrds); return


    def TEC_OnOFF(self, OnOFF):
        if (OnOFF) :  self.wr_reg(self.rTECT_CNT[0],self.EFM_CMD_TEC_ON)
        else : self.wr_reg(self.rTECT_CNT[0],self.EFM_CMD_TEC_OFF)
        return


    #  Sets Target Values
    def add_TEC_setDACold(self,DACVALUEU16):
        '''Sets EFM DAC0 12 bits: first byte: 01****** The lowest 6 bits of first word are DAC0 LSB 6 bits
                                second byte:  10****** The lowest 6 bits of second byte are DAC0 MSB 6 bits
        '''
        for i in range(8):
            self.addWrReg(self.rTECT_CNT[0],(0x4000|(self.TTECTable[i]&0xff)))
            self.addWrReg(self.rTECT_CNT[0],(0x4000|(self.TTECTable[i]>>8)))
        if (self.ftsend()) :  return self.ok
        else: return self.notConnected

    def add_TEC_setDAC(self,DACVALUEU16):
        self.addWrReg(self.TIMER[0],0x3000)
        DACL=np.uint16(0x4040 | (0x003F & DACVALUEU16))
        self.addWrReg(self.rTECT_CNT[0],DACL)
        self.barrayTX[self.txbarrayindex] = self.waitus_cmd ; self.txbarrayindex += 1
        DACH=np.uint16(0x4080 | (0x003F & (DACVALUEU16 >> 6)))
        self.addWrReg(self.rTECT_CNT[0],DACH)
        self.barrayTX[self.txbarrayindex] = self.waitus_cmd ; self.txbarrayindex += 1
        return

    def TEC_setDAC(self,DACVALUEU16):
        '''Sets EFM DAC0 12 bits: first byte: 01**_**** The lowest 6 bits of first word are DAC0 LSB 6 bits
                                second byte:  10**_**** The lowest 6 bits of second byte are DAC0 MSB 6 bits
        '''
        DACL=np.uint16(0x4040 | (0x003F & DACVALUEU16))
        self.wr_reg(self.rTECT_CNT[0],DACL)
        time.sleep(0.02)
        DACH=np.uint16(0x4080 | (0x003F & (DACVALUEU16 >> 6)))
        self.wr_reg(self.rTECT_CNT[0],DACH)
        return

    #def TEC_setDACH(self):
    #    self.wr_reg(self.rTECT_CNT[0],np.uint16(0x4082))
    #    return
    #def TEC_setDACL(self):
    #    self.wr_reg(self.rTECT_CNT[0],np.uint16(0x4045))
    #    return

    def TEC_SetTemperature(self, temperature):
        #self.wr_reg(self.rTECT_CNT[0],(0x4000|(self.TTECTable[i]&0xff)))
        return

        #########################################################################
        #self.txbarrayindex=0;  self.getb(0x8000,0x8)
    def getb_rq(self,adr,qty):
        self.barrayTX[self.txbarrayindex] = self.lpointer_cmd         ; self.txbarrayindex += 1
        self.barrayTX[self.txbarrayindex] = np.uint8(adr&0xff)        ; self.txbarrayindex += 1
        self.barrayTX[self.txbarrayindex] = np.uint8(adr>>8)          ; self.txbarrayindex += 1
        # set length
        wordqty_n=qty-1
        self.barrayTX[self.txbarrayindex] = self.llength_cmd          ; self.txbarrayindex += 1
        self.barrayTX[self.txbarrayindex] = np.uint8(wordqty_n&0xff)  ; self.txbarrayindex += 1
        self.barrayTX[self.txbarrayindex] = np.uint8(wordqty_n>>8)    ; self.txbarrayindex += 1
        #getbuf
        self.barrayTX[self.txbarrayindex] = np.uint8(self.rdbuf_cmd) ;  self.txbarrayindex += 1
        self.barrayTX[self.txbarrayindex] = np.uint8(self.pktend_cmd);  self.txbarrayindex += 1


    def getb(self,adr,qty):  # TODO  gets Buffer by it's address and qty of 16bit addresses
        # set pointer

        self.getb_rq(adr,qty)
        if (self.ftsend()):
            self.getbytescntRX=qty<<1
            self.ftget()
            return self.ok
        else:
            self.getbytescntRX = 0
            self.txbarrayindex = 0
            return self.notConnected




    def setFIFOread(self):  # T
        self.rRemainCyclesCNT[1]=np.uint16(0x8000)
        self.addWrReg(self.rRemainCyclesCNT[0],self.rRemainCyclesCNT[1]) # adding remain cycles =0 (just 1 cycle)
        #getbuf
        self.barrayTX[self.txbarrayindex] = np.uint8(self.getfifo_cmd) ;  self.txbarrayindex += 1   # adding get Fifo  cmd
        self.barrayTX[self.txbarrayindex] = np.uint8(self.pktend_cmd);    self.txbarrayindex+=1  # adding get Fifo  cmd
        # set pointer

    def setFifoPointernLength(self):
        self.barrayTX[self.txbarrayindex] = self.lpointer_cmd ; self.txbarrayindex += 1
        self.barrayTX[self.txbarrayindex] = np.uint8(self.FIFO_Adr&0xff)        ; self.txbarrayindex += 1
        self.barrayTX[self.txbarrayindex] = np.uint8(self.FIFO_Adr>>8)          ; self.txbarrayindex += 1
        # set length
        wordqty_n=np.uint16(self.TotalWords16ToGet-1)
        self.barrayTX[self.txbarrayindex] = self.llength_cmd  ; self.txbarrayindex += 1
        self.barrayTX[self.txbarrayindex] = np.uint8(wordqty_n&0xff)  ; self.txbarrayindex += 1
        self.barrayTX[self.txbarrayindex] = np.uint8(wordqty_n>>8)    ; self.txbarrayindex += 1
        return (self.ftsend())
        # send and get

##############################
    def getFIFOData(self,TWordsToget,wchank_W):  #  TWordsToget
        # Implements sequence of
        # Set FIFOaddress
        # Set REMEIN counter into 0x8000
        # Sets loop getting by 256 words
        # implementing

        #set FIFO adr
        #print("TWordsToget=",TWordsToget)
        #set rRemainCyclesCNT cmd

        self.rRemainCyclesCNT[1]=np.uint16(0x8000)
        self.addWrReg(self.rRemainCyclesCNT[0],self.rRemainCyclesCNT[1])  # adding remain cycles =0 (just 1 cycle)
        self.getbytescntRX=(int(TWordsToget))<<1

#        print("TotalBytesToget=",self.getbytescnt)
#        print("TWordsToget=",TWordsToget)

        remainwords=np.uint16(TWordsToget)
        while remainwords > wchank_W :
            self.getchunk(wchank_W)
            remainwords -= wchank_W
        self.getchunk(remainwords)
        return (self.ftsendget())


#########################################################################
        ##############################
    def addSetPointerADR(self):
        self.barrayTX[self.txbarrayindex]=self.lpointer_cmd; self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex]=np.uint8(self.FIFO_Adr&0xff); self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex]=np.uint8(self.FIFO_Adr>>8); self.txbarrayindex+=1
        self.ftsend()

    def getFIFOreq(self,TotalWordsToget,frames):
        # Implements sequence of
        # Set FIFOaddress
        # Set REMEIN counter into 0x8000
        # Sets loop getting by 256 words
        # implementing
        # set FIFO adr

        self.rRemainCyclesCNT[1]=self.rRemainCyclesCNTMODE + frames - np.uint16(1)
        self.addWrReg(self.rRemainCyclesCNT[0],self.rRemainCyclesCNT[1])  # adding remain cycles =0 (just 1 cycle)
        qtya=np.uint16(TotalWordsToget-1)
        self.barrayTX[self.txbarrayindex]=self.llength_cmd;      self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex]=np.uint8(qtya&0xff);   self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex]=np.uint8(qtya>>8);     self.txbarrayindex+=1
        i=0;
        for i in  range(frames):
            self.barrayTX[self.txbarrayindex]= np.uint8(self.getfifo_cmd); self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex]    = np.uint8(self.pktend_cmd);  self.txbarrayindex+=1
        return (self.ftsend())

#########################################################################
    def sc_getFIFOreq(self,TWordsToget,frames):
        # Load Pointer
        self.barrayTX[self.txbarrayindex]=self.lpointer_cmd;            self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex]=np.uint8(self.FIFO_Adr&0xff); self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex]=np.uint8(self.FIFO_Adr>>8);   self.txbarrayindex+=1
        # Load Length
        # TWordsToget should be less than 65536 (16bit counter)
        qtya=np.uint16((TWordsToget-1)  & 0xFFFF)  # this will go into
        self.barrayTX[self.txbarrayindex]=self.llength_cmd;      self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex]=np.uint8(qtya&0xff);   self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex]=np.uint8(qtya>>8);     self.txbarrayindex+=1
        # Load LengthH
        qtyb=np.uint16(( (TWordsToget-1)) >> 16)
        self.barrayTX[self.txbarrayindex] = self.llengthH_cmd;     self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex] = np.uint8(qtyb&0xff);   self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex] = np.uint8(qtyb>>8);     self.txbarrayindex+=1

        # Load getfifo_cmd as many frames as many we read but limit it with FT232FIFO
        # each getfifo_cmd reads 1 frame only
        # Load remain register
        self.addWrReg(self.rRemainCyclesCNT[0],self.rRemainCyclesCNT[1])  # adding remain cycles (if =0 (just 1 cycle)

        i=0
        for i in  range(frames):
            # each getfifo_cmd gets the number of 16bit words pointed in length register (up to 65536 words
            self.barrayTX[self.txbarrayindex]=np.uint8(self.getfifo_cmd); self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex] = np.uint8(self.pktend_cmd);  self.txbarrayindex+=1
        return

    #############################################################
    def ftgetNbytesMframes(self,TWordsToget,frames):  # gets N bytes
        if self.ft232h_connected:
            NBYTESTOGET = (np.uint32(TWordsToget) << 1)
            for i in range(frames):
                P = NBYTESTOGET + self.nextByteBufferWritePointer
                # read a frame at a time
                self.barrayRXA[self.nextByteBufferWritePointer: P] = self.ft232h.read(int(NBYTESTOGET))
                #TODO Enter converting into float here . Number of samples in onr read = self.SamplesInFrame
                ##############
                self.nextCycleToPlotStart = self.nextCycleToRead*(self.SamplesInFrame<<2) # offset in words
                    #self.DataReadyFlag=True
                self.nextCycleToRead = (self.nextCycleToRead+1)%self.NcyclesinBuffer
                self.nextByteBufferWritePointer =self.nextCycleToRead*self.CycleBytes
                self.getbytescntRX=0

                if (i < frames-1):
                    self.unformatFramenCalcFiltersOnly()

            # TODO  - add processing unformat here
            self.unformatFramenCalcFiltersnPLotVars() # unformat only last frame
            return True
        else:
            self.getbytescntRX=0
            return False


#####################################################################################
#####################################################################################
# P_R_O_C_E_S_S_I_N_G  T_H_E D_A_T_A, P_R_E_P_A_R_E T_H_E_M F_O_R P_L_O_T_T_I_N_G  ##
#####################################################################################
    def unformatFramenCalcFiltersnPLotVars(self): #   unformat , prepare data, prepare plot
        P = self.nextCycleToPlotStart
        for i in range(self.SamplesInFrame):
            self.unformatSample(P)
            self.PreparePlotFilterData(i)
            self.AddOFFSETnMultGain(i)
            P+=4

    def unformatFramenCalcFiltersOnly(self): #   unformat , prepare data, prepare plot
        P = self.nextCycleToPlotStart
        for i in range(self.SamplesInFrame):
            self.unformatSample(P)
            self.PreparePlotFilterData(i)
            P+=4


    def unformatFrameOnly(self,startingword,samplesinframe): #
        '''
        startingword -starting offset in words,
        startingword - number of samples in Frame
        '''
        P = startingword
        for i in range(samplesinframe):
            self.unformatSample(P)
            P+=4

    def unformatFrame2(self,startingword,samplesinframe): #
        '''
        startingword -starting offset in words,
        startingword - number of samples in Frame
        '''
        P = startingword
        for i in range(samplesinframe):
            self.unformatSample(P)
            ###################
            self.PreparePlotFilterData(i)
            P+=4

    def AddOFFSETnMultGain(self, i):        # scaling samples, variance shouldn't be scaled
        for y in range(4):
            self.i32arrayRXV[y,i] = self.msOffset[y] + (self.msGain[y] * self.i32arrayRXV_EST[y,i])
        if (self.plotmode4or6) :
            self.i32arrayRXV[4,i] = self.msOffset[4] + (self.msGain[4] * (self.i32arrayRXV_EST[0,i] + self.i32arrayRXV_EST[3,i]))
            self.i32arrayRXV[5,i] = self.msOffset[5] + (self.msGain[5] * (self.i32arrayRXV_EST[0,i] - self.i32arrayRXV_EST[3,i]))
        else:
            self.i32arrayRXV[4,i] = self.msOffset[4] + (self.msGain[4] * self.i32arrayRXV_EST[4,i])
            self.i32arrayRXV[5,i] = self.msOffset[5] + (self.msGain[5] * self.i32arrayRXV_EST[5,i])

    def unformatSample(self,P):
        self.anpu32=np.uint32(0x000FFFFF) & (self.i32arrayRX[P])
        if (self.anpu32 & 0x00080000):  self.mscurrent[0] =  float(np.int32(self.anpu32|np.uint32(0xFFF00000)))
        else:                           self.mscurrent[0] = float(np.int32(self.anpu32))

        self.anpu32=np.uint32(0x000FFFFF) & np.uint32(self.i32arrayRX[P+1])
        if (self.anpu32 & 0x00080000):  self.mscurrent[1] = float(np.int32(self.anpu32|np.uint32(0xFFF00000)))
        else:                           self.mscurrent[1] = float(np.int32(self.anpu32))

        self.anpu32=np.uint32(0x000FFFFF) & np.uint32(self.i32arrayRX[P+2])
        if (self.anpu32 & 0x00080000):  self.mscurrent[2] = float(np.int32(self.anpu32|np.uint32(0xFFF00000)))
        else:                           self.mscurrent[2] = float(np.int32(self.anpu32))

        self.anpu32=np.uint32(0x000FFFFF) & np.uint32(self.i32arrayRX[P+3])
        if (self.anpu32 & 0x00080000):  self.mscurrent[3] = float(np.int32(self.anpu32|np.uint32(0xFFF00000)))
        else:                           self.mscurrent[3] = float(np.int32(self.anpu32))
        #Powersignals
        self.anpu32=((0xFFF00000 &  (self.i32arrayRX[P]))>>20)|(0x0FF00000&(self.i32arrayRX[P+1]))>>8
        if (self.anpu32 & 0x00080000):  self.mscurrent[4] = float(np.int32(self.anpu32|np.uint32(0xFFF00000)))
        else:                           self.mscurrent[4] = float(np.int32(self.anpu32))

        self.anpu32=((0xFFF00000 & (self.i32arrayRX[P+2]))>>20)|(0x0FF00000&(self.i32arrayRX[P+3]))>>8
        if (self.anpu32 & 0x00080000):    self.mscurrent[5] = float(np.int32(self.anpu32|np.uint32(0xFFF00000)))
        else:                             self.mscurrent[5] = float(np.int32(self.anpu32))

        self.mscurrent = self.mscurrent * self.ADCLSBmvminus


    def PreparePlotFilterData(self,i):
        for j in range(6):
            self.msError [j] = self.mscurrent[j] - self.i32arrayRXV_EST[j,i]
            self.i32arrayRXV_EST[j,i] = self.i32arrayRXV_EST[j,i] + (self.Kalpha * (self.msError [j]))

            self.msErrorsqr[j] = self.msError[j] * self.msError[j]
            self.i32arrayRXV_msqr[j,i] = self.i32arrayRXV_msqr[j,i] + (self.Kalpha * (self.msErrorsqr[j] - self.i32arrayRXV_msqr[j,i]) ) # scaled to V*V

######    E_N_D   O_F   D_A_T_A   P_R_O_C_E_S_S_I_N_G             ##
####################################################################
####################################################################
####################################################################

    #def ftgetN(self,N):  # gets N bytes
    #    if self.ft232h_connected:
    #        P= N + self.nextByteBufferWritePointer
    #        self.barrayRXA[self.nextByteBufferWritePointer: P] = self.ft232h.read(int(N))
    #
    #        self.nextCycleToPlotStart =self.nextCycleToRead*(self.SamplesInFrame<<2) # offset in words
    #        self.nextCycleToRead   =(self.nextCycleToRead+1)%self.NcyclesinBuffer
    #        self.nextByteBufferWritePointer =self.nextCycleToRead*self.CycleBytes
    #
    #        #print("The value is : {:d}".format(self.ft232h.getQueueStatus() ) )
    #        self.getbytescntRX=0
    #
    #        return True
    #    else:
    #        self.getbytescntRX=0
    #        return False
#
#    def savelastparams(self):
#        self.Recordtail=self.nextCycleToRead # numerated frame pointing to the most old data
#        self.lastCyclesinBuffer=self.NcyclesinBuffer
#        self.lastSamplesInCycle=self.SamplesInCycle

#############################################################

    def sc_pktend(self): self.barrayTX[self.txbarrayindex]=np.uint8(self.pktend_cmd); self.txbarrayindex+=1

    #        self.barrayTX[self.txbarrayindex]=np.uint8(self.nop_cmd); self.txbarrayindex+=1

    def getFIFOreq2(self,TWordsToget,frames):
        # Implements sequence of
        # Set FIFOaddress
        # Set REMEIN counter into 0x8000
        # Sets loop getting by 256 words
        # implementing
        # set FIFO adr

        self.rRemainCyclesCNT[1]=np.uint16(0x8000)
        self.addWrReg(self.rRemainCyclesCNT[0],self.rRemainCyclesCNT[1])  # adding remain cycles =0 (just 1 cycle)
        qtya=np.uint16(TWordsToget-1)
        self.barrayTX[self.txbarrayindex]=self.llength_cmd;      self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex]=np.uint8(qtya&0xff);   self.txbarrayindex+=1
        self.barrayTX[self.txbarrayindex]=np.uint8(qtya>>8);     self.txbarrayindex+=1

        self.getchunk(1)
        #self.ft232h.purge(3) # TX
#        return (self.ftsendget())
        return (self.ftsend())
#########################################################################

    def getchunk(self,n):  # qty is a word number
        for i in  range(n):
            self.barrayTX[self.txbarrayindex]=np.uint8(self.getfifo_cmd); self.txbarrayindex+=1
            self.barrayTX[self.txbarrayindex]=np.uint8(self.pktend_cmd); self.txbarrayindex+=1

    def stopInf(self):
        self.rRemainCyclesCNT[1]=np.uint16(0x0000)
        self.addWrReg(self.rRemainCyclesCNT[0],self.rRemainCyclesCNT[1])  # adding remain cycles =0 (just 1 cycle)
        return (self.ftsend())

#   self.barrayTX[self.txbarrayindex]=np.uint8(self.nop_cmd); self.txbarrayindex+=1


    #########################################################################
    def RunCycles(self,cycles):
        self.rRemainCyclesCNT[1] = np.uint16(cycles) - np.uint16(1)
        self.addWrReg(self.rRemainCyclesCNT[0], self.rRemainCyclesCNT[1])  # 11:0 remain bit 16 should bi 0 to load, this trigger start
        if (self.ftsend()) :  return self.ok
        else: return self.notConnected

    def getFPGAversion(self):
        self.FPGAVersion=self.getshortcmd(self.ver_cmd)
        return self.FPGAVersion

# self.listHistory.addItem(str('{:04x}{:04x}'.format(self.parser.ADC0MD[1],self.parser.ADC0LD[1])))

    def getshortcmd(self, cmd):
        #print(str("{:04x}".format(cmd)))
        r_value=np.uint16(0)
        if self.ft232h_connected:
            self.txbarrayindex = 0
            self.barrayTX[self.txbarrayindex] = cmd
            self.txbarrayindex = 1
            self.ftsend()
            self.getbytescntRX = 2
            self.ftget()
            r_value =np.uint16(self.barrayRX[0])+(np.uint16(self.barrayRX[1])<<8)
            self.enableResultShow = True
        return r_value

    def rd_reg(self,adr):
        self.barrayTX[0]=adr
        if self.ft232h_connected:
            s=bytes(self.barrayTX[:1])
            self.ft232h.write(s)
            self.barrayRX[:2]=self.ft232h.read(2)
            return (np.uint16(self.barrayRX[0]) << 8) + np.uint16(self.barrayRX[0])

    def wr_reg(self,adr,data):
        self.barrayTX[0] = self.wr_cmd | adr
        self.barrayTX[1] = np.uint8(data&0xFF)
        self.barrayTX[2] = np.uint8(data>>8)
        if self.ft232h_connected:
            s=bytes(self.barrayTX[:3])
            self.ft232h.write(s)
            return True
        else:
            return False

    #########################################################################
    def ftsend(self):
        if self.ft232h_connected:
            s = bytes(self.barrayTX[:self.txbarrayindex])
            self.ft232h.write(s)
            self.txbarrayindex = 0
            return True
        else:
            self.txbarrayindex = 0
            return False
    # gets reads by buffer sequence

    def getTECbuffer(self):
        ''' Gets TECbuffer in accordance to TEC_TERMO_BUF_Blength'''
        self.getbytescntRX = self.TEC_TERMO_BUF_Blength # sets number of bytes to get by next ftget()
        self.ftget()

    def ftget(self):
        if self.ft232h_connected:
            self.barrayRX[0:self.getbytescntRX] = self.ft232h.read(int(self.getbytescntRX))
            #print("The value is : {:d}".format(self.ft232h.getQueueStatus() ) )
            self.getbytescntRX = 0
            return True
        else:
            self.getbytescntRX = 0
            return False

#    def ftgetCount(self,count):
#        if self.ft232h_connected:
#            self.barrayRXA[:count] = self.ft232h.read(count)
#            return True
#        else:
#            return False

#    def reReadfifo(self):
#        if self.ft232h_connected:
#            self.ft232h.write(bytes(self.barrayRX[:4]))
#            return True
#        else:
#            return False

#    def test(self,adr,value):
#        if (self.wr_reg(adr,value)):
#           return self.rd_reg(adr,value)

#    def test1(self,adr,value):
#        if (self.wr_reg(adr,value)):
#           return self.rd_reg(adr,value)
################################################################
    def closeUSB(self):
        if (self.ft232h_connected):
            self.ft232h.purge(3)
            self.ft232h.close()

# FT_STATUS FT_SetBitmode (FT_HANDLE ftHandle, UCHAR ucMask, UCHAR ucMode)
# ftHandle Handle of the device.
# ucMask Required value for bit mode mask. This sets up which bits are inputs and outputs.
# A bit value of 0 sets the corresponding pin to an input, a bit value of 1 sets
# the corresponding pin to an output.
#
# In the case of CBUS Bit Bang, the upper nibble of this value controls which pins are
# inputs and outputs, while the lower nibble controls which of the outputs are high and low.
# ucMode Mode value. Can be one of the following:
# 0x0 = Reset
# 0x1 = Asynchronous Bit Bang
# 0x2 = MPSSE (FT2232, FT2232H, FT4232H and FT232H devices only)
# 0x4 = Synchronous Bit Bang (FT232R, FT245R, FT2232, FT2232H, FT4232H and FT232H devices only)
# 0x8 = MCU Host Bus Emulation Mode (FT2232, FT2232H, FT4232H and FT232H devices only)
# 0x10 = Fast Opto-Isolated Serial Mode (FT2232, FT2232H, FT4232H and FT232H devices only)
# 0x20 = CBUS Bit Bang Mode (FT232R and FT232H devices only)
# 0x40 = Single Channel Synchronous 245 FIFO Mode (FT2232H and FT232H devices only)
    def connectUSB(self):
        if self.ft232h_connected:
            self.ft232h.setBitMode(0x0, 0x00)  # Reset pins to default mode  Set pin as output, and async bit bang mode
            self.ft232h.close()
            self.ft232h_connected = False
            return 0
        else:
            try:
                #               print(ftd.listDevices())
                #                self.ft232h = ftd.open()
                #               self.ft232h = ftd.openEx(b'USB <-> Serial Converter', ftd.ftd2xx.OPEN_BY_DESCRIPTION)
               #  self.ft232h = ftd.openEx(b'ROCKLEY', ftd.OPEN_BY_DESCRIPTION)
                self.ft232h = ftd.openEx(b'ROCKLEY', ftd.ftd2xx.OPEN_BY_DESCRIPTION)
            except:
                self.ft232h_connected = False
                return 2
            else:

                self.ft232h_connected = True
                self.ft232h.purge(3)
                #print("Latency=",self.ft232h.getLatencyTimer())
                #self.ft232h.setLatencyTimer(np.uint8(2))
                #                self.ft232h.resetDevice()
                #self.ft232h.purge(3)
                self.ft232h.setTimeouts(2000,2000)
                #self.ResetFpga()
                # self.ft232h.setBitMode(0x0, 0x40)  # 0x40 FT245SYNC MODE
                # self.ft232h.setBitMode(0xFF, 0x01)  # 0x1  Asynchronous Bit Bang
                # self.ft232h.setBitMode(0x0, 0x20)  # 0x20 = CBUS Bit Bang Mode (FT232R and FT232H devices only)
                # self.BRDSERIAL= int (  self.ft232h.getDeviceInfo()['serial'].decode("utf-8") )
                return 1



    def connectFPGA(self):
        self.ResetFpga()
        self.FPGAVersion = self.getshortcmd(self.ver_cmd)
        self.FPGAVer = (self.FPGAVersion >> 4) & 0xf
        self.FPGARev = (self.FPGAVersion ) & 0xf
        if self.FPGAVer == 7:
            self.LASER_LUT_Adr = np.uint16(0xA000)
            self.TEC_TERMO_BUF_Wlength = 10
            self.TEC_TERMO_BUF_Blength =self.TEC_TERMO_BUF_Wlength*2
            self.LUTMAX=2048
            self.slotparams0 =4
            self.slotparams1 =0
        elif self.FPGAVer == 6:
            self.LASER_LUT_Adr = np.uint16(0x8800)
            self.TEC_TERMO_BUF_Wlength = 10
            self.TEC_TERMO_BUF_Blength =self.TEC_TERMO_BUF_Wlength*2
            self.LUTMAX = 256
            self.slotparams0 =4
            self.slotparams1 =0
        elif self.FPGAVer == 8:
            self.LASER_LUT_Adr     = np.uint16(0x0000)  # main LUT adresss
            self.LASER_LUT2_Adr    = np.uint16(0x8000)  # small LUT address
            self.DDSPAGE_ADD       = np.uint16(0xEF00)
            self.FIFO_Adr          = np.uint16(0xFF00)
            self.TEC_TERMO_BUF_Adr = np.uint16(0xFE00)
            self.TEC_TERMO_BUF_Wlength = 12
            self.TEC_TERMO_BUF_Blength =self.TEC_TERMO_BUF_Wlength*2
            self.LUTMAX=1024
            self.slotparams0 =16
            self.slotparams1 =4

        else:
            return 0
        return 1
    # ------------------------------------------------------

    def getTTECSTATUS(self):
        self.wr_reg(self.rTECT_CNT[0],self.EFM_CMD_GETVERSION)
        time.sleep(.1)
        self.TTEC_GETDATA(10)
        for x in range(0,20):
            self.uCUDATA_STATEX8[x]=self.barrayRX[x]
    # ------------------------------------------------------

    def SetBingBangMode(self):
        if self.ft232h_connected:
            self.ft232h.setBitMode(0xFF, 0x01)  # Set bit  ACBUS8,ACBUS9 to 00
            time.sleep(.1)
    # ------------------------------------------------------

    def ResetFpga(self):
        '''
        Toggling ACBUS 9 down and up to reset FPGA
        '''
        if self.ft232h_connected:
            self.ft232h.setBitMode(0xF0, 0x20)  # Set bit  ACBUS9, ACBUS8 to 00
            self.ft232h.setBitMode(0xF8, 0x20)  # Set bit  ACBUS9, ACBUS8 to 10
            time.sleep(.001)
            self.ft232h.setBitMode(0x0,  0x40)   # return to main mode
            self.ft232h.purge(3)
            time.sleep(.001)
        return self.ft232h_connected
    # ------------------------------------------------------

    def setACS98(self, ACS98_00):  # sets bit ACS9andACS8 for FTDI FT232H
        self.ft232h.setBitMode(np.uint8(ACS98_00), 0x20)
        self.ft232h.setBitMode(0x0, 0x40)  # return to main mode
    # ------------------------------------------------------
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
######################################################################
    def V2_SN74HCS594_set (self):
        '''
        Sets bits of SN74HCS594ControlByte
        '''
        currentbit = np.uint8(self.SN74HCS594ControlByte)
        for i in range(8):
            if (currentbit & 0x80) :  # Shift bit is 1
                self.ft232h.setBitMode(0xF4, 0x20)  # Set Data bit to 1, clock to 0
                self.ft232h.setBitMode(0xFC, 0x20)  # Set Data bit to 1 clock to 1

            else:
                self.ft232h.setBitMode(0xF0, 0x20)  # Set Data bit to 0 clock to 0
                self.ft232h.setBitMode(0xF8, 0x20)  # Set Data bit to 0 clock to 1
            currentbit = currentbit << 1
        time.sleep(.02)
        return
    # ------------------------------------------------------
    def V2_resetFPGA(self):
        self.SN74HCS594ControlByte = self.SN74HCS594ControlByte & np.uint8(0xF7)
        self.V2_SN74HCS594_set()
        self.SN74HCS594ControlByte = self.SN74HCS594ControlByte | np.uint8(0x08)
        self.V2_SN74HCS594_set()
    # ------------------------------------------------------
    def V2_SN74HCS594_LED_OnTrue_OffFalse(self,OnOff):
        '''
        OnOff = "True" turns LED ON
        OnOff = "True" turns LED OFF
        '''
        if (OnOff) :
            self.SN74HCS594ControlByte = self.SN74HCS594ControlByte | np.uint8(0x80)
        else:
            self.SN74HCS594ControlByte = self.SN74HCS594ControlByte & np.uint8(0x7F)
        self.V2_SN74HCS594_set()
    # ------------------------------------------------------
    def V2_ReloadFromFlash(self):
        '''Reloads  FPGA from Flash '''
        # Set bits State[1:0] into 00, Program_B0 into 1,Soft RST into 1, M1_2_0 into 0,SPARE sinto 00, LED into ON
        self.SN74HCS594ControlByte = 0x8C # 10001100
        self.V2_SN74HCS594_set()
        # Now toggle Program_B0
        self.SN74HCS594ControlByte = 0x88 # 10001100
        self.V2_SN74HCS594_set()
        self.SN74HCS594ControlByte = 0x8C # 10001100
        self.V2_SN74HCS594_set()
        time.sleep(.5)
        # set FT245 ASSYNC MODE
        self.ft232h.setBitMode(0x0,  0x40)   # return to main mode
    # ------------------------------------------------------

    ###################################################################################################
    #def SendBingBangMode(self):
    #    self.txbarrayindex=0;
    #    self.barrayTX[self.txbarrayindex] = np.uint8(0x00);    self.txbarrayindex += 1
    #    self.barrayTX[self.txbarrayindex] = np.uint8(0x01);    self.txbarrayindex += 1
    #    self.barrayTX[self.txbarrayindex] = np.uint8(0x02);    self.txbarrayindex += 1
    #    self.barrayTX[self.txbarrayindex] = np.uint8(0x03);    self.txbarrayindex += 1
    #    self.barrayTX[self.txbarrayindex] = np.uint8(0x04);    self.txbarrayindex += 1
    #    self.barrayTX[self.txbarrayindex] = np.uint8(0x05);    self.txbarrayindex += 1
    #    self.barrayTX[self.txbarrayindex] = np.uint8(0x06);    self.txbarrayindex += 1
    #    self.barrayTX[self.txbarrayindex] = np.uint8(0x07);    self.txbarrayindex += 1
    #    self.ftsend()
    #    return





    #   need to be deleted
    #def getAllRegisters1(self):
    #    self.barrayTX[self.txbarrayindex]=self.ver_cmd;       self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.gmask_cmd;     self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.gpointer_cmd;  self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.glength_cmd;   self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.gcnt_cmd;      self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.gtimer_cmd;    self.txbarrayindex+=1  ; self.getbytescntRX+=2#
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.rSPInSELECT[0]) );      self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.rNumberOfTSlots[0]) );  self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.rRemainCyclesCNT[0]) ); self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.rSample_Period[0]) );   self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.ADC0MD[0]) );        self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.ADC0LD[0]) );        self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.rAD5541TX[0]) );        self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.ADC1MD[0]) );        self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.ADC1LD[0]) );        self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.ADC2MD[0]) );        self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.ADC2LD[0]) );        self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.ADC3MD[0]) );        self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.ADC3LD[0]) );        self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.ADC4MD[0]) );        self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.barrayTX[self.txbarrayindex]=self.rd_cmd|(np.uint8(self.ADC3LD[0]) );        self.txbarrayindex+=1  ; self.getbytescntRX+=2
    #    self.ftsend()
    #    self.ftget()
    #    i=0
    #    self.VER[1]               =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.MASK[1]              =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.BUF_pnt[1]           =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.BUF_lng[1]           =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.CNTreg[1]            =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.TIMER[1]             =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.rAD5541TX[1]         =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.rSPInSELECT[1]       =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.rTECT_CNT[1]         =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.rNumberOfTSlots[1]   =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.rRemainCyclesCNT[1]  =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.rSample_Period[1]    =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.ADC0MD[1]            =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.ADC0LD[1]            =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.ADC1MD[1]            =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.ADC1LD[1]            =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.ADC2MD[1]            =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.ADC2LD[1]            =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.ADC3MD[1]            =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.ADC3LD[1]            =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.ADC4MD[1]            =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    self.ADC4LD[1]            =np.uint16(self.barrayRXA[i])+(np.uint16(self.barrayRXA[i+1])<<8)  ; i +=2
    #    return

    #########################################################################
