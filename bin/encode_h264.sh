#!/bin/bash

# Encodes a video from jpegs using mencoder
# Options: hour, day, week, month, year

# Example calls:
#./encode.sh -h 2014031501
#./encode.sh -m 201403

# TODO date range
#./encode.sh -r 20140305 20140312 # must be two days, also used for weeks

if [ $# -eq 0 ]; then
  echo "No arguments supplied"
  exit
fi

interval=$1
datetime=$2
IMGDIR=/media/ww/imgs
VIDDIR=/media/ww/vids

## Setup mencode paramters ##
if [ $interval == "-h" ]; then
    search_string=$datetime*jpg
    expected_imgs=3650; fps=60
    destination=$VIDDIR/hour
elif [ $interval == "-d" ]; then
    search_string=$datetime?????0.jpg
    expected_imgs=9000; fps=125
    destination=$VIDDIR/day
elif [ $interval == "-w" ]; then
    search_string=$datetime?????0.jpg
    expected_imgs=0; fps=120
    destination=$VIDDIR/week
elif [ $interval == "-m" ]; then
    search_string=$datetime?????000.jpg
    day_regex="([0-9][0-9])(0[5-9]|1[0-9]|2[0-1])"
    expected_imgs=10000; fps=60
    destination=$VIDDIR/month
elif [ $interval == "-y" ]; then
    search_string=$datetime??????0000.jpg
    day_regex="([0-9][0-9][0-9][0-9])(0[5-9]|1[0-9]|2[0-1])"
    expected_imgs=10000; fps=60
    destination=$VIDDIR/year
elif [ $interval == "-r" ]; then
    # Get num imgs between two days
    # Calculate num imgs to use and FPS
    search_string=$datetime
else
    echo "Unknown interval"
    exit 3
fi

## Gather list of images to encode ##
# /20140328(0[5-9]|1[0-9]|2[0-1])/g
echo "Creating image list ..."
# Monthly and yearly videos are daytime only (5AM - 9PM)
if [ $interval == "-m" ] || [ $interval == "-y" ]; then
    echo "find $IMGDIR -name $search_string | egrep "$datetime$day_regex" | sort -n > imglist.txt"
    find $IMGDIR -name $search_string | egrep "$datetime$day_regex" | sort -n > imglist.txt
else # Get all files matching the date criteria
    find $IMGDIR -name "$search_string" | sort -n > imglist.txt
fi

file_count=$(wc -l imglist.txt | tr -dc '[0-9]')
echo "File count: $file_count"

if [ $file_count -eq 0 ]; then
    echo "No files found for given datetime."
    exit 1
elif [ $file_count -gt $(($expected_imgs + 500)) ]; then
    echo "There are an unusual amount of images for this range."
    echo "Expected $expected_imgs, Found $file_count. Exiting ..."
    exit 2
fi

## Encode it ##
echo "Encoding video ..."
mencoder -nosound -mf fps=$fps -o $destination/${datetime}_x264.avi -ovc x264 -x264encopts bitrate=6000 mf://@imglist.txt
# TODO - Get mencoder's return value
#rm imglist.txt

exit 0
