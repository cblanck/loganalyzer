#!/usr/bin/env python
import fileinput
import os
import re
import sys
import threading
import time

from server import Server
from request import DuplicateEvent

LOG_LOCATION = '/tmp/log_analyzer.out.{}'.format(os.getpid())
LOG_FMT = ('Endpoint: {}\tTotal Requests: {}\t'
           'Average Request Time: {}\tMedian Request Time: {}')
MAX_SERVERS = 10000 

def summarize_all(servers):
    if not servers:
        return
    with open(LOG_LOCATION, 'w') as log:
        for s in servers.itervalues():
            log.write(LOG_FMT.format(*s.summarize())+'\n')
    print 'Analysis complete, logs can be fount at {}'.format(LOG_LOCATION)

def summarize_some(servers):
    if not servers:
        return
    server_list = []
    for s in servers.itervalues():
        id, num_req, avg_req_time, med_req_time  = s.summarize()
        server_list.append((id, num_req, avg_req_time, med_req_time))
    busiest = sorted(server_list, cmp=lambda x,y: cmp(y[1], x[1]))[:5]
    slowest = sorted(server_list, cmp=lambda x,y: cmp(y[2], x[2]))[:5]
    print '====5 Busiest Endpoints===='
    for b in busiest:
        print LOG_FMT.format(*b)
    print '====5 Slowest Endpoints===='
    for s in slowest:
        print LOG_FMT.format(*s)
    print

def pop_least_active_server(servers):
    lowest_inflight = None
    least_active = None
    for s_id, s in servers.iteritems():
        num_inflight = s.get_num_inflight()
        if not lowest_inflight or num_inflight < lowest_inflight:
            lowest_inflight = s.get_num_inflight()
            least_active = s_id
    servers.pop(least_active)

def main():
    last_summary = time.time()
    servers = dict()
    try:
        for line in fileinput.input():
            if time.time() - last_summary >= 30.0:
                summarize_some(servers)
                last_summary = time.time()
            try:
                timestamp, endpoint, req_id, event = line.split(' ')
            except ValueError:
                sys.stderr.write('Invalid log format: {}'.format(line))
                continue
            if endpoint not in servers:
                if len(servers) >= MAX_SERVERS:
                    pop_least_active_server(servers)
                servers[endpoint] = Server(endpoint)
            timestamp = float(timestamp)
            endpoint = endpoint.strip()
            req_id = req_id.strip()
            event = event.strip()
            try:
                servers[endpoint].add_event(timestamp, req_id, event)
            except DuplicateEvent as e:
                sys.stderr.write(('Encountered duplicate event {} sent to '
                                  'endpoint {} with id {} at {}\n').format(event,
                                                                           endpoint,
                                                                           req_id,
                                                                           timestamp))
    except KeyboardInterrupt:
        summarize_all(servers)
    else:
        summarize_all(servers)

if __name__ == '__main__':
    main()
