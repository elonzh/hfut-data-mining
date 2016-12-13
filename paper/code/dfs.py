def __dfs(self):
    def dispatch(step=0, args=tuple()):
        job = self.jobs[step]
        rv = job(*args)
        if rv:
            step += 1
            for next_args in rv:
                self.pool.spawn(dispatch, step, args=next_args)

                
    dispatch()
    self.pool.join()
