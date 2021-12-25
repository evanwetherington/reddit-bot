import operator
import threading
import time
from functools import reduce
from threading import Thread
from Utilities import sql_util, reddit_util
from Bots.submission_bot import SubmissionBot
from Bots.subreddit_bot import SubredditBot
from Utilities.thread_pool import ThreadPool
from config import *


class ShelfStocker:

    def __init__(self):
        print("Created Shelf Stocker")
        self.uploaded_comments = 0
        self.uploaded_submissions = 0
        self.lock = threading.Lock()
        self.update_from_stream()

    def update_from_stream(self):
        self.update_subreddits()
        threads = []
        srbot = SubredditBot()
        srbot.load_reddit_models()
        subreddits = srbot.list_subreddits()
        chnk_subreddits = []
        ctr = 0
        while ctr < len(subreddits):
            chnk_subreddits.append([subreddits[ctr:ctr + Config.DEFAULT_TASK_CHUNKSIZE]])
            ctr += Config.DEFAULT_TASK_CHUNKSIZE
        for i, chnk in enumerate(chnk_subreddits):
            threads.append(Thread(target=self.update_submissions_from_stream, args=chnk,
                                  name="Submission Thread " + str(i)))
            threads.append(Thread(target=self.update_comments_from_stream, args=chnk,
                                  name="Comments Thread " + str(i)))
        while True:
            self.thread_print("Checking status...")
            self.thread_print("Total Uploaded: [Comments - {} Submissions - {}]"
                              .format(self.uploaded_comments, self.uploaded_submissions))
            self.thread_print("Active Thread Count - " + str(threading.active_count()))
            for t in threads:
                if not t.is_alive():
                    self.thread_print("Starting: " + t.name)
                    time.sleep(.25)
                    t.start()
            time.sleep(60)

    def update_submissions_from_stream(self, subreddits):
        reddit = reddit_util.get_reddit_bot()
        subreddit = reddit.subreddit("+".join(subreddits))
        submissions = []
        for submission in subreddit.stream.submissions(pause_after=Config.STREAM_PAUSE_AFTER):
            if submission:
                # print(submission.subreddit, submission.title)
                submissions.append(submission)
                if len(submissions) >= Config.STREAM_SUBMISSION_SIZE:
                    self.thread_print("Uploading " + str(len(submissions)) + " submissions")
                    t = Thread(target=reddit_util.update_posts, args=[submissions[:]])
                    t.start()
                    self.uploaded_submissions += len(submissions)
                    submissions.clear()

    def update_comments_from_stream(self, subreddits):
        reddit = reddit_util.get_reddit_bot()
        subreddit = reddit.subreddit("+".join(subreddits))
        comments = []
        for comment in subreddit.stream.comments(pause_after=Config.STREAM_PAUSE_AFTER):
            if comment:
                comments.append(comment)
                if len(comments) >= Config.STREAM_COMMENT_BATCH_SIZE:
                    self.thread_print("Uploading " + str(len(comments)) + " comments")
                    t = Thread(target=reddit_util.update_comments, args=[comments[:]])
                    t.start()
                    self.uploaded_comments += len(comments)
                    comments.clear()

    def thread_print(self, msg):
        with self.lock:
            print(" - {t:25} {m}".format(t=threading.currentThread().name,  m=msg))

    def update_old_submissions(self, records=Config.UPDATE_OLD_BATCH_SIZE, chunksize=Config.UPDATE_OLD_CHUNKSIZE):
        ids = sql_util.get_oldest_ids('submission', records)
        submission_bots = []
        i = 0
        while i < len(ids):
            submission_bots.append(SubmissionBot(submission_ids=ids[i:i + chunksize]))
            i += chunksize
        self.update_submissions(submission_bots)
        self.update_submission_comments(submission_bots)

    def get_new_submissions(self):
        subreddit_bot = self.update_subreddits()
        self.update_subreddit_submissions(subreddit_bot)

    def update_subreddits(self):
        srbot = SubredditBot()
        srbot.load_reddit_models()
        subreddit_tasks = self.split_tasks(srbot.save_reddit_models, srbot.models, 10)
        print("Updating " + str(len(srbot.models)) + " Subreddits")
        ThreadPool(subreddit_tasks, threads=2).run()
        print("Completed updating subreddits")
        return srbot

    def update_subreddit_submissions(self, subreddit_bot):
        submission_bots = subreddit_bot.get_child_bots()
        return self.update_submissions(submission_bots)

    def update_submissions(self, submission_bots):
        submission_tasks = []
        for bot in submission_bots:
            submission_tasks.append(bot.update)
        print("Updating " + str(len(submission_tasks)) + " Submissions")
        ThreadPool(submission_tasks).run()
        print("Completed updating Submissions")
        return submission_bots

    def update_submission_comments(self, submission_bots):
        comment_tasks = []
        comment_bots = [bot.get_child_bots() for bot in submission_bots]
        for bot in reduce(operator.concat, comment_bots):
            comment_tasks.append(bot.update)
        print("Updating " + str(len(comment_tasks)) + " Submissions")
        ThreadPool(comment_tasks).run()
        print("Completed updating Submissions")
        return comment_bots

    def split_tasks(self, task, args, chunksize=Config.DEFAULT_TASK_CHUNKSIZE):
        tasks = []
        i = 0
        while i < len(args):
            tasks.append((task, args[i:i + chunksize]))
            i += chunksize
        return tasks
