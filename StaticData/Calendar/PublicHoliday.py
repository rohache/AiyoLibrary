import workalendar.america as america
import workalendar.usa as usa
import workalendar.asia as asia
import workalendar.europe as europe
import workalendar.africa as africa
import workalendar.oceania as oceania
from datetime import datetime, date, timedelta

american_countries=set(america.__all__.__str__().split("'")) -set(['(',')',", ",","])
usa_countries=set(usa.__all__.__str__().split("'")) -set(['(',')',", ",","])
asian_countries=set(asia.__all__.__str__().split("'")) -set(['(',')',", ",","])
european_countries=set(europe.__all__.__str__().split("'")) -set(['(',')',", ",","])
african_countries=set(africa.__all__.__str__().split("'")) -set(['(',')',", ",","])
oceanian_countries=set(oceania.__all__.__str__().split("'")) -set(['(',')',", ",","])


class publicHoliday:
    def __init__(self,country: str):
        self.country=None
        if country in american_countries:
            exec(f'self.country=america.{country}()')
        elif country in usa_countries:
            exec(f'self.country=usa.{country}()')
        elif country in asian_countries:
            exec(f'self.country=asia.{country}()')
        elif country in european_countries:
            exec(f'self.country=europe.{country}()')
        elif country in african_countries:
            exec(f'self.country=africa.{country}()')
        elif country in oceanian_countries:
            exec(f'self.country=oceania.{country}()')
        else :
            print("Country is not correctly spelled. Please check workalendar list of countries.")

        if country in ['Canada','Australia','NewZealand']:
            self.ISDA_compliance='wednesday_the_third'
        else:
            self.ISDA_compliance = 'friday_the_second'

    def get_holidays(self, start_date: datetime, end_date: datetime):
        years=range(start_date.year,end_date.year,1)
        list_days_off=[]
        [list_days_off.extend(self.country.get_calendar_holidays(year)) for year in years]
        list_days_off_dt = [datetime(temp[0].year,temp[0].month,temp[0].day) for temp in list_days_off]
        return list_days_off_dt
