#!/bin/bash

# Run this using netcat:
# while true; do netcat -e ./server.demo.sh -l -p 1717; done

PEER=$(netstat -an | grep 1717 | awk '{print $5}')
PEERMAC=$(arp -a | grep ${PEER%:*} | awk '{print $4}')
echo ${PEERMAC} >> /tmp/arduino.env

if [[ "${PEERMAC}" == "2c:f4:32:c0:77:15" ]]; then
    # We have the living room SonOff
    if [[ -f /tmp/living.room.on ]]; then
        rm -f /tmp/living.room.on
        echo ZHASNI
    else
        touch /tmp/living.room.on
        echo ROZNI
    fi
fi
