#!/bin/bash

cd /home/nvidia/PolarisNNet2/

./polarisnnet detector line /home/nvidia/PolarisNNet/data/obj.data /home/nvidia/PolarisNNet/data/27_v1_run.cfg /home/nvidia/PolarisNNet/data/27_v1_best.weights /dev/video2 -g_vid 1
