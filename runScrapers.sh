#!/bin/bash

python3 madisonDruidHillsScraper.py 2>&1 | tee -a log/madison.log
python3 leaseLabsScraper.py https://87022266.onlineleasing.realpage.com infoCalibre.csv 2>&1 | tee -a log/calibre.log
python3 leaseLabsScraper.py https://4548768.onlineleasing.realpage.com infoLegacy.csv 2>&1 | tee -a log/legacy.log
