# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from gevent.pool import Pool
from gevent.queue import Queue

from collections import Iterable

from .log import logger


class JobManager:
    def __init__(self, jobs=None, pool_size=None):
        self.jobs = jobs or []
        self.pool = Pool(pool_size)

    def start(self, dfs_mode=False):
        if not isinstance(self.jobs, Iterable):
            raise TypeError('jobs should be a Iterable, not %s' % type(self.jobs))
        if dfs_mode:
            self.__dfs()
        else:
            self.__bfs()

    def __dfs(self):
        def dispatch(step=0, args=tuple()):
            job = self.jobs[step]
            job_name = '%s%s' % (job.__name__, args)
            logger.info('Dispatching jobs of %s.', job_name)
            rv = job(*args)
            if rv:
                step += 1
                for next_args in rv:
                    # 异步的调用导致快照功能失去了作用, 同时当池大小不够时容易发生死锁
                    self.pool.spawn(dispatch, step, args=next_args)
            logger.info('Jobs of %s have been dispatched.', job_name)

        dispatch()
        self.pool.join()

    def __bfs(self):
        q = Queue()

        # 消费者
        def dispatch(step=0, args=tuple()):
            job = self.jobs[step]
            job_name = '%s%s' % (job.__name__, args)
            logger.info('Dispatching jobs of %s.', job_name)
            rv = job(*args)
            if rv:
                step += 1
                for next_args in rv:
                    q.put((step, next_args))
            logger.info('Jobs of %s have been dispatched.', job_name)

        # 生产者
        q.put((0, tuple()))
        while True:
            while not q.empty():
                self.pool.spawn(dispatch, *q.get())
            self.pool.join()
            if q.empty():
                break


class DatabaseManager:
    def __init__(self, db, pool_size=None, batch_size=50):
        self.db = db
        self.pool = Pool(pool_size)
        self.db = db
        self.batch_size = batch_size
        self.requests = {}

    def request(self, collection, request):
        q = self.requests.setdefault(collection, Queue())
        q.put(request)
        if len(q) >= self.batch_size:
            requests = []
            for i in range(self.batch_size):
                requests.append(q.get())
            # bulk_write 即使两个请求一样也会执行两次
            # https://docs.mongodb.com/v3.2/core/bulk-write-operations/
            # Bulk write operations affect a single collection
            self.pool.spawn(self.db[collection].bulk_write, requests, ordered=False)

    def join(self):
        for collection, queue in self.requests.items():
            requests = []
            while not queue.empty():
                requests.append(queue.get())
            # 避免队列已清空时发送请求导致出错
            if requests:
                self.pool.spawn(self.db[collection].bulk_write, requests, ordered=False)
        self.pool.join()
