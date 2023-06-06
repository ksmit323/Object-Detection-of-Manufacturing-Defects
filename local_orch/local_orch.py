# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 13:52 2023

@author: Hai Vu
"""

# ------------------------------------------------------#
#    This Orchestrator is intended for PLCNNET         #
#       It Function is to Read PLC Tags and            #  
#         Update the Inspection.txt files              #
#                                                      # 
# ------------------------------------------------------#

from ntpath import expanduser
from re import S
import subprocess
from pickle import APPEND
import sys
import os
import time
import cv2
from pyModbusTCP.client import ModbusClient

# subprocess.Popen(['python3', '/home/nvidia/PolarisNNet/polarisnnet.py'])
# TCP auto connect on first modbus request
# # File Location Paths

# Read PLC Tags Return Values
def main():
    try:
        # Initial Step
        global path
        global pathLogs       
        global callnn
        callnn = False        
        path = str('/home/nvidia/PolarisNNet/') 
        pathObj = str('/home/nvidia/local_orch/')
        pathLogs = '/home/nvidia/LOGS/'
        print("Starting PLCNNET Orchestrator")
        print(get_realtime())
        NullInspString = "NULL|NULL|NULL"
        Cam_1_Null = NullInspString
        TimeString = None
        process =None
        writeInsCam1(Cam_1_Null, TimeString,0)
        Current_Cam_1_Insp = Cam_1_Null
        Insp_Cam_1 = "NULL|NULL|NULL"
        lastBikeModel = None
        # ModelIndex, VIN, Insp_Complete, FullRead, PPEnable, StIndex , heartbeat, Cam_select = ['N23NTC00PC'],['RLTNTC004P6002670'],['0'],['1'],['1'],60,['1'],['0']

        while True:
            
            clear() 
            # Get the Model, VIN, Inspection Status, Full read, PPEnable and Station Index from PLC
            ModelIndex, VIN, Insp_Complete, FullRead, PPEnable, StIndex , heartbeat, Cam_select = callPLC()
            # Get Objects depend on model running on station
            ModelIndex =  str(ModelIndex) 
            thisBikeModel = ModelIndex[3]
            # This for select File to run NN
            configfile, weightsfile, classesclasses , InsSeqFile = fileSelect(thisBikeModel)
            if thisBikeModel != lastBikeModel:
                
            # if callnn == False:
            # if station is on inspection, call the Neural Network Program once
            #this callnn var for call NN once 
                callnn = True
                process.terminate()
                print("")
                print("!! Waiting Call Neural Network!!")
                print("")                
                process = subprocess.Popen(['python3', '/home/nvidia/PolarisNNet/demo.py' ,'--ca', str(Cam_select),\
                                            '--config', str(configfile), '--w', str(weightsfile),'--cl',str(classesclasses)])
                print("!!!CALLLLLLLLLLLLLLLLLLL NEURALLLLLLL NETWORKKKKKKKKK?!!!!!")
                time.sleep(2)
                lastBikeModel = thisBikeModel
            TimeString = get_realtime()
            
            # this one to get list object from VINtoObj.txt File
            filename = pathObj + "VINtoObjs.txt"

            


            Model, Object = read_model_ins(filename, ModelIndex, InsSeqFile,PPEnable)
  
            if StIndex == 60 and VIN != "NULL":                         
                Insp_Cam_1 = "NULL|NULL|NULL"
                # Once PP enables the Inspection send Object List To NN,  For each Camera check if using static objects,
                # else send PLC Obj list.  Make sure PLC list is not empty - Fill with "NULL" value
                if Insp_Complete != 1:
                    if Object[0] == "NULL":
                        Insp_Cam_1 = (VIN + "|" + Model + "|" + "NULL")
                        # callnn = False
                    else:
                        Insp_Cam_1 = str(VIN) + "|"+ str(Model) + "|"
                        for ins in Object:
                            Insp_Cam_1 = Insp_Cam_1 + str(ins) + ","
                        Insp_Cam_1 = Insp_Cam_1[:-1]
                    print("Station Status    =Waiting for PP Complete")
                    # if callnn == False:
                    # # if station is on inspection, call the Neural Network Program once
                    #     #this callnn var for call NN once 
                    #     callnn = True

                    #     process = subprocess.Popen(['python3', '/home/nvidia/PolarisNNet/demo.py' ,'--ca', str(Cam_select),\
                    #                                 '--config', str(configfile), '--w', str(weightsfile),'--cl',str(classesclasses)])
                    #     print("!!!CALLLLLLLLLLLLLLLLLLL NEURALLLLLLL NETWORKKKKKKKKK?!!!!!")

            elif StIndex < 60:
      
                print("Station Status    =Waiting for Engine")
                Insp_Cam_1 = Cam_1_Null
            elif StIndex == 70 or StIndex == 50:
                callnn = False
                print("Station Status    =Inspection Done!")
                # if station is done, terminate the Neural Network Program
                # if process != None:
                #     callnn = False
                #     process.terminate()
                Insp_Cam_1 = Cam_1_Null

            # Write to Inspection.txt if there is a change to the inspection
            if Insp_Cam_1 != Current_Cam_1_Insp:
                writeInsCam1(Insp_Cam_1, TimeString,Cam_select)
                Current_Cam_1_Insp = Insp_Cam_1
                
            print(" ")
            print("Time              =" + TimeString)
            print("!! Info From Line PLC  !!")
            print("heartbeat          ="+ str(heartbeat))
            print("Camera Select:        = "+ str(Cam_select))
            print("Model Number      =" + str(Model))
            print("Session Complete  =" + str(Insp_Complete))
            print("PLC Read Complete =" + str(FullRead))
            print("PLC StIndex       =" + str(StIndex))
            print("PinPoint Enable   =" + str(PPEnable))
            print("VIN               =" + str(VIN))
            print(f'Current Cam Inspection: {Current_Cam_1_Insp}')
            # Display Status to Shell Window
            # if callnn == False:
            #     print("Call NN   =  False  ")
            # else:
            #     print("Call NN  = True")

            print(" ")
            print("!! Info To PLCNNET Inspection.txt  !!")
            time.sleep(2)
            key = cv2.waitKey(1) & 0xFF
            # if Cam1FileFound == 0:
            #     print("Cam 1 Inspection  =" + str(Insp_Cam_1))
            # break
            

    ########################### UI COMPONENTS WOULD BE BELOW THIS  #######################

    except KeyboardInterrupt:
        print("\nExit")
    except:
        print("Unexpected error:", sys.exc_info()[0])
        print("Error info:", sys.exc_info()[1])
        writeLog("Orchestrator Exception on VIN ")

def get_realtime ():
    Time = time.localtime(time.time())
    TimeString = str(Time[0]) + "-" + str(Time[1]) + "-" + str(Time[2]) + "-" + str(Time[3]) + ":" + str(
                Time[4]) + ":" + str(Time[5])
    return TimeString
# Write Log to File
def writeLog(l):
    lt = time.localtime(time.time())
    lt2 = str(lt[0]) + "-" + str(lt[1]) + "-" + str(lt[2]) + "-" + str(lt[3]) + "." + str(lt[4]) + "." + str(lt[5])
    lg = lt2 + " : " + l
    with open('orch_log.txt', 'a') as logfile:
        logfile.write(lg + "\n")
        print(lg)
    return 0

# Write the inspection result to PLC
def write_to_PLC(result):

    c = ModbusClient(host="10.191.96.40", port=502, unit_id=1, auto_open=True)
    c.open()
    c.write_single_register(3, result)
    # print('Da write vao PLC')
    print(c.read_holding_registers(5, 1))

# Read the inspection Result, if done >> Pass
def read_ins_res():
    with open(path + 'InspectionResults.txt', 'r') as file:
        Ins_result = file.read()
        print(Ins_result)
    return Ins_result

# Connect to PLC Siemens, get the infomation from PLC
def callPLC():
    print("Call PLC!!!!")
    c = ModbusClient(host="10.191.96.40", port=502, unit_id=1, auto_open=True)
    status = c.open()
    print(f'Connection Status: {status}')
    # print(c.open())
    VIN = ""
    Model_fromPLC = ''
    
    try:
        # Write Value 1 to PLC, PLC will read that and reset to 0. After 10s PLC cannot get the Value 1 from
        # NN, turn on the Andon Yellow Alarm
        
        heartbeat =  c.write_single_register(2, 1)
        print("Written heartbeat")
        # When going in the step to check object, Pinpoint send value from PLC >> NN , the Number will
        # define what inspection we will get on that step!
        PP_Enable = c.read_holding_register(4,1)
        print("PinPoint Enable   =" + str(PP_Enable))
        # PP_Enable = int(c.read_holding_registers(4, 1)[0])
        PP_Enable = int(PP_Enable[0])
        if PPEnable == 0:
            PPEnable = 255
        print("PinPoint Enable   =" + str(PP_Enable))
        # Station Index
        '''
        Tag	Definition	Description
        0	Station Empty	
        50	Inspection failed	
        60	Wait for PinPoint to Complete	
        70	Inspection Done: Return to 60 when have another Inspection
        100	Station Complete	
        '''
        try:
            St_Index = int(c.read_holding_registers(3, 1)[0])
        
        except:
            St_Index = int(255)

        # Read Camera to perform from PLC
        '''
        0: Camera 1
        4: Camera 2
        ....
        24: Camera 7 
        '''
        Cam_select = int(c.read_holding_registers(2,1)[0])
        # When the Inspection Completed, get the value 1
        InspComplete = int(c.read_holding_registers(5, 1)[0])


        '''
        # This one for old version
        # Ins = c.read_holding_registers(6, 1)
        # Inspection_select = decimal_to_binary(int(Ins[0]))
        '''
        # Read model number from PLC, convert from list of int >> String
        ModelPLC = c.read_holding_registers(10, 10)  
        Model_fromPLC = ""
        # If no Bike in station, the will be an array of ascii 32 in here, so we need this code to delete the error code
        if ModelPLC == ([32] * 10):
            Model_fromPLC = "NULL"
        else:
            for number in ModelPLC:
                char = chr(number)
                Model_fromPLC = Model_fromPLC + char

        # Read VIN number from PLC, convert from list of int >> String        
        VINint = c.read_holding_registers(20, 17)
        VIN = ""
        # If no Bike in station, the will be an array of ascii 32 in here, so we need this code to delete the error code
        if VINint == ([32] * 17):
            VIN = "NULL"
        else:
            for number2 in VINint:
                char2 = chr(number2)
                VIN = VIN + char2

        # Reading the Inspction Result.
        Ins_result = read_ins_res()
        # print(f'Thís is inspection Results : {Ins_result}')
        with open(path + 'InspectionResults.txt', 'w') as file:
            # print("Read Inspection results file")
            if Ins_result == 'Inspection Done':
                c.write_single_register(5, 1)
                file.write('None')
                callnn = False
            elif Ins_result == 'Inspection Failed':
                c.write_single_registr(5, 50)
                file.write('None')
                callnn = False
            else:
                print("Chua hoan thanh")

        Full_Read = 1   
        return Model_fromPLC, VIN, InspComplete, Full_Read, PP_Enable, St_Index, heartbeat, Cam_select

    except:      
        print("!!Something trouble with the connection between PLC-PC!!")
        time.sleep(2)
        quit()
    

    

# --------------------------------------------------------------------------#
# Read model and inspection from File, choose the inspection depend on Inpection Selected from PLC
def read_model_ins(filename, input_string, InsSeqFile,PPEnable):
    # Read the contents of the file and split it into lines


    # print(f'This is PP Enable:    =  {PPEnable}')
    Step = convertPPenable(PPEnable)
    # print(f'This is after convert :   = {Step}')
    with open(InsSeqFile, "r") as f:
        lines = f.read().splitlines()
        print(f'this is fthe line :   ={lines[Step]}')
   
    with open(filename, "r") as f:
        lines2 = f.read().splitlines()
        # print(lines)
    # Initialize the "Model" and "Objects" variables
    Model_fromPLC = None
    Objects_fromPLC = []   
    # Iterate through each line in the file
    for line in lines2:
        # Check if the input string is found in the line
        if input_string in line:
            # Extract the "Model" and "Objects" from the line
            Model_fromPLC, Objects_str = line.split("|")
            Object_list = [s.strip() for s in Objects_str.split(",")]
    try:
        for i, item in enumerate(Object_list):

                if int(lines[Step][i])  == 1:                   
                    Objects_fromPLC.append(item)
    except:
        return Model_fromPLC, Objects_fromPLC

    return Model_fromPLC, Objects_fromPLC

# write Inspection.txt file per Camera
def writeInsCam1(Ins1, Tm,Cam_select):
    try:
        infile = open(path + 'Inspections.txt', 'w')
        infile.write(Ins1)
        infile.close()
        with open(pathLogs + 'Inspection_Cam_1.txt', 'a') as f:
            f.write(Tm + "  " + Ins1 + "\n")
        NoFile = 0
        with open((path + 'Camselect.txt', 'w')) as f:
            f.write(Cam_select)
    except:
        NoFile = 1
    return NoFile

# Read the inspection Result from file>> Done >> release process 
def readInsResults():
    with open(path + 'InspectionResults.txt', 'r') as file:
        Ins_result = file.read()
        print(Ins_result)
    return Ins_result

''' Out of Date Function
# Write heartbeat to PLC to know NN is running
def writeHB():
    try:
        # Code work with Siemens PLC
        c = ModbusClient(host="10.191.96.40", port=502, unit_id=1, auto_open=True)
        hb = c.write_single_register(1, 1)
        hb = c.read_holding_registers(1, 1)
        
    except:
        hb = 100
        writeLog("Failed to Write to hb  ")
    return hb
'''

''' Out of Date Function
# Define a function to convert decimal to binary 
def decimal_to_binary(n):
    output = []
    # print(n)
    # Initialize an empty string to store the binary digits
    binary = ""
    # Loop until n becomes zero
    while n > 0:
        # Get the remainder of n divided by 2 and append it to the binary string
        binary = str(n % 2) + binary
        # Update n by dividing it by 2
        n = n // 2
    # Return the binary string
    # Initialize an empty string to store the reversed string
    # print(binary)
    for i in binary:
        output.append(i)
    output = list(reversed(output))
    return output
'''
def convertPPenable(n):
    # n = int(n[0])
    # Initialize an empty string to store the binary digits
    binary = ""
    reversedlist  = []
    if n ==1:
        output = 1
    else:
    # Loop until n becomes zero
        while n > 0:
            # Get the remainder of n divided by 2 and append it to the binary string
            binary = str(n % 2) + binary
            # Update n by dividing it by 2
            n = n // 2
        for i in binary:
            reversedlist.append(i)
        reversedlist = list(reversed(reversedlist))
        # Return the binary string
        for index,i in enumerate(reversedlist):        
            if int(i) == 1:
                output = index
    # print("Đây là Out Put: " + str(output))
    return output

# Clears shell every pass to display data in a static location
def clear():
    clearscreen = os.system('clear')

# this Function for select which file using depend on Model of Bike    
def fileSelect (bike_model):
    # Read the Bike model 4th digit, if it's "F" (Ascii = 70) , read FTR file, else read 
    if bike_model == "F":
        configfile = '/home/nvidia/PolarisNNet/Goodpackage/1001_Fixcam1_FTR.cfg'  
        weightsfile = '/home/nvidia/PolarisNNet/Goodpackage/1001_Fixcam1_FTR.weights'
        classesclasses = '/home/nvidia/PolarisNNet/Goodpackage/1001_Fixcam1_FTR.names'
        InsSeqFile = "/home/nvidia/PolarisNNet/Goodpackage/1001_Fixcam1_FTR_Inspection_Select.txt"
    else:
        configfile = "/home/nvidia/PolarisNNet/Goodpackage/1001_Fixcam1_SCOUT.cfg"
        weightsfile = "/home/nvidia/PolarisNNet/Goodpackage/1001_Fixcam1_SCOUT.weights"
        classesclasses = "/home/nvidia/PolarisNNet/Goodpackage/1001_Fixcam1_SCOUT.names"
        InsSeqFile  = "/home/nvidia/PolarisNNet/Goodpackage/1001_Fixcam1_SCOUT_Inspection_Select.txt"
    return configfile, weightsfile, classesclasses , InsSeqFile




if __name__ == '__main__':
    main()
    