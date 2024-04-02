# request_latency_tool

I once had a need to try and pinpoint where latency was originating from in a web application. This is the initial code I came up with. The tool measures TCP, DNS and HTTP response times and tries to output a visual graph of the results. The results are conveniently output to a graph in a PDF. This is a first version, and has been succesfully used to troubleshoot latency issues (must be run from different network segments). Of course this is only really effective at measuring latency between 2 endpoints (A and B), and if you are troubleshooting an application that goes through several proxies, (A, B, C, D) you will need to run it from different locations... You'd still need to run the tool at different points in the traffic flow to get a more accurate picture. 

This is complete and working (as it is in it's current state), but I will be revising this soon when I have the bandwidth to do so as there are several improvements needed. 
