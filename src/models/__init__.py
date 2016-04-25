from datetime import datetime

from google.appengine.ext import ndb
from google.appengine.api import taskqueue

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

    def _update_vk_questions(self, questions_data):
        for post in questions_data:
            uid = self.data.get('uid', None)
            gid = self.data.get('gid', None)
            id_ = uid or -gid
            q_id = 'vk:{}_{}'.format(id_, post['id'])
            q = Question.get_or_insert(q_id)
            if not q.channel:
                q.channel = self.key
                q.text = post['text']
                q.title = post['text'][:q.MAX_TITLE_LENGTH]
                q.created_at = datetime.fromtimestamp(int(post['date']))
                q.put()
            taskqueue.add(url='/tasks/q/{}/fetch_answers'.format(q.key.urlsafe()), method='GET')

    def fetch_questions(self):
        """
        Fetches new and old questions in the channel.
        """
        self._update_data()
        if self.type == 'in' and 'vk.com' in self.link:

            # fetch new
            questions_data = vk.fetch_questions(self.data)
            self._update_vk_questions(questions_data)

            # fetch old
            offset = self.data.get('offset', 0)
            questions_data = vk.fetch_questions(self.data, offset=offset)
            self._update_vk_questions(questions_data)

            if questions_data:
                self.data['offset'] = offset + vk.WALL_POSTS_COUNT
            else:
                self.data['offset'] = 0
            self.put()


class Question(ndb.Model):
    answers_fetched_at = ndb.DateTimeProperty(default=datetime(2000, 1, 1), verbose_name='Time Answers Fetched')
    channel = ndb.KeyProperty(kind=Channel)
    created_at = ndb.DateTimeProperty(verbose_name='Time Created')
    text = ndb.TextProperty(default='', verbose_name='Text')
    title = ndb.StringProperty(default='', verbose_name='Title')
    updated_at = ndb.DateTimeProperty(auto_now=True, verbose_name='Time Updated')

    MAX_TITLE_LENGTH = 500
    VK_POST_URL_TEMPLATE = 'https://vk.com/wall{owner_and_post_id}'
    ANSWERS_UPDATE_NUMBER = 20

    @property
    def vk_owner_and_post_id(self):
        """
        VK questions have id in the form "vk:<owner_id>_<post_id>".
        This method returns "<owner_id>_<post_id>".
        """
        return self.key.id().split(':')[1]

    @property
    def source_url(self):
        return self.VK_POST_URL_TEMPLATE.format(owner_and_post_id=self.vk_owner_and_post_id)

    @property
    def title_plus(self):
        return self.title or 'Post'

    @staticmethod
    def _fetch_questions_answers(questions):
        for q in questions:
            taskqueue.add(url='/tasks/q/{}/fetch_answers'.format(q.key.urlsafe()), method='GET')

    @classmethod
    def fetch_old_questions_answers(cls):
        questions = cls.query().order(cls.answers_fetched_at).fetch(cls.ANSWERS_UPDATE_NUMBER)
        cls._fetch_questions_answers(questions)
        return len(questions)

    @classmethod
    def fetch_new_questions_answers(cls):
        questions = cls.query().order(-cls.created_at).fetch(cls.ANSWERS_UPDATE_NUMBER)
        cls._fetch_questions_answers(questions)
        return len(questions)

    def _update_answers(self, answers):
        for comment in answers:
            a = Answer.get_or_insert(self.key.id() + '_{}'.format(comment['cid']))
            if not a.question:
                a.question = self.key
                a.text = comment['text']
                a.created_at = datetime.fromtimestamp(int(comment['date']))
                a.put()
        self.answers_fetched_at = datetime.utcnow()
        self.put()

    def fetch_answers(self):
        answers = vk.fetch_post_comments(*self.vk_owner_and_post_id.split('_'))
        self._update_answers(answers)


class Answer(ndb.Model):
    question = ndb.KeyProperty(kind=Question)
    text = ndb.TextProperty(default='', verbose_name='Text')
    created_at = ndb.DateTimeProperty(verbose_name='Time Created')
