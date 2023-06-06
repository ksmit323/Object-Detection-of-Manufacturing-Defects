import os, sys
from azure.storage.blob import BlockBlobService, PublicAccess, ContentSettings
import time
from datetime import datetime
import numpy as np
import json
from applicationinsights import TelemetryClient
import platform
from os.path import expanduser
import glob


# ==================== vars ====================
current_dir_path = os.path.dirname(os.path.realpath(__file__))
object_result_core = {}
object_directory = None
json_content_type = 'application/json'
error_count = 0
upload_count = 0

# ==================== config ====================
configJson = {}
configLocation = os.path.join(expanduser("~"),"polaris","config.json")

def load_config():
	global configJson
	#load local config file and convert to JSON
	if(os.path.isfile(configLocation) == True):  
		configRaw = open(configLocation, "r")
		configJson = json.load(configRaw)		
	else:
		print("[Error]: issue loading config.json")
		exit()

load_config()
deviceName = configJson["azure_iotHubDeviceConnectionString"].split(";")[1].split("=")[1]
# ==================== app insights ==================== 
tc = TelemetryClient(configJson["appInsights_instrumentationKey"])    
tc.context.user.id = deviceName
tc.context.operation.id = os.path.basename(__file__)
tc.context.device.os_version =  platform.platform()
session_status = 0

#start it up
try:
    object_directory = sys.argv[1]    
    
    if object_directory.startswith("F_") or object_directory.startswith("F2_"):
        if object_directory[1:2] == "_":
            session_status = 1
        else:
            session_status = int(object_directory[1:2])        
    #print(session_status)
except Exception as e:
    tc.track_exception(*sys.exc_info())    
    tc.flush()
    time.sleep(2)  
    error_count += 1
    exit() #no directory specified


custom_dims = {
    'directory': object_directory
}

via_processed_mode = False

try:
    via_processed_mode = sys.argv[2]
    
    if via_processed_mode:
        object_directory = os.path.join("processed", object_directory)    
except:
    via_processed_mode = False

#print(object_directory)

# ==================== blob setup ====================

block_blob_service = BlockBlobService(account_name=configJson["results_blobStorageAccount"], sas_token=configJson["results_sasToken"])


def writeLog(VIN,msg):
    lt = time.localtime(time.time())
    lt2 = str(lt[0])+"-"+str(lt[1])+"-"+str(lt[2])+"-"+str(lt[3])+"."+str(lt[4])+"."+str(lt[5])
    lg = lt2+" : "+VIN+"|"+msg
    with open('QED_UPLOADS.txt','a') as f:
        f.write(lg+"\n")
    return 0



def sendResultsToBlob(blob_meta,blob_name,path_to_file,container_name=configJson["results_blobContainer"], file_content_type='image/jpeg'):
    global block_blob_service
    global tc
    global error_count
    global upload_count

    try:        
        
        #convert ints to strings for blob
        for k, v in blob_meta.items():        
            if type(v) is not str:
                blob_meta[k] = str(v)
                
        block_blob_service.create_blob_from_path(container_name, blob_name, path_to_file, content_settings=ContentSettings(content_type=file_content_type))
        block_blob_service.set_blob_metadata(container_name, blob_name,metadata=blob_meta)
        upload_count += 1
        result = 1
    except Exception as ex:
        print(str(ex))
        tc.track_exception(*sys.exc_info(),custom_dims)        
        tc.flush()
        time.sleep(2)
        error_count += 1
        result = 0 
                   
    return result

# ==================== results ====================

# get all files that are ready to upload
stat_file_name = "statfile.txt"
max_ci_file_name = "maxCI.txt"
results_dir_path = os.path.join(current_dir_path, object_directory)

result_dir_list = None

if os.path.exists(results_dir_path):
    result_dir_list = os.listdir(results_dir_path)
else:
    print("DIRECTORY DOES NOT EXIST")
    writeLog(object_directory,"DIR DOES NOT EXIST")
    exit()

     
