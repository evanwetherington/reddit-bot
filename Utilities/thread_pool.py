import queue
from threading import Thread
from config import *

"""
Multithreaded task executor
"""
class ThreadPool:

    q: queue.Queue = queue.Queue()
    tasks = [()]
    exit_flag: bool

    def __init__(self, tasks=None, threads=Config.DEFAULT_MAX_THREADS):
        if tasks: self.tasks = tasks
        self.threads = threads

    def add_task(self, task, args):
        self.tasks.append((task, args))

    def do_work(self, task, args):
        try:
            if args:
                task(args)
            else:
                task()
        except Exception as ex:
            print(ex)

    def worker(self):
        while not (self.exit_flag or self.q.empty()):
            item = self.q.get()
            try:
                if callable(item):
                    self.do_work(item, None)
                else:
                    self.do_work(item[0], item[1])
            except Exception as ex:
                print(ex)
            self.q.task_done()

    def run(self, wait_for_completion=True):
        self.exit_flag = False
        for item in self.tasks:
            self.q.put(item)
        for i in range(self.threads):
             t = Thread(target=self.worker)
             t.daemon = True
             t.start()
        if wait_for_completion:
            self.q.join()       # block until all tasks are done
            self.exit_flag = True
            self.threads = None
            self.tasks = None




