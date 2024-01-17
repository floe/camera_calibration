#!/bin/bash

# on the remote display, run (e.g.):
# gst-launch-1.0 filesrc location=output.mp4 ! decodebin ! waylandsink display=wayland-1 fullscreen=true

i=0

while [ $i -le 50 ] ; do
	NAME=capture-$(printf %02i $i).jpg
	echo Capturing $NAME ...
	import -window gst-launch-1.0 $NAME
	sleep 2
	i=$(($i+1))
done
