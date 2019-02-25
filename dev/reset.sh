#!/bin/bash

shopt -s globstar
start=$SECONDS

./ch2/migraine/sqlp2sqlp.sh
dev/ch2 --dev activities ~/archive/fit/bike/*.fit --fast
dev/ch2 --dev activities ~/archive/fit/batch/**/*.fit --fast
dev/ch2 --dev monitor ~/archive/fit/monitor/*.fit --fast
dev/ch2 --dev monitor ~/archive/fit/batch/**/*.fit --fast
dev/ch2 --dev statistics

duration=$(($SECONDS - $start))
echo "$(($duration/60)) min $(($duration%60)) sec"
