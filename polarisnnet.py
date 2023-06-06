"""
This is the main file for running the neural network.
"""
import time
import os
import cv2
import argparse
import numpy as np
import sys
from UploadToAzure import AzureBlobUploader
# from imutils.video import VideoStream
# import imutils


def main():

    #* Instantiate an UploadToBlob class.  MUST CHANGE THE IP ADDRESS SO THE RESULTS ARE UPLOADED TO THE RIGHT CONTAINER
    # TODO: input correct IP address from the device
    ip_address = None
    upload_results = AzureBlobUploader(ip_address)

    # Delete this condition after you have changed the IP address
    if not ip_address:
        sys.exit("You need to input the correct IP address so the results will upload")

    nCount = 0
    # local_orch_path = "/home/nvidia/local_orch/local_orch.py"
    global path 
    path = '/home/nvidia/PolarisNNet/'         
    # Read the inspection file and get model number and objects
    # Create new Folder name VIN in the Polarisnnet folder
    videostream = cv2.VideoCapture(0)
    cap = videostream

    # Parse arguments
    args = arg_parse()

    # time.sleep(3)

    # Start the video stream
    # videopath1 ="/home/nvidia/Hello2.mp4"

    # Read classes in file
    with open(args.classes, 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    # print(classes)

    # Load the neural network
    # net = cv2.dnn.readNet(args.weights, args.config)
    net = cv2.dnn.readNetFromDarknet(args.config, args.weights)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)    
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)       
    ln = get_output_layers(net)

    # Initialize variable for objects detected
    Find_Full_obj = 0
    img_dict = {} 
    obj_dict = {} 
    print("[INFO] starting video stream...")
    print("[INFO] loading YOLO from disk...")

    # Framerate Intializer
    tm = cv2.TickMeter()
    Curr_CamSelect = 0

    while True:

        print("OK")
        VIN_fromPLC, Model_fromPLC, Objects_fromPLC, CamSelect_File, InsDuration, Confidence2NN = read_inspection('/home/nvidia/PolarisNNet/Inspections.txt')

        if CamSelect_File != Curr_CamSelect:
            Curr_CamSelect =CamSelect_File
            videostream = cv2.VideoCapture(int(Curr_CamSelect))

        # If the Inspection from PLC is NULL, then skip the inspection
        if Objects_fromPLC[0] == 'NULL':
            if nCount != 0:
                cv2.destroyAllWindows()
                # os.system('clear')
                nCount = 0
                obj_dict = {}
                img_dict = {}  
                Find_Full_obj = 0
            time.sleep(1)
            # cv2.destroyAllWindows()
        else:
            # videostream = cv2.VideoCapture(int(CamSelect))
            # cap = videostream

            # Set paths to store the result
            path2VIN = '/home/nvidia/PolarisNNet/results/'
            resultspath =path2VIN + str(VIN_fromPLC) + '/'
            # Set path for Training Purpose
            # trainingpath = path2VIN + str(VIN_fromPLC) + "f00"+ str(nCount) + '.png'

            #! ---------------- DELETE IF UPLOADING TO AZURE IS SUCCESFUL --------------------------- #
            # VIN_path = resultspath  + str(VIN_fromPLC) 
            # maxCI_path = resultspath  + str("maxCI.txt")
            # statfile_path = resultspath + str('statfile.txt')
            # if not os.path.exists('/home/nvidia/PolarisNNet/results/' + VIN_fromPLC):
            #     os.makedirs('/home/nvidia/PolarisNNet/results/' + VIN_fromPLC)
            #! -------------------------------------------------------------------------------------- #
            
            _, frame = cap.read()     # Change assignment variables to ret, frame for video capture

            # print FPS to the frame
            tm.start()

            # Resize the frame (Get better Process time)    
            frame = cv2.resize(frame, (416,416))            
        
            # Get the height and width of the frame
            height = frame.shape[0] 
            width = frame.shape[1]

            # Create a 4D blob from the frame to be inputted to the NN
            blob = cv2.dnn.blobFromImage(frame, 1/255, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)

            # Get the output layers from the forward pass
            outs = net.forward(ln)
            tm.stop()
            fps = tm.getFPS()

            # Initialize lists for the detected objects
            class_ids = []
            confidences = []
            boxes = []

            # Initialize threshold variables, the confidence2NN get from goodfile
            conf_threshold = Confidence2NN
            nms_threshold = 0.4
                               
            # Loop through all the output layers
            for out in outs:           
                # Loop through all the detections
                for detection in out:

                    # Get the scores, class id and the confidence
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                                       
                    # If the confidence is greater than the threshold, then save the values
                    if str(classes[class_id]) in Objects_fromPLC:

                        confidence = scores[class_id]

                        if confidence > conf_threshold:
                            # Get the center coordinates, width and height of the bounding box
                            center_x = int(detection[0] * width)
                            center_y = int(detection[1] * height)
                            w = int(detection[2] * width)
                            h = int(detection[3] * height)

                            # Get the top left corner of the bounding box
                            x = int(center_x - w / 2)
                            y = int(center_y - h / 2)
                            class_ids.append(class_id)
                            confidences.append(float(confidence))
                            boxes.append([x, y, w, h])  

            # Apply non-max suppression to the bounding boxes
            indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
            print("OK")
            # Loop through all the indices
            for i in indices:

                # Get the bounding box
                box = boxes[i]

                # Get the x, y coordinates of the bounding box
                x = box[0]
                y = box[1]

                # Get the width and height of the bounding box
                w = box[2]
                h = box[3]

                # Get the label for the class name and the confidence
                label = str(classes[class_ids[i]])
                confidence = confidences[i]

                # if classes[class_ids[i]] in Objects_fromPLC:
                if classes[class_ids[i]] not in obj_dict :
                        # If not, add it and store confidence and bbox coordinates, Image
                        obj_dict[classes[class_ids[i]]] = confidences[i]
                        img_dict[classes[class_ids[i]]] = frame

                else:
                # If it is, compare current confidence with stored confidence
                    if confidences[i] > obj_dict.get(classes[class_ids[i]]): # if confidences[i] > obj_dict[classes[class_ids]]['conf']: 
                        # If current confidence is higher, update stored confidence, image and bbox coordinates
                        obj_dict[classes[class_ids[i]]] = confidences[i]
                        img_dict[classes[class_ids[i]]] = frame
               
                    # Draw the bounding box
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)

                # Draw the label
                cv2.putText(frame, label + ":" + str(round(confidence, 2)), (x - 10, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)  
        
            # Check if the objects detected are the same as the objects in the inspection file
            if all(key in obj_dict for key in Objects_fromPLC):
                # Get notice that all object has been detected, ramp up the process
                Find_Full_obj = 1
                nCount +=50
            else:
                nCount += 1
                if nCount % 10 == 0: print(f'No object detected for {nCount} frames')

            if nCount > InsDuration :
                # Get current Time
                Time = time.localtime(time.time())
                TimeString = str(Time[0]) + "-" + str(Time[1]) + "-" + str(Time[2]) + "-" + str(Time[3]) + ":" + str(
                    Time[4]) + ":" + str(Time[5])
                
                #  Write to Inspection Result file the Result
                if Find_Full_obj == 1:   
                    Inspection_to_Orch = 'Inspection Done' # It must be exactly "Inspection Done" for Local_orch.py to notice the inspection is completed
                else:
                    Inspection_to_Orch = 'Inspection Failed'
                write_insp_results(Inspection_to_Orch, TimeString,VIN_fromPLC)

                #! ------------------ DELETE THIS SECTION IF UPLOADING TO AZURE SUCCESSFULLY -------------------------- #
                # # Write the stat file to VIN folder
                # with open(maxCI_path, 'a') as f:
                #     for key, value in obj_dict.items():
                #         f.write(f'{key} {value} \n')
                # with open(statfile_path, 'w') as f:
                #     f.write(f"{Inspection_to_Orch}\n")
                #     f.write('VIN|' + str(VIN_fromPLC) + '\n')   
                #     f.write('MODEL|' + str(Model_fromPLC) + '\n')
                # # Write Image to VIN Folder
                # cv2.putText(frame,VIN_fromPLC, (20,400),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1)
                # for i in obj_dict:    
                #     cv2.imwrite(VIN_path + "_" + str(i) +'.png',img_dict[i] )
                #! ---------------------------------------------------------------------------------------------------- #

                #*--------------------THIS CODE IS RESPONSIBLE FOR UPLOADING TO AZURE --------------------------------- #
                # Upload each image, the inspection results and log all instances where the upload failed
                upload_results.vin = VIN_fromPLC
                for object, frame in img_dict.items():
                    upload_results.upload_images(object, frame)
                upload_results.upload_results(TimeString, Model_fromPLC, obj_dict, Inspection_to_Orch)
                #*----------------------------------------------------------------------------------------------------- #

            cv2.putText(frame, 'FPS: {:.2f}'.format(fps), (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
            tm.reset()
            cv2.imshow("object detection", frame)    
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
       
    # cap.stop()
    # cv2.release()
    cv2.destroyAllWindows()


def read_inspection(filename):
    """
    This function reads the inspection file and returns the model and objects.
    """
    # Read the contents of the file and split it into lines
    with open(filename, "r") as file:
        for line in file:

            # Initialize the "Objects" list
            Objects_fromPLC = []

            # Extract the "Model" and "Objects" from the line
            parts = line.strip().split('|')
            VIN_fromPLC = parts[0]
            Model_fromPLC = parts[1]
            object_strings = parts[2].split(',')
            CamSelect = int(parts[3])
            InsDuration = int(parts[4])
            Confidence2NN = round(float(parts[5]),2)

            Objects_fromPLC.extend(object_strings)
    
    return VIN_fromPLC, Model_fromPLC, Objects_fromPLC,CamSelect,InsDuration,Confidence2NN


def arg_parse():
    """   
    """
    ap = argparse.ArgumentParser()    
    ap.add_argument('-ca','--camera' ,help='path to yolo config file')
    ap.add_argument('-f', '--frame', default=20, type=int,help='path to yolo config file')
    ap.add_argument('-c', '--config', help='path to yolo config file')
    ap.add_argument('-w', '--weights', help='path to yolo pre-trained weights')
    ap.add_argument('-cl', '--classes',help='path to text file containing class names')
    args = ap.parse_args()
    return args


def get_output_layers(net):
    """
    This function gets the output layers of the neural network.
    """
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers


def write_insp_results(Inspection, TimeString,VIN_fromPLC):
    """
    This function writes the inspection results to the inspection results file.
    """
    try:
        with open(path + 'InspectionResults.txt', 'w') as f:
            f.write(Inspection)

        with open(path + 'InspectionResults_Log.txt', 'a') as f:
            f.write(f'{TimeString}: {VIN_fromPLC}|{Inspection} |\n')

        NoFile = 0
        
    except:
        NoFile = 1

    return NoFile



if __name__ == '__main__':
    main()
