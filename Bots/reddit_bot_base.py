from abc import ABC, abstractmethod
from Utilities import sql_util

"""
Base class for subreddit bots. Contains function definitions for loading and saving the
PRAW reddit models.
"""
class RedditBotBase(ABC):

    models = []

    @abstractmethod
    def load_reddit_models(self): pass

    @abstractmethod
    def save_reddit_models(self, models): pass

    @abstractmethod
    def get_child_bots(self): pass

    def update(self):
        self.load_reddit_models()
        self.save_reddit_models()

    def get_oldest_ids(self, records):
        return sql_util.get_oldest_ids(self.table, records)

    def __init__(self, table, limit=None):
        self.table = table
        self.limit = limit
