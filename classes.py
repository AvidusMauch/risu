from datetime import date
import requests
from lxml import html
import fnmatch
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class Mensa:
    day_range = 15
    dish_range = 14
    
    def __init__(self):
        self.__lastupdate = date.today()
        self.__dishes = self.import_dishes()
    
    def update(self):
        if (self.__lastupdate < date.today()):
            self.__lastupdate = date.today()
            self.__dishes = self.import_dishes()

    def import_dishes(self):
        dishes = [[0 for x in range(self.dish_range)] for x in range(self.day_range)] 
        page = requests.get("http://www.studentenwerk.uni-heidelberg.de/speiseplan")
        tree = html.fromstring(page.text)
        mensa_feld = tree.xpath("//div[@class='collapse-content']")[0]
        self.__day = [0 for x in range(self.day_range)] 
        
        for i in range(0, len(mensa_feld.xpath("table"))):
            tages_essen = mensa_feld.xpath("table")[i]
            self.__day[i] = mensa_feld.xpath("h4")[i].text
            for j in range(0, len(tages_essen.xpath("tr"))-1):
                dishes_buffer = tages_essen.xpath("tr")[j+1]
                dishes[i][j] = dishes_buffer.xpath("td")[0].text
        return dishes

    def get_dishes(self, day):
        self.update()
        garnish = self.__dishes[day][4] + ", "
        if ((type(day) is int) and 0 <= day <=15): 
            for i in range(7, self.dish_range):
                if self.__dishes[day][i] != 0:
                    garnish += self.__dishes[day][i] + ", "        
            return [self.__dishes[day][2],  self.__dishes[day][3], self.__dishes[day][5], self.__dishes[day][6], garnish[:-2], self.__day[day]]
        else:
            return None

    def search_dish(self, dish_name):
        self.update()
        day_buffer = []
        search_pattern = "*" + dish_name + "*"
        found = False
        for i in range(0, self.day_range):
            for j in range(2, self.dish_range):
                if fnmatch.fnmatch(str(self.__dishes[i][j]), str(search_pattern)):
                    found = True
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

