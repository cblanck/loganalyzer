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
    def __init__(self, s_id):
        self.id = s_id
        self.requests = dict()
        self.max_active_requests = 10000
        self.num_active_requests = 0
        self.num_requests = 0
        self.avg_request_time = 0
        self.med_request_time = 0
        self.reservoir = Reservoir()

    def get_num_inflight(self):
        return self.num_active_requests

    def add_event(self, time, req_id, event):
        if req_id not in self.requests:
            if self.num_active_requests >= self.max_active_requests:
                self.requests.popitem()
            else:
                self.num_active_requests += 1
            self.requests[req_id] = Request(req_id)
        self.requests[req_id].add_event(time, event)

    def summarize(self):
        num_requests = len(self.requests)        
        total_time = 0
        to_pop = []
        for req_id, request in self.requests.iteritems():
            try:
                req_time = request.get_elapsed_time()
            except UnfinishedRequest:
                num_requests -= 1
                continue
            total_time += req_time
            self.reservoir.add(req_time)
            to_pop.append(req_id)
            self.num_active_requests -= 1
        if (self.num_requests + num_requests) == 0:
            return self.id, 0, 0, 0
        self.avg_request_time = ((self.avg_request_time * self.num_requests) + total_time) / (num_requests + self.num_requests)
        self.num_requests += num_requests
        self.med_request_time = self.reservoir.get_median()

        for req_id in to_pop:
            self.requests.pop(req_id)
        return self.id, self.num_requests, self.avg_request_time, self.med_request_time
