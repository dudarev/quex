"""
Get data for a user or a group.
"""

from __future__ import print_function
import requests
import pprint


GROUP_DATA_ENDPOINT = (
    'https://api.vk.com/method/groups.getById?'
    'group_ids={group_id}&'
    'version=5.50&'
)

USER_DATA_ENDPOINT = (
    'https://api.vk.com/method/users.get?'
    'user_ids={user_ids}&'
    'version=5.50&'
)

GROUP_1 = 'brd24_com'
GROUP_2 = 'brd48'


def get_data(group_or_user_id):
    r = requests.get(
        GROUP_DATA_ENDPOINT.format(
            group_id=group_or_user_id
        )
    )
    res = r.json()
    if res.get('error', False):
        r = requests.get(
            USER_DATA_ENDPOINT.format(
                user_ids=group_or_user_id
            )
        )
        res = r.json()
        if res.get('error', False):
            return None
    return res['response'][0]


data = get_data(GROUP_1)
pprint.pprint(data)

data = get_data(GROUP_2)
pprint.pprint(data)
