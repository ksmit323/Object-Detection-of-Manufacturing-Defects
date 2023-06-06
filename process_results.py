# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 07:23:58 2018

@author: JStitt


"""
import sys
import os
import json
import requests
import base64
import datetime
import time

VIN = sys.argv[1]
# print(VIN)
# VIN = "56KMSA002L3155809"
#############################################
configJson = {}
configLocation = '/home/nvidia/polaris/config.json'
#load local config file and convert to JSON
if(os.path.isfile(configLocation) == True):
    configRaw = open(configLocation, "r")
    configJson = json.load(configRaw)
else:
    print("[Error]: issue loading config.json")
    exit()

PLC_IP = configJson["PLC_IP"] #'172.21.10.10'
PLC_SLOT = configJson["PLC_SLOT"]
PLC_TRY = configJson["PLC_TRY"]
INSTALL_ID = configJson["INSTALL_ID"]
LINE = configJson["LINE"]
PLANT = configJson["PLANT"]
IBMI_L = configJson["IBMI_L"]
IBMI_P = configJson["IBMI_P"]
STATION_ID = configJson["STATION_ID"]
#line and zone perhaps

###########################################

path=VIN

def logging(cId,model,state):
    d = datetime.datetime.now()
    dout = d.isoformat()
    call = 'https://prd-qed-session-log.azurewebsites.net/api/CreateSessionLog'
    hdr = ''
    post_url = 'https://prd-qed-session-log.azurewebsites.net/api/CreateSessionLog'
    body = {'Session':cId,'ParentObject':model,'InstallId':INSTALL_ID,'SessionLogDate':dout,'SessionLogType':str(state)}
    try:
        r = requests.post(post_url,data=json.dumps(body), headers=hdr)
        CRI = r.text
        if (r.status_code):
            writeLog("wrote "+cId+" "+str(state)+" "+dout)
            writeLog(json.dumps(body))
        else:
            writeLog("Fail write "+cId+" "+str(state)+" "+dout)
    except:
        writeLog("FAILED TO POST "+cId+" "+str(state)+" "+dout)

    return

def writeLog(l):
    lt = time.localtime(time.time())
    lt2 = str(lt[0])+"-"+str(lt[1])+"-"+str(lt[2])+"-"+str(lt[3])+"."+str(lt[4])+"."+str(lt[5])
    lg = lt2+" : "+l
    with open('/home/nvidia/polaris/process_log.txt','a') as lfile:
        lfile.write(lg+"\n")
    return 0




statfile = 'statfile.txt'

cifile = 'maxCI.txt'

objs = []
ci_s = []
stats = []

try:
    cinfo = os.stat(path+'/'+cifile)
    if cinfo.st_size > 0:
        with open(path+'/'+cifile,"r") as f:
            for line in f:
                fp1 = line.split('\t')
                objs.append(fp1[0].rstrip())
                ci_s.append(fp1[1].rstrip())
    else:
        exit()

    with open(path+'/'+statfile,"r") as f:
        for i, line in enumerate(f):
            sp1 = line.split('|')
            if i == 1:
                VINF = sp1[1].rstrip()
            if i == 2:
                model = sp1[1].rstrip()
            stats.append(line.rstrip())
except: # inspection not completed
    exit()



# FILES SPECIFIC TO VIA INSPECTIONS #
Ifile = 'ModtoIC.txt' # MODEL | OBJ1,OBJ2,OBJ3
ICfile = 'IC_Details.txt' # IC|station_id|system_id|subsystem_id|zone_ID
FPfile = 'FailureParts.txt'# IC | OBJ1,OBJ2,OBJ3 

## GET INSPECTIONS
Ins ={}
# Ins Model to: model_id,  Inspection Criteria

with open(Ifile,"r") as f:
    
    for word in f.readlines():
        word = word.rstrip()
        fp1 = word.split('|')
        # Ins={fp1[0]:fp1[1:]}
        Ins[fp1[0]]= fp1[1:]
ICD = {}



# READ PREVIOUS VINS
VINlog = 'VINlog.txt'
Sent = []
with open(VINlog,"r") as f:
    for word in f.readlines():
        word = word.rstrip()
        Sent.append(word)

if (VIN in Sent):
    ren = "mv "+VIN+" XX"+VIN
    os.system(ren)
    logging(VINF,model,5)
    exit()
# else
with open("VINlog.txt","a") as fw:
    fw.writelines(VIN+'\n')




#  ICD Inspection Criteria to: station_Id, system_id, subsystem_id, zone_ID
with open(ICfile,"r") as f:
    for word in f.readlines():
        word = word.rstrip()
        fp1 = word.split('|')
        ICD[fp1[0]]=fp1[1:]
    
# PARTS PER INSPECTION CRITERIA    
FP = {}
with open(FPfile,'r') as f:
    for line in f.readlines():
        line = line.rstrip()
        lines = line.split('|')
        obj = lines[1]
        # print(obj)
        FP[lines[0]]= lines[1]


# POST saveinspectionresults creates inpsection result for given vin
# post_url = 'https://stg-polvehicleinspec-api.azurewebsites.net/api/InspectionResults'
# put_url = 'https://stg-polvehicleinspec-api.azurewebsites.net/api/InspectionResults'
                
#response.text assume is the criteria result ID

## PROD END POINTS
post_url = 'https://prd-polvehicleinspec-api.azurewebsites.net/api/InspectionResults'
put_url = 'https://prd-polvehicleinspec-api.azurewebsites.net/api/InspectionResults'

hdr = {'Accept':'application/json','Content-Type':'application/json'}
IA = '00000'
IN = 'PolarisNNet'
SHI =0

try:
    model_id = Ins[model][0]
except:
    stats.append("COULD NOT FIND MODEL IN INSPECTIONS\n")
    stats[0] = 'NOT UPLOADED\n'
    stats[1] = stats[1]+'\n'
    stats[2] = stats[2]+'\n'
    with open(path+'/'+statfile,"w") as f:
        for line in stats:
            f.writelines(line)
    mv = "mv "+VIN+" processed/__"+VIN
    os.system(mv)
    logging(VINF,model,6)
    exit()
################# CREATE & SEND API PAYLOADS ##################################
try:
    criteria = Ins[model][1].split(',')
except:
    stats.append("COULD NOT FIND IC IN MODtoIC\n")
    stats[0] = 'NOT UPLOADED\n'
    stats[1] = stats[1]+'\n'
    stats[2] = stats[2]+'\n'
    with open(path+'/'+statfile,"w") as f:
        for line in stats:
            f.writelines(line)
    mv = "mv "+VIN+" processed/__"+VIN
    os.system(mv)
    logging(VINF,model,6)
    exit()

# criteria = (Ins[model]).split(',')
e = 0 # count of errors
j=0
for j in range(0,len(criteria)): # LOOP THRU ALL CRITERIA FOR THE MODEL
    try:
        IC = criteria[j]
        station = ICD[IC][0]
        sys_id = ICD[IC][1]
        ssys_id = ICD[IC][2]
        z_id = ICD[IC][3]
    except:
        stats.append("could not find Criteria-Model details\n")
        e=e+1
    
#    nObjs = len(FP[IC].split(','))
    try:
        nObjs = len(FP[IC].split(','))
    except:
        stats.append("COULD NOT FIND NONE IN INSPECTIONS\n")
        stats[0] = 'NOT VIA\n'
        stats[1] = stats[1]+'\n'
        stats[2] = stats[2]+'\n'
        with open(path+'/'+statfile,"w") as f:
            for line in stats:
                f.writelines(line)
        mv = "mv "+VIN+" processed/__"+VIN
        os.system(mv)
        logging(VINF,model,6)
        exit()


    if nObjs == 1:
        objs2 = FP[IC]
    else:
        objs2 = FP[IC].split(',')
        objs2 = [x.strip(' ') for x in objs2]
        
    i = 0
    flog = 0
    for i in range(0,nObjs): # LOOP THRU FAILUREPARTS FOR CRITERIA
        ci_i = 0
        if nObjs == 1:
            obji = objs2
        else:
            obji = objs2[i]
            
        try:
            idx = objs.index(obji) # IS CRITIERIA j's object i in maxCI.txt
            ci_i = float(ci_s[idx])
        except:
            stats.append("failed to match "+obji+"\n")
            e=e+1
            ci_i = -1.000
        if (ci_i > 0.5): # Confidence Interval > 0
            ## CREATE PASSED INSPECTION PAYLOAD
            PI = True
            FPT = ''
            FCI = None
            FC = None
            FS = 0
            dfile = path+'/_'+str(idx)+'.txt'
            try:
                with open(dfile,'r') as b:
                    for line in b:
                        obline = line.split('\t')
                COORD = "["+obline[2].strip()+","+obline[3].strip()+","+obline[4].strip()+","+obline[5].strip()+"]"        
            except:
                stats.append("cannot open-read "+dfile+"\n")
                e=e+1
            body = {'CriteriaId':int(IC),'PassedInspection':PI,'FailurePart':FPT,'FailureCodeId':FCI,'FailureComments':FC,'StationId':int(station),'ShiftId':SHI,'VIN':VIN,'ModelId':int(model_id),'SystemId':int(sys_id),'SubSystemId':int(ssys_id),'InspectorAuth0Id':IA,'InspectorName':IN,'FlagStatus':FS}
            stats.append(json.dumps(body))
            try:
                r = requests.post(post_url,data=json.dumps(body), headers=hdr)
                CRI = r.text
                if (int(CRI) > 0):
                    stats.append("SUCCESSFULLY POSTED RESULT FOR "+obji+"\n")
                else:
                    stats.append("POST DID NOT RETURN CriteriaId for "+obji+"\n")
            except:
                    stats.append("FAILED TO POST RESULT FOR "+ obji+"\n" )
                    e=e+1
            
            try: # push image and coordinates
                CI = str(ci_i)
                ST = "NN_OBJ_DET"
                EN = "0"
                ED = "None"
                OB = obji
                
                pathimg = path+'/'+VIN+"_"+str(idx)+'__.jpg'
                
                with open(pathimg, "rb") as imageFile:
                    IMG = base64.b64encode(imageFile.read())
                IMG2 = str(IMG)
                IMG3= IMG2[2:-1] # STRIP BYTES FROM base64 encoding
                payload = {
                            "CriteriaResultId": CRI,
                            "Attributes": {
                                    "Coordinates": COORD,
                                    "STATION": ST,
                                    "Confidence": CI,
                                    "ErrorNumber": EN,
                                    "ErrorDescription": ED,
                                    "DetectedObject": obji
                                    },
                                    "ImageData": IMG3
                                    }
                stats.append("CREATED IMAGE PAYLOAD for "+obji+"\n")        
            except:
                stats.append("FAILED TO CREATE IMAGE PAYLOAD for "+obji+"\n")
                e=e+1
            try:
                ri = requests.put(put_url,data=json.dumps(payload), headers=hdr)
                ResultId = ri.text
                if (int(ResultId) > 0):
                    stats.append("SUCCESSFULLY DELIVERED IMAGE PAYLOAD for "+obji+"\n")
                else:
                    stats.append("IMAGE PAYLOAD POST DID NOT RETURN CRITERIA for "+obji+"\n")
            except:
                stats.append("FAILED TO DELIVER IMAGE PAYLOAD for "+obji+"\n")
                e = e+1
                
        else: # OBJECT NOT FOUND
            # OBJECT NOT FOUND
            flog = flog +1
            stats.append("FAILED TO FIND "+obji+" FOR CRITERIA "+IC+"\n")
            ## CREATE FAILED INSPECTION PAYLOAD
            PI = False
            FPT = obji
            FCI = 7
            FC = obji
            FS = 0
            ST = 1
            
            body = {'CriteriaId':int(IC),'PassedInspection':PI,'FailurePart':FPT,'FailureCodeId':FCI,'FailureComments':FC,'StationId':int(station),'ShiftId':SHI,'VIN':VIN,'ModelId':int(model_id),'SystemId':int(sys_id),'SubSystemId':int(ssys_id),'InspectorAuth0Id':IA,'InspectorName':IN,'FlagStatus':FS,'Status':ST}
            stats.append(json.dumps(body))
            try:
                r = requests.post(post_url,data=json.dumps(body), headers=hdr)
                CRI = r.text
                if (int(CRI) > 0):
                    stats.append("SUCCESSFULLY POSTED RESULT FOR "+obji+"\n")
            except: 
                    stats.append("FAILED TO POST FAIL RESULT FOR "+obji+"\n")


logging(VINF,model,4) 
### UPDATE STATFILE
stats[0] = 'UPLOADED WITH '+str(e)+' ERRORS\n'
stats[1] = stats[1]+'\n'
stats[2] = stats[2]+'\n'

with open(path+'/'+statfile,"w") as f:
    for line in stats:
        f.writelines(line)

mv = "mv "+VIN+" processed/__"+VIN
os.system(mv)


print(stats[0][0:8])
