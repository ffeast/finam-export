#!/bin/sh

DIRTY_PATTNS="*.pyc .coverage .noseids htmlcov *.egg-info dist"

for pattn in $DIRTY_PATTNS; do
    find . -name ${pattn} -exec rm -rf {} \;
done
