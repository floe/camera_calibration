#!/bin/bash

SCALES="100 50 25"
DISTORT="0,0,0,0  0,1000,0,1000  1000,0,1000,200  1000,1000,1000,800"
ROTATE="0 45 135 180"
GRAVITY="NorthWest North NorthEast West Center East SouthWest South SouthEast"

for r in $ROTATE ; do
	for s in $SCALES ; do
		for g in $GRAVITY ; do
			convert base.png -background white -mattecolor white -resize $s% -rotate $r -gravity $g -extent 1920x1080 tmp-$g-$s-$r.png
			convert base.png -background white -mattecolor white -distort Perspective "$DISTORT" -resize $s% -rotate $r -gravity $g -extent 1920x1080 dst-$g-$s-$r.png
		done
	done
done

# pipe file list through shuf for randomization
# use ffmpeg to make mp4 with every file for 1 second
