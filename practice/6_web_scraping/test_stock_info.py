import pytest
from stock_info import StockInfo

TEST_DICT = {
    "AAPL": {
        "profile": {
            "ceo_name": "Mr. Timothy D. Cook",
            "ceo_year": 1961,
            "country": "United States",
            "employees": "100,000"
        },
        "statistics": {
            "total_cash": "63.91B",
            "week_change": 40.58
        },
        "title": "Apple Inc."
    },
    "AMC": {
        "profile": {
            "ceo_name": "Mr. Adam M. Aron",
            "ceo_year": 1955,
            "country": "United States",
            "employees": "3,046"
        },
        "statistics": {
            "total_cash": "1.59B",
            "week_change": 102.44
        },
        "title": "AMC Entertainment Holdings, Inc."
    },
    "AMD": {
        "profile": {
            "ceo_name": "Dr. Lisa T. Su Ph.D.",
            "ceo_year": 1970,
            "country": "United States",
            "employees": "15,500"
        },
        "statistics": {
            "total_cash": "3.61B",
            "week_change": 50.08
        },
        "title": "Advanced Micro Devices, Inc."
    },
    "BABA": {
        "profile": {
            "ceo_name": "Mr. Joseph C.  Tsai",
            "ceo_year": 1964,
            "country": "China",
            "employees": "259,316"
        },
        "statistics": {
            "total_cash": "494.93B",
            "week_change": -49.92
        },
        "title": "Alibaba Group Holding Limited"
    },
    "BLK": {
        "holders": {
            "1": {
                "date_reported": "Dec 30, 2021",
                "name": "Vanguard Group, Inc. (The)",
                "percent_out": "8.05%",
                "shares": "12,236,134",
                "value": "11,202,914,845"
            },
            "2": {
                "date_reported": "Dec 30, 2021",
                "name": "Blackrock Inc.",
                "percent_out": "6.67%",
                "shares": "10,141,086",
                "value": "9,284,772,698"
            },
            "3": {
                "date_reported": "Dec 30, 2021",
                "name": "Capital World Investors",
                "percent_out": "5.09%",
                "shares": "7,737,458",
                "value": "7,084,107,046"
            },
            "4": {
                "date_reported": "Dec 30, 2021",
                "name": "State Street Corporation",
                "percent_out": "4.30%",
                "shares": "6,539,029",
                "value": "5,986,873,391"
            },
            "5": {
                "date_reported": "Dec 30, 2021",
                "name": "Bank of America Corporation",
                "percent_out": "3.44%",
                "shares": "5,225,461",
                "value": "4,784,223,073"
            },
            "6": {
                "date_reported": "Dec 30, 2021",
                "name": "Temasek Holdings (Private) Limited",
                "percent_out": "3.35%",
                "shares": "5,092,825",
                "value": "4,662,786,857"
            },
            "7": {
                "date_reported": "Dec 30, 2021",
                "name": "FMR, LLC",
                "percent_out": "2.72%",
                "shares": "4,142,281",
                "value": "3,792,506,792"
            },
            "8": {
                "date_reported": "Dec 30, 2021",
                "name": "Wellington Management Group, LLP",
                "percent_out": "2.67%",
                "shares": "4,065,146",
                "value": "3,721,885,071"
            },
            "9": {
                "date_reported": "Dec 30, 2021",
                "name": "Capital International Investors",
                "percent_out": "2.16%",
                "shares": "3,288,052",
                "value": "3,010,408,889"
            },
            "10": {
                "date_reported": "Dec 30, 2021",
                "name": "Wells Fargo & Company",
                "percent_out": "1.64%",
                "shares": "2,495,532",
                "value": "2,284,809,277"
            }
        }
    },
    "DIDI": {
        "profile": {
            "ceo_name": "Mr. Wei  Cheng",
            "ceo_year": 1983,
            "country": "China",
            "employees": "15,914"
        },
        "statistics": {
            "total_cash": "61.2B",
            "week_change": -71.71
        },
        "title": "DiDi Global Inc."
    },
    "F": {
        "profile": {
            "ceo_name": "Mr. William Clay Ford Jr.",
            "ceo_year": 1957,
            "country": "United States",
            "employees": "183,000"
        },
        "statistics": {
            "total_cash": "36.46B",
            "week_change": 40.77
        },
        "title": "Ford Motor Company"
    },
    "NIO": {
        "profile": {
            "ceo_name": "Mr. William  Li",
            "ceo_year": 1974,
            "country": "China",
            "employees": "7,763"
        },
        "statistics": {
            "total_cash": "43.37B",
            "week_change": -41.1
        },
        "title": "NIO Inc."
    },
    "NVDA": {
        "profile": {
            "ceo_name": "Mr. Jen-Hsun  Huang",
            "ceo_year": 1963,
            "country": "United States",
            "employees": "22,473"
        },
        "statistics": {
            "total_cash": "21.21B",
            "week_change": 109.79
        },
        "title": "NVIDIA Corporation"
    },
    "PDD": {
        "profile": {
            "ceo_name": "Mr. Lei  Chen",
            "ceo_year": 1980,
            "country": "China",
            "employees": ""
        },
        "statistics": {
            "total_cash": "92.94B",
            "week_change": -61.72
        },
        "title": "Pinduoduo Inc."
    },
    "SOFI": {
        "profile": {
            "ceo_name": "Mr. George Thompson Hutton",
            "ceo_year": 1956,
            "country": "United States",
            "employees": "2,500"
        },
        "statistics": {
            "total_cash": "494.71M",
            "week_change": -41.02
        },
        "title": "SoFi Technologies, Inc."
    },
}


@pytest.fixture
def stock_info_obj():
    info = StockInfo.__new__(StockInfo)
    info.companies = TEST_DICT
    return info


def test_youngest_ceo(stock_info_obj):
    ceos = stock_info_obj.find_five_youngest()
    assert len(ceos) == 5
    assert [1983, 1980, 1974, 1970, 1964] == [val[1] for val in ceos]


def test_blackrock_holders(stock_info_obj):
    holders = stock_info_obj.sheet_10_holds_blk()
    assert holders.rows[0] == ['Vanguard Group, Inc. (The)', '12,236,134', 'Dec 30, 2021', '8.05%', '11,202,914,845']
    assert holders.rows[-1] == ['Wells Fargo & Company', '2,495,532', 'Dec 30, 2021', '1.64%', '2,284,809,277']


def test_best_52_week_change(stock_info_obj):
    change = stock_info_obj.find_best_52_week_change()
    assert len(change) == 10
    assert [val[1] for val in change] == [109.79, 102.44, 50.08, 40.77, 40.58, -41.02, -41.1, -49.92, -61.72, -71.71]
