import requests
from bs4 import BeautifulSoup
import re
from os.path import exists
import os
import csv
from datetime import datetime

wordToNum = {'one': 1, 'two': 2, 'three': 3, 'four': 4}


def getApartmentNumericChars(apt, selector):
    return re.sub("[^0-9\-]", "", apt.select_one(selector).get_text())


def saveInfo(aptInfo, fileName):
    openMode = 'a' if exists(fileName) else 'w'
    with open(fileName, openMode) as openFile:
        fileWriter = csv.writer(openFile)
        columnNames = ['scraping_date', 'scraping_time', 'floorplan_name', 'bedroom', 'bathroom', 'apartment_number', 'square_footage', 'rent_min', 'rent_max', 'move_in_month', 'move_in_day', 'move_in_year']
        if openMode == 'w':
            fileWriter.writerow(columnNames)
        fileWriter.writerows(aptInfo)

def runMadisonScraper(fileName):
    currentDate = datetime.now().strftime("%Y/%m/%d")
    currentTime = datetime.now().strftime("%H")

    url = "https://www.madisondruidhills.com/floorplans/availableunits?handler=Filter"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    floorplanInfo = soup.select(".mb-3")
    apartmentsForFloorplan = soup.select(".table-tab-widget")

    aptsInfo = []
    for floorplan, floorplanApts in zip(floorplanInfo, apartmentsForFloorplan):
        sentence = floorplan.get_text().split()
        floorplanInfo = [wordToNum[sentence[i]] if sentence[i] in wordToNum else sentence[i] for i in [1, 4, 6]]

        # Get Every Apartment
        apts = floorplanApts.select("[data-selenium-id^=\"urow\"]")
        
        for apt in apts:
            apartmentNumber = getApartmentNumericChars(apt, ".td-card-name")
            squareFootage = getApartmentNumericChars(apt, ".td-card-sqft")
            rentRange = getApartmentNumericChars(apt, ".td-card-rent").split('-')
            moveInDate = apt.button['onclick'].split("MoveInDate=")[-1][:-1].split('/')
            aptInfo = [currentDate, currentTime, *floorplanInfo, apartmentNumber, squareFootage, *rentRange, *moveInDate]
            aptsInfo.append(aptInfo)

    saveInfo(aptsInfo, f"{os.getcwd()}/{fileName}")


if __name__ == "__main__":
    fileName = 'csvs/infoMadison.csv'
    runMadisonScraper(fileName)