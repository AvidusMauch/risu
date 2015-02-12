from datetime import date
import requests
from lxml import html
import fnmatch
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

"""
Class to handle parsing and processing  of the mensa dishes of the comming weeks
"""
class Mensa:
    day_range = 15
    dish_range = 14
    
    def __init__(self): # initiate object with current date and mensa schedule
        self.__lastupdate = date.today()
        self.__dishes = self.import_dishes()
    
    def update(self): # check if new day, and if so update mensa schedule
        if (self.__lastupdate < date.today()):
            self.__lastupdate = date.today()
            self.__dishes = self.import_dishes()

    def import_dishes(self): # get the mensa schedule and save it
        dishes = [[0 for x in range(self.dish_range)] for x in range(self.day_range)] #firts index is for day second for dishnumber
        page = requests.get("http://www.studentenwerk.uni-heidelberg.de/speiseplan")
        tree = html.fromstring(page.text)
        mensa_feld = tree.xpath("//div[@class='collapse-content']")[0]
        self.__day = [0 for x in range(self.day_range)] #saving formated dates as string list
        
        for i in range(0, len(mensa_feld.xpath("table"))): # parsing mensa schdule
            tages_essen = mensa_feld.xpath("table")[i]
            self.__day[i] = mensa_feld.xpath("h4")[i].text
            for j in range(0, len(tages_essen.xpath("tr"))-1):
                dishes_buffer = tages_essen.xpath("tr")[j+1]
                dishes[i][j] = dishes_buffer.xpath("td")[0].text
        return dishes

    def get_dishes(self, day): #get the dishes for a given day and return them
        self.update() #check if new day
        garnish = self.__dishes[day][4] + ", "
        if ((type(day) is int) and 0 <= day <=15): #check for correct day
            for i in range(7, self.dish_range):
                if self.__dishes[day][i] != 0:
                    garnish += self.__dishes[day][i] + ", "        
            # retrun format: D1, D2, E main courses, garnish, Date
            return [self.__dishes[day][2],  self.__dishes[day][3], self.__dishes[day][5], self.__dishes[day][6], garnish[:-2], self.__day[day]]
        else:
            return None

    def search_dish(self, dish_name): #search all dishes fpr given string dish_name
        self.update() # check if new day
        day_buffer = []
        search_pattern = "*" + dish_name + "*"
        found = False
        for i in range(0, self.day_range):
            for j in range(2, self.dish_range):
                if fnmatch.fnmatch(str(self.__dishes[i][j]), str(search_pattern)):
                    found = True
                    # format the output acording to mensa part
                    if 2 <= j <= 3: 
                        day_buffer.append("Am " + self.__day[i] + " gibt es bei Aufgang D: " + self.__dishes[i][j])
                    elif 4 <= j <= 5:
                        day_buffer.append("Am " + self.__day[i] + " gibt es bei Aufgang D: " + self.__dishes[i][j])
                    else: 
                        day_buffer.append("Am " + self.__day[i] + " gibt es bei die Beilage: " + self.__dishes[i][j])
        if found:
            return day_buffer
        else:
            return None

