from Utilities.sql_util import *
import praw

def get_reddit_bot():
    try:
        file = open('credentials.json')
        credentials = json.load(file)
        return praw.Reddit(client_id=credentials["praw_client_id"],
                           client_secret=credentials["praw_client_secret"],
                           user_agent=credentials["praw_user_agent"])
    except FileNotFoundError as fnfe:
        print('Could not find user credentials file.')
        raise fnfe
    except Exception as e:
        print("Error loading praw instance.")
        raise e


def update_posts(posts):
    table = 'submission'
    cols = 'id, title, author, author_id, created_utc, is_original_content, subreddit, subreddit_id' \
           ', score, is_self, link_flair_text, locked, over_18, permalink, selftext, upvote_ratio, num_comments'
    values = []
    for post in posts:
        try:
            author_name = None if post.author is None else post.author.name
            author_id = None
            val = (post.id, post.title, author_name, author_id, post.created_utc
                   , post.is_original_content, post.subreddit.display_name, post.subreddit.id
                   , post.score, post.is_self, post.link_flair_text
                   , post.locked, post.over_18, post.permalink, post.selftext, post.upvote_ratio, post.num_comments)
            values.append(val)
        except Exception as error:
            print(error)
    insert_with_replacements(table, cols, values)


def update_subreddits(srs):
    print("Updating subreddit catalogue...")
    table = 'subreddit'
    cols = 'id, name, description, subscribers, active_user_count, over_18, title, created_utc'
    values = []
    for rdt in srs:
        try:
            val = (rdt.id, rdt.display_name, rdt.description, rdt.subscribers, rdt.active_user_count, rdt.over18,
                   rdt.title, rdt.created_utc)
            values.append(val)
        except Exception as error:
            print(error)
    insert_with_replacements(table, cols, values)


def update_comments(comments):
    col = 'id, author, author_id, submission_id, body, created_utc, parent_id, subreddit, subreddit_id, score'
    values = [[0] * 9] * len(comments)
    for i, comment in enumerate(comments):
        try:
            author_name = None if comment.author is None else comment.author.name
            author_id = None
            values[i] = (comment.name, author_name, author_id, comment.submission.id, comment.body, comment.created_utc,
                         comment.parent_id, comment.subreddit.name, comment.subreddit.id, comment.score)
        except Exception as error:
            print(error)
    insert_with_replacements('comment', col, values)
