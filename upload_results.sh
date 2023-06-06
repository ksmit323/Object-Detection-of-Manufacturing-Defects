#!/bin/bash
run_count=`ps aux | grep -i "upload_results_qed_after_via.sh" | grep -v "grep" | wc -l`
if [ $run_count -gt 3 ]
   then
        echo "ALREADY RUNNING"
   else
   		#move any fails as well
		mv /home/nvidia/PolarisNNet/F_* /home/nvidia/PolarisNNet/processed/
		mv /home/nvidia/PolarisNNet/F2_* /home/nvidia/PolarisNNet/processed/
		cd /home/nvidia/PolarisNNet/processed
		results=($(ls -d {__56*,F_*,F2_*} ))
		us="_"
		ul="UPLOADED"
		for result in "${results[@]}"
		do
			echo $result
			
			ret=$(python3 /home/nvidia/PolarisNNet/upload_results.py $result True)
			echo $ret
			if [ "$ret" = "$ul" ]; then
				result2="$us$us$result"
				echo $result2
				mv  "$result" "$result2"
					
			fi

		done
		rm -r /home/nvidia/PolarisNNet/processed/____*
fi
