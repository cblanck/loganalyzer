class DuplicateEvent(Exception):
    def __init__(self, id, timestamp, event):
        self.id = id
        self.timestamp = timestamp
        self.event = event

class UnfinishedRequest(Exception):
    pass

class Request(object):
    def __init__(self, req_id):
        self.id = req_id
        self.start_time = None
        self.end_time = None
        self.elapsed_time = None

    def add_event(self, timestamp, event):
        if event == 'START':
            if self.start_time:
                raise DuplicateEvent(self.id, timestamp, event)
            self.start_time = timestamp
        elif event == 'FINISH':
            if self.end_time:
                raise DuplicateEvent(self.id, timestamp, event)
            self.end_time = timestamp

    def get_elapsed_time(self):
        if not self.elapsed_time:
            if self.start_time and self.end_time:
                self.elapsed_time = self.end_time - self.start_time
            else:
                raise UnfinishedRequest
        return self.elapsed_time

    def __str__(self):
        return '<Request id={} start_time={} end_time={} elapsed_time={}'.format(self.id, self.start_time, self.end_time, self.elapsed_time)
