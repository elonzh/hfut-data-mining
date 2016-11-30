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
