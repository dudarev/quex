from google.appengine.ext import ndb


class Config(ndb.Model):
    twitter_consumer_key = ndb.StringProperty(default='', verbose_name='Twitter Consumer Key')
    twitter_consumer_secret = ndb.StringProperty(default='', verbose_name='Twitter Consumer Secret')
    google_analytics_id = ndb.StringProperty(default='', verbose_name='Google Analytics ID')

    @classmethod
    def get(cls):
        return cls.get_or_insert('master')


class Channel(ndb.Model):
    link = ndb.StringProperty(default='', verbose_name='Link')
    title = ndb.StringProperty(default='', verbose_name='Title')
    type = ndb.StringProperty(default='in', choices=['in', 'out'], verbose_name='Type')

    @property
    def title_plus(self):
        return self.title or self.link or self.key.id()
