from Utilities import reddit_util
from Bots.reddit_bot_base import RedditBotBase
from config import *

"""
Retreives and uploads comments for a given submission.
"""
class CommentBot(RedditBotBase):

    def __init__(self, submission=None, ids=None, limit=Config.COMMENT_LIMIT):
        RedditBotBase.__init__(self, 'comment', limit)
        self.ids = ids
        self.submission = submission
        if not (submission or ids):
            raise Exception('Comment bots constructor requires either \'submission\' or \'ids\'')

    def load_reddit_models(self):
        self.models = []
        if self.submission:
            self.submission.comments.replace_more(limit=None)
            self.models = list(self.submission.comments.list())
        elif self.ids:
            bot = reddit_util.get_reddit_bot()
            self.models = [bot.comment(cid[3:]) for cid in self.ids]
        else:
            raise Exception('No values found for \'submission\' or \'ids\'')
        return self.models

    def save_reddit_models(self, models=None):
        reddit_util.update_comments(models or self.models)

    def get_child_bots(self): pass
