#!/bin/bash

USER="temp_measure"
GROUP="temperature"
DIR="/home/temp_measure/var"
DB="unin_temperature.db"

function backupday {
    date +'%Y %m' | (\
        read Y M;\
        if [[ $M -eq 1 ]]; then\
            printf "%04d-%02d" $(( $Y - 1 )) 12 ;\
        else\
            printf "%04d-%02d" $Y $(( $M - 1 )) ;\
        fi;\
    )
}

# Check whether there is anything to do
if [[ -e "${DIR}/${DB}.$(backupday)" ]]; then
    # The file seems to exists
    :
else
    # The backup file does not exists, create it
    mv "${DIR}/${DB}" "${DIR}/${DB}.$(backupday)"
    touch "${DIR}/${DB}"
    chmod 0640 "${DIR}/${DB}"
    chown ${USER}:${GROUP} "${DIR}/${DB}"
fi
