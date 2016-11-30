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
