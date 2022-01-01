import logging
import re
from time import sleep
from typing import List, Any, Union

from mercari.common import Item, Common, _get_soup

# noinspection PyProtectedMember

logger = logging.getLogger(__name__)


class Mercari(Common):

    def fetch_all_items(
            self,
            keyword: str = 'clothes',
            price_min: Union[None, int] = None,
            price_max: Union[None, int] = None,
            max_items_to_fetch: Union[None, int] = 100
    ) -> List[str]:  # list of URLs.
        items_list = []
        for page_id in range(int(1e9)):
            items, search_res_head_tag = self.fetch_items_pagination(keyword, page_id, price_min, price_max)
            items_list.extend(items)
            logger.debug(f'Found {len(items_list)} items so far.')

            if max_items_to_fetch is not None and len(items_list) > max_items_to_fetch:
                logger.debug(f'Reached the maximum items to fetch: {max_items_to_fetch}.')
                break

            if search_res_head_tag is None:
                break
            else:
                search_res_head = str(search_res_head_tag.contents[0]).strip()
                num_items = re.findall('\d+', search_res_head)
                if len(num_items) == 1 and num_items[0] == '0':
                    break
            sleep(2)
        logger.debug('No more items to fetch.')
        return items_list

    def fetch_search_items_pagination(
            self,
            keyword: str,
            page_id: int = 0,
            price_min: Union[None, int] = None,
            price_max: Union[None, int] = None
    ) -> Union[List[str], Any]:  # List of URLS and a HTML marker.
        soup = _get_soup(self._fetch_search_url(page_id, keyword, price_min=price_min, price_max=price_max))
        search_res_head_tag = soup.find('h2', {'class': 'search-result-head'})
        items = [s.find('a').attrs['href'] for s in soup.find_all('section', {'class': 'items-box'})]
        items = [it if it.startswith('http') else 'https://www.mercari.com' + it for it in items]
        return items, search_res_head_tag

    def fetch_user_items_pagination(
            self,
            user_id: int,
            page_id: int = 1
    ) -> Union[List[str], Any]:  # List of URLS and a HTML marker.
        soup = _get_soup(self._fetch_profile_url(user_id, page_id))
        no_items_response = soup.find('p', {'class': re.compile('(Text__H3*)')})
        items = [s.find('a').attrs['href'] for s in
                 soup.find_all('div', {'class': re.compile('(Flex__Box*)[\\S]+\\s(Grid2__Col*)')})]
        items = [it if it.startswith('http') else 'https://www.mercari.com' + it for it in items]
        return items, no_items_response

    def get_item_info(
            self,
            item_url: str
    ) -> Item:
        soup = _get_soup(item_url)
        price = str(soup.find('p', {'data-testid': 'ItemPrice'}).contents[0]).replace('$', '').replace(',', '')
        name = str(soup.find('p', {'data-testid': 'ItemName'}).contents[0])
        desc = str(soup.find('p', {'class': re.compile('(Spec__Description*)')}).contents[0])

        sold_out = soup.find('p', {'class': re.compile('(Product__RibbonText*)')})
        sold_out = sold_out is not None

        photo = soup.find('img', {'class': re.compile('(Product__FullImage*)')}).attrs['src']

        item = Item(name=name, price=price, desc=desc, sold_out=sold_out, url_photo=photo, url=item_url)
        return item

    def _fetch_search_url(
            self,
            page: int = 0,
            keyword: str = 'bicycle',
            price_min: Union[None, int] = None,
            price_max: Union[None, int] = None
    ):
        url = f'https://www.mercari.com/search/?'
        url += f'keyword={keyword}'
        return url

    def _fetch_profile_url(
            self,
            user_id: int,
            page: int = 1
    ):
        url = f'https://www.mercari.com/u/{user_id}/?'
        url += f'page={page}'
        return url

    def fetch_all_items_from_profile(
            self,
            user_id: int
    ) -> List[str]:  # list of URLs.
        items_list = []
        for page_id in range(int(1e9+1)):
            items, no_items_response = self.fetch_user_items_pagination(user_id, page_id)
            items_list.extend(items)
            logger.debug(f'Found {len(items_list)} items so far.')

            if no_items_response is not None:
                break

            sleep(2)
        logger.debug('No more items to fetch.')
        return items_list

    @property
    def name(self) -> str:
        return 'mercari'
