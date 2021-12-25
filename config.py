

class Config:

    # Threading
    DEFAULT_MAX_THREADS = 16
    DEFAULT_TASK_CHUNKSIZE = 4

    # Reddit
    SUBREDDIT_LIMIT = 150
    SUBMISSION_LIMIT = 100
    COMMENT_LIMIT = 20

    # Batching and Processing Rates
    UPDATE_OLD_BATCH_SIZE = 1000
    UPDATE_OLD_CHUNKSIZE = 20

    STREAM_COMMENT_BATCH_SIZE = 100
    STREAM_SUBMISSION_SIZE = 50
    STREAM_PAUSE_AFTER = 1
