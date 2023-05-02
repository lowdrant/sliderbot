#!/usr/bin/env bash
#
# Wrap serlog.py with fn. Pass any other CLI args to python3 script
#
fn=stream_imu.csv
wd="$(dirname "$(realpath "$0")")"
root="$(dirname "$wd")"
python3 "$wd"/serlog.py $fn $@