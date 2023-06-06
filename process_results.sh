#!/bin/bash

cd /home/nvidia/PolarisNNet

vins=($(ls -d 56* ))
us="_"
ul="UPLOADED"
for vin in "${vins[@]}"
do
        echo $vin

        ret=$(python3 process_results.py $vin)
        echo $ret
        if [ "$ret" = "$ul" ]; then
                vin2="$us$us$vin"
                echo $vin2
                mv  "$vin" "$vin2"

        fi

done
mv /home/nvidia/PolarisNNet/__* /home/nvidia/PolarisNNet/processed/

