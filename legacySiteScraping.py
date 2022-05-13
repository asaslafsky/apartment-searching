from playwright.sync_api import Playwright, sync_playwright
import time
from datetime import datetime, date, timedelta
import calendar
import csv
from os.path import exists

numMonths = 4 #(end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)


def clickOnCalendar(mainFrame):
    mainFrame.click("#calendarInput")


def clickOnCalendarDate(mainFrame, day, extra=""):
    mainFrame.click(f".uib-day button:has-text(\"{day}\"){extra}")


# In The Calendar There Might Be Buttons With Numbers From Previous or Future Months
#   At The Beginning or End of the Calendar, Respectively. 
def chooseFirstOrLastButton(day):
    return " >> nth=0" if day <= 15 else " >> nth=-1"


def clickOnNextMonth(mainFrame):
    mainFrame.click(".glyphicon-chevron-right")


def getFloorplanOfInterestInfo(mainFrame):
    # For Every Apartment Floorplan
    for floorplan in mainFrame.query_selector_all(".floorplan-tile"):
        # If the Floorplan is a 3 or 4 Bedroom and is Available (we assume single digit # of bedrooms)
        numBedrooms = str(floorplan.query_selector(".specs").get_property('innerText'))[0]
        isAvailable = str(floorplan.query_selector("button").get_property('innerText'))[0] != 'C'
        if (numBedrooms == '3' or numBedrooms == '4') and isAvailable is True:
            # Return Floorplan Name, Cost, And Number Of Bedrooms
            name = str(floorplan.query_selector(".name").get_property('innerText'))
            price = str(floorplan.query_selector(".range").get_property('innerText'))
            return name, price, numBedrooms


def run(playwright: Playwright) -> None:
    legacyInfo = []
    currentDate = datetime.now().strftime("%Y/%m/%d")
    currentTime = datetime.now().strftime("%H")

    try:
        # Prepare To Open Website
        browser = playwright.firefox.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Open Website
        page.goto("https://4548768.onlineleasing.realpage.com/")
        time.sleep(5)

        # Click On The Calendar
        mainFrame = page.query_selector('iframe').content_frame()
        mainFrame.click("text=Start")

        # First And Last Date We Can Access In The Calendar
        thisDate = date.today() #+ timedelta(days=30)
        lastDate = thisDate + timedelta(days=30*numMonths) ### 3
        # First Day Of The Month We Can Access On The Calendar
        firstDayOfMonth = thisDate.day

        # For Every Month We Can Access
        isFirstMonth = True # False
        for i in range(numMonths + 1): #numMonths
            # Last Day Of The Month We Can Access On The Calendar
            lastDayOfMonth = (lastDate.day if thisDate.month == lastDate.month 
                            else calendar.monthrange(thisDate.year, thisDate.month)[1])

            if not isFirstMonth:
                # Go To First Day Of The Next Month In The Calendar
                clickOnCalendar(mainFrame)
                clickOnNextMonth(mainFrame)
                firstDayOfMonth = 1
                clickOnCalendarDate(mainFrame, str(firstDayOfMonth).zfill(2), chooseFirstOrLastButton(firstDayOfMonth))
                time.sleep(5)
            isFirstMonth = False

            # For Every Day Of This Month We Can Access, Get The Cost Of Floorplans Of Interest
            for day in range(firstDayOfMonth, lastDayOfMonth + 1):
                clickOnCalendar(mainFrame)
                clickOnCalendarDate(mainFrame, str(day).zfill(2), chooseFirstOrLastButton(day))
                time.sleep(5)
                floorplanInfo = getFloorplanOfInterestInfo(mainFrame)
                if floorplanInfo:
                    legacyInfo.append((currentDate, currentTime, thisDate.year, thisDate.month, day, *floorplanInfo))
            
            # Update The Current Date To 30 Days From thisDate
            thisDate += timedelta(days=30)
        
        fileName = 'infoLegacy.csv'
        openMode = 'a' if exists(fileName) else 'w'
        with open(fileName, openMode) as openFile:
            fileWriter = csv.writer(openFile)
            columnNames = ['date_scraping_occurred', 'time_scraping_occurred', 'year', 'month', 'day', 'floorplan', 'price', 'num_bedrooms']
            if openMode == 'w':
                fileWriter.writerow(columnNames)
            fileWriter.writerows(legacyInfo)

    except Exception as e:
        print((thisDate.year, thisDate.month, day))
        raise(e)
    finally:
        time.sleep(4)
        context.close()
        browser.close()

with sync_playwright() as playwright:
    run(playwright)