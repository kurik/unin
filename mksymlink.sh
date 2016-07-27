#!/bin/bash

function get_db() {
    /store/devel/unin.devel/uninconfig.py | awk '/Database filename: / {print $3}'
}

function updatelinks() {
    if cd ~temp_upload/var; then
        for i in /root/var/unin_temperature.db*; do
            [[ -e $(basename ${i}) ]] || ln $i
        done
    fi
}

rm -f /root/var/unin_temperature.db
ln -s "$(get_db)" /root/var/unin_temperature.db
updatelinks