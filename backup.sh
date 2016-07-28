#!/bin/bash

USER="temp_measure"
GROUP="temperature"
DIR="/home/temp_measure/var"
DB="unin_temperature.db"
TSTAMP=$(date +'%Y-%m' -d "1 month ago")

# Check whether there is anything to do
if [[ -e "${DIR}/${DB}.${TSTAMP}" ]]; then
    # The file seems to exists
    :
else
    # The backup file does not exists, create it
    echo mv "${DIR}/${DB}" "${DIR}/${DB}.${TSTAMP}"
    echo touch "${DIR}/${DB}"
    echo chmod 0640 "${DIR}/${DB}"
    echo chown ${USER}:${GROUP} "${DIR}/${DB}"
fi
