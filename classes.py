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
    def __init__(self): # initiate object with current date and mensa schedule
        self.__lastupdate = date.today()
        [self.__dishes, self.__day] = self.import_dishes()
    
    def update(self): # check if new day, and if so update mensa schedule
        if (self.__lastupdate < date.today()):
            self.__lastupdate = date.today()
            [self.__dishes,self.__day] = self.import_dishes()

    def allesdreck(self):
        page = requests.get("http://rolf-schneider.net/mensa/?translation=reality")
        tree = html.fromstring(page.text)
        allesdreck = tree.xpath("//td[@id='meal']")
        garnish = allesdreck[4].text
        for i in range(7, len(allesdreck)):
            garnish += allesdreck[i].text + ", " 
        return [allesdreck[2].text,  allesdreck[3].text, allesdreck[5].text, allesdreck[6].text, garnish[:-2]]

    def import_dishes(self): # get the mensa schedule and save it
        page = requests.get("http://www.studentenwerk.uni-heidelberg.de/speiseplan")
        tree = html.fromstring(page.text)
        mensa_feld = tree.xpath("//div[@class='collapse-content']")[0]
        dishes = []
        
        #loop trough all avaiable days
        for i in range(0, len(mensa_feld.xpath("table[@class='mensa mash-info-table']"))):
            dish_menu = mensa_feld.xpath("table[@class='mensa mash-info-table']")[i]
            day_menu_buffer = []
            #loop for all avaiable dishes, first 3 entries are useless
            for j in range(0, len(dish_menu.xpath("tr"))-3):
                dishes_buffer = dish_menu.xpath("tr")[j+3]
                day_menu_buffer.append(dishes_buffer.xpath("td")[0].text)
            dishes.append(day_menu_buffer)

        day = [] #saving formated dates as string list
        for k in range(0, len(mensa_feld.xpath("h4"))):
            day_buffer = mensa_feld.xpath("h4")[k]
            if day_buffer.text[0] != "S":
                day.append(day_buffer.text)
     
        return dishes, day
    
    def get_dishes(self, day): #get the dishes for a given day and return them
        self.update() #check if new day
        if ((type(day) is int) and 0 <= day <len(self.__dishes)): #check for correct day
            garnish = self.__dishes[day][2] + ", "
            for i in range(5, len(self.__dishes[day])):
                garnish += self.__dishes[day][i] + ", "        
            # retrun format: D1, D2, E main courses, garnish, Date
            return [self.__dishes[day][0],  self.__dishes[day][1], self.__dishes[day][3], self.__dishes[day][4], garnish[:-2], self.__day[day]]
        else:
            return None

    def search_dish(self, dish_name): #search all dishes fpr given string dish_name
        self.update() # check if new day
        day_buffer = []
        search_pattern = "*" + dish_name + "*"
        found = False
        for i in range(0, len(self.__dishes)):
            for j in range(0,len(self.__dishes[i]) ):
                if fnmatch.fnmatch(str(self.__dishes[i][j]), str(search_pattern)):
                    found = True
                    # format the output acording to mensa part
                    if 0 <= j <= 1: 
                        day_buffer.append("Am " + self.__day[i] + "(%d) gibt es bei Aufgang D: " % i + self.__dishes[i][j])
                    elif 3 <= j <= 4:
                        day_buffer.append("Am " + self.__day[i] + "(%d) gibt es bei Aufgang E: " % i + self.__dishes[i][j])
                    else: 
                        day_buffer.append("Am " + self.__day[i] + "(%d) gibt es die Beilage: " % i+ self.__dishes[i][j])
        if found:
            return day_buffer
        else:
            return None

