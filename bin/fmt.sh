#!/usr/bin/env bash
#
# Format python and c/h/ino files
#
sd="$(dirname "$(realpath "$0")")"
pd="$(dirname "$sd")"
pushd "$pd" &> /dev/null

pyfiles="$(find "$(pwd)" -ipath *.py)"
inofiles="$(find "$(pwd)" -ipath *.ino)"
cfiles="$(find "$(pwd)" -ipath *.c)"
hfiles="$(find "$(pwd)" -ipath *.h)"

autopep8 -i $pyfiles
isort $pyfiles
indent $inofiles $cfiles $hfiles

popd &> /dev/null