# make sure results have completed
if stat_file_name in result_dir_list:
    # read folder level metadata
    with open(os.path.join(results_dir_path,stat_file_name),"r") as f: 
        for i, line in enumerate(f):
            if i == 1:
                object_result_core["Session"] = line.strip().replace("VIN|","")

            if i == 2:
                object_result_core["ParentObject"] = line.strip().replace("MODEL|","")
else:
    writeLog(object_directory,"RESULTS INCOMPLETE")
    print("RESULTS INCOMPLETE")
    exit()

# set values from config
object_result_core["DeviceName"] = deviceName
        
#check max CI file for results
max_ci_objects = []
max_ci_cis = []
max_ci_file_path = os.path.join(results_dir_path,max_ci_file_name)
max_ci_file_info = os.stat(max_ci_file_path)
if max_ci_file_info.st_size > 0:
    writeLog(object_directory,"Opening MAX CI")
    with open(max_ci_file_path,"r") as f: # read maxCI data
        for line in f:
            txt = line.split('\t')
            max_ci_objects.append(txt[0].strip())
            max_ci_cis.append(txt[1].strip())
else:
    print("MAX CI INCOMPLETE")
    writeLog(object_directory,"MAX CI INCOMPLETE")
    exit()




#upload status file
uploading_status_file = os.path.join(results_dir_path, "uploading.txt")

#check for mp4 file
avi_files = glob.glob(os.path.join(results_dir_path,"*.avi"))
mp4_files = glob.glob(os.path.join(results_dir_path,"*.mp4"))
hasVideo = len(avi_files) > 0
needsVideoConversion = hasVideo and len(mp4_files) == 0

