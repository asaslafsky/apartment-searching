import sys
from playwright.sync_api import sync_playwright
import time
import re
from datetime import datetime
from os.path import exists
import csv


def clickOnCalendar(frame):
    frame.click("#calendarInput")


def grabAllDaysForMonth(frame):
    return frame.query_selector_all(".uib-day ")


def isClickable(day):
    return str(day.query_selector("button").get_property('disabled')) == 'false'


def isInCurrentMonth(day):
    return day.query_selector("button .text-muted") is None


def clickNextMonth(frame):
    return frame.query_selector('.glyphicon-chevron-right').click()


def getText(jshandle, selector):
    return str(jshandle.query_selector(selector).get_property('innerText')).replace(',', '')


def grabAptsInfo(frame, aptsInfo, currentDateTime, moveInDate):
    # For Every Floorplan Shown On This Calendar Day
    for floorplan in frame.query_selector_all(".floorplan-tile"):
        # If There Isn't A Number In The String, No Apartments With This Floorplan Are Available
        # So Go To The Next Floorplan
        isntAvailable = re.search('\d', getText(floorplan, '.primary')) is None
        if isntAvailable:
            continue

        floorplanName = getText(floorplan, ".name")
        bedBathSquareFootage = [int(word) for word in getText(floorplan, ".specs").split() if word.isdigit()]
        
        rentRange = re.sub("[^0-9\-]", "",getText(floorplan, '.range')).split('-')
        if len(rentRange) == 1:
            rentRange.append(rentRange[0])
        
        aptsInfo.append([*currentDateTime, floorplanName, *bedBathSquareFootage, *rentRange, *moveInDate])

    return aptsInfo


def saveInfo(aptInfo, fileName):
    openMode = 'a' if exists(fileName) else 'w'
    with open(fileName, openMode) as openFile:
        fileWriter = csv.writer(openFile)
        columnNames = ['scraping_date', 'scraping_time', 'floorplan_name', 'bedroom', 'bathroom', 'squareFootage', 'rent_min', 'rent_max', 'move_in_month', 'move_in_day', 'move_in_year']
        if openMode == 'w':
            fileWriter.writerow(columnNames)
        fileWriter.writerows(aptInfo)


def run(playwright, url, fileName):
    aptsInfo = []
    currentDateTime = [datetime.now().strftime("%Y/%m/%d"), datetime.now().strftime("%H")]

    try:
        # Get Frame Info
        browser = playwright.firefox.launch() #headless=False
        page = browser.new_page()
        page.goto(url)
        frame = page.wait_for_selector("#rp-leasing-widget").content_frame()
        
        # Enter Into Frame
        frame.click("text=Start")

        # Go Through All The Available Days In The Calendar And Grab Their Information
        isntFirstMonth = False
        thereIsMoreInfo = True
        while thereIsMoreInfo:
            
            # Open The Calendar
            clickOnCalendar(frame)
            if isntFirstMonth:
                clickNextMonth(frame)
            calendarMonth = grabAllDaysForMonth(frame)
            # Close The Calendar
            clickOnCalendar(frame)
            
            # Grab The Indices Of All The Days That Are In The Current Month
            availableDaysForCurrentMonth = []
            for i, calendarDay in enumerate(calendarMonth):
                if isClickable(calendarDay) and isInCurrentMonth(calendarDay):
                    availableDaysForCurrentMonth.append(i)
            
            # If There Are 0 Days We Can Access In The Current Month,
            # Then There Is No More New Information And We Should Save The Data
            if len(availableDaysForCurrentMonth) == 0:
                thereIsMoreInfo = False

            # Loop Through All The Days That In The Current Month
            # And Grab The Apartment Information On Each Day
            isFirstDayOfMonth = True
            for daysIndex in availableDaysForCurrentMonth:
                clickOnCalendar(frame)
                if isntFirstMonth and isFirstDayOfMonth:
                    clickNextMonth(frame)
                isFirstDayOfMonth = False

                grabAllDaysForMonth(frame)[daysIndex].click()
                moveInDate = str(frame.query_selector("#calendarInput").get_property('value')).replace(',', '').split(' ')
                moveInDate[0] = datetime.strptime(moveInDate[0], "%B").month
                print(moveInDate[:3])
                aptsInfo = grabAptsInfo(frame, aptsInfo, currentDateTime, moveInDate[:3])
                
            
            isntFirstMonth = True
        saveInfo(aptsInfo, fileName)

    except Exception as e:
        time.sleep(4)
        raise(e)
    finally:
        page.close()
        browser.close()


def runPlaywright(url, fileName):
    with sync_playwright() as playwright:
        run(playwright, url, fileName)

if __name__ == '__main__':
    url, fileName = sys.argv[1:3]
    # calibreUrl = "https://87022266.onlineleasing.realpage.com"
    # calibreFileName = "infoCalibre.csv"

    # legacyURL = "https://4548768.onlineleasing.realpage.com"
    # legacyFileName = "infoLegacy.csv"

    runPlaywright(url, fileName)
    