# request_latency_tool

This was written because I wanted a way to measure latency over time for HTTP, DNS, and TCP.

Essentially, the tool establishes a TCP connection, makes a DNS request and an HTTP request and records start and end timestamps for each, 
allowing us to get a latency measurement for each in milliseconds. The results are output to a graph in a PDF. 

This is a first version, and has been succesfully used to troubleshoot latency issues (must be run from different network segments).

The script can run in a docker container on a Ubuntu EC2 instance or VM (docker file not included here).
