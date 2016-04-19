from datetime import datetime

from google.appengine.ext import ndb

import vk


class Config(ndb.Model):
    twitter_consumer_key = ndb.StringProperty(default='', verbose_name='Twitter Consumer Key')
    twitter_consumer_secret = ndb.StringProperty(default='', verbose_name='Twitter Consumer Secret')
    google_analytics_id = ndb.StringProperty(default='', verbose_name='Google Analytics ID')

    @classmethod
    def get(cls):
        return cls.get_or_insert('master')


class Channel(ndb.Model):
    data = ndb.JsonProperty(verbose_name='Channel Data')
    link = ndb.StringProperty(default='', verbose_name='Link')
    last_accessed_at = ndb.DateTimeProperty(auto_now=True, verbose_name='Last Accessed')
    title = ndb.StringProperty(default='', verbose_name='Title')
    type = ndb.StringProperty(default='in', choices=['in', 'out'], verbose_name='Type')

    @property
    def title_plus(self):
        return self.title or self.link or self.key.id()

    @classmethod
    def get_oldest_fetched(cls):
        c = Channel.query(Channel.type == 'in').order(-Channel.last_accessed_at).fetch(1)
        if not c:
            return None
        else:
            return c[0]

    def _update_data(self):
        if self.type == 'in' and 'vk.com' in self.link:
            data = vk.fetch_user_or_group_data(self.link)
        else:
            data = {}
        if self.data:
            self.data.update(data)
        else:
            self.data = data
        self.put()
        return self.data

    def fetch_questions(self):
        data = self._update_data()
        if self.type == 'in' and 'vk.com' in self.link:
            questions_data = vk.fetch_questions(self.data)
            Question.update_vk_questions(questions_data, self)


class Question(ndb.Model):
    channel = ndb.KeyProperty(kind=Channel)
    title = ndb.StringProperty(default='', verbose_name='Title')
    text = ndb.TextProperty(default='', verbose_name='Text')
    updated_at = ndb.DateTimeProperty(auto_now=True, verbose_name='Time Updated')
    created_at = ndb.DateTimeProperty(verbose_name='Time Created')

    MAX_TITLE_LENGTH = 500
    VK_POST_URL_TEPMPLATE = 'https://vk.com/wall{owner_and_post_id}'

    @classmethod
    def update_vk_questions(cls, questions_data, channel):
        for post in questions_data:
            q = cls.get_or_insert('vk:{}_{}'.format(channel.data['uid'], post['id']))
            q.channel = channel.key
            q.text = post['text']
            q.title = post['text'][:cls.MAX_TITLE_LENGTH]
            q.created_at = datetime.fromtimestamp(int(post['date']))
            q.put()

    @property
    def source_url(self):
        owner_and_post_id = self.key.id().split(':')[1]
        return self.VK_POST_URL_TEPMPLATE.format(owner_and_post_id=owner_and_post_id)

    @property
    def title_plus(self):
        return self.title or 'Post'
