#!/bin/bash


# find /home/nvidia/PolarisNNet/*/  -name "video.avi"  -type f -mtime +1 -delete


pkill -f polarisnnet
# pkill -f polarisnnet2
pkill -f lxterminal
sleep 1
pkill -f lxterminal
sync
sleep 5
export DISPLAY=:0.0
# gnome-terminal
# xterm
# OPEN ORCH FIRST

lxterminal -e /home/nvidia/local_orch/utilities/run_orch.sh &
sleep 5
lxterminal -e /home/nvidia/local_orch/utilities/run_nn.sh &
# lxterminal -e /home/nvidia/local_orch/utilities/run_nn2.sh
sleep 20
wmctrl -r "Inspection Instruction" -e 0,0,0,1000,800
wmctrl -r "Polaris Object Detection" -e 0,1001,561,640,480
sleep 1
#NN view
wmctrl -r "run_nn.sh" -e 0,1200,800,10,10
wmctrl -r "run_orch.sh" -e 0,0,900,100,50
wmctrl -a "run_orch.sh"