if os.path.exists(uploading_status_file) == False and (hasVideo == False or (hasVideo and needsVideoConversion)):
#if os.path.exists(uploading_status_file) == False and (hasVideo == False or (hasVideo)):
    writeLog(object_directory,"UPLOADING VIDEO 0")

    #check for sent carrier file to change sessions staus
    if session_status == 0:
        if os.path.exists(os.path.join(results_dir_path, "AGCSent.txt")):
            session_status = 1
        
    meta_for_json = []
    
    os.mknod(uploading_status_file)
    
    if hasVideo:                
        #convert video    
        avi_file_path = os.path.join(results_dir_path,"video.avi")
        mp4_file_name = str(session_status) + "_" + deviceName + ".mp4"
        mp4_file_path = os.path.join(results_dir_path, mp4_file_name)
        os.system("ffmpeg -i %s -an -r 15 -b:v 1M -loglevel quiet %s" % (avi_file_path, mp4_file_path))
        writeLog(object_directory,"Converting Video")

        #os.remove(avi_file_path)                
    
    hasPassed = 1
    #get result date from maxCI.txt file
    max_ci_datetime = int(os.stat(max_ci_file_path).st_mtime)
    max_ci_datetime_formatted = datetime.utcfromtimestamp(max_ci_datetime).isoformat()

    #loop max ci file to build the rest of the meta data
    for i in range(0,len(max_ci_objects)):
        try:
            if (float(max_ci_cis[i]) >0): # if we have a result                
                writeLog(object_directory,"Have Result for object "+str(i))
                #create copy of object_result_core            
                object_result = object_result_core.copy()
                with open(os.path.join(results_dir_path,'_'+str(i)+'.txt')) as f:
                    for line in f:                
                        items = line.split('\t')                
                        coordsStr = list(map(lambda x: str(x).strip(),items[2:6]))
                        
                        object_result["Object"] = items[0].strip()
                        object_result["Value"] = float(max_ci_cis[i])
                        object_result["Coordinates"] = "["+",".join(coordsStr)+"]"
                        object_result["BlobUri"] = object_result["Session"] + "/" + object_result["Object"].replace(' ','_') + "_" + str(session_status) + "_" + deviceName + ".jpg"
                        object_result["HasPassed"] = 1
                        object_result["ResultTypeId"] = 1
                        object_result["SessionStatus"] = session_status
    
                        object_image_path = os.path.join(results_dir_path,object_result["Session"] + "_" + str(i) + "__.jpg")
                        object_image_datetime = int(os.stat(object_image_path).st_mtime)
                        object_image_datetime_formatted = datetime.utcfromtimestamp(object_image_datetime).isoformat()
                        object_result["ResultDate"] = object_image_datetime_formatted
                        
                        #append meta for json file
                        meta_for_json.append(json.dumps(object_result))
    
                        #prep meta for blob
                        object_result_for_blob = object_result.copy()
                        del object_result_for_blob["BlobUri"]
    
                        #send image to blob
                        sendResultsToBlob(object_result_for_blob, object_result["BlobUri"], object_image_path)                        
            else:
                hasPassed = 0
                writeLog(object_directory,"NO Result for Object "+str(i))

                #failed result for json file
                object_result = object_result_core.copy()
                object_result["Value"] = float(max_ci_cis[i])
                object_result["Object"] = max_ci_objects[i]
                object_result["HasPassed"] = 0
                object_result["ResultTypeId"] = 1
                object_result["SessionStatus"] = session_status                                
                object_result["ResultDate"] = max_ci_datetime_formatted
    
                #append meta for json file
                meta_for_json.append(json.dumps(object_result))
        except:
            tc.track_exception(*sys.exc_info(),custom_dims)
            tc.flush()
            time.sleep(2)
            error_count += 1           
            writeLog(object_directory, "ci metadata error")     


    if hasVideo: 
        try:
            #upload video
            video_result = object_result_core.copy()
            video_result["BlobUri"] = video_result["Session"] + "/" + video_result["Session"] + "_" + mp4_file_name
            video_result["ResultTypeId"] = 2
            video_result["SessionStatus"] = session_status
            video_result["Object"] = session_status
            video_result["HasPassed"] = hasPassed
            video_result["ResultDate"] = max_ci_datetime_formatted
            meta_for_json.append(json.dumps(video_result))
            
            sendResultsToBlob(video_result,video_result["BlobUri"],mp4_file_path,file_content_type='video/mp4')
        except:
            tc.track_exception(*sys.exc_info(),custom_dims)
            tc.flush()
            time.sleep(2)
            error_count += 1    
            writeLog(object_directory, "video upload error")
        
    #print(meta_for_json)
    try:
        # write meta to file
        results_file_path = os.path.join(results_dir_path, "results.json")
        results_file_content = "\n".join(meta_for_json)
        with open(results_file_path,"w") as f:
            f.writelines(results_file_content)
        # meta for meta file
        results_blob_meta = object_result_core.copy()
        
        sendResultsToBlob(results_blob_meta, object_result_core["Session"] + "/results_" + object_result_core["Session"] + "_"+ str(session_status) + "_" + deviceName + ".json", results_file_path, file_content_type=json_content_type)
        #to metadata
        now = datetime.now()
        date_path = now.strftime("%Y/%m/%d/")
            
        sendResultsToBlob(results_blob_meta, date_path + "results_" + object_result_core["Session"] + "_"+ str(session_status) + "_" + deviceName + ".json", results_file_path, container_name=configJson["results_blobMetadataContainer"], file_content_type=json_content_type)        
    except:
        tc.track_exception(*sys.exc_info(),custom_dims)
        tc.flush()
        time.sleep(2)
        error_count += 1
        writeLog(object_directory, "results json upload error")    
    
    writeLog(object_directory,"Error count: " + str(error_count))
       
    if(error_count == 0):
        tc.track_event("SUCCESS",custom_dims,{'count': upload_count})
        tc.flush()
        time.sleep(2)
        writeLog(object_directory,"uploaded")

        print("UPLOADED")
    
else:
    print("SKIP")
