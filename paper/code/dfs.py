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
