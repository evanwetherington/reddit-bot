from Utilities import reddit_util
from Bots.reddit_bot_base import RedditBotBase
from Bots.submission_bot import SubmissionBot
from config import *

"""
Retreives and uploads subreddits.
"""
class SubredditBot(RedditBotBase):

    active_subreddit_sql = 'select id, name, updated_dttm, inserted_dttm from subreddit where enabled=0;'

    def __init__(self, limit=Config.SUBREDDIT_LIMIT):
        RedditBotBase.__init__(self, 'subreddit', limit)

    def load_reddit_models(self):
        self.models = []
        for sr in reddit_util.get_reddit_bot().subreddits.popular(limit=self.limit):
            self.models.append(sr)
        return self.models

    def save_reddit_models(self, models=None):
        if not models: models = self.models
        reddit_util.update_subreddits(models)

    def get_child_bots(self):
        submission_bots: list[SubmissionBot] = []
        for sr in self.models:
            submission_bots.append(SubmissionBot(sr))
        return submission_bots

    def list_subreddits(self):
        return [sr.display_name for sr in self.models]