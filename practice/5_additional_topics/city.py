from typing import Dict, Optional, Any


class City:
    def __init__(self, city_name: str) -> None:
        self.name = city_name
        self.t_max = float('-inf')
        self.t_min = float('+inf')
        self.t_all = 0.0
        self.w_max = float('-inf')
        self.w_min = float('+inf')
        self.w_all = 0.0
        self.data_entries = 0

    def __str__(self):
        return f'City({self.name})'

    def __repr__(self):
        return f'{self.__class__.__name__}('\
               f'{self.name}, {self.t_min}, {self.t_max}, {self.w_min}, {self.w_max})'

    def add_data(self, temp: float, wind: float) -> None:
        self.t_max, self.t_min = max(self.t_max, temp), min(self.t_min, temp)
        self.t_all = self.t_all + temp
        self.w_max, self.w_min = max(self.w_max, wind), min(self.w_min, wind)
        self.w_all = self.w_all + wind
        self.data_entries = self.data_entries + 1

    def get_temperature(self) -> Optional[Dict[str, float]]:
        if self.data_entries:
            return {
                'mean_temp': self.t_all / self.data_entries,
                'max_temp': self.t_max,
                'min_temp': self.t_min,
            }

    def get_wind(self) -> Optional[Dict[str, float]]:
        if self.data_entries:
            return {
                'mean_wind_speed': self.w_all / self.data_entries,
                'max_wind_speed': self.w_max,
                'min_wind_speed': self.w_min,
            }

    def get_prepared_xml_values(self) -> Optional[Dict[str, Any]]:
        values = self.get_wind()
        values.update(self.get_temperature())
        city_name = self.name if ' ' not in self.name else '_'.join(self.name.split(' '))
        return {
            'city': city_name,
            'attrs': {k: repr(round(v, 2)) for k, v in values.items()}
        }
