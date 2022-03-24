"""
There is a list of most active Stocks on Yahoo Finance https://finance.yahoo.com/most-active.
You need to compose several sheets based on data about companies from this list.
To fetch data from webpage you can use requests lib. To parse html you can use beautiful soup lib or lxml.
Sheets which are needed:
1. 5 stocks with most youngest CEOs and print sheet to output. You can find CEO info in Profile tab of concrete stock.
    Sheet's fields: Name, Code, Country, Employees, CEO Name, CEO Year Born.
2. 10 stocks with best 52-Week Change. 52-Week Change placed on Statistics tab.
    Sheet's fields: Name, Code, 52-Week Change, Total Cash
3. 10 largest holds of Blackrock Inc. You can find related info on the Holders tab.
    Blackrock Inc is an investment management corporation.
    Sheet's fields: Name, Code, Shares, Date Reported, % Out, Value.
    All fields except first two should be taken from Holders tab.


Example for the first sheet (you need to use same sheet format):
==================================== 5 stocks with most youngest CEOs ===================================
| Name        | Code | Country       | Employees | CEO Name                             | CEO Year Born |
---------------------------------------------------------------------------------------------------------
| Pfizer Inc. | PFE  | United States | 78500     | Dr. Albert Bourla D.V.M., DVM, Ph.D. | 1962          |
...

About sheet format:
- sheet title should be aligned to center
- all columns should be aligned to the left
- empty line after sheet

Write at least 2 tests on your choose.
Links:
    - requests docs: https://docs.python-requests.org/en/latest/
    - beautiful soup docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    - lxml docs: https://lxml.de/
"""
import random

import bs4
from bs4 import BeautifulSoup as BS
import requests
import re
import logging
from prettytable import PrettyTable
import json
from typing import Dict, Optional, List, Any, Iterable, Tuple


