import copy
from datetime import datetime, timedelta

from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.api import taskqueue

import config
import vk
from helpers import stem_and_lower


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

    MAXIMUM_CHANNELS_NUMBER = 100

    @property
    def title_plus(self):
        return self.title or self.link or self.key.id()

    def _update_data(self):
        if self.type == 'in' and 'vk.com' in self.link:
            data = vk.fetch_user_or_group_data(self.link)
        else:
            data = {}
        old_data = copy.deepcopy(self.data)
        if self.data:
            self.data.update(data)
        else:
            self.data = data
        if not old_data == self.data:
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
                taskqueue.add(
                    queue_name=Question.ANSWERS_QUEUE_NAME,
                    url='/tasks/q/{}/fetch_answers'.format(q.key.urlsafe()), method='GET')

    def fetch_new_questions(self):
        """ Does not update channel access time. """
        self._update_data()
        if self.type == 'in' and 'vk.com' in self.link:
            questions_data = vk.fetch_questions(self.data)
            self._update_vk_questions(questions_data)

    def fetch_old_questions(self):
        """ Updates channel access time. """
        self._update_data()
        if self.type == 'in' and 'vk.com' in self.link:
            offset = self.data.get('offset', 0)
            questions_data = vk.fetch_questions(self.data, offset=offset)
            self._update_vk_questions(questions_data)
            if questions_data:
                self.data['offset'] = offset + len(questions_data)
            else:
                self.data['offset'] = 0
            self.put()


class Question(ndb.Model):

    channel = ndb.KeyProperty(kind=Channel)
    text = ndb.TextProperty(default='', verbose_name='Text')
    title = ndb.StringProperty(default='', verbose_name='Title')

    added_to_search_index_at = ndb.DateTimeProperty(default=datetime(2000, 1, 1))
    answers_fetched_at = ndb.DateTimeProperty(default=datetime(2000, 1, 1))
    created_at = ndb.DateTimeProperty()
    last_fetched_answer_at = ndb.DateTimeProperty(default=datetime(2000, 1, 1))

    ANSWERS_QUEUE_NAME = 'answers'
    MAX_ANSWERS_NUMBER = 100
    MAX_TITLE_LENGTH = 500
    NUMBER_OF_QUESTIONS_TO_INDEX = 20
    NUMBER_OF_QUESTIONS_TO_UPDATE_ANSWERS = 20
    SEARCH_INDEX_NAME = 'questions'
    SMALLEST_REINDEX_INTERVAL = timedelta(hours=1)
    VK_POST_URL_TEMPLATE = 'https://vk.com/wall{owner_and_post_id}'

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
            taskqueue.add(
                queue_name=Question.ANSWERS_QUEUE_NAME,
                url='/tasks/q/{}/fetch_answers'.format(q.key.urlsafe()), method='GET')

    @classmethod
    def fetch_old_questions_answers(cls):
        questions = cls.query().order(cls.answers_fetched_at).fetch(cls.NUMBER_OF_QUESTIONS_TO_UPDATE_ANSWERS)
        cls._fetch_questions_answers(questions)
        return len(questions)

    @classmethod
    def fetch_new_questions_answers(cls):
        questions = cls.query().order(-cls.created_at).fetch(cls.NUMBER_OF_QUESTIONS_TO_UPDATE_ANSWERS)
        cls._fetch_questions_answers(questions)
        return len(questions)

    @classmethod
    def add_batch_to_search_index(cls):
        questions = Question.query().order(
            Question.added_to_search_index_at
        ).fetch(Question.NUMBER_OF_QUESTIONS_TO_INDEX)
        for q in questions:
            taskqueue.add(
                url='/tasks/q/{}/add_to_search_index'.format(q.key.urlsafe()), method='GET')
        return len(questions)

    def _update_answers(self, answers):
        for comment in answers:
            a = Answer.get_or_insert(self.key.id() + '_{}'.format(comment['cid']))
            if not a.question:
                a.question = self.key
                a.text = comment['text']
                a.created_at = datetime.fromtimestamp(int(comment['date']))
                a.put()
                if self.last_fetched_answer_at < a.created_at:
                    self.last_fetched_answer_at = a.created_at
        self.answers_fetched_at = datetime.utcnow()
        self.put()

    def fetch_answers(self):
        answers = vk.fetch_post_comments(*self.vk_owner_and_post_id.split('_'))
        self._update_answers(answers)

    def _create_search_document(self):
        answers = Answer.query(Answer.question == self.key).fetch(self.MAX_ANSWERS_NUMBER)
        # join self.text and all answers
        # stem them
        stemmed_content = stem_and_lower(
            ' '.join([self.text] + [a.text for a in answers])
        )
        return search.Document(
            doc_id=self.key.urlsafe(),
            fields=[
                search.TextField(name='title', value=self.title_plus, language=config.LANGUAGE),
                search.TextField(name='stemmed_content', value=stemmed_content, language=config.LANGUAGE),
                search.DateField(name='created_at', value=self.created_at),
            ],
            language=config.LANGUAGE
        )

    def add_to_search_index(self):
        if self.last_fetched_answer_at >= self.added_to_search_index_at:
            search.Index(name=self.SEARCH_INDEX_NAME).put(self._create_search_document())
            self.added_to_search_index_at = datetime.utcnow()
            self.put()
            return True
        else:
            return False


class Answer(ndb.Model):
    question = ndb.KeyProperty(kind=Question)
    text = ndb.TextProperty(default='', verbose_name='Text')
    created_at = ndb.DateTimeProperty(verbose_name='Time Created')
