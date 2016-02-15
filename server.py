import random
from numpy import median
from request import Request, UnfinishedRequest
random.seed()

class Reservoir(object):
    def __init__(self):
        self.max_size = 10000
        self.num_data = 0
        self.reservoir = [None]*self.max_size

    def add(self, n):
        if self.num_data < self.max_size:
            self.reservoir[self.num_data] = n
            self.num_data += 1
        else:
            rand = random.randint(0, self.max_size-1)
            self.reservoir[rand] = n

    def get_median(self):
        median_candidates = filter(lambda x: x is not None, sorted(self.reservoir))
        return median(median_candidates)

class Server(object):
    def __init__(self, id):
        self.id = id
        self.requests = dict()
        self.num_requests = 0
        self.avg_request_time = 0
        self.med_request_time = 0
        self.reservoir = Reservoir()

    def add_event(self, time, req_id, event):
        if req_id not in self.requests:
            self.requests[req_id] = Request(req_id)
        self.requests[req_id].add_event(time, event)

    def summarize(self):
        num_requests = len(self.requests)        
        total_time = 0
        for id, request in self.requests.iteritems():
            try:
                req_time = request.get_elapsed_time()
            except UnfinishedRequest:
                num_requests -= 1
                continue
            total_time += req_time
            self.reservoir.add(req_time)
        if (self.num_requests + num_requests) == 0:
            return self.id, 0, 0, 0
        self.avg_request_time = ((self.avg_request_time * self.num_requests) + total_time) / (num_requests + self.num_requests)
        self.num_requests += num_requests
        self.med_request_time = self.reservoir.get_median()

        self.requests.clear()
        return self.id, self.num_requests, self.avg_request_time, self.med_request_time