class StockInfo:
    DEBUG = False
    BASE_URL = 'https://finance.yahoo.com'
    MOST_ACTIVE = BASE_URL + '/most-active'
    COMPANIES_NUM = 0
    BLK = 'BLK'

    def _prepare_session(self) -> None:
        """
        Getting sample user agents from a json file.
        """
        with open('user_agents.json', 'r') as fp:
            self.headers_list = json.load(fp)
        self._update_session()

    def _update_session(self) -> None:
        """
        Creating a new requests session and updating a user agent.
        """
        self.session = requests.Session()
        self.session.headers = random.choice(self.headers_list)
        logging.info('updating session and user-agent.')

    def _set_logging(self) -> None:
        """
        Setting up logging if DEBUG variable is True.
        """
        if self.DEBUG:
            fmt = '%(asctime)s — %(name)s — %(funcName)s:%(lineno)d — %(message)s'
            logging.basicConfig(filename='stock_info.log', filemode='w',
                                format=fmt,
                                level=logging.DEBUG)

    def __init__(self) -> None:
        self.companies = dict()
        self._prepare_session()
        self._set_logging()

    def get_soup_from_url(self, url: str, params: Optional[Dict[str, int]] = None) -> bs4.BeautifulSoup:
        """
        Takes a URL, gets the page from it, and returns a BS4 instance from the page.
        """
        page = self.session.get(url, params=params)
        if not page.ok:
            raise requests.exceptions.ConnectionError
        return BS(page.content, 'html.parser')

    @staticmethod
    def re_parse_results(string: str) -> int:
        comp = re.compile(r'.*?of (\d+) results.*?')
        return int(comp.search(string).group(1))

    def gen_listing_soups(self) -> Iterable[bs4.BeautifulSoup]:
        """
        Generator of pages, where the companies are listed.
        """
        count = 100
        n = self.COMPANIES_NUM // count + 1
        for i in range(n):
            logging.info(f'getting page at count: {count}, offset: {i * count}')
            yield self.get_soup_from_url(
                self.MOST_ACTIVE,
                {'count': count, 'offset': i * count}
            )

    @staticmethod
    def parse_info_from_trows(soup: bs4.BeautifulSoup) -> Dict[str, Dict[Any, str]]:
        """
        Parsing the code and title of a company from the page.
        """
        table = soup.select('div#scr-res-table>div>table>tbody>tr')
        logging.info(f'Found {len(table)} rows in a table')
        result = dict()
        for tr in table:
            link = tr.select_one('a')
            result[link.text] = dict(title=link['title'])
        return result

    def get_basic_info(self) -> None:
        """
        Fills in a dict with {code name: full title} info about companies.
        """
        soup = self.get_soup_from_url(self.MOST_ACTIVE)
        res_num = soup.find(
            'span',
            {'class': ""},
            text=lambda text: text and 'results' in text).text
        self.COMPANIES_NUM = self.re_parse_results(res_num)
        logging.info(f'Found {self.COMPANIES_NUM} results in total.')
        links_generator = self.gen_listing_soups()
        for link in links_generator:
            self.companies.update(self.parse_info_from_trows(link))

    def collect_statistics(self, code: str) -> None:
        """
        Collects 52-Week Change and Total Cash from statistics tab of a company.
        """
        soup = self.get_soup_from_url(f'{self.BASE_URL}/quote/{code}/key-statistics')
        section = soup.select_one('div#Main').find('section')
        if not section:
            raise requests.exceptions.ConnectionError
        tcells = section.find_all('td')
        week_change = total_cash = None
        for cell in tcells:
            if cell.text == '52-Week Change 3':
                week_change = cell.next_sibling.text.strip('%')
            if cell.text == 'Total Cash (mrq)':
                total_cash = cell.next_sibling.text
        if week_change and week_change != 'N/A':
            week_change = float(week_change)
        else:
            week_change = None
        self.companies[code]['statistics'] = {
            'week_change': week_change,
            'total_cash': total_cash,
        }

    def collect_profile(self, code: str) -> None:
        """
        Collects Country, Employees, CEO Name and CEO Year of birth for a company.
        """
        try:
            soup = self.get_soup_from_url(f'{self.BASE_URL}/quote/{code}/profile')
            section = soup.select_one('div#Main').find('section')
            country = section.p.a.previous_sibling.previous_sibling.text
            employees = section.find_all('p')[1].find_all('span')[-1].text
            tr = section.tbody.tr.find_all('span')
            ceo_name = tr[0].text
            ceo_year = tr[-1].text
            ceo_year = int(ceo_year) if (ceo_year and ceo_year != 'N/A') else None
        except Exception as exc:
            raise requests.exceptions.ConnectionError from exc
        else:
            self.companies[code]['profile'] = {
                'country': country,
                'employees': employees,
                'ceo_name': ceo_name,
                'ceo_year': ceo_year,
            }

    def collect_holders(self, code: str) -> None:
        """
        Collects Shares, Date Reported, % Out, Value about a company.
        """
        try:
            soup = self.get_soup_from_url(f'{self.BASE_URL}/quote/{code}/holders')
            section = soup.select_one('div#Main').section
            trows = section.find(
                text='Top Institutional Holders'
            ).next_element.find('tbody').find_all('tr')
        except Exception as exc:
            raise requests.exceptions.ConnectionError from exc
        else:
            if code not in self.companies:
                self.companies[code] = dict()
            holders = dict()
            i = 1
            for row in trows:
                holders[i] = dict()
                vals = [str(s) for s in list(row.strings)]
                holders[i]['name'] = vals[0]
                holders[i]['shares'] = vals[1]
                holders[i]['date_reported'] = vals[2]
                holders[i]['percent_out'] = vals[3]
                holders[i]['value'] = vals[4]
                i = i + 1
            self.companies[code]['holders'] = holders

    def collect_blk_holders(self) -> None:
        """
        Collecting info about top 10 Blackrock Inc holders.
        """
        try:
            self.collect_holders(self.BLK)
        except requests.exceptions.ConnectionError:
            self._update_session()
            try:
                self.collect_holders(self.BLK)
            except requests.exceptions.ConnectionError:
                logging.warning('Black Rock holdings data have not been collected')

    def _get_full_info(self, code: str) -> None:
        """
        Trying to get data for a company by its code, changing user-agent on exception.
        """
        try:
            self.collect_statistics(code)
            self.collect_profile(code)
        except requests.exceptions.ConnectionError:
            self._update_session()
            try:
                self.collect_statistics(code)
                self.collect_profile(code)
            except requests.exceptions.ConnectionError:
                logging.warning(f'Some data for {code} have not been collected.')

    def get_full_info(self) -> None:
        """
        Collecting full info about the companies by their code names.
        """
        logging.info(f'Scraped {len(self.companies)} results')
        i = 1
        for k in self.companies:
            print(f'Collecting full data for {k}: ', end='')
            self._get_full_info(k)
            print('(OK)')
            if i % 10 == 0:
                print(f'Done: {i / self.COMPANIES_NUM * 100:.1f}%.')
            i += 1

    def close(self) -> None:
        self.session.close()

    def save_json(self, name: str) -> None:
        with open(name, 'w') as fp:
            json.dump(obj=self.companies, fp=fp, indent=4, sort_keys=True)

    def find_five_youngest(self) -> List[Tuple[str, int]]:
        rows = []
        for k, v in self.companies.items():
            if 'profile' in v and v['profile']['ceo_year']:
                rows.append((k, v['profile']['ceo_year']))
        return sorted(rows, reverse=True, key=lambda x: x[1])[:5]

    def sheet_youngest_ceo(self) -> PrettyTable:
        """
        Prepares a sheet about top 5 stocks with the youngest CEOs.
        """
        x = PrettyTable()
        x.title = '5 stocks with the youngest CEOs'
        x.field_names = ['Name', 'Code', 'Country', 'Employees', 'CEO Name', 'CEO Year']
        youngest = self.find_five_youngest()
        for row in youngest:
            code = row[0]
            year = row[1]
            title = self.companies[code]['title']
            country = self.companies[code]['profile']['country']
            employees = self.companies[code]['profile']['employees'] or 'N/A'
            ceo = self.companies[code]['profile']['ceo_name']
            x.add_row([title, code, country, employees, ceo, year])
        x.align = 'l'
        return x

    def find_best_52_week_change(self) -> List[Tuple[str, float]]:
        best_change = []
        for k, v in self.companies.items():
            if 'statistics' in v and v['statistics']['week_change']:
                best_change.append((k, v['statistics']['week_change']))
        return sorted(best_change, reverse=True, key=lambda x: x[1])[:10]

    def sheet_best_52_change(self) -> PrettyTable:
        """
        Prepares a sheet with top 10 stocks with the best 52-week change.
        """
        x = PrettyTable()
        x.title = '10 stocks with the best 52-week change'
        x.field_names = ['Name', 'Code', '52-Week Change', 'Total Cash']
        best_change = self.find_best_52_week_change()
        for row in best_change:
            code = row[0]
            change = f'{row[1]}%'
            title = self.companies[code]['title']
            total_cash = self.companies[code]['statistics']['total_cash']
            x.add_row([title, code, change, total_cash])
        x.align = 'l'
        return x

    def sheet_10_holds_blk(self) -> PrettyTable:
        """
        Prepares a sheet with top 10 largest holds of Blackrock Inc.
        """
        x = PrettyTable()
        x.title = '10 largest holds of Blackrock Inc'
        x.field_names = ['Name', 'Shares', 'Date Reported', '% Out', 'Value']
        holders = self.companies['BLK']['holders']
        for v in holders.values():
            x.add_row([
                v['name'], v['shares'], v['date_reported'],
                v['percent_out'], v['value']
            ])
        x.align = 'l'
        return x


if __name__ == '__main__':
    info = StockInfo()
    print('Collecting basic info about companies... ', end='')
    info.get_basic_info()
    print(f'(OK) Collected {info.COMPANIES_NUM} companies in total.')
    info.get_full_info()
    info.collect_blk_holders()
    print('Done: 100%')
    info.save_json('data.json')
    info.close()

    with open('table_youngest_ceo.txt', 'w') as f:
        f.write(info.sheet_youngest_ceo().get_string() + '\n')
    with open('table_blackrock_top_holders.txt', 'w') as f:
        f.write(info.sheet_10_holds_blk().get_string() + '\n')
    with open('table_best_52_week_change.txt', 'w') as f:
        f.write(info.sheet_best_52_change().get_string() + '\n')
