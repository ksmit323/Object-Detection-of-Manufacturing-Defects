# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 13:03:40 2018

@author: JStitt
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 15:17:01 2018

@author: JStitt
"""

import json
import requests

###################GET INSPECTIONS PER MODEL  for the NN ZONE (138) on Line A (13)  ###########################
try:
	response = requests.get("https://prd-polvehicleinspec-api.azurewebsites.net/api/Inspections?LineId=13&ZoneId=138&ShiftId=1&LangId=1")
	print("Connect OK")
except:
	print("res ERROR")

ins = json.loads(response.text)
infile = open('ModtoIC.txt','w')
infile.write('MODEL|MODEL_ID|IC\n')
gr= {}

# c=0
############ GET INSPECTIONS PER MODEL  ############################
# for c in range(0,len(ins['Models'])):
# print(ins['Models'])
for c in range(len(ins['Models'])):
    # print(ins['Models'][c])
    mod = ins['Models'][c]['ModelNumber']
    # print(mod)
    if ins['Models'][c]['MandatoryInspectionIds'] is None:
        ic = ''
    else:
        ic = ins['Models'][c]['MandatoryInspectionIds']
    mod_id = ins['Models'][c]['ModelId']
    # print(f'this is IC: {ic}')
    try:
        ic2 = ic.split(',')
        ic3 = list(map(int, ic2))
        # print(f'this is IC2 :{ic2}')
        # print(f'this is IC3 :{ic3}')
    except:
        ic = 'NONE'
        ic3 = ''
    # i3 = map(int,i2) python 2
    gr[mod] =  ic3
    # print(str(mod)+"|"+str(mod_id)+"|"+ic+'\n')
    infile.write(str(mod)+"|"+str(mod_id)+"|"+ic+'\n')

infile.close()

# ############GET PARTS PER INSPECTION #################################
# infile = open('FailureParts.txt','w')
# infile.write('IC|FP|\n')

# for c in range(0,len(ins['InspectionItems'])):
    
#     ic = ins['InspectionItems'][c]['InspectionId']
#     fp = ins['InspectionItems'][c]['FailureParts']
#     fp = fp.rstrip()
#     fp = fp.replace('\n','')
#     fp = fp.replace('\r','')
#     fp = fp.replace(' ','')
#     infile.write(str(ic)+"|"+fp+"\n")

# infile.close()


# ######### WRITE IC DETAILS for VIA UPLOAD
# infile = open('IC_Details.txt','w')
# infile.write('IC|station_id|system_id|subsystem_id|zone_ID\n')

# for c in range(0,len(ins['InspectionItems'])):
#     ic = ins['InspectionItems'][c]['InspectionId']
#     s_id = ins['InspectionItems'][c]['StationId']
#     sy_id = ins['InspectionItems'][c]['SystemId']
#     ssy_id = ins['InspectionItems'][c]['SubSystemId']
#     z_id = ins['InspectionItems'][c]['ZoneId']
    
#     infile.write(str(ic)+"|"+str(s_id)+"|"+str(sy_id)+"|"+str(ssy_id)+"|"+str(z_id)+"\n")
# infile.close()



# infile = open('VINtoObjs.txt','w')
# ######### ENUMERATE PARTS PER MODEL ON LINE A, NN ZONE
# for i in range(0,len(ins['Models'])):
#     ic3 ={}
#     mod = ins['Models'][i]['ModelNumber']
#     if ins['Models'][i]['MandatoryInspectionIds'] is None:
#         ic = ''
#     else:
#         ic = ins['Models'][i]['MandatoryInspectionIds']
        
#     mod_id = ins['Models'][i]['ModelId']
#     try:
#         ic2 = ic.split(',')
#         ic3 = list(map(int, ic2))
#     except:
#         ic = 'NONE'
#         ic3 = ''

#     fp0 = ''
#     for j in range(0,len(ic3)):
#         L = [item for item in ins['InspectionItems']
#         if item['InspectionId'] == int(ic3[j])]
#         try:

#             if (j==0):
#                 fp = L[0]['FailureParts']
#                 fp = fp.rstrip()
#                 fp = fp.replace('\r','')
#                 fp = fp.replace('\n','')
#                 fp0 = fp.split(',')
#             else:
#                 fp = L[0]['FailureParts']
#                 fp = fp.rstrip()
#                 fp = fp.replace('\r','')
#                 fp = fp.replace('\n','')
#                 fp1 = fp.split(',')
#                 fp0.extend(fp1)
#         except:
#             a = 'bob'
#     objs = ','.join(list(map(str, [x.strip(' ') for x in fp0])))
#     infile.write(mod+"|"+objs+"\n");
# infile.close()


# #########SAVE RAW JSON ##################################
# infile = open('raw.txt','w')
# infile.write(response.text)
# infile.close()

