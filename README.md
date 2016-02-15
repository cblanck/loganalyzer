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

Often logs will be processed in batches, so START/FINISH eventscould come out of
order, in this case the program will not use these unfinished requests in determining
busy-ness. This could lead to a situation where an endpoint is hit with a 
multitude of START requests, and crashes as a result, leaving no FINISH events.
This sort of event would not contribute to busy-ness as calculated in this analyzer.
