"""
Collect posts and comments to them from a VK user wall.
Save them to file.
"""

from __future__ import print_function
import codecs
import requests
from datetime import datetime


OWNER_ID = '145645005'
TOTAL_POSTS = 10000

WALL_ENDPOINT = (
    'https://api.vk.com/method/wall.get?'
    'owner_id={owner_id}&'
    'version=5.50&'
    'offset={offset}'
)
COMMENTS_ENDPOINT = (
    'https://api.vk.com/method/wall.getComments?'
    'owner_id={owner_id}&'
    'post_id={post_id}&'
    'offset={offset}&'
    'count=100'
)
POST_URL_TEPMPLATE = 'https://vk.com/brd24_com?w=wall{owner_id}_{post_id}'


def get_posts(offset=0):
    r = requests.get(
        WALL_ENDPOINT.format(
            owner_id=OWNER_ID, offset=offset
        )
    )
    try:
        res = r.json()['response'][1:]
    except KeyError:
        res = []
    return res


def get_comments(post_id, offset=0):
    r = requests.get(
        COMMENTS_ENDPOINT.format(
            owner_id=OWNER_ID, post_id=post_id, offset=offset
        )
    )
    try:
        res = r.json()['response'][1:]
    except KeyError:
        res = []
    return res


f = codecs.open('out.txt', 'w', encoding='utf-8')

count = 0
while count < TOTAL_POSTS:
    posts = get_posts(offset=count)
    for p in posts:
        count += 1
        dt = datetime.fromtimestamp(p['date'])
        post_id = p['id']
        print(count, file=f)
        print(dt.strftime('%Y-%m-%d'), file=f)
        print(p['text'], file=f)
        print(POST_URL_TEPMPLATE.format(owner_id=OWNER_ID, post_id=post_id), file=f)
        comments = get_comments(post_id)
        for c in comments:
            print('-- ' + c['text'], file=f)
        print(40 * '-', file=f)
    print(count)

f.close()
