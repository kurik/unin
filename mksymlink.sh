#!/bin/bash

function get_db() {
    /store/devel/unin.devel/uninconfig.py | awk '/Database filename: / {print $3}'
}

rm -f /root/var/unin_temperature.db
ln -s "$(get_db)" /root/var/unin_temperature.db
