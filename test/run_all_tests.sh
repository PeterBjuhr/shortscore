#!/bin/bash

for filename in ./*
do
	base=$(basename "$filename")
	call="${base%.*}"
	ext="${base##*.}"
	if [ $ext == "py" ]; then
		python -m unittest $call
	fi
done
