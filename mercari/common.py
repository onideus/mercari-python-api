import logging
import tempfile
from pathlib import Path
from typing import List, Any, Union
from urllib.parse import urlparse

import requests
import wget
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Item:

    def __init__(self,
                 name: str, price: Union[int, str], desc: str,
                 sold_out: bool, url_photo: str, url: str):
        self.name = name
        self.price = int(price)
        self.desc = desc
        self.sold_out = sold_out
        self.url_photo = url_photo
        self.url = url
        self.local_url = _download_photo(self.url_photo)

    def __str__(self) -> str:
        return f'name={self.name}, price={self.price}, desc={self.desc}, sold_out={self.sold_out},' \
               f'url_photo={self.url_photo}, url={self.url}, local_url={self.local_url}'


class Common:

    def fetch_all_items(
            self,
            keyword: str = 'bicycle',
            price_min: int = None,
            price_max: int = None,
            max_items_to_fetch: int = None
    ) -> List[str]:  # list of URLs.
        pass

    def fetch_items_pagination(
            self,
            keyword: str,
            page_id: int,
            price_min: int = None,
            price_max: int = None
    ) -> Union[List[str], Any]:  # List of URLS and a HTML marker.
        pass

    def get_item_info(
            self,
            item_url: str
    ) -> Item:
        pass

    def fetch_url(
            self,
            page: int = 0,
            keyword: str = 'bicycle',
            price_min: Union[None, int] = None,
            price_max: Union[None, int] = None
    ) -> str:
        # https://fril.jp/s?max=30000&min=10000&order=desc&page=2&query=clothes&sort=relevance
        # https://www.mercari.com/jp/search/?page=200&keyword=%E9%9F%BF%EF%BC%91%EF%BC%97&sort_order=&price_max=10000
        pass


def _get_soup(url):
    logger.debug(f'GET: {url}')
    headers = {'User-Agent': "'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36'"}
    response = requests.get(url, headers=headers, timeout=20)
    assert response.status_code == 200
    soup = BeautifulSoup(response.content, 'lxml')
    return soup


def _download_photo(url_photo: str, temp_dir: Union[None, str] = None):
    if temp_dir is None:
        temp_dir = Path(tempfile.gettempdir()) / 'photos'
    else:
        temp_dir = Path(temp_dir)
    if not temp_dir.exists():
        temp_dir.mkdir(parents=True, exist_ok=True)

    logger.debug(f'Selected tmp folder: {temp_dir}.')
    remote_filename = Path(urlparse(url_photo).path).name
    wget.download(url=url_photo, out=str(temp_dir), bar=None)
    local_url = str(temp_dir / remote_filename)
    return local_url
