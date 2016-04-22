import json

from google.appengine.api import urlfetch


WALL_POSTS_COUNT = 20
WALL_COMMENTS_COUNT = 100
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
WALL_POSTS_ENDPOINT = (
    'https://api.vk.com/method/wall.get?'
    'owner_id={owner_id}&'
    'version=5.50&'
    'offset={offset}&'
    'count={count}&'
)
WALL_COMMENTS_ENDPOINT = (
    'https://api.vk.com/method/wall.getComments?'
    'owner_id={owner_id}&'
    'post_id={post_id}&'
    'offset={offset}&'
    'count={count}&'
)


def _to_json(res):
    """ Converts response from urlfetch to json."""
    return json.loads(res.content)


def fetch_user_or_group_data(link):
    """
    :param link: link to VK user or group
    :return: dict with data from response
    """
    group_or_user_id = link.split('/')[-1]
    r = urlfetch.fetch(
        GROUP_DATA_ENDPOINT.format(
            group_id=group_or_user_id
        )
    )
    res = _to_json(r)
    if res.get('error', False):
        r = urlfetch.fetch(
            USER_DATA_ENDPOINT.format(
                user_ids=group_or_user_id
            )
        )
        res = _to_json(r)
        if res.get('error', False):
            return None
    return res['response'][0]


def fetch_user_wall_posts(uid, offset=0):
    r = urlfetch.fetch(
        WALL_POSTS_ENDPOINT.format(
            owner_id=uid, offset=offset, count=WALL_POSTS_COUNT
        )
    )
    try:
        res = _to_json(r)['response'][1:]
    except KeyError:
        res = []
    return res


def fetch_post_comments(owner_id, post_id, offset=0):
    r = urlfetch.fetch(
        WALL_COMMENTS_ENDPOINT.format(
            owner_id=owner_id, post_id=post_id, offset=offset, count=WALL_COMMENTS_COUNT
        )
    )
    try:
        res = _to_json(r)['response'][1:]
    except KeyError:
        res = []
    return res


def fetch_group_posts(offset=0):
    return []


def fetch_questions(channel_data, offset=0):
    """
    VK channel can be either a user or a group.
    :param channel_data: data obtained with ``fetch_data`` above.
    :param offset: offset to use use to get next questions batch.
    :return:
    """
    uid = channel_data.get('uid', None)
    gid = channel_data.get('gid', None)
    res = []
    if uid:
        res = fetch_user_wall_posts(uid, offset=offset)
    if gid:
        res = fetch_group_posts(gid, offset=offset)
    return res
