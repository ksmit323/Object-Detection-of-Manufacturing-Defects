#!/bin/bash


pkill -f polarisnnet
pkill -f lxterminal
sleep 1
pkill -f lxterminal
sync
sleep 2
export DISPLAY=:0.0
# gnome-terminal
# xterm
# OPEN ORCH FIRST

lxterminal -e /home/nvidia/local_orch/utilities/run_nn.sh &

