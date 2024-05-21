#!/bin/bash

while :
do
    killall -s SIGKILL -o 3m java
    sleep 10s
done