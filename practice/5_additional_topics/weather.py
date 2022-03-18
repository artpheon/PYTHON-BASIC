from city import City
from datetime import date
from typing import Optional, Dict, Any


class Weather:
    def __init__(self, country_name: str, cur_date: date):
        self.country = country_name
        self.date = cur_date
        self.all_temp = 0
        self.all_wind = 0
        self.coldest = dict(city=None, temp=float('+inf'))
        self.warmest = dict(city=None, temp=float('-inf'))
        self.windiest = dict(city=None, wind=float('-inf'))
        self.cities = dict()

    def add_city_data(self, city: City) -> None:
        temp = city.get_temperature()
        wind = city.get_wind()
        self.all_temp = self.all_temp + temp['mean_temp']
        self.all_wind = self.all_wind + wind['mean_wind_speed']
        if self.coldest['temp'] > temp['min_temp']:
            self.coldest['temp'] = temp['min_temp']
            self.coldest['city'] = city.name
        if self.warmest['temp'] < temp['max_temp']:
            self.warmest['temp'] = temp['max_temp']
            self.warmest['city'] = city.name
        if self.windiest['wind'] < wind['max_wind_speed']:
            self.windiest['wind'] = wind['max_wind_speed']
            self.windiest['city'] = city.name
        self.cities[city.name] = city

    def get_mean_temp(self) -> Optional[float]:
        if self.cities:
            return self.all_temp / len(self.cities)

    def get_mean_wind(self) -> Optional[float]:
        if self.cities:
            return self.all_wind / len(self.cities)

    def get_prepared_xml_values(self) -> Optional[Dict[str, Any]]:
        return {
            'mean_temp': repr(round(self.get_mean_temp(), 2)),
            'mean_wind_speed': repr(round(self.get_mean_wind(), 2)),
            'coldest_place': self.coldest['city'],
            'warmest_place': self.warmest['city'],
            'windiest_place': self.windiest['city']
        }
