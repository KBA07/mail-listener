"""
File which would be used to fetch the orders from the ECWID API
"""
from time import time

import json
import requests

from logger import LOG
from secrets import ECWID_PRIVATE_TOKEN, ECWID_PUBLIC_TOKEN, STORE_ID

ECWID_HOST = "https://app.ecwid.com/"
TEST_MODE = True
CACHED_CONTENT = json.load(open("response.json"))


class Orders(object):
    DEFAULT_LIMIT = 100
    DEFAULT_OFFSET = 0
    
    DEFAULT_STATUS_200 = 200

    DEFAULT_FROM_TIMESTAMP = 1 # Tue Dec 31 2019 18:30:00 GMT+0000
    DEFAULT_TO_TIMESTAMP = int(time()) # Till The Current System Time


    ORDERS_URI = "api/v3/{store_id}/orders"

    def __init__(self, host, store_id, access_token):
        LOG.debug("Got host as {host}, store id {store_id} and access token as {access_token}")
        self.host = host
        self.store_id = store_id
        self.access_token = access_token

    def _add_auth(self, params):
        params["token"] = self.access_token
    
    def get_orders(self, created_from=DEFAULT_FROM_TIMESTAMP, created_to=DEFAULT_TO_TIMESTAMP, 
        limit=DEFAULT_LIMIT, offset=DEFAULT_FROM_TIMESTAMP):
        URL = self.host + self.ORDERS_URI.format(store_id=self.store_id)
        params = {
            "limit": limit,
            "offset": offset,
            "createdFrom": created_from,
            "createdTo": created_to
        }
        LOG.info(f"Requesting URL: {URL} with parameters: {params}")
        self._add_auth(params)

        content = {}
        if TEST_MODE:
            content = CACHED_CONTENT
        else:
            resp = requests.get(URL, params=params)

            if resp.status_code == self.DEFAULT_STATUS_200:
                LOG.debug(f"Raw content is :{resp.content}")
                content = json.loads(resp.content)
            
        return content

    # A generator object which can be used to iterate efficiently between all the orders between two timestamp
    def get_all_orders(self, created_from=DEFAULT_FROM_TIMESTAMP, created_to=DEFAULT_TO_TIMESTAMP):
        offset = self.DEFAULT_OFFSET
        limit = self.DEFAULT_LIMIT

        total_count = 1

        LOG.info(f"offset {offset}, total_count {total_count}")

        while offset < total_count:
            content = self.get_orders(created_from, created_to, limit, offset)
            total_count = content.get("total", 0)

            LOG.debug(f"Recieved total count as {total_count}")

            if not total_count:
                yield None

            item_len = len(content.get("items"))
            print(f"Yielding total {item_len} number of items")
            for items in content["items"]:
                yield items

            offset += limit


orders_obj = Orders(ECWID_HOST, STORE_ID, ECWID_PRIVATE_TOKEN)
        

# if __name__ == "__main__":
    
#     content = ord.get_orders()

#     print(f"Response for all the orders is {content}")
