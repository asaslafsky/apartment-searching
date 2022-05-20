#!/bin/bash

python3 madisonDruidHillsScraper.py 2>&1 | tee -a logs/madison.log
python3 leaseLabsScraper.py https://87022266.onlineleasing.realpage.com csvs/infoCalibre.csv 2>&1 | tee -a logs/calibre.log
python3 leaseLabsScraper.py https://4548768.onlineleasing.realpage.com csvs/infoLegacy.csv 2>&1 | tee -a logs/legacy.log
