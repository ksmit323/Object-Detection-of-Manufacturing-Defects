#!/bin/bash

cd /home/nvidia/PolarisNNet/


# ./polarisnnet detector line data/obj_run.data data/14_v6_run.cfg data/14_v6_best.weights js2.mp4 -g_vid 1 -g_ui 1


./polarisnnet detector line data/obj_run.data data/57_v5_run.cfg data/57_v5_best.weights /dev/video0 -g_vid 1 
