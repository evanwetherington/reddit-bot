from Utilities import reddit_util
from Bots.comment_bot import CommentBot
from Bots.reddit_bot_base import RedditBotBase
from config import *

"""
Retreives and uploads submissions for a given subreddit.
"""
class SubmissionBot(RedditBotBase):

    def __init__(self, subreddit=None, submission_ids=None, limit=Config.SUBMISSION_LIMIT):
        RedditBotBase.__init__(self, 'submission', limit)
        self.subreddit = subreddit
        self.submission_ids = submission_ids
        if not (subreddit or submission_ids):
            raise Exception('Comment bots constructor requires either \'subreddit\' or \'ids\'')

    def load_reddit_models(self):
        self.models = []
        if self.subreddit:
            for sub in self.subreddit.new(limit=self.limit):
                self.models.append(sub)
            return self.models
        elif self.submission_ids:
            bot = reddit_util.get_reddit_bot()
            self.models = [bot.submission(sid) for sid in self.submission_ids]
        else:
            raise Exception('No values found for \'subreddit\' or \'ids\'')
        return self.models

    def save_reddit_models(self, models=None):
        reddit_util.update_posts(models or self.models)

    def get_child_bots(self):
        comment_bots: list[CommentBot] = []
        for comment in self.models:
            comment_bots.append(CommentBot(comment))
        return comment_bots
