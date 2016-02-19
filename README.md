README
======

Usage
-----

    cat log.txt | analyze.py

Requirements
------------

python 2.7.3 or greater
numpy 1.11.0b3 or greater


Documentation
-------------
This is a python program that analyzes logs via stdin.

The log format is the following whitespace delimited values:
Timestamp, unique endpoint identifier, unique request identifier, START/FINISH token

Every 30 seconds, it will print a list of the 5 average slowest and 5 busiest
endpoints since the program started along with the request count, average timing,
and an approximation of median for each in either list.

This program will continue until the end of input or CTRL-C. Upon exit it will
write request count, average timing and approximate median for all endpoints
to a file (/tmp/loganalyzer.out.$PID) and output the file location to stdout.

As this program is meant to be run in finite memory, the median is calculated 
using a method similar to reservoir sampling. This means that each endpoint
keeps track of a reservoir (currently set at 10000) of requests that are
randomly replaced when the reservoir fills. This ensures an even distribution of
samples without keeping track of each request. The median is calculated based on
this reservoir. While this is not exact, and could throw away valuable data,
it is a good compromise to save space.

Endpoints and requests are also buffered (to 10000 endpoints and 10000 requests
per endpoint) to operate within finite memory. Endpoints are evicted based
on the number of inflight requests at the time of encountering a new endpoint.
The endpoint with the lowest inflight requests will be removed only when a new one
is being added to keep as much timing information intact as possible. While this
does favor more active servers staying around longer, this means that more request
data can be saved in total.

Requests are evicted in two ways: 1. during summarization, which takes place every 
30 seconds, finished requests are rolled into the data for the endpoint that served 
them and  2. when a new request is added that would exceed the max active requests,
an arbitary request is evicted using dict.popitem(). This may result in a situation
where the max active requests is reached for a server, and requests are thrown away
before befing summarized. However, it keeps the add_event function quick, as it 
does not need to decide which requests to throw away.

Often logs will be processed in batches, so START/FINISH eventscould come out of
order, in this case the program will not use these unfinished requests in determining
busy-ness. This could lead to a situation where an endpoint is hit with a 
multitude of START requests, and crashes as a result, leaving no FINISH events.
This sort of event would not contribute to busy-ness as calculated in this analyzer.
