from city import City
from weather import Weather
from datetime import date
import json
from lxml import etree
from lxml.builder import E
import os
from pathlib import Path
from typing import List, Optional


BASE_DIR = Path(__file__).resolve().parent
TASK_PATH = BASE_DIR.joinpath('parsing_serialization_task')
CITIES_PATH = TASK_PATH.joinpath('source_data')
RESULT_DIR = TASK_PATH.joinpath('result')
DATE = date(2021, 9, 25)
DATE_FORMATTED = '{:%Y_%m_%d}'.format(DATE)
FILENAME = f'{DATE_FORMATTED}.json'
CITIES_LIST = next(os.walk(CITIES_PATH))[1]
COUNTRY = 'Spain'


def get_cities() -> Optional[List[City]]:
    cities_list = []
    for city in CITIES_LIST:
        current_city = City(city)
        data_file = CITIES_PATH.joinpath(city, FILENAME)
        with open(data_file, 'r') as f:
            load = json.load(f)
            for entry in load['hourly']:
                current_city.add_data(entry['temp'], entry['wind_speed'])
        cities_list.append(current_city)
    return cities_list


def get_weather():
    weather = Weather(COUNTRY, DATE)
    cities = get_cities()
    for city in cities:
        weather.add_city_data(city)
    return weather


def build_xml():
    w = get_weather()
    weather_xml = E.weather(
        E.summary(w.get_prepared_xml_values()),
        E.cities(),
        country=w.country, date=str(w.date),
    )
    cities_element = weather_xml.find('cities')
    for city in w.cities.values():
        values = city.get_prepared_xml_values()
        etree.SubElement(cities_element, values['city'], values['attrs'])
    return etree.ElementTree(weather_xml)


def write_xml_to_file(xml_tree: etree.ElementTree):
    os.makedirs(RESULT_DIR, 0o755, exist_ok=True)
    with open(f'{RESULT_DIR}/out.xml', 'wb') as f:
        xml_tree.write(f, pretty_print=True, xml_declaration=True, encoding="utf-8")
    print(f'Saved XML results at {RESULT_DIR}')


if __name__ == '__main__':
    xml = build_xml()
    write_xml_to_file(xml)
