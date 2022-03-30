import requests
import os
from time import perf_counter
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple

API_KEY = "Uw15whEUb9tHSVxLMsWZ0tcPkziA8qN9Kw0uZxmf"
APOD_ENDPOINT = 'https://api.nasa.gov/planetary/apod'
OUTPUT_IMAGES = './output'


def get_apod_metadata(start_date: str, end_date: str, api_key: str) -> list:
    s = requests.Session()
    res = s.get(url=APOD_ENDPOINT,
                params=dict(start_date=start_date, end_date=end_date, api_key=api_key),
                timeout=10)
    return res.json()


def download_one_image(args: Tuple[str, str]):
    with open(f'{OUTPUT_IMAGES}/{args[1]}', 'wb') as f:
        f.write(requests.get(args[0]).content)


def download_apod_images(metadata: list):
    download_data = [
        (data['url'], data['url'].split('/')[-1])
        for data in metadata
        if data['media_type'] == 'image'
    ]
    with ThreadPoolExecutor(max_workers=min(32, len(download_data))) as executor:
        executor.map(download_one_image, download_data)


if __name__ == '__main__':
    # between 2020-07-06 and 2020-08-06
    if not os.path.exists(OUTPUT_IMAGES):
        os.mkdir(OUTPUT_IMAGES)
    start = perf_counter()
    metadata = get_apod_metadata(
        start_date='2020-07-06',
        end_date='2020-08-06',
        api_key=API_KEY,
    )
    download_apod_images(metadata=metadata)
    duration = perf_counter() - start
    print(f'Downloading files took {duration:.2f} seconds')